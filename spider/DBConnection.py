# -*- coding: utf-8 -*-
# Created by bohuanshi on 2019/4/18
import pymysql
from DBUtils.PooledDB import PooledDB
from scrapy.utils.project import get_project_settings


class DBConnectionPool(object):
    __pool = None

    def __init__(self):
        self.setting = get_project_settings()

    def __enter__(self):
        self.conn = self.getConn()
        self.cursor = self.conn.cursor()
        return self

    def getConn(self):
        if self.__pool is None:
            self.__pool = PooledDB(creator=pymysql, mincached=self.setting.get('DB_MIN_CACHED'),
                                   maxcached=self.setting.get('Config.DB_MAX_CACHED'),
                                   maxshared=self.setting.get('DB_MAX_SHARED'),
                                   maxconnections=self.setting.get('DB_MAX_CONNECYIONS'),
                                   blocking=self.setting.get('DB_BLOCKING'), maxusage=self.setting.get('DB_MAX_USAGE'),
                                   setsession=self.setting.get('DB_SET_SESSION'),
                                   host=self.setting.get('MYSQL_HOST'), port=self.setting.get('MYSQL_PORT'),
                                   user=self.setting.get('MYSQL_USER'), passwd=self.setting.get('MYSQL_PASSWD'),
                                   db=self.setting.get('MYSQL_DBNAME'), use_unicode=False,
                                   charset=self.setting.get('DB_CHARSET'))

        return self.__pool.connection()

    """
    @summary: 释放连接池资源
    """

    def __exit__(self, type, value, trace):
        self.cursor.close()
        self.conn.close()


'''
@功能：获取数据库连接
'''


def get_db_connect():
    return DBConnectionPool()
