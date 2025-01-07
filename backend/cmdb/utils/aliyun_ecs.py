import logging

from aliyunsdkcore.auth.credentials import AccessKeyCredential
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526.DescribeInstancesRequest import DescribeInstancesRequest
from aliyunsdkbssopenapi.request.v20171214.QueryAccountBillRequest import QueryAccountBillRequest

import json
import pytz
from datetime import datetime
from cmdb.models import ServerInstance, CloudCost

def time_conversion(time):
    default_time = time
    time_utc = datetime.strptime(default_time, "%Y-%m-%dT%H:%M%z").replace(tzinfo=pytz.UTC)
    time_local = time_utc.astimezone(pytz.timezone("Asia/Shanghai"))
    time_local_none = time_local.replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")
    return time_local_none

def get_aliyun_server_instance(server_platform_id, account_name_id, accesskey_id, accesskey_secret, region):
    server_platform_id = server_platform_id
    account_name_id = account_name_id
    accesskey_id = accesskey_id
    accesskey_secret = accesskey_secret
    region = region

    # 调用阿里云api获取ecs所有信息并返回，注意目前只做了支持100条记录的更新，暂时未做分页的处理
    credentials = AccessKeyCredential(accesskey_id, accesskey_secret)
    client = AcsClient(region_id=region, credential=credentials)
    request = DescribeInstancesRequest()
    request.set_accept_format('json')
    request.set_PageSize(100)
    response = client.do_action_with_exception(request)
    data = json.loads(response)
    base_data = data['Instances']['Instance']

    # 先查出该账号平台区域下的所有服务器，然后根据上面api查出的记录进行对比，如果数据库中的记录存在某个InstanceId在api返回的记录中没有，则删除数据库中该条记录
    db_records = ServerInstance.objects.filter(server_platform_id=server_platform_id, account_name_id=account_name_id, region=region)
    db_records_to_delete = []
    for db_record in db_records:
        if db_record.instanceid not in [api_record['InstanceId'] for api_record in base_data]:
            db_records_to_delete.append(db_record)
    for record in db_records_to_delete:
        record.delete()

    # 遍历api返回的所有值，如果数据库中有该记录则更新，没有的话进行创建
    for data in base_data:
        server_platform_id = server_platform_id
        account_name_id = account_name_id
        instanceid = data['InstanceId']
        instancename = data['InstanceName']
        if data['PublicIpAddress']['IpAddress']:
            public_ip = data['PublicIpAddress']['IpAddress'][0]
        elif data['EipAddress']['IpAddress']:
            public_ip = data['EipAddress']['IpAddress']
        else:
            public_ip = ''

        defaults = { 'server_platform_id': server_platform_id,
                     'account_name_id': account_name_id,
                     'instancename': instancename,
                     'instancetype': data["InstanceType"],
                     'hostname': data["HostName"],
                     'region': data["RegionId"],
                     'zone': data["ZoneId"],
                     'osname': data["OSName"],
                     'ostype': data["OSType"],
                     'cpu': data["Cpu"],
                     'memory': data["Memory"],
                     'public_ip': public_ip,
                     'primary_ip': data["VpcAttributes"]["PrivateIpAddress"]["IpAddress"][0],
                     'status': data["Status"],
                     'create_time': time_conversion(data["CreationTime"]),
                     'exprire_time': time_conversion(data["ExpiredTime"]),
                     'start_time': time_conversion(data["StartTime"])
                    }
        ServerInstance.objects.update_or_create(defaults, instanceid=instanceid)


def get_aliyun_month_count(server_platform_id, account_name_id, accesskey_id, accesskey_secret, BillingCycle):
    credentials = AccessKeyCredential(accesskey_id, accesskey_secret)
    client = AcsClient(region_id='cn-hangzhou', credential=credentials)
    request = QueryAccountBillRequest()
    request.set_accept_format('json')
    request.set_BillingCycle(BillingCycle)
    response = client.do_action_with_exception(request)
    month_data_json = json.loads(str(response, encoding='utf-8'))
    month_bill_data = month_data_json['Data']['Items']['Item']
    for i in month_bill_data:
        expense = i['PretaxAmount']
    defaults = {'cost': expense}
    CloudCost.objects.update_or_create(defaults, server_platform_id=server_platform_id, account_name_id=account_name_id, bill_cycle=BillingCycle)
    return expense