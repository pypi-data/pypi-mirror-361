import os
from typing import Optional, Any

import pymssql
import pymysql

from giga_auto.base_class import SingletonMeta
from giga_auto.constants import DBType
from giga_auto.logger import db_log
from giga_auto.conf.settings import settings


class DBUtils():
    oracle_client_initialized = False

    def __init__(self, db_config, db_type=None):
        self.db_config = db_config
        self.conn = None
        self.cursor = None
        self.db_type = db_type or DBType.mysql

    def _connect(self):
        if self.db_type == DBType.sqlserver:
            self.sqlserver_connection()
        elif self.db_type == DBType.mysql:
            self.mysql_connect()
        elif self.db_type == DBType.oracle:
            self.oracle_connect()
        self.cursor = self.conn.cursor()

    def sqlserver_connection(self):
        self.conn = pymssql.connect(
            server=self.db_config["db_host"],
            port=int(self.db_config["db_port"]),
            user=self.db_config["db_user"],
            password=self.db_config["db_password"],
            database=self.db_config["db_name"]
        )

    def mysql_connect(self):
        self.conn = pymysql.connect(
            host=self.db_config["db_host"],
            port=int(self.db_config["db_port"]),
            user=self.db_config["db_user"],
            password=self.db_config["db_password"],
            database=self.db_config["db_name"],
            charset=self.db_config["db_charset"]
        )
        return self.conn

    def oracle_connect(self):
        import oracledb
        self.conn = oracledb.connect(
            user=self.db_config["db_user"],
            password=self.db_config["db_password"],
            dsn=f"{self.db_config['db_host']}:{self.db_config['db_port']}/{self.db_config['db_name']}"
        )
        self.cursor = self.conn.cursor()

    def mongodb_connect(self):
        from pymongo import MongoClient
        self.conn = MongoClient(
            host=self.db_config["db_host"],
            username=self.db_config["db_user"],
            password=self.db_config["db_password"],
            authSource=self.db_config["db_name"],
            replicaSet=self.db_config.get("replica_set")
        )
        self.db = self.conn[self.db_config["db_name"]]

    def get_cursor(self, dict_cursor):
        cursor = self.cursor
        if self.conn is None:
            self._connect()
        if self.db_type == DBType.mysql:
            cursor = self.conn.cursor(pymysql.cursors.DictCursor) if dict_cursor else self.conn.cursor()
        elif self.db_type == DBType.sqlserver:
            cursor = self.conn.cursor(
                as_dict=True) if dict_cursor else self.conn.cursor()  # SQL Server supports `as_dict`
        return cursor

    @db_log
    def _execute(self, sql, params=None):
        """

        :param sql:
        :param params: [()] or [[]]
        :return:
        """
        if self.cursor is None:
            self._connect()
        many = params and len(params) > 1
        if many:
            self.cursor.executemany(sql, params)
        else:
            self.cursor.execute(sql, params[0] if params else None)
        self.conn.commit()
        return self.cursor.rowcount

    @db_log
    def _fetchone(self, sql, args=None, dict_cursor=True):
        cursor = self.get_cursor(dict_cursor)
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)

        row = cursor.fetchone()
        if self.db_type == DBType.oracle:
            return self.fetch_as_dict(cursor, row)
        return row

    @db_log
    def _fetchall(self, sql, args=None, dict_cursor=True):
        cursor = self.get_cursor(dict_cursor)
        if args:
            cursor.execute(sql, args)
        else:
            cursor.execute(sql)
        rows = cursor.fetchall()
        if self.db_type == DBType.oracle:
            return self.fetch_as_dict(cursor, rows)
        return rows

    @db_log
    def _mongo_find_one(self, collection, query, projection=None):
        return self.db[collection].find_one(query, projection)

    @db_log
    def _mongo_find_all(self, collection, query, projection=None):
        return list(self.db[collection].find(query, projection))

    @db_log
    def _mongo_insert(self, collection, data):
        if isinstance(data, list):
            result = self.db[collection].insert_many(data)
        else:
            result = self.db[collection].insert_one(data)
        return result.inserted_ids if isinstance(data, list) else result.inserted_id

    @db_log
    def _mongo_update(self, collection, query, update_data):
        return self.db[collection].update_many(query, {'$set': update_data}).modified_count

    @db_log
    def _mongo_delete(self, collection, query):
        return self.db[collection].delete_many(query).deleted_count

    def fetch_as_dict(self, cursor, rows):
        """
        将 cx_Oracle cursor 的 fetchone() 或 fetchall() 结果转换为字典
        :param cursor: cx_Oracle cursor 对象
        :param rows: cursor.fetchone() 或 cursor.fetchall() 结果
        :return: 单条数据（字典）或多条数据（字典列表）
        """
        if not rows:
            return None if isinstance(rows, tuple) else []  # 返回 None 或 空列表

        columns = [col[0] for col in cursor.description]  # 获取列名并转换为小写

        if isinstance(rows, tuple):  # 处理 fetchone() 结果
            return dict(zip(columns, rows))

        return [dict(zip(columns, row)) for row in rows]  # 处理 fetchall() 结果


class DBOperation(metaclass=SingletonMeta):
    _data = {}

    def set(self, key: str, db_info:dict):
        if key not in self._data:
            if 'db_host' in db_info:
                db_utils=DBUtils(db_info,db_info.pop('db_type',None))
                self._data[key] = db_utils
            else: # 适配同一server存在多个数据库的情况
                self._data[key] = {}
                for db_key in db_info:
                    self._data[key][db_key] = DBUtils(db_info[db_key],db_info[db_key].pop('db_type',None))

    def setup(self):
        for serv in settings.db_info:
            self.set(serv, settings.db_info[serv])

    def get(self, key: str, db_key=None) -> DBUtils:
        """
        美国drp一个系统用了两个数据库，需要二级key,其余的不用管一个service key就够了
        """
        if isinstance(self._data.get(key),DBUtils):
            return self._data.get(key)
        elif isinstance(self._data.get(key),dict): # 处理二级key
            return self._data.get(key).get(db_key or 'default')
        raise Exception('%s not found in settings db_info' % key)

    def has(self, key: str,db_type=None) -> bool:
        return key in self._data if db_type is None else db_type in self._data.get(key)

    def clear(self):
        for k,v in self._data.items():
            if isinstance(v,dict):
                for k1,v1 in v.items():
                    v1.conn.close() if v1.conn is not None else None
            else:v.conn.close() if v.conn is not None else None
        self._data.clear()

    def __repr__(self):
        return f"<DB: {self._data}>"


if __name__ == '__main__':
    os.environ['GIGA_SETTINGS_MODULE']='configs.settings'
    db_operation=DBOperation()
    db_operation.setup()
    a1=db_operation.get('wms_us_web')
    a2=db_operation.get('drp')
    a3=db_operation.get('drp','origin')
    db_operation.clear()