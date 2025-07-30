# Dbm

Project with usefull utilities for managing you DB.

## Usage

### Config

#### 1. Config via dict

Create you config in dictionary:

```python
config = {
    "dms": "mysql",
    "host": "host",
    "port": "port",
    "user": "<your user>",
    "password": "<your password>",
    "database": "<your_db_name>"
}
```

#### *IMPORTANT* : Make sure to use ENV variables for user and password:

Example
```python
user = os.environ.get('MYSQL_PROD_USER')
password = os.environ.get('MYSQL_PROD_PWD')
```

#### 2. class config

Alternatively - you can create it dirrectly in DBmanagerConfig class.

```python 
from dbmanager import DBmanagerConfig

conf = return DBmanagerConfig(
    'mysql',
    '<your database>',
    user,
    password,
    host='host',
    port='port')
```

### DBmanager creation

```python
from dmanager import make_db_manager
from sqlalchemy import MetaData

metadata = MetaData()

dbm = make_db_manager(config, metadata)
```

**metadata** - sqlalchemy class for storing all infor about tales.
Even if you dont have it yet in your project - you must create it.

### DBmanager usage example

```python
import pandas as pd
from sqlalchemy import Integer, MetaData
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from dbmanager import make_db_manager
from dbmanager.manager import DBmanager

METADATA = MetaData()

def make_dbm(dbms: str) -> DBmanager:
    config['dbms'] = dbms
    return make_db_manager(config, METADATA)

class Base(DeclarativeBase):
    metadata = METADATA


class FooTable(Base):
    __tablename__ = 'foo_bar_table'

    id: Mapped[int] = mapped_column(Integer, primapy_key=True)
    data: Mapped[str]



if __name__ == '__main__':
    dbm = make_dbm('mysql')
    dbm.create_table(FooTable)
    data = pd.read_csv('somecsv.csv')
    dbm.upsert(FooTable, data)
```