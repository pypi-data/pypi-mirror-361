from sqlalchemy import Engine, create_engine
from warehouser.util import get_keys
from typing import Literal, Optional, TypeAlias, get_args



supportedDbms = Literal['mysql', 'postgres', 'doris']
dbmsConfigDict = dict[Literal['host', 'port', 'user', 'password'], str]
dbConfigDict: TypeAlias = dict[Literal['dbms', 'host', 'port', 'user', 'password', 'database'], str]


MYSQL_DEFAULT_PORT = "3306"
PG_DEFAULT_PORT = "5432"
DORIS_DEFULT_PORT = "9030"


MYSQL_ENGINE = 'pymysql'

portType: TypeAlias = str|int

def _default_port(rdbms:supportedDbms) -> str:
    match rdbms:
        case 'mysql':
            return MYSQL_DEFAULT_PORT
        case 'postgres':
            return PG_DEFAULT_PORT
        case 'doris':
            return DORIS_DEFULT_PORT
    raise SyntaxError(f'Unsupported RDBMS: {rdbms}')


def _engine_type(rdbms:supportedDbms) -> str:
    match rdbms:
        case 'mysql':
            return f'mysql+{MYSQL_ENGINE}'
        case 'postgres':
            return 'postgresql+psycopg2'
        case 'doris':
            return f'doris+{MYSQL_ENGINE}'
    raise SyntaxError(f'Unsupported RDBMS: {rdbms}')





class WarehouserConfig:
    """DBmanager config class.
    Contains full database config data, needed for connection and vendor specific logic.
    Contains fields:
        dbms (str): Database management system name. Can be on of: ['mysql', 'postgres']\n
        host (str): DBMS host\n
        port (str): DBMS port\n
        user (str): DBMS user name\n
        pwd (str): DBMS user password\n
        database (str, optional): Database name to be used in connection. Defaults to None.
    """
    def __init__(self, dbms: supportedDbms, database: str, user: str, pwd: str, /, *,
                 host: str = 'localhost',
                 port: Optional[portType] = None) -> None:
        """Creates config object for DBmanager.

        Args:
            dbms (str): Database management system name. Can be on of: ['mysql', 'postgres']
            host (str): DBMS host
            port (str): DBMS port
            user (str): DBMS user name
            pwd (str): DBMS user password
            database (str, optional): Database name to be used in connection. Defaults to None.
        """
        assert dbms in get_args(supportedDbms), f'Unsupported DBMS literal. Must be one of: {get_args(supportedDbms)}'
        self.__dbms: supportedDbms = dbms
        self.__host: str = host
        self.__port: str = WarehouserConfig.__dbms_port(dbms, port)
        self.__user: str = user
        self.__pwd: str  = pwd
        self.__database: str = database
    
    
    @staticmethod
    def __dbms_port(dbms: supportedDbms, port: Optional[portType]) -> str:
        if port is None:
            return _default_port(dbms)
        return str(port)
    
    
    @property
    def dbms(self) -> supportedDbms:
        return self.__dbms
    
    @property
    def host(self) -> str:
        return self.__host
    
    @property
    def port(self) -> str:
        return self.__port
    
    @property
    def user(self) -> str:
        return self.__user
    
    @property
    def pwd(self) -> str:
        return self.__pwd
    
    @property
    def database(self) -> str:
        return self.__database
    
    @database.setter
    def database(self, database_name: str):
        self.__database = database_name
    
    def engine_str(self):
        return WarehouserConfig.make_eng_str(self.dbms, self.user, self.pwd, self.host, self.port, database=self.__database)
    
    def db_params(self) -> tuple[str, str, str, str]:
        """Returns tuple with (host, port, user, password) - Config parameters for current DB.

        Returns:
            
            tuple[str, str, str, str]: Resulting tuple.
        """        
        return (self.host, self.port, self.user, self.pwd)
    
    
    def __repr__(self) -> str:
        eng_str = self.engine_str()
        return 'DBmanagerConf[{}:"{}"]'.format(self.dbms, eng_str)
    
    @staticmethod
    def make_eng_str(rdbms:supportedDbms, 
                    user:str, password:str, 
                    host:str,
                    port:str, *,
                    database:Optional[str]=None) -> str:
        """Creates sqlalchemy Engine for use in DBmanager

        Args:
            rdbms ('mysql'|'postgres'): RDBMS to be used in engine
            user (str): DB user
            password (str): Password for user
            host (str): DB host
            port (str, optional): DB host port. If None - default port for chosen RDBMS will be used. Defaults to None.
            database (str, optional): Database to be connected to. If None - connection to RDBMS root. Defaults to None.

        Returns:
            Engine: sqlalchemy engine class.
        """
        engine_type = _engine_type(rdbms)
        dbstr = f'/{database}' if database else ''
        return f'{engine_type}://{user}:{password}@{host}:{port}{dbstr}'
    
    
    @staticmethod
    def make_engine(rdbms:supportedDbms, 
                    user:str, password:str, 
                    host:str='localhost',
                    port:Optional[str|int]=None, *,
                    database:Optional[str]=None) -> Engine:
        """Creates sqlalchemy Engine for use in DBmanager

        Args:
            rdbms ('mysql'|'postgres'): RDBMS to be used in engine
            user (str): DB user
            password (str): Password for user
            host (str): DB host
            port (str, optional): DB host port. If None - default port for chosen RDBMS will be used. Defaults to None.
            database (str, optional): Database to be connected to. If None - connection to RDBMS root. Defaults to None.

        Returns:
            Engine: sqlalchemy engine class.
        """
        if not port:
            port = _default_port(rdbms)
        engine_type = _engine_type(rdbms)
        dbstr = f'/{database}' if database else ''
        return create_engine(f'{engine_type}://{user}:{password}@{host}:{port}{dbstr}')


def config_from_dict(config_dict: dbConfigDict, /) -> WarehouserConfig:
    d = config_dict
    assert 'dbms' in d,     'Missing "dbms" field in DB config!'
    assert 'host' in d,     'Missing "host" field in DB config!'
    assert 'user' in d,     'Missing "user" field in DB config!'
    assert 'password' in d, 'Missing "password" field in DB config!'
    assert d['dbms'] in get_args(supportedDbms), f'Unsupported "dbms" field value. Must be one of: {get_args(supportedDbms)}'
    user, password, host, port, database = get_keys(d, ('user', 'password', 'host', 'port', 'database'))
    assert isinstance(user, str), f'"user" field must be str! Got: {d["user"]}'
    assert isinstance(password, str), f'"password" field must be str! Got: {d["password"]}'
    assert isinstance(host, str), f'"host" field must by str! Got: {host}'
    assert isinstance(port, Optional[str]), f'"port" field must by str|None! Got: {port}'
    assert isinstance(database, str), f'"database" field must by str! Got: {database}'
    return WarehouserConfig(
        d['dbms'], # type: ignore
        database,
        user,
        password,
        host=host,
        port=port)
