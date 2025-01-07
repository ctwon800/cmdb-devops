import logging

from django.http import HttpResponse
from dvadmin.utils.json_response import DetailResponse
import json
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from cmdb import models
from cmdb.models import AccountManagement
from monitors.models import DomainMonitors
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from monitors.utils.aliyun_domain import AliyunDomain
import datetime
from monitors.utils.dingtalk import send_dingtalk_message
import whois
from dvadmin.system.models import dispatch
from monitors.utils.aws_domain import aws_domain_list
import requests
import socket
from monitors.utils.namecheap_domain import get_namecheap_domain_info
socket.setdefaulttimeout(300)



def notify_ding_talk(domain, cert_expiry_date, days_until_expiry):
    # 钉钉通知
    content = f"""\n![域名](https://images.hulian.top/image/201812/2018122817421830214.png)\n ### 域名到期提醒\n - 域名：{domain}\n - 到期时间：{cert_expiry_date}\n - 到期天数：{days_until_expiry}
    """
    # 获取钉钉配置
    access_token = dispatch.get_system_config_values("configdingtalk.access_token")
    secret = dispatch.get_system_config_values("configdingtalk.secret")
    # 发送钉钉通知
    send_dingtalk_message(content, access_token, secret)


def domain_expiry_date(domain):
    try:
        domain_info = whois.whois(domain)
        expiry_date = domain_info.expiration_date
        # 如果whois查询不到到期时间，则使用下面单独的接口进行查询
        if expiry_date is None:
            logging.info(f"whois查询不到{domain}的到期时间，使用单独接口进行查询")
            url = f"https://who-dat.as93.net/{domain}"
            response = requests.get(url).text
            json_data = json.loads(response)
            json_expriry_data = json_data['domain']["expiration_date_in_time"]
            a = datetime.datetime.strptime(json_expriry_data, '%Y-%m-%dT%H:%M:%SZ')
            expiry_date_asia = a + datetime.timedelta(hours=8)
            # expiry_date_local = expiry_date_asia.strftime('%Y-%m-%d %H:%M:%S')
            return expiry_date_asia
        else:
            # 处理返回的过期日期
            if isinstance(expiry_date, list):
                expiry_date = expiry_date[0]
            # 转换为本地时间
            logging.info(domain)
            logging.info(domain_info)
            logging.info(expiry_date)
            expiry_date_local = expiry_date + datetime.timedelta(hours=8)
            return expiry_date_local
    except Exception as e:
        logging.info(f"whois查询{domain}的到期时间失败，错误信息为{e}")
        return None

def update_domain_monitors(domain):
    domain_expire_time = domain_expiry_date(domain)
    current_date = datetime.datetime.now()
    days_until_expiry = (domain_expire_time - current_date).days
    DomainMonitors.objects.filter(domain_name=domain).update(domain_expire_time=domain_expire_time, domain_expire_days=days_until_expiry)
    logging.info("判断是否发送通知")
    determine_send_notify(domain, domain_expire_time, days_until_expiry)

#   判断是否发送通知
def determine_send_notify(domain, domain_expire_time, days_until_expiry):
    if days_until_expiry > 31:
        DomainMonitors.objects.filter(domain_name=domain).update(domain_status="正常")
        logging.info(f"The domain for {domain} is valid and will expire in {days_until_expiry} days.")
    elif days_until_expiry <= 31 and days_until_expiry > 15:
        try:
            if days_until_expiry % 31 == 0 and DomainMonitors.objects.filter(domain_name=domain).get(domain_notice_enable="1"):
                notify_ding_talk(domain, domain_expire_time, days_until_expiry)
        except Exception as e:
            logging.info(e)
        DomainMonitors.objects.filter(domain_name=domain).update(domain_status="即将过期")
        logging.info(f"The domain for {domain} is valid and will expire in {days_until_expiry} days.")
    elif days_until_expiry <= 15 and days_until_expiry > 1:
        try:
            if days_until_expiry % 7 == 0 and DomainMonitors.objects.filter(domain_name=domain).get(domain_notice_enable="1"):
                notify_ding_talk(domain, domain_expire_time, days_until_expiry)
        except Exception as e:
            logging.info(e)
        DomainMonitors.objects.filter(domain_name=domain).update(domain_status="即将过期")
        logging.info(f"The domain for {domain} is valid and will expire in {days_until_expiry} days.")
    elif days_until_expiry <= 1 and days_until_expiry > 0:
        notify_ding_talk(domain, domain_expire_time, days_until_expiry)
        logging.info(f"The domain for {domain} is valid and will expire in {days_until_expiry} days.")
    else:
        DomainMonitors.objects.filter(domain_name=domain).update(domain_status="已过期")
        DomainMonitors.objects.filter(domain_name=domain).update(domain_expire_days=0)
        logging.info(f"The domain for {domain} has expired.")


def aliyun_update_domain_list(accesskey_id, accesskey_secret, account_name):
    data = AliyunDomain.main(accesskey_id, accesskey_secret)
    if not data:
        logging.info("获取域名列表为空")
    else:
        domain_data = json.loads(data)
        for i in domain_data['Data']['Domain']:
            expiry_date_local = datetime.datetime.strptime(i['ExpirationDate'], '%Y-%m-%d %H:%M:%S')
            if i['DomainStatus'] == '3':
                defaults = {
                    "domain_account": account_name,
                    "domain_expire_time": i['ExpirationDate'],
                    "domain_expire_days": (expiry_date_local - datetime.datetime.now()).days,
                }
                DomainMonitors.objects.update_or_create(domain_name=i['DomainName'], defaults=defaults)

def aws_update_domain_list(accesskey_id, accesskey_secret, account_name):
    domains_list = aws_domain_list(accesskey_id, accesskey_secret)
    logging.info(f"开始更新{account_name}账号{domains_list}的域名列表")
    for i in domains_list:
        defaults = {
            "domain_account": account_name
        }
        DomainMonitors.objects.update_or_create(domain_name=i, defaults=defaults)


def namecheap_update_domain_list(accesskey_id, accesskey_secret, account_name):
    domain_info_list = get_namecheap_domain_info(api_user=accesskey_id, api_key=accesskey_secret)
    for i in domain_info_list:
        expiry_date_local = datetime.datetime.strptime(i['expires'], '%Y-%m-%d %H:%M:%S')
        defaults = {
            "domain_account": account_name,
            "domain_expire_time": i['expires'],
            "domain_expire_days": (expiry_date_local - datetime.datetime.now()).days,
        }
        DomainMonitors.objects.update_or_create(domain_name=i['domain'], defaults=defaults)

def auto_update_domain_list():
    # 自动更新各账号下域名列表
    all_account = models.AccountManagement.objects.all()
    try:
        for account in all_account:
            account_name = account.account_name
            accesskey_id = account.accesskey_id
            accesskey_secret = account.accesskey_secret
            logging.info(f"开始更新{account_name}账号的域名列表")
            if account.server_platform.server_platform == "ALIYUN":
                # if account.account_name == "刀豆123":
                aliyun_update_domain_list(accesskey_id, accesskey_secret, account_name)
            elif account.server_platform.server_platform == "AWS":
                aws_update_domain_list(accesskey_id, accesskey_secret, account_name)
            elif account.server_platform.server_platform == "NAMECHEAP":
                namecheap_update_domain_list(accesskey_id, accesskey_secret, account_name)
            else:
                logging.info(f"暂不支持{account.server_platform}平台")

        # 判断如果该条域名是阿里云的，则不进行过期时间等的更新
        # 阿里云的域名到期时间是通过阿里云的接口获取的，所以不用自己去查询
        domain_name_list = DomainMonitors.objects.get_queryset().values_list('domain_name', flat=True)
        for i in domain_name_list:
            domain_data = DomainMonitors.objects.get(domain_name=i)
            account_name = domain_data.domain_account
            if AccountManagement.objects.filter(account_name=account_name).filter(server_platform__server_platform__in=["ALIYUN", "NAMECHEAP"]):
                logging.info(f"阿里云或namecheap域名{i},不更新过期时间")
                logging.info("判断是否发送通知")
                domain_expire_time = domain_data.domain_expire_time
                days_until_expiry = domain_data.domain_expire_days
                determine_send_notify(i, domain_expire_time, days_until_expiry)
            else:
                logging.info(f"非阿里云或namecheap域名, 开始更新域名{i}的过期时间")
                update_domain_monitors(i)
        result = [
            {
                'instancename': "域名到期时间",
                'output': "Domain monitors update success!"
            }
        ]
    except Exception as e:
        logging.info(e)
        result = [
            {
                'instancename': "域名到期时间",
                'output': f"Domain monitors update failed! Error is {e}"
            }
        ]

    return result
    # return "Domain monitors update success!"

class DomainMonitorsSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = DomainMonitors
        fields = '__all__'

class DomainMonitorsViewSet(CustomModelViewSet):
    queryset = DomainMonitors.objects.all()
    serializer_class = DomainMonitorsSerializer

    # 排序规则进行配置
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by('domain_expire_days')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def domain_monitors_update(self, request):
        auto_update_domain_list()
        return HttpResponse("更新成功")

