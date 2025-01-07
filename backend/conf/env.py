import os
from application.settings import BASE_DIR

# ================================================= #
# *************** mysql数据库 配置  *************** #
# ================================================= #
# 数据库 ENGINE ，默认演示使用 sqlite3 数据库，正式环境建议使用 mysql 数据库
# sqlite3 设置
# DATABASE_ENGINE = "django.db.backends.sqlite3"
# DATABASE_NAME = os.path.join(BASE_DIR, "db.sqlite3")

# 使用mysql时，改为此配置
DATABASE_ENGINE = "django.db.backends.mysql"
# DATABASE_ENGINE = "django_mysql.backends.mysql"
DATABASE_NAME = os.environ.get('DATABASE_NAME', default='')

# 数据库地址 改为自己数据库地址
DATABASE_HOST = os.environ.get('DATABASE_HOST', default='')

# # 数据库端口
DATABASE_PORT = os.environ.get('DATABASE_PORT', default='')

# # 数据库用户名
DATABASE_USER = os.environ.get('DATABASE_USER', default='')
# # 数据库密码
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD', default='')


# 表前缀
TABLE_PREFIX = "dvadmin_"
# ================================================= #
# ******** redis配置，无redis 可不进行配置  ******** #
# ================================================= #
REDIS_PASSWORD = os.environ.get('REDIS_PASSWORD', default='')
# REDIS_HOST = '47.99.48.248:10803'
REDIS_HOST = os.environ.get('REDIS_HOST', default='')
REDIS_PORT = os.environ.get('REDIS_PORT', default='')
REDIS_URL = f'redis://:{REDIS_PASSWORD or ""}@{REDIS_HOST}:{REDIS_PORT}'
# ================================================= #
# ****************** 功能 启停  ******************* #
# ================================================= #
DEBUG = True
# 启动登录详细概略获取(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True
# 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
LOGIN_NO_CAPTCHA_AUTH = True
# 是否启动API日志记录
API_LOG_ENABLE = locals().get("API_LOG_ENABLE", True)
# API 日志记录的请求方式
API_LOG_METHODS = locals().get("API_LOG_METHODS", ["POST", "UPDATE", "DELETE", "PUT"])
# API_LOG_METHODS = 'ALL' # ['POST', 'DELETE']
# ================================================= #
# ****************** 其他 配置  ******************* #
# ================================================= #
ENVIRONMENT = os.environ.get('ENVIRONMENT', default='local')  # 环境，test 测试环境;prod线上环境;local本地环境
ALLOWED_HOSTS = ["*"]
# 系统配置存放位置：redis/memory(默认)
DISPATCH_DB_TYPE = 'redis'

