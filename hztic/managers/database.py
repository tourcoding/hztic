import mysql.connector
from config import DB_CONFIG

class Database:
    """管理 MySQL 数据库连接"""

    def __init__(self):
        self.connection = None

    def connect(self):
        """建立数据库连接"""
        if not self.connection:
            self.connection = mysql.connector.connect(**DB_CONFIG)

    def execute_query(self, query, params=None):
        """执行数据库查询"""
        self.connect()
        cursor = self.connection.cursor(dictionary=True)
        cursor.execute(query, params or ())
        return cursor

    def commit(self):
        """提交事务"""
        if self.connection:
            self.connection.commit()

    def close(self):
        """关闭连接"""
        if self.connection:
            self.connection.close()
            self.connection = None

# 创建数据库实例供项目复用
db = Database()