import subprocess
from datetime import datetime, timedelta
from cmdb import models
from celery import current_task
import logging


# 该import语句是为了引入celery的app对象，不可删除
from task_celery.celery import app
from celery import shared_task
from cmdb.views.account_management import AutoUpdateYunRes
from cmdb.views.cloud_cost import publicUpdateCloudCost
from cmdb.models import ServerInstance
from cmdb.utils.consumers import check_ip_port_open
import paramiko
from celery.result import AsyncResult
from django_celery_results.models import TaskResult

from django.utils import timezone
from monitors.views.ssl_monitors import auto_update_account_ssl, update_ssl_monitors_domain
from monitors.views.domain_monitors import auto_update_domain_list
from monitors.views.web_monitors import auto_update_web_monitors_status, update_web_monitors_domain


def local_job(command, command_type):
    command_script = '\n'.join(command)
    if command_type == 'shell':
        result = subprocess.run(command_script, shell=True, capture_output=True, text=True, executable='/bin/bash')
        output = result.stdout
    elif command_type == 'python':
        try:
            result = subprocess.run(["python3", "-c", command_script], capture_output=True, text=True)
            output = result.stdout
            if result.returncode != 0:
                output = f"Error: {result.stderr}"
        except Exception as e:
            output = f"Exception occurred: {str(e)}"
    # result = subprocess.run([command_script], shell=True, capture_output=True, text=True)
    # output = result.stdout
    logging.info('Shell command %s executed with output: %s', command, output)
    res = {
        'instancename': 'local',
        'output': output
    }
    # print(res)
    return res


def AutoUpdateCloudCost():
    all_account = models.AccountManagement.objects.all()
    now_time = datetime.now()
    last_month_time = now_time.replace(month=now_time.month - 1)
    last_month = last_month_time.strftime('%Y-%m')
    results = []
    for account in all_account:
        account_id = account.id
        res = publicUpdateCloudCost(account_id, last_month)
        # print(res)
        results.append(res)
    return results

def remote_job(instancename, command, command_type):
    a = ServerInstance.objects.get(instancename=instancename)
    if a.remote_auth.remote_type == 1:
        from_private_key_file = a.remote_auth.remote_private_key
        pkey = paramiko.RSAKey.from_private_key_file(from_private_key_file)
    if check_ip_port_open(a.primary_ip, a.remote_port):
        ip = a.primary_ip
        logging.info("使用内网地址链接")
    else:
        ip = a.public_ip
        logging.info("使用外网地址链接")
    username = a.remote_auth.remote_username
    password = a.remote_auth.remote_password
    port = a.remote_port
    # 创建SSH客户端
    client = paramiko.SSHClient()
    # 自动添加远程主机的SSH密钥
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if a.remote_auth.remote_type == 0:
        client.connect(hostname=ip, port=port, username=username, password=password)
    elif a.remote_auth.remote_type == 1:
        client.connect(hostname=ip, port=port, username=username, pkey=pkey)

    command_script = '\n'.join(command)
    if command_type == 'shell':
        # logging.info(f"Executing script:\n{command_script}")
        stdin, stdout, stderr = client.exec_command(command_script)
        output = stdout.read().decode('utf-8')
        # logging.info(output)
    elif command_type == 'python':
        res = subprocess.run(["python", "-c", command_script], capture_output=True, text=True)
        output = res.stdout.encode('utf-8').decode('utf-8')
        # logging.info(output)
    # 获取命令执行结果


    # 关闭SSH连接
    client.close()
    logging.info('Shell command %s executed with output: %s', command, output)

    res = {
        'instancename': instancename,
        'output': output
    }
    return res



# 阿里云账号资源自动获取
@shared_task
def autoUpdateYunRes_task():
    return AutoUpdateYunRes()

# 云费用自动获取
@shared_task
def autoUpdateCloudCost_task(*args, **kwargs):
    result = AutoUpdateCloudCost()
    return result

# 本地执行命令
@shared_task
def local_job_task(*args, **kwargs):
    command_type = kwargs.get('command_type')
    command = args
    results = []
    results_detail = local_job(command, command_type)
    results.append(results_detail)
    # print(results)
    return results

# 远程执行命令
@shared_task
def remote_job_task(*args, **kwargs):
    command_type = kwargs.get('command_type')
    command = args
    instance_list = kwargs.get('instance_name')
    results = []
    for instancename in instance_list:
        result = remote_job(instancename, command, command_type)
        results.append(result)
    return results

# 阿里云账号SSL证书自动获取
@shared_task
def auto_update_aliyun_account_ssl(*args, **kwargs):
    return auto_update_account_ssl()

# 云账号域名自动获取
@shared_task
def auto_update_account_domain(*args, **kwargs):
    return auto_update_domain_list()

# 网站监控
@shared_task
def auto_update_web_monitors(*args, **kwargs):
    return auto_update_web_monitors_status()

# 域名监控
@shared_task
def auto_update_domain_monitors(*args, **kwargs):
    return auto_update_domain_list()

# web站点域名自动更新
@shared_task
def auto_update_web_monitors_domain(*args, **kwargs):
    return update_web_monitors_domain()

# ssl证书域名自动更新
@shared_task
def auto_update_ssl_monitors_domain(*args, **kwargs):
    return update_ssl_monitors_domain()







# 代码段自定义一个周期任务
# # 创建或者获取一个时间间隔对象
# auto_update_domain_monitors_schedule, created = CrontabSchedule.objects.get_or_create(
#     minute='30',
#     hour='11',
#     day_of_week='*',
#     day_of_month='*',
#     month_of_year='*',
# )
#
# # 创建一个周期性任务
# auto_update_domain_monitors_periodic_task = PeriodicTask.objects.update_or_create(
#     name='域名信息每日更新',  # 周期性任务的名称
#     defaults={
#         'crontab': auto_update_domain_monitors_schedule,  # 上文创建的时间间隔
#         'task': 'task_celery.tasks.auto_update_domain_monitors',  # 这里是Celery任务的路径，格式为'项目名称.模块名称.任务函数名称'
# # 也可以添加关键字参数（kwargs），expiry time等
#     }
# )