# -*- coding: utf-8 -*-
from django.urls import path
from application.websocketConfig import MegCenter
from cmdb.utils.consumers import SSHConsumer
from task_celery.utils.consumers import AnsibleTaskConsumer
websocket_urlpatterns = [
    path('ws/<str:service_uid>/', MegCenter.as_asgi()), #consumers.DvadminWebSocket 是该路由的消费者
    path(r'socket/ws/ssh/<str:loginUserInstanceId>', SSHConsumer.as_asgi()),
    path('ws/ansible/<str:task_id>/', AnsibleTaskConsumer.as_asgi()),
]

