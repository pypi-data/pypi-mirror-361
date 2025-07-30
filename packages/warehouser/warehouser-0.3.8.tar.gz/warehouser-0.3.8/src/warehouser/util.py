from datetime import datetime, timezone
from itertools import groupby
import os
import time
from typing import Any, Callable, Hashable, Iterable, Sequence, TypeAlias, TypeVar

from warehouser.log import DbLogger, DbLoggerBase, make_db_logger

# from dbmanager.log import error, exception


# ================================================================

T = TypeVar('T')
T1 = TypeVar('T1')
T2 = TypeVar('T2')


# ==============================================================
#           FUNC

def constantly(val):
    return lambda *args: val


def identity(val):
    return val


def isnone(val) -> bool:
    return val is None


def isnot_none(val) -> bool:
    return val is not None


def _join_str_list(s, str_list):
    if not str_list:
        return None
    return str.join(s, str_list)


def str_joiner(join_str) -> Callable[[Any, Any], Any]:
    return lambda str1, str2: _join_str_list(join_str, [str1, str2])

# ================================================================
#           ITERATION

class PartCounter:
    def __init__(self, count: int) -> None:
        self.__count = count
        self.__i = 0
        self.__part_number = 0
        
    def __call__(self, *_) -> int:
        if self.__i >= self.__count:
            self.__i = 0
            self.__part_number += 1
        self.__i += 1
        return self.__part_number

def partition_iter(coll: Iterable, part_size: int, /) -> Iterable[tuple]:
    """
    Lazily partition the iterable into tuples of the given size.

    Args:
    `coll` (iterable): The iterable to be partitioned.
    `part_size` (int): The size of each tuple.

    Yields:
    tuple: Tuples of the given size from the iterable.
    """
    
    # __iterate = True
    groups = groupby(coll, PartCounter(part_size))
    for _, g in groups:
        yield tuple(g)


# ==============================================================
#           DICT

GetInKey: TypeAlias = str|Hashable|Callable
GetInPath: TypeAlias = Sequence[GetInKey]|GetInKey

def _try_get_key(d:dict, key: GetInKey) -> tuple[Any, bool]:
    try:
        if callable(key):
            return (key(d),True)
        if key not in d:
            return (None, False)
        return (d[key], True)
    except:
        return (None, False)


def getin(dictionary:dict, keys:Sequence[GetInKey], default:Any=False) -> Any:
    res = dictionary
    for k in keys:
        res, success = _try_get_key(res, k)
        if not success:
            return default
    return res


def select_keys(dictionary:dict, keys:list, /) -> dict:
    return {k: dictionary.get(k) for k in keys}


def get_keys(dictionary:dict, keys:Sequence[Hashable], /) -> tuple:
    return tuple(dictionary.get(k) for k in keys)


def make_dict(keys: Iterable[T1], vals: Iterable[T2]) -> dict[T1, T2]:
    pairs = [(k, v) for k, v in zip(keys, vals)]
    return dict(pairs)


# ===========================================================
#           RETRY


T = TypeVar('T')
retryFn: TypeAlias = Callable[[None], T]

def run_with_retry(f: Callable[[], T], retry_count=3, *,
                   logger: DbLoggerBase,
                   timeout:int=10,
                   ) -> T:
    retries = retry_count
    running = True
    result = None
    while running:
        try:
            result = f()
            return result
        except Exception as e:
            logger.exception(e)
            if retries <= 0:
                running = False
                raise
            logger.error(f'Failed running fn. Retries left: {retries}')
            retries -= 1
            time.sleep(timeout)
    raise Exception("Failed to execute function with retry!!!")


# ===============================================================
#           DATE

def current_utc_timestamp():
    return datetime.now(timezone.utc)