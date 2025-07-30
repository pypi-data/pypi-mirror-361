# from dbmanager.alchemy import is_table_defined
from logging import Logger
from typing import (
    Any,
    Dict,
    Hashable,
    Iterable,
    Literal,
    Optional,
    Tuple,
    Type,
    TypeAlias,
    TypeVar,
)

import numpy as np
import pandas as pd
from sqlalchemy import (
    ColumnElement,
    Connection,
    Delete,
    Engine,
    Insert,
    MetaData,
    Result,
    Row,
    ScalarResult,
    Select,
    Table,
    TextClause,
    Update,
    create_engine,
    delete,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Session

from warehouser.const import LAST_UPDATE_COLUMN_NAME
from warehouser.db_config import WarehouserConfig, supportedDbms

# from dbmanager.log import debug, exception
from warehouser.log import DbLogger, DbLoggerBase, make_db_logger
from warehouser.reflection import reflect_table
from warehouser.sql_builder import SQLBuilder, make_sql_builder
from warehouser.sql_util import table_data_columns
from warehouser.util import (
    current_utc_timestamp,
    getin,
    isnot_none,
    make_dict,
    partition_iter,
    run_with_retry,
    select_keys,
)

sqlQueryType: TypeAlias = Select|Insert|Update|Delete|TextClause
TableArgType = str|Table|Type[DeclarativeBase]

T = TypeVar('T')
_TP = TypeVar("_TP", bound=Tuple[Any, ...])

class BaseWarehouser():
    def __init__(self, database, config: WarehouserConfig, metadata: MetaData, *,
                partition_size:int=500,
                safe:bool=True,
                logger: Optional[Logger] = None) -> None:
        self._logger: DbLoggerBase = make_db_logger(logger)
        self._config: WarehouserConfig = config
        self._config.database = database
        self._sql_builder:SQLBuilder = make_sql_builder(metadata, self._config.dbms)
        self._safe = safe
        self._partition:int = partition_size
        self._eng = create_engine(self._config.engine_str())
        self._metadata: MetaData = metadata
        self._session: Optional[Session] = None
        self._db_engines: dict[str, Engine] = {}
    
    
    # ====================   INTERFACE   ========================
    
    @property
    def dbms(self) -> supportedDbms:
        return self._config.dbms
    
    @property
    def dialect(self) -> supportedDbms:
        return self._config.dbms
    
    @property
    def database(self) -> str:
        return self._config.database
    
    @property
    def partition_size(self) -> int:
        return self._partition
    
    @property
    def connection(self) -> Connection:
        return self.conn()
    
    @property
    def session(self) -> Session:
        return self.sess()
    
    @property
    def engine(self) -> Engine:
        return self.eng()
    
    
    def conn(self, database:Optional[str]=None) -> Connection:
        if not database:
            return self._eng.connect()
        eng = self.eng(database)
        return eng.connect()
    
    
    def sess(self, database:Optional[str]=None, /, *,
             autobegin: bool = True) -> Session:
        if not database:
            return Session(self._eng)
        eng = self.eng(database)
        return Session(eng, autobegin=autobegin)
    
    
    def eng(self, database:Optional[str]=None, /) -> Engine:
        """Createds a new sqlalchemy engine, using credentials from DBmanagerConfig provided.

        Args:
            database (Optional[str], optional): If provided: Engine will be created connected to specified database. Defaults to None.

        Returns:
            Engine: sqlalchemy Engine object
        """        
        if not database:
            return self._eng
        if database in self._db_engines:
            return self._db_engines[database]
        host, port, user, password = self._config.db_params()
        eng = WarehouserConfig.make_engine(self._config.dbms, user, password, host, port, database=database)
        self._db_engines[database] = eng
        return eng
    
    
    def is_table_exists(self, table_name):
        q = f'''
        SELECT * FROM information_schema.tables
        WHERE
            table_schema = "{self._config.database}" AND 
            table_name = "{table_name}"
        
        '''
        q = text(q)
        res = self._select(q)
        if len(res) > 1:
            raise Exception(f"There are more than one table: {self._config.database}.{table_name}!!!")
        return len(res) == 1
    
    
    def is_table_defined(self, table:str|Table):
        if isinstance(table, Table):
            return True
        return table in self._metadata.tables
    
    
    def create_table(self, table:TableArgType) -> bool:
        """Creates a table using existing definition (either a Table or Orm model).\n
        --- Use `DBmanager.remake_table` if you have a need to update table structure.\n
        --- Use `DBmanager.rebuild_table` to completely rewrite table with new data (and updated structure as side-effect).

        Args:
            `table` (TableArgType): Table to create.

        Returns:
            bool: Flag, indicating wheathe a new table was created. (True - ONLY when new table was CREATED. If it already existed - False)
        """        
        t = self.get_table(table)
        try:
            with self.sess() as s:
                with s.connection() as c:
                    exists = self._eng.dialect.has_table(c, t.name)
        except Exception as e:
            self._logger.exception(e)
            return False
        if exists:
            self._logger.debug(f"Table {t.name} already exists. Skipping CREATE TABLE.")
            return False
        t.create(self._eng)
        return True
    
    
    def drop_table(self, table:TableArgType):
        if self._safe:
            raise Exception("Can't drop any tables in safe mode.")
        t = self.get_table(table)
        self.__drop_table(t)
    
    
    # ============================================================================
    
    def remake_table(self, table:TableArgType, *,
                     approve_drop_table: bool = False):
        t = self.get_table(table)
        def __remake():
            self.__drop_table(t, approve_drop_table=approve_drop_table)
            self.create_table(t)
        run_with_retry(__remake, self._retries(), logger=self._logger)
        return t.name
    
    
    def rebuild_table(self, table:TableArgType, data:pd.DataFrame|Iterable[dict]|dict, *,
                       soft=True,
                       approve_drop_table: bool = False):
        self.remake_table(table, approve_drop_table=approve_drop_table)
        return self.upsert(table, data)
    
    
    def rewrite_table(self, table: TableArgType, data: pd.DataFrame|Iterable[dict]|dict, *,
                      chunk_size: Optional[int] = None,
                      approve_clean_table: bool = False) -> int:
        t = self.get_table(table)
        self.clean_table(t, approve_clean_table=approve_clean_table)
        return self.upsert(t, data, chunk_size=chunk_size)
    
    
    # ============================================================================
    
    def execute(self, sql_query:sqlQueryType, parameters=None):
        def __exec():
            with self.conn() as conn:
                with conn.begin():
                    res = conn.execute(sql_query, parameters=parameters)
            return res
        return run_with_retry(__exec, self._retries(), logger=self._logger)
    
    
    def s_execute(self, session: Session, sql_query:sqlQueryType) -> Optional[Result[Any]]:
        def __exec():
            with session.begin():
                res = session.execute(sql_query)
            return res
        return run_with_retry(__exec, logger=self._logger)
    
    
    def select_from(self, table:TableArgType, *,
                    columns=None,
                    where:Optional[str|ColumnElement]=None,
                    with_last_update=False) -> list[dict[str, Any]]:
        t = self.get_table(table)
        query, cols = self._sql_builder.select(t, columns)
        if where is not None:
            if isinstance(where, str):
                query = query.where(text(where))
            else:
                query = query.where(where)
        res = self._select(query)
        res = [make_dict(cols, vals) for vals in res]
        return res
    
    
    def upsert(self, table:TableArgType, data:pd.DataFrame|Iterable[Optional[Dict]]|Dict, *,
               with_last_updated: bool = False,
               chunk_size:Optional[int]=None) -> int:
        self.__except_if_not_defined(table)
        data_list = BaseWarehouser._prepare_rows(data)
        t = self.get_table(table)
        chunk_size = chunk_size if chunk_size else self._partition
        
        res = self._upsert_chunked(t, chunk_size, data_list, with_last_updated=with_last_updated)
        return res
    
    
    def insert(self, table: TableArgType, data:Iterable[dict]|dict, /, *,
               columns=None,
               on_colflict_ignore: bool = True,
               chunk_size:Optional[int] = None) -> int:
        data_list = BaseWarehouser._prepare_rows(data)
        t = self.get_table(table)
        chunk_size = chunk_size if chunk_size else self._partition
        __on_conflict = 'ignore' if on_colflict_ignore else 'error'
        q = self._sql_builder.insert(t, columns, exclude_cols=[LAST_UPDATE_COLUMN_NAME],
                                     on_conflict_do=__on_conflict)
        count = self._insert_chunked(q, chunk_size, data_list)
        return count
    
    
    def select(self, query: Select[_TP]) -> list[Row[_TP]]:
        with self.sess() as s:
            rows = s.execute(query)
            res = list(rows)
        return res
    
    
    def scalars(self, query: Select[Tuple[T]]) -> list[T]:
        with self.sess() as s:
            rows = s.scalars(query)
            res = list(rows)
        return res
    
    
    # =====================   PRIVATE   =============================

    
    def __except_if_not_defined(self, table:TableArgType):
        if isinstance(table, Table):
            return True
        __t = self.get_table(table)
        return True
    
    
    def _insert_chunked(self, q:Insert, chunk_size: int, data_list: Iterable[dict], /) -> int:
        data_chunks = partition_iter(data_list, chunk_size)
        def __insert() -> int:
            rows_count = 0
            with self.conn() as conn:
                for chunk in data_chunks:
                    rows = list(chunk)
                    rows_count += len(rows)
                    with conn.begin():
                        conn.execute(q, rows)
                return rows_count
        res = run_with_retry(__insert, self._retries(), logger=self._logger)
        if res is None:
            raise Exception('Failed to upsert data!!')
        return res
    

    def _upsert_chunked(self, table:Table, chunk_size:int, data_seq:Iterable[dict], /, *,
                        with_last_updated: bool = False) -> int:
        q = self._sql_builder.insert(table, on_conflict_do='update')
        cols = [c.name for c in table_data_columns(table)]
        if with_last_updated:
            cols.append(LAST_UPDATE_COLUMN_NAME)
        def _keys(_row):
            return select_keys(_row, cols)
        rows = map(_keys, data_seq)
        if not with_last_updated:
            ts = current_utc_timestamp()
            def _add_lu(row):
                row[LAST_UPDATE_COLUMN_NAME] = ts
                return row
            rows = map(_add_lu, rows)
        return self._insert_chunked(q, chunk_size, rows)
        
    
    
    def _select(self, query:Select|TextClause) -> list:
        res = None
        res = self.execute(query)
        if res:
            return list(res)
        print('Failed to select data from DBmanager')
        return []
    
    
    def __drop_table(self, table:str|Table, *,
                     approve_drop_table: bool = False) -> bool:
        
        if not self.is_table_defined(table):
            return False
        t = self.get_table(table)
        if not approve_drop_table:
            inp = input(f' > Are you SURE you want to drop {t.fullname}?!!! [Yes/No]: ')
            if inp.lower() != 'yes':
                self._logger.info(f' >>> NOT dropping table {t.fullname}.')
                return False
        self._logger.debug(f' >>> Dropping table {t.fullname}.')
        try:
            with self.sess() as s:
                with s.connection() as c:
                    exists = self._eng.dialect.has_table(c, t.fullname)
        except Exception as e:
            self._logger.exception(e)
            return False
        if not exists:
            self._logger.debug(f"Table '{t.fullname}' does not exist. Skipping DROP TABLE.")
            return False
        if not self._safe and self._config.dbms == 'mysql':
            self.execute(text('SET FOREIGN_KEY_CHECKS=0'))
        t.drop(self._eng)
        if not self._safe and self._config.dbms == 'mysql':
            self.execute(text('SET FOREIGN_KEY_CHECKS=1'))
        return True
    
    
    def clean_table(self, table:TableArgType, *,
                    approve_clean_table: bool = False):
        t = self.get_table(table)
        if not approve_clean_table:
            inp = input(f' > Are you SURE you want to CLEAN {t.fullname}?!!! [Yes/No]: ')
            if inp.lower() != 'yes':
                self._logger.info(f' >>> NOT cleaning table {t.fullname}.')
                return False
        q = delete(t)
        def __del():
            with self.sess() as s:
                with s.begin():
                    s.execute(q)
        run_with_retry(__del, self._retries(), logger=self._logger)
    
    
    def _retries(self) -> int:
        if self._safe:
            return 5
        return 0
    
    
    def get_table(self, table:TableArgType, /) -> Table:
        t = BaseWarehouser.__get_table(self._metadata, table)
        if t is None and isinstance(table, str):
            t = reflect_table(self._metadata, self.eng(), table)
        if t is None:
            raise SyntaxError(f'Table {table} is not defined!! And failed to reflect!!')
        return t
    
    # =======================================================================
    
    def __repr__(self) -> str:
        return f'DBmanager[{self._config.dbms}:"{self._config.engine_str()}"]'
    
    
    # =======================================================================
    #           SESSION CONTEXT
    
    def __enter__(self) -> Session:
        self._session = self.sess()
        return self._session
        
    
    def __exit__(self, type, value, traceback) -> bool:
        if type or self._session is None:
            return False
        self._session.close()
        del self._session
        self._session = None
        return True
    
    # =======================================================================
    #                       STATIC
    
    @staticmethod
    def _prepare_rows(rows: pd.DataFrame|Dict[str, Any]|Iterable[Optional[Dict[str, Any]]]) -> Iterable[Dict[Hashable, Any]]:
        if rows is None:
            return []
        if isinstance(rows, pd.DataFrame):
            rows = rows.replace({np.nan: None, pd.NaT: None})
            return rows.to_dict('records')
        if isinstance(rows, dict):
            return [rows] # type: ignore
        if isinstance(rows, Iterable):
            return filter(isnot_none, rows) # type: ignore
        raise Exception(f'Value {rows} must be Dict or Iterable!!')
    
    
    @staticmethod
    def __get_table(metadata: MetaData, table:TableArgType) -> Optional[Table]:
        """Returns table by table_name, if it is defined in _definitions or _op_defs.

        Args:
            table (str | Table): table name, or Table itself (added for consisntecy in code)

        Raises:
            SyntaxError: If table is not difend

        Returns:
            Table: SQL table
        """
        assert isinstance(table, str|Table) or issubclass(table, DeclarativeBase), 'Table must be of type str|Table|Type[Base]' 
        if isinstance(table, Table):
            return table
        if isinstance(table, str):
            if table in metadata.tables:
                return metadata.tables[table]
            return None
        tname = table.__tablename__
        schema = getin(table.__table_args__, ['schema'])
        if schema:
            tname = f'{schema}.{tname}'
        if tname in table.metadata.tables:
            return table.metadata.tables[tname]
        return None