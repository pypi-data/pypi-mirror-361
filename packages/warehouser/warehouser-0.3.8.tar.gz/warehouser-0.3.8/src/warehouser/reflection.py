from decimal import Decimal
from pprint import pprint
from typing import Optional
from sqlalchemy import Column, Date, DateTime, Double, Engine, Integer, MetaData, Numeric, String, Table, Enum
from sqlalchemy.orm import mapped_column


# ===============================================

def reflect_table(mtd: MetaData, eng:Engine, table_name: str, /) -> Optional[Table]:
    try:
        return Table(table_name, mtd, autoload_with=eng)
    except:
        return None


# ======================================================================
#                         MODEL AUTO GENERATION
# ======================================================================


def _col_mapped_type(c: Column) -> str:
    pytype = c.type.python_type
    if pytype == Decimal:
        pytype = float
    res = f'Optional[{pytype.__name__}]' if c.nullable else f'{pytype.__name__}'
    return res


def _col_sql_type(c: Column) -> tuple[bool, str]:
    is_described = False
    tp = c.type.as_generic()
    stype_str = str(tp)
    if isinstance(tp, Double):
        stype_str = 'Double()'
        is_described = True
    elif isinstance(tp, Enum):
        stype_str = f'Enum{tuple(tp.enums)}'
        is_described = True
    elif isinstance(tp, String):
        if tp.length:
            stype_str = f'String({tp.length})'
            is_described = True
        else:
            stype_str = 'Text'
    elif isinstance(tp, DateTime):
        stype_str = 'DateTime(False)'
        # is_described = True
    elif isinstance(tp, Date):
        stype_str = 'Date()'
    elif isinstance(tp, Integer):
        stype_str = 'Integer()'
    elif isinstance(tp, Numeric):
        stype_str = f'Numeric({tp.precision}, {tp.scale})'
        is_described = True
    return (is_described, stype_str)


def _col_comment(include: bool, c: Column) -> tuple[bool, str]:
    if not include or c.comment is None:
        return (False, '')
    return (True, f', comment="{c.comment}"')


def _col_description(c: Column, *, for_all: bool = False,
                     include_comments: bool = True):
    is_col_described, stype_str = _col_sql_type(c)
    is_commented, comment_str = _col_comment(include_comments, c)
    is_described = for_all or c.primary_key or is_col_described or is_commented
    
    primary_str = ', primary_key=True' if c.primary_key else ''
    nullable_str = ', nullable=True' if c.nullable and not c.primary_key else ''
    
    description_str = f' = mapped_column({stype_str}{primary_str}{nullable_str}{comment_str})' if is_described else ''
    return description_str


def _col_to_mapped_str(c:Column, with_description:bool=False,
                       with_comments: bool = True) -> str:
    name = c.name
    mapped_type_str = _col_mapped_type(c)
    mapped_str = f'Mapped[{mapped_type_str}]'
    description_str = _col_description(c, for_all=with_description,
                                       include_comments=with_comments)
    res = f'    {name}: {mapped_str}{description_str}'
    return res


def gen_table_model_str(t:Table, *, with_description: bool = False,
                        with_comments: bool = True,) -> str:
    t_name = ''.join(x for x in t.name.title() if not x.isspace())
    t_name = t_name.replace('_', '')
    header_str = f'class {t_name}(Base):'
    header_str += f"\n    __tablename__ = '{t.name}'\n"
    col_strs = []
    for c in t.columns:
        if c.name != 'last_updated':
            col_strs.append(_col_to_mapped_str(c,
                                               with_description=with_description,
                                               with_comments=with_comments))
    colsstr = str.join("\n", col_strs)
    res = f'{header_str}\n{colsstr}'
    return res


def create_model_from_reflection(mtd: MetaData, eng:Engine, table_name:str, /, *,
                                 with_description: bool = False,
                                 with_comments: bool = True):
    t = reflect_table(mtd, eng, table_name)
    if t is None:
        raise Exception(f'Failed to reflect table: {table_name}')
    model_str = gen_table_model_str(t, with_description=with_description,
                                    with_comments=with_comments)
    return model_str