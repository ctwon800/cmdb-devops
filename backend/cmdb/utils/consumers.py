import json
import logging
import os
from threading import Thread
import socket
from channels.generic.websocket import WebsocketConsumer
import paramiko
from cmdb.models import ServerInstance, ServerRemoteRecord
import time
import datetime

def check_ip_port_open(ip, port):
    try:
        sock = socket.create_connection((ip, port), timeout=1)
        sock.close()
        return True
    except socket.error:
        logging.info("内网地址不通，准备使用外网地址链接")
        return False


class SSHConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ip = None
        self.instanceid = None
        self.chan = None
        self.ssh = None
        self.loginUser = None


    def connect(self):
        # self.instanceid = self.scope['url_route']['kwargs']['instanceId']
        self.loginUserInstanceId = self.scope['url_route']['kwargs']['loginUserInstanceId'].split("&")
        self.instanceid = self.loginUserInstanceId[1]
        self.loginUser = self.loginUserInstanceId[0]
        self.a = ServerInstance.objects.get(instanceid=self.instanceid)
        if self.a.remote_auth.remote_type == 1:
            self.from_private_key_file = self.a.remote_auth.remote_private_key
            self.pkey = paramiko.RSAKey.from_private_key_file(self.from_private_key_file)
        if check_ip_port_open(self.a.primary_ip, self.a.remote_port):
            self.ip = self.a.primary_ip
            logging.info("使用内网地址链接")
        else:
            self.ip = self.a.public_ip
            logging.info("使用外网地址链接")
        self.username = self.a.remote_auth.remote_username
        self.password = self.a.remote_auth.remote_password
        self.port = self.a.remote_port
        self.instancename = self.a.instancename
        self.accept()
        self._init()

    def disconnect(self, close_code):
        self.chan.close()
        self.ssh.close()
        self.recode_end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
        save_record = ServerRemoteRecord(record_user=self.loginUser, record_host=self.instancename, record_filepath=self.record_file_path, record_start_time=self.recode_start_time,
                                         record_end_time=self.recode_end_time)
        save_record.save()

    def get_client(self):
        # p_key = paramiko.RSAKey.from_private_key_file("/root/.ssh/id_rsa")  # ssh免密登录私钥
        ssh = paramiko.SSHClient()
        # ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if self.a.remote_auth.remote_type == 0:
            ssh.connect(hostname=self.ip, port=self.port, username=self.username, password=self.password)
        elif self.a.remote_auth.remote_type == 1:
            ssh.connect(hostname=self.ip, port=self.port, username=self.username, pkey=self.pkey)
        return ssh

    def loop_read(self):
        try:
            while True:
                data = self.chan.recv(1024)
                if not data:
                    self.close(1000)
                    self.writedata.close()
                    break
                self.send(bytes_data=data)
                desshmess = data.decode('utf-8')
                iodata2 = [time.time() - self.date, 'o', f'{desshmess}']  # 构造格式
                self.writedata.write(json.dumps(iodata2) + '\n')  # 写进文件
        except Exception as e:
            if not self.is_closed():
                self.close(1000)
            logging.error(f"WebSocket loop_read error: {str(e)}")

    def _init(self):
        self.send(bytes_data=b'Connecting ...\r\n')

        try:
            self.ssh = self.get_client()
        except Exception as e:
            self.send(bytes_data=f'Exception: {e}\r\n'.encode())
            self.close()
            return

        self.chan = self.ssh.invoke_shell(term='xterm')
        self.chan.transport.set_keepalive(30)

        recode_year = datetime.datetime.now().strftime('%Y')
        recode_month = datetime.datetime.now().strftime('%m')
        recode_date = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        self.recode_start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f%z")
        recode_webssh_dir = f'media/record_webssh/{recode_year}/{recode_month}/'
        if not os.path.exists(recode_webssh_dir):
            os.makedirs(recode_webssh_dir)
        filename = '%s-%s.cast' %(recode_date, self.instanceid)  # 文件名，用ip+开始时间为文件名
        self.date = time.time()  # 开始时间戳
        header = {
            "version": 2,
            "width": 160,
            "height": 48,
            "timestamp": self.date,   #开始时间戳
            "env": {"SHELL": "/bin/bash",
            "TERM": "xterm-256color"},
            "title": "video"
        }
        self.record_file_path = recode_webssh_dir + filename
        self.writedata = open(recode_webssh_dir + filename, 'w')  # 打开文件
        self.writedata.write(json.dumps(header) + '\n')  # 将header写入文件

        for i in range(2):
            messa = self.chan.recv(1024)
            self.send(text_data=messa.decode('utf-8'))
            demessa = messa.decode('utf-8')
            iodata = [time.time() - self.date, 'o', f'{demessa}']  # 构造格式
            self.writedata.write(json.dumps(iodata) + '\n')  # 写入文件

        Thread(target=self.loop_read).start()

    def receive(self, text_data=None, bytes_data=None):
        data = text_data or bytes_data
        if data:
            data = json.loads(data)

            resize = data.get('resize')
            if resize and len(resize) == 2:
                self.chan.resize_pty(*resize)
            else:
                self.chan.send(data['data'])

    def close(self, code=1000):
        try:
            if not hasattr(self, '_closed'):
                self._closed = True
                super().close(code)
        except Exception as e:
            logger.error(f"WebSocket close error: {str(e)}")

    def is_closed(self):
        return hasattr(self, '_closed') and self._closed