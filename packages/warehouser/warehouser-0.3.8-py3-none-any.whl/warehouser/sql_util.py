from typing import Any, Optional
from sqlalchemy import Column, Engine, MetaData, Table
from trent import cfilter, cmap, coll

from warehouser.const import LAST_UPDATE_COLUMN_NAME
from warehouser.util import constantly, identity, str_joiner


def _get_table_columns(table:Table, *, 
                       filter_fn=constantly(True),
                       mapper_fn=identity) -> list[Column]:
    cols = table.columns.values()
    return cfilter(filter_fn, cols).map(mapper_fn).to_list()


def _is_data_column(column:Column):
    return column.name != LAST_UPDATE_COLUMN_NAME


def update_columns_str(columns:list[Column], *, values:bool=False) -> str:
    def __update_str(col:Column):
        __name = col.name
        if values:
            return '\n\t\t' + __name + f' = VALUES({__name})'
        return '\n\t\t' + __name + ' = %s'
    columns_str:str = cmap(__update_str, columns).reduce(str_joiner(', '))
    return columns_str


def _table_data_columns(table:Table) -> list[Column]:
    res = _get_table_columns(table, filter_fn=_is_data_column)
    if not res or len(res) == 0:
        raise Exception(f'Table {table} has no data columns!')
    return res


def table_data_columns(table:Table, columns:Optional[list[str]]=None) -> list[Column]:
    data_columns =  _table_data_columns(table)
    cols = coll(data_columns)
    if columns:
        invalid = cfilter(lambda c: c not in table.columns, columns).to_list()
        if len(invalid) > 0:
            raise Exception(f'Columns {invalid} are not present in table {table}!!!')
        cols.filter(lambda c: c.name in columns) 
    return cols.to_list()


def reflect_table(mtd: MetaData, eng:Engine, table_name:str) -> Optional[Table]:
    try:
        return Table(table_name, mtd, autoload_with=eng)
    except:
        return None