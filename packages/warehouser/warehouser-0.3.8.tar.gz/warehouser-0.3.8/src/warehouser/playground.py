from sqlalchemy import MetaData
from warehouser.core import make_warehouser


if __name__ == '__main__':
    conf = {
        'dbms': 'postgres',
        'host': 'localhost',
        # 'port': '5432',
        'database': 'mpu_ariba_data',
        'user': 'test_user',
        'password': 'some_test_password_1234'
    }
    mtd = MetaData()
    wh = make_warehouser(conf, mtd)
    print(wh)
    # d = wh.select_from('ariba_contracts')
    # print(d)