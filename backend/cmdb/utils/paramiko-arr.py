import paramiko
from threading import Thread
from webssh.tools.tools import get_key_obj
import socket
import json
import time
import datetime
import os
from boamp.settings import logger
from boamp.settings import BASE_DIR
data_list = {}

class SSH:

    def __init__(self, host, user, websocker, message):
        self.host = host
        self.user = user
        self.websocker = websocker
        self.message = message
        self.time = time.time()     #获取起始时间戳
        self.date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H%M')
        self.msg_list = data_list["%s_%s"%(self.host,self.date_time)] = []

    def record_webssh(self, host, user, type, data_list):
        try:
            record_dir_path = os.path.join(BASE_DIR,"static/webssh/record_webssh/")
            if not os.path.exists(record_dir_path):
                os.makedirs(record_dir_path)
            record_filename = '%s_%s_%s.cast' % (self.date_time,host, user)     #命名录像文件名
            record_filename_path = os.path.join(record_dir_path, record_filename)
            if type == 'header':        #是否是头部header内容，只写入一次头部header内容
                with open(record_filename_path, 'w') as f:
                        f.write(json.dumps(data_list) + '\n')
            else:
                with open(record_filename_path, 'a', buffering=1) as f:     #self.msg_list 必须为列表，如果使用字典格式会出现很多问题，已彩坑1天，换回列表就好了
                    for data in self.msg_list:
                        now_time = data[0]
                        message = data[1]
                        iodata = [now_time - self.time, 'o', message]       #生成数据流格式内容
                        f.write((json.dumps(iodata) + '\n'))        #写入执行输出输入的内容数据流
        except Exception as e:
            print(e)
            print('异常文件：%s ,异常行号：%s' % (e.__traceback__.tb_frame.f_globals['__file__'], e.__traceback__.tb_lineno))

    def connect(self, host, user, password, pkey=None, port=22, timeout=30,term='xterm', pty_width=80, pty_height=24):
        global data_list
        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if pkey:
                key = get_key_obj(paramiko.RSAKey, pkey_obj=pkey, password=password) or \
                      get_key_obj(paramiko.DSSKey, pkey_obj=pkey, password=password) or \
                      get_key_obj(paramiko.ECDSAKey, pkey_obj=pkey, password=password) or \
                      get_key_obj(paramiko.Ed25519Key, pkey_obj=pkey, password=password)

                print("使用密钥登陆")
                try:
                    ssh_client.connect(username=user, hostname=host, port=port, pkey=key, timeout=timeout)
                    logger.info("以[%s]用户通过[密钥]方式登陆机器[%s]成功"%(user,host))
                except Exception as e:
                    print("error：",e)
                    logger.warning("以[%s]用户通过[密钥]方式登陆机器[%s]失败，错误：%s" % (user, host,e))
            else:
                print("使用密码登陆")
                try:
                    ssh_client.connect(username=user, password=password, hostname=host, port=port, timeout=timeout)
                    logger.info("以[%s]用户通过[密码]方式登陆机器[%s]成功" % (user, host))
                except Exception as e:
                    print("error：",e)
                    logger.warning("以[%s]用户通过[密码]方式登陆机器[%s]失败，错误：%s" % (user, host, e))

            transport = ssh_client.get_transport()
            self.channel = transport.open_session()
            self.channel.get_pty(term=term, width=pty_width, height=pty_height)
            self.channel.invoke_shell()
            # 构建录像文件header
            header_data = {
                "version": 2,
                "width": 250,
                "height": 57,
                "timestamp": self.time,
                "env": {
                    "SHELL": "/bin/bash",
                    "TERM": "linux"
                },
                "title": "boamp_webssh_record"
            }
            self.record_webssh(host, user,'header', header_data)
            # 连接建立一次，之后交互数据不会再进入该方法

            for i in range(2):
                recv = self.channel.recv(102400).decode('utf-8')
                self.message['status'] = 0
                self.message['message'] = recv
                message = json.dumps(self.message)
                self.websocker.send(message)
                now_time = time.time()
                data_list_temp = [now_time,recv]
                self.msg_list.append(data_list_temp)
                self.record_webssh(host,user,'iodata',data_list)
                self.msg_list = []

        except socket.timeout as e:
            self.message['status'] = 1
            self.message['message'] = 'ssh connection timed out'
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close()
            now_time = time.time()
            data_list_temp = [now_time, self.message['message']]
            self.msg_list.append(data_list_temp)
            self.record_webssh(host, user, 'iodata', data_list)
            self.msg_list = []
        except Exception as e:
            print(e)
            print('异常文件：%s ,异常行号：%s' % (e.__traceback__.tb_frame.f_globals['__file__'], e.__traceback__.tb_lineno))
            self.message['status'] = 1
            self.message['message'] = str(e)
            message = json.dumps(self.message)
            self.websocker.send(message)
            self.websocker.close()
            now_time = time.time()
            data_list_temp = [now_time, self.message['message']]
            self.msg_list.append(data_list_temp)
            self.record_webssh(host, user, 'iodata', data_list)
            self.msg_list = []

    def resize_pty(self, cols, rows):
        self.channel.resize_pty(width=cols, height=rows)

    def django_to_ssh(self, data):
        try:
            self.channel.send(data)
            return
        except:
            self.close()

    def websocket_to_django(self):
        global data_list
        try:
            while True:
                data = self.channel.recv(1024).decode('utf-8','ignore')
                if len(data) != 0:
                    self.message['status'] = 0
                    self.message['message'] = data
                    message = json.dumps(self.message)
                    self.websocker.send(message)
                    print("===================",len(self.msg_list))
                    now_time = time.time()
                    data_list_temp = [now_time,data]
                    if len(self.msg_list) < 60:     #判断数据列表长度，60个内容就写入一次文件，避免了频繁写入文件，消耗io导致数据丢失的问题
                        self.msg_list.append(data_list_temp)
                    else:
                        self.msg_list.append(data_list_temp)
                        self.record_webssh(self.host, self.user, 'iodata', data_list)
                        self.msg_list = []
                else:
                    return
        except:
            self.close()

    def close(self):
        global data_list
        self.message['status'] = 1
        self.message['message'] = 'Close connection'
        message = json.dumps(self.message)
        now_time = time.time()
        data_list_temp = [now_time, self.message['message']]
        self.msg_list.append(data_list_temp)
        self.record_webssh(self.host, self.user, 'iodata', data_list)
        self.msg_list = []
        self.websocker.send(message)
        self.channel.close()
        self.websocker.close()

    def shell(self, data):
        Thread(target=self.django_to_ssh, args=(data,)).start()
        Thread(target=self.websocket_to_django).start()