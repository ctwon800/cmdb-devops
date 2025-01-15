from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class AnsibleTaskConsumer(WebsocketConsumer):
    def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        self.group_name = f"ansible_task_{self.task_id}"

        # 加入群组
        async_to_sync(self.channel_layer.group_add)(
            self.group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        # 离开群组
        async_to_sync(self.channel_layer.group_discard)(
            self.group_name,
            self.channel_name
        )

    def send_message(self, event):
        # 发送消息到WebSocket
        self.send(text_data=event["message"])