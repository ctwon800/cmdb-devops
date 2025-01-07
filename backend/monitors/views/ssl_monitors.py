import logging

from django.http import HttpResponse
from datetime import datetime
from rest_framework import filters
from dvadmin.utils.json_response import DetailResponse

from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from application import dispatch
from cmdb import models
from cmdb.models import ServerPlatform
from monitors.models import SSLMonitors
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from monitors.utils.aliyun_ssl import AliyunSSL
import ssl
import datetime
import socket
from monitors.utils.dingtalk import send_dingtalk_message
from container.views.k8s_ingress import ing_all_namespace_domain
from container.models import K8sCluster
import time
import json
from monitors.models import WebMonitors

def notify_ding_talk(domain, cert_expiry_date, days_until_expiry):
    # 钉钉通知
    content = f"""\n![ssl证书](https://img2.baidu.com/it/u=2391008139,1661176715&fm=253&fmt=auto&app=138&f=JPEG?w=816&h=351)\n ### SSL证书到期提醒\n - 证书域名：{domain}\n - 到期时间：{cert_expiry_date}\n - 到期天数：{days_until_expiry}
    """
    # 获取钉钉配置
    access_token = dispatch.get_system_config_values("configdingtalk.access_token")
    secret = dispatch.get_system_config_values("configdingtalk.secret")
    # 发送钉钉通知
    send_dingtalk_message(content, access_token, secret)


def check_certificate_expiry(domain):
    max_retries = 3
    retry_count = 0
    while retry_count < max_retries:
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    cert_expiry_date = datetime.datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    current_date = datetime.datetime.now()
                    days_until_expiry = (cert_expiry_date - current_date).days
                    
                    # 成功获取证书信息后，更新数据库并返回
                    SSLMonitors.objects.filter(ssl_domain=domain).update(
                        ssl_expire_days=days_until_expiry,
                        ssl_expire_time=cert_expiry_date
                    )
                    
                    if days_until_expiry > 31:
                        SSLMonitors.objects.filter(ssl_domain=domain).update(ssl_status="正常")
                        logging.info(f"The certificate for {domain} is valid and will expire in {days_until_expiry} days.")
                    elif days_until_expiry <= 31 and days_until_expiry > 15:
                        try:
                            if days_until_expiry % 31 == 0 and SSLMonitors.objects.filter(ssl_domain=domain).get(ssl_notice_enable="1"):
                                notify_ding_talk(domain, cert_expiry_date, days_until_expiry)
                        except Exception as e:
                            logging.info(e)
                        SSLMonitors.objects.filter(ssl_domain=domain).update(ssl_status="即将过期")
                        logging.info(f"The certificate for {domain} is valid and will expire in {days_until_expiry} days.")
                    elif days_until_expiry <= 15 and days_until_expiry > 1:
                        try:
                            if days_until_expiry % 7 == 0 and SSLMonitors.objects.filter(ssl_domain=domain).get(ssl_notice_enable="1"):
                                notify_ding_talk(domain, cert_expiry_date, days_until_expiry)
                        except Exception as e:
                            logging.info(e)
                        SSLMonitors.objects.filter(ssl_domain=domain).update(ssl_status="即将过期")
                        logging.info(f"The certificate for {domain} is valid and will expire in {days_until_expiry} days.")
                    elif days_until_expiry <=  1 and days_until_expiry > 0:
                        notify_ding_talk(domain, cert_expiry_date, days_until_expiry)
                        logging.info(f"The certificate for {domain} is valid and will expire in {days_until_expiry} days.")
                    else:
                        SSLMonitors.objects.filter(ssl_domain=domain).update(ssl_status="已过期")
                        SSLMonitors.objects.filter(ssl_domain=domain).update(ssl_expire_days=0)
                        logging.info(f"The certificate for {domain} has expired.")
                    break
                    
        except (socket.error, ssl.SSLError) as e:
            retry_count += 1
            if retry_count == max_retries:
                # 检查是否存在过期时间且过期时间大于当前时间
                cert_info = SSLMonitors.objects.filter(ssl_domain=domain).values('ssl_expire_time').first()
                if cert_info and cert_info['ssl_expire_time'] and cert_info['ssl_expire_time'] > datetime.datetime.now():
                    logging.info(f"证书 {domain} 过期时间存在且未过期，不设置为异常状态。")
                else:
                    # 所有重试都失败后，更新为异常状态
                    SSLMonitors.objects.filter(ssl_domain=domain).update(
                        ssl_status="异常",
                        ssl_notice_enable=0
                    )
                    logging.error(f"连接 {domain} 失败，已重试 {max_retries} 次: {str(e)}")
            else:
                logging.warning(f"连接 {domain} 失败，正在进行第 {retry_count + 1} 次重试")
                time.sleep(3)
                continue
        except Exception as e:
            # 检查是否存在过期时间且过期时间大于当前时间
            cert_info = SSLMonitors.objects.filter(ssl_domain=domain).values('ssl_expire_time').first()
            if cert_info and cert_info['ssl_expire_time'] and cert_info['ssl_expire_time'] > datetime.datetime.now():
                logging.info(f"证书 {domain} 过期时间存在且未过期，不设置为异常状态。")
            else:
                # 处理其他异常
                SSLMonitors.objects.filter(ssl_domain=domain).update(
                    ssl_status="异常",
                    ssl_notice_enable=0
                )
                logging.error(f"检查 {domain} 证书时发生错误: {str(e)}")
            break


def update_account_ssl(accesskey_id, accesskey_secret, account_name):

    data = AliyunSSL.main(accesskey_id, accesskey_secret)
    if not data:
        logging.info("获取证书为空")
    else:
        for i in data:
            if i['Status'] == "ISSUED" or i['Status'] == "WILLEXPIRED":
                defaults = {
                    "ssl_type": i['CertType'],
                    "ssl_account": account_name
                }
                SSLMonitors.objects.get_or_create(ssl_domain=i['Domain'], defaults=defaults)


def update_k8s_cluster_domain():
    k8s_cluster_name = K8sCluster.objects.values_list("k8s_cluster_name", flat=True)
    for i in k8s_cluster_name:
        domain_list = ing_all_namespace_domain(i)
        logging.info(f"获取集群{i}的域名列表为{domain_list}")
        for j in domain_list:
            defaults = {
                "ssl_type": "k8s",
                "ssl_account": i,
                "ssl_domain": j
            }
            defaults_web = {
                "web_uri": j,
                "web_account": i
            }
            SSLMonitors.objects.get_or_create(ssl_domain=j, defaults=defaults)
            WebMonitors.objects.get_or_create(web_uri=j, defaults=defaults_web)


def update_ssl_monitors_domain():
    platform = ServerPlatform.objects.get(server_platform="ALIYUN")
    all_account = models.AccountManagement.objects.filter(server_platform_id=platform.id)
    try:
        for account in all_account:
            account_name = account.account_name
            accesskey_id = account.accesskey_id
            accesskey_secret = account.accesskey_secret
            logging.info(f"开始更新{account_name}的SSL证书域名")
            update_account_ssl(accesskey_id, accesskey_secret, account_name)
        logging.info("开始更新k8s集群的域名列表")
        update_k8s_cluster_domain()
        result = [
            {
                'instancename': "SSL证书域名",
                'output': "SSL monitors update success!"
            }
        ]
        return result
    except Exception as e:
        result = [
            {
                'instancename': "SSL证书域名",
                'output': f"SSL monitors update failed! Error is {e}"
            }
        ]
        return result


def auto_update_account_ssl():
    ssl_monitors_domain = SSLMonitors.objects.get_queryset().values_list('ssl_domain', flat=True)
    for i in ssl_monitors_domain:
        check_certificate_expiry(i)
    result = [
        {
            'instancename': "SSL证书",
            'output': "SSL monitors update success!"
        }
    ]
    return result


class SSLMonitorsSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = SSLMonitors
        fields = '__all__'

class SSLMonitorsViewSet(CustomModelViewSet):
    queryset = SSLMonitors.objects.all()
    serializer_class = SSLMonitorsSerializer

    # 排序规则进行配置
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.exclude(ssl_status='异常').order_by('ssl_expire_days')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def ssl_monitors_update(self, request):
        auto_update_account_ssl()
        return HttpResponse("更新成功")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def ssl_monitors_error(self, request):
        """
        获取异常的证书列表
        """
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(ssl_status='异常')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return DetailResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def updateStatus(self, request, *args, **kwargs):
        """
        更改证书状态：正常与异常状态互相切换
        """
        try:
            data = json.loads(request.body.decode())
            ssl_id = data.get('id')
            if not ssl_id:
                return DetailResponse(code=400, msg="缺少必要的id参数")
            
            ssl_monitor = SSLMonitors.objects.filter(id=ssl_id).first()
            if not ssl_monitor:
                return DetailResponse(code=404, msg="未找到对应的SSL记录")
            
            # 状态切换逻辑
            new_status = "异常" if ssl_monitor.ssl_status == "正常" else "正常"
            ssl_monitor.ssl_status = new_status
            ssl_monitor.save()
            
            return DetailResponse(msg=f"状态已更新为：{new_status}")
        except Exception as e:
            return DetailResponse(code=500, msg=f"更新失败：{str(e)}")
    
    

