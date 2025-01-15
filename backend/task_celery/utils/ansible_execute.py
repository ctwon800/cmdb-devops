import paramiko
import json
from threading import Thread
from django.http import StreamingHttpResponse
from cmdb.models import ServerInstance
import logging
from cmdb.utils.consumers import check_ip_port_open
from datetime import datetime



def execute_command(server, command, callback):
    """执行远程命令并通过回调函数返回结果"""
    logging.info(f"开始执行远程命令: {command} 在服务器: {server.instancename}")
    
    # 提前检查远程认证信息
    if not hasattr(server, 'remote_auth') or not server.remote_auth:
        error_msg = f"当前服务器 {server.instancename} 未绑定远程连接认证信息"
        logging.error(error_msg)
        callback(json.dumps({
            'type': 'task_error',
            'data': {
                'code': 500,
                'server_id': server.id,
                'data': None,
                'message': error_msg
            }
        }, ensure_ascii=False))
        return False

    try:
        # 建立 SSH 连接
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if check_ip_port_open(server.primary_ip, server.remote_port):
            host = server.primary_ip
            logging.info("使用内网地址链接")
        else:
            host = server.public_ip
            logging.info("使用外网地址链接")

        username = server.remote_auth.remote_username
        password = server.remote_auth.remote_password

        # 认证逻辑
        try:
            if server.remote_auth.remote_type == 1:
                pkey = paramiko.RSAKey.from_private_key_file('')
                ssh.connect(hostname=host, username=username, pkey=pkey)
            else:
                ssh.connect(hostname=host, username=username, password=password)
        except Exception as e:
            auth_type = "密钥" if server.remote_auth.remote_type == 1 else "密码"
            error_msg = f"服务器 {server.instancename} SSH{auth_type}认证连接失败: {str(e)}"
            logging.error(error_msg)
            callback(json.dumps({
                'type': 'task_error',
                'data': {
                    'code': 500,
                    'server_id': server.id,
                    'data': None,
                    'message': error_msg
                }
            }, ensure_ascii=False))
            return False

        # 首先发送服务器信息
        server_info = {
            'type': 'task_output',
            'data': {
                'code': 200,
                'server_id': server.id,
                'data': f"\n当前服务器: {server.instancename}({host})\n执行时间: {datetime.now()}\n",
                'message': 'success'
            }
        }
        callback(json.dumps(server_info, ensure_ascii=False))

        # 添加开始执行的消息
        start_info = {
            'type': 'task_start',  # 新增消息类型
            'data': {
                'code': 200,
                'server_id': server.id,
                'data': '开始执行：',
                'message': 'start'
            }
        }
        callback(json.dumps(start_info, ensure_ascii=False))

        # 执行命令，并设置获取伪终端
        stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)
        
        # 实时处理标准输出
        while True:
            line = stdout.readline()
            if not line:
                break
            output_line = line.strip()
            callback(json.dumps({
                'type': 'task_output',
                'data': {
                    'code': 200,
                    'server_instancename': server.instancename,
                    'data': output_line,
                    'message': 'success'
                }
            }, ensure_ascii=False))
            
        # 检查命令执行状态
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            error_message = f"命令执行失败，退出状态码: {exit_status}"
            logging.error(error_message)
            callback(json.dumps({
                'type': 'task_error',
                'data': {
                    'code': 500,
                    'server_instancename': server.instancename,
                    'data': None,
                    'message': error_message
                }
            }, ensure_ascii=False))
            return False
            
        # 修改完成消息，确保不会导致连接关闭
        callback(json.dumps({
            'type': 'task_progress',  # 改为进度消息类型
            'data': {
                'code': 200,
                'server_id': server.id,
                'data': None,
                'message': f'服务器 {server.instancename} 执行完成'
            }
        }, ensure_ascii=False))
        
        return True
            
    except Exception as e:
        error_message = f"连接或执行出错: {str(e)}"
        callback(json.dumps({
            'type': 'task_progress',  # 改为进度消息类型
            'data': {
                'code': 500,
                'server_id': server.id,
                'data': None,
                'message': error_message
            }
        }))
        return False
    finally:
        ssh.close()