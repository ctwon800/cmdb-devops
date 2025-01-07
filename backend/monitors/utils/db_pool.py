from dbutils.pooled_db import PooledDB
import MySQLdb
from django.conf import settings

class DatabasePool:
    _pool = None

    @staticmethod
    def get_pool():
        if DatabasePool._pool is None:
            db_settings = settings.DATABASES['default']
            DatabasePool._pool = PooledDB(
                creator=MySQLdb,  # 使用 MySQLdb 作为连接器
                maxconnections=30,  # 连接池最大连接数
                mincached=5,      # 初始化时创建的空闲连接数
                maxcached=10,      # 连接池中最多闲置的连接数
                maxshared=5,      # 连接池中最多共享的连接数
                blocking=True,    # 连接池中如果没有可用连接后是否阻塞等待
                maxusage=None,    # 一个连接最多被重复使用的次数
                setsession=[],    # 开始会话前执行的命令
                host=db_settings['HOST'],
                port=int(db_settings['PORT']),
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                database=db_settings['NAME'],
                charset='utf8mb4'
            )
        return DatabasePool._pool

    @staticmethod
    def get_connection():
        """获取数据库连接"""
        return DatabasePool.get_pool().connection() 