import logging
import logging.config
import os
from typing import Any, Callable, Literal, Optional


class DbLoggerBase:
    def __init__(self) -> None:
        pass
    
    def error(self, msg:str):
        print(msg)

    def exception(self, e:Exception):
        print(e)
        
    def warn(self, msg:str|Exception|Warning):
        print(msg)

    def info(self, msg):
        print(msg)
        
    def debug(self, msg):
        print(msg)


class DbLogger(DbLoggerBase):
    def __init__(self, logger: logging.Logger) -> None:
        self._logger: logging.Logger = logger
    
    
    def error(self, msg:str):
        self._logger.error(msg)

    def exception(self, e:Exception):
        self._logger.exception(e)
        
    def warn(self, msg:str|Exception|Warning):
        if isinstance(msg, str):
            self._logger.warning(msg)
        else:
            self._logger.warning(msg, exc_info=True)

    def info(self, msg):
        self._logger.info(msg)
        
    def debug(self, msg):
        self._logger.debug(msg)


def make_db_logger(logger: Optional[logging.Logger] = None) -> DbLoggerBase:
    if logger:
        return DbLogger(logger)
    return DbLoggerBase()
