from typing import Literal, Optional
from sqlalchemy import Insert, MetaData, Select, Table, Column, select, text
from sqlalchemy.dialects import mysql, postgresql
from sqlalchemy.sql.cache_key import HasCacheKey
from abc import abstractmethod

from warehouser.db_config import supportedDbms
from warehouser.sql_util import update_columns_str
from warehouser.util import str_joiner
from trent import cmap

# from src.config.db_config import METADATA, supportedDbms
# from src.db.manager.column import update_columns_str


OnConflictLiteral = Literal['error', 'ignore', 'update']





class SQLBuilder():
    def __init__(self, metadata) -> None:
        self._metadata:MetaData = metadata
    
    
    def select(self, table:Table, columns:Optional[list[str|Column]]=None) -> tuple[Select, list[str]]:
        table = self._get_table(table)
        q = select(table)
        cols:list[Column] = []
        if columns:
            cols = [SQLBuilder.__get_col(table, c) for c in columns]
            q = select(*cols)
        else:
            cols = table.columns.values()
            q = select(table)
        res_cols = [c.name for c in cols]
        return (q, res_cols)
            
    
    
    def _get_table(self, table:Table) -> Table:
        if isinstance(table, Table):
            return table
        if table not in self._metadata.tables:
            raise SyntaxError(f'Table {table} is not defined!!')
        return self._metadata.tables[table]
    
    @abstractmethod
    def insert_row(self, table:Table, data_row:dict, /, *,
               update:bool=True) -> Insert:
        pass
    
    @abstractmethod
    def insert_many_rows(self, table:Table, data_rows:list[dict], /, *,
                        ignore:bool=True) -> Insert:
        pass
    
    @abstractmethod
    def insert(self, table:Table, columns:Optional[list]=None, /, *,
                    exclude_cols:list=[],
                    on_conflict_do: OnConflictLiteral = 'update') -> Insert:
        pass
    
    
    @staticmethod
    def __get_col(__table:Table, __col:str|Column):
        if isinstance(__col, Column):
            return __col
        if __col not in __table.columns:
            raise SyntaxError(f'Column {__col} is not defined for table {__table.name}')
        return __table.c[__col]


class MysqlInsert(mysql.Insert, HasCacheKey):
    
    inherit_cache: Optional[bool] = True
     
    def __init__(self, table):
        super().__init__(table)
        
    
    def on_conflict_update(self, columns:Optional[list[str]]):
        t = self.table
        cols:list[Column] = list(t.columns.values()) # type: ignore
        # primary = [k.name for k in t.primary_key]
        # cols = [c for c in cols if c.name not in primary]
        if columns:
            cols = [c for c in cols if c.name in columns]
        if len(cols) <= 0:
            raise Exception('Not columns for INSERT with on_conflict_update statement provided')
        cols_str = update_columns_str(cols, values=True)
        self._post_values_clause = text(f'\n\tON DUPLICATE KEY UPDATE {cols_str}')
        self._gen_cache_key
        return self



class MysqlBuilder(SQLBuilder):
    def __init__(self, metadata) -> None:
        super().__init__(metadata)
        
    
    def insert_row(self, table:Table, data_row:dict, /, *, 
               update:bool=True):
        query = mysql.insert(table).values(data_row)
        if update:
            query = query.on_duplicate_key_update(data_row)
        return query

    
    def insert_many_rows(self, table:Table, data_rows:list[dict], /, *,
                   ignore:bool=True) -> Insert:
        if len(data_rows) <= 0:
            return postgresql.insert(table)
        query = self.insert_row(table, data_rows[0], update=False)
        if ignore:
            query.prefix_with('IGNORE')
        if len(data_rows) > 1:
            for row in data_rows[1:]:
                query.values(row)
        return query
    
    
    def insert(self, table: Table, columns: Optional[list]=None, /, *,
                    exclude_cols:list=[],
                    on_conflict_do: OnConflictLiteral = 'update') -> Insert:
        cols = table.columns.keys()
        cols = [c for c in cols if c not in exclude_cols]
        if columns:
            cols = [c for c in cols if c in columns]
        match on_conflict_do:
            case 'ignore':
                q = mysql.insert(table).prefix_with("IGNORE")
            case 'update':
                q = MysqlInsert(table).on_conflict_update(cols)
            case _:
                q = mysql.insert(table)
        return q
        



class PgBuilder(SQLBuilder):
    def __init__(self, metadata) -> None:
        super().__init__(metadata)
    
    
    def insert_row(self, table:Table, data_row:dict, /, *,
               update:bool=True) -> Insert:
        query = postgresql.insert(table)
        if update:
            query = query.on_conflict_do_update(index_elements=table.primary_key, set_=data_row)
        return query
    
    
    def insert(self, table: Table, columns: Optional[list] = None, /, *,
               exclude_cols: list = [],
               on_conflict_do: OnConflictLiteral = 'update') -> Insert:
        q = postgresql.insert(table)
        
        if on_conflict_do == 'ignore':
            q = q.on_conflict_do_nothing(constraint=table.primary_key)
        elif on_conflict_do == 'update':
            primary_keys = list(table.primary_key.columns)
            update_cols = [c.name for c in table.c if c.name not in exclude_cols]
            __set = {k: q.excluded.get(k) for k in update_cols}
            q = q.on_conflict_do_update(index_elements=primary_keys, set_=__set)
        
        return q


class DorisBuilder(SQLBuilder):
    def __init__(self, metadata) -> None:
        super().__init__(metadata)
    
    def insert_row(self, table: Table, data_row: dict, /, *, 
                   update: bool = True):
        q = mysql.insert(table).values(data_row)
        return q
    
    
    def insert(self, table: Table, columns: Optional[list] = None, /, *,
               exclude_cols: list = [],
               on_conflict_do: OnConflictLiteral = 'update') -> Insert:
        q = mysql.insert(table)
        return q


def make_sql_builder(mtd: MetaData, dbms: supportedDbms) -> SQLBuilder:
    match dbms:
        case 'mysql':
            return MysqlBuilder(mtd)
        case 'postgres':
            return PgBuilder(mtd)
        case 'doris':
            return DorisBuilder(mtd)