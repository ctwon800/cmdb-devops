import os

from celery import Celery

from application import settings

# 为celery 设置环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "application.settings")
# 创建celery app
app = Celery('task_celery')
# 从单独的配置模块中加载配置
app.config_from_object(settings)

# 设置app自动加载任务
app.autodiscover_tasks([
    'task_celery',
])
