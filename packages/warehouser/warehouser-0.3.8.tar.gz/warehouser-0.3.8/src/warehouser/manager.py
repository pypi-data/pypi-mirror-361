from collections.abc import Callable
from logging import Logger
from typing import Iterable, Optional

import numpy as np
import pandas as pd
from sqlalchemy import MetaData, Row, Select, Table, select, ScalarResult

from warehouser.base_manager import BaseWarehouser, TableArgType
from warehouser.db_config import WarehouserConfig
from warehouser.reflection import gen_table_model_str
from warehouser.sql_util import reflect_table
from warehouser.util import identity


class Warehouser(BaseWarehouser):
    def __init__(self,
                 database: str,
                 config: WarehouserConfig,
                 metadata: MetaData,
                 /, *,
                 logger: Optional[Logger] = None,
                 partition_size:int=500,
                 safe:bool=True) -> None:
        super().__init__(database, config, metadata,
                         logger=logger,
                         partition_size=partition_size,
                         safe=safe)
    
    
    # ========================================================================================
    #               READ / WRITE
    
    def select_to_df(self, query: Select) -> pd.DataFrame:
        with self.conn() as c:
            df = pd.read_sql(query, c)
        df = df.replace({np.nan: None, pd.NaT: None})
        return df



    # ========================================================================================
    #               BACKUP
    
    
    def backup_table(self, table:TableArgType, target_dbm:Optional[BaseWarehouser]=None):
        target_dbm = target_dbm if target_dbm else self
        t = self.get_table(table)
        if t.schema is not None:
            raise Exception(f'Backup for {t.fullname} FAILED: Can only backup tables from current database!')
        __reflected = reflect_table(self._metadata, self.eng(), t.name)
        if __reflected is None:
            raise Exception(f'Failed to reflect table "{t.fullname}"')
        bak = self.table_backup_copy(t)
        target_dbm.remake_table(bak)
        data = self.select_from(__reflected)
        target_dbm.upsert(bak, data)
            
    
    def restore_table(self, table:TableArgType, source_dbm:Optional[BaseWarehouser]=None) -> bool:
        source_dbm = source_dbm if source_dbm else self
        t = self.get_table(table)
        bak = self.table_backup_copy(t)
        if not source_dbm.is_table_exists(bak.name):
            raise Exception(f"Failes to restore table: {t.fullname} from backup: {bak.fullname}. Backup doesn't exist.")
        data = source_dbm.select_from(bak)
        self.rebuild_table(t, data)
        return True
    
    
    def reassemble_table(self, table:TableArgType) -> bool:
        t = self.get_table(table)
        if t.schema is not None:
            raise Exception(f'Reassembling for {t.fullname} FAILED: Can only backup tables from current database!')
        __reflected = reflect_table(self._metadata, self.eng(), t.name)
        if __reflected is None:
            raise Exception(f'Failed to reflect table "{t.fullname}"')
        self.backup_table(t)
        try:
            self.remake_table(t)
            __safe = self._safe
            self._safe = False
            self.restore_table(t)
            self._safe = __safe
            return True
        except:
            self._logger.debug('''
FAILED reassembling table, reverting back!
Check if you dont have any new NOT NULL columns in table!''')
            self.restore_table(__reflected)
            return False
    
    
    def table_backup_copy(self, table:TableArgType) -> Table:
        """Makes table copy with new name, for backup.

        Args:
            table (TableArgType): Table|type[DeclarativeBase]

        Returns:
            Table: Table
        """        
        t = self.get_table(table)
        bak = self._make_table_copy(t, Warehouser._backup_name(t))
        return bak
    
    
    # ====================================================================================
    #               REFLECTION
    
    def reflect_table(self, table_name: str, /, *, database: Optional[str] = None) -> Table:
        """Reflect table by name, for local database, of for `database`, if provided.
        Table `table_name` MUST BE created in databse.

        Args:
            table_name (str): Reflected table name.
            database (Optional[str], optional): external database, if needed. Defaults to None.

        Raises:
            Exception: Raises exception if table is not found.

        Returns:
            Table: Reflected table
        """        
        eng = self.eng(database)
        t = reflect_table(self._metadata, eng, table_name)
        if t is None:
            raise Exception(f'Failed to reflect table {table_name}!')
        return t
    
    
    def model_str_from_table(self, table: Table, /, *,
                             with_description: bool = False) -> str:
        """Generates str with ORM model definition from Table provided.

        Args:
            table (Table): sqlalchemy Table object
            with_description (bool, optional): if True: generate description for ALL columns, regardless of need for it. Defaults to False.

        Returns:
            str: ORM model class definition in str.
        """        
        return gen_table_model_str(table)
    
    
    def model_str_from_reflection(self, table_name: str, /, *,
                                  database: Optional[str] = None,
                                  with_description: bool = False,
                                  with_comments: bool = True):
        """Reflects table by name, and generates ORM model class for it.

        Args:
            table_name (str): Table name in str
            database (Optional[str], optional): External database name, if needed. Defaults to None.
            with_description (bool, optional): If True: generate description for all columns, regardless of need for it.. Defaults to False.

        Returns:
            str: ORM model class definition in string.
        """         
        t = self.reflect_table(table_name, database=database)
        return gen_table_model_str(t, with_description=with_description,
                                   with_comments=with_comments)
        
        
    
    # ====================================================================================
    #               MIGRATION
    
    def migrate_table_to(self, table: TableArgType, dest: "Warehouser", /, *,
                         rewrite: bool = False,
                         remake: bool = False,
                         create_if_not_exists: bool = False,
                         partition_size: Optional[int] = None,
                         row_map_fn: Callable[[dict], dict] = identity):
        if isinstance(table, str):
            t = reflect_table(self._metadata, self.eng(), table)
        else:
            t = self.get_table(table)
        if t is None:
            return
        if create_if_not_exists:
            dest.create_table(t)
        elif remake:
            self._logger.debug(f'Remaking table {dest.dbms}|{dest.database}|{t.fullname}')
            dest.remake_table(t)
        self._logger.debug(f'Migrating table "{t.name}"')
        if rewrite:
            self._logger.debug(f'Cleaning up table {dest.dbms}|{dest.database}|{t.fullname}')
            dest.clean_table(t, approve_clean_table=True)
        _part_size = partition_size if partition_size else dest.partition_size
        q = select(* t.columns).execution_options(yield_per=_part_size)
        with self.sess() as s:
            rows = s.scalars(q)
            rows = map(Row._asdict, rows)
            rows = map(row_map_fn, rows)
            dest.upsert(t, rows, with_last_updated=True, chunk_size=_part_size)
    
    
    def migrate_tables(self, tables:Iterable[TableArgType], dbm: "Warehouser"):
        for t in tables:
            self.migrate_table_to(t, dbm)
    
    
    def __upser_data_to_remote(self, dbm: BaseWarehouser, table:TableArgType, data: Iterable[dict]) -> bool:
        if isinstance(table, str):
            t = reflect_table(self._metadata, self.eng(), table)
        else:
            t = self.get_table(table)
        if t is None:
            return False
        dbm.upsert(t, data)
        return True
    
    
    def migrate_data(self, table:TableArgType, dbm: BaseWarehouser) -> bool:
        t = self.get_table(table)
        data = self.select_from(t)
        return self.__upser_data_to_remote(dbm, table, data)
    
    
    @staticmethod
    def _backup_name(table:Table) -> str:
        return f'_{table.name}__dbm_backup'
    
    
    def _make_table_copy(self, table:Table, name:str) -> Table:
        __reflected = reflect_table(self._metadata, self.eng(), table.name)
        __table = __reflected if __reflected is not None else table
        res = Table(name, MetaData(), *[col.copy() for col in __table.columns.values()])
        return res