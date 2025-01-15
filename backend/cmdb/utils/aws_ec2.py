import datetime
import logging

import requests
import boto3
from cmdb.models import ServerInstance, CloudCost



def usd_to_cny(amount):
    # 获取汇率
    url = "https://api.exchangerate-api.com/v4/latest/USD"  # 使用 exchangerate-api 提供的免费汇率 API
    response = requests.get(url)
    data = response.json()
    exchange_rate = data['rates']['CNY']
    logging.info(f"当前美元转人民币汇率 {exchange_rate}")
    # 进行转换
    cny_amount = amount * exchange_rate
    return cny_amount


def get_tag(Tags, key):
    value = [tag['Value'] for tag in Tags if tag['Key'] == key or tag['Key'] == 'aws:autoscaling:groupName']
    try:
        value = value[0]
    except:
        value = 'None'
    return value

def get_aws_server_instance(server_platform_id, account_name_id, aws_access_key_id, aws_secret_access_key, region):
    server_platform_id = server_platform_id
    account_name_id = account_name_id
    aws_access_key_id = aws_access_key_id
    aws_secret_access_key = aws_secret_access_key
    region = region
    ec2 = boto3.client(
        'ec2',
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region
    )

    res = ec2.describe_instances()



    ec2_instanceid_list = []
    for item in res['Reservations']:
        for instance in item['Instances']:
            instanceid = instance['InstanceId']
            Tags = instance['Tags']
            instance_info = {
                'instanceid': instanceid
            }
            ec2_instanceid_list.append(instance_info)
            instancename = ''
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    if tag['Key'] == 'Name':
                        instancename = tag['Value']
                    else:
                        instancename = instance['PrivateDnsName']
            # 获取实例类型信息
            instance_type_info = ec2.describe_instance_types(
                InstanceTypes=[instance['InstanceType']]
            )['InstanceTypes'][0]

            defaults = {'server_platform_id': server_platform_id,
                        'account_name_id': account_name_id,
                        'instancename': instancename,
                        'instancetype': instance['InstanceType'],
                        'region': region,
                        'ostype': instance['PlatformDetails'],
                        'zone': instance['Placement']['AvailabilityZone'],
                        'cpu': instance_type_info['VCpuInfo']['DefaultVCpus'],
                        'memory': f"{instance_type_info['MemoryInfo']['SizeInMiB']/1024:.0f}",
                        'public_ip': instance['PublicIpAddress'],
                        'primary_ip': instance['PrivateIpAddress'],
                        'status': instance['State']['Name']
                        }
            ServerInstance.objects.update_or_create(defaults, instanceid=instanceid)


    # 先查出该账号平台区域下的所有服务器，然后根据上面api查出的记录进行对比，如果数据库中的记录存在某个InstanceId在api返回的记录中没有，则删除数据库中该条记录
    db_records = ServerInstance.objects.filter(server_platform_id=server_platform_id, account_name_id=account_name_id, region=region)
    db_records_to_delete = []
    for db_record in db_records:
        if db_record.instanceid not in [api_record['instanceid'] for api_record in ec2_instanceid_list]:
            db_records_to_delete.append(db_record)
    for record in db_records_to_delete:
        record.delete()



def get_aws_month_bill(server_platform_id, account_name_id, accesskey_id, accesskey_secret, BillingCycle):
    client = boto3.client(
        'ce',
        aws_access_key_id=accesskey_id,
        aws_secret_access_key=accesskey_secret
    )
    # 根据传入月份账单，计算出开始和结束时间
    start_date = datetime.datetime.strptime(BillingCycle, '%Y-%m')
    start_time = start_date.strftime('%Y-%m-%d')
    end_date = start_date + datetime.timedelta(days=31)
    end_mon = end_date.strftime('%Y-%m')
    end_time = end_mon + '-01'

    time_period = {
        'Start': start_time,
        'End': end_time
    }
    response = client.get_cost_and_usage(
        TimePeriod=time_period,
        Granularity='MONTHLY',
        # Granularity='HOURLY',
        Metrics=['BlendedCost']
    )
    results = response['ResultsByTime']
    for result in results:
        start = result['TimePeriod']['Start']
        end = result['TimePeriod']['End']
        cost = result['Total']['BlendedCost']['Amount']
        logging.info(f"统计费用信息：{start} - {end}为： ${cost}")

    cost_usd = round(float(cost), 2)
    cost_cny_trans = usd_to_cny(cost_usd)
    cost_cny = round(cost_cny_trans, 2)
    defaults = {'cost': cost_cny, 'cost_usd': cost_usd}
    CloudCost.objects.update_or_create(defaults, server_platform_id=server_platform_id, account_name_id=account_name_id, bill_cycle=BillingCycle)


if __name__ == '__main__':
    get_aws_month_bill()