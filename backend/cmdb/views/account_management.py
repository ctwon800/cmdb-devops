import logging
import time

from django.http import HttpResponse
import pytz
from datetime import datetime


from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action

from cmdb import models
from cmdb.utils.aliyun_ecs import get_aliyun_server_instance
from cmdb.utils.aws_ec2 import get_aws_server_instance, get_aws_month_bill
from cmdb.models import ServerInstance, ServerPlatform, AccountManagement
import json
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer


def publicUpdateYunRes(account_name_id):
    data = models.AccountManagement.objects.get(id=account_name_id)
    platform = models.ServerPlatform.objects.get(id=data.server_platform_id)
    platform_name = platform.server_platform
    if platform_name == "ALIYUN":
        for region in data.region.split(","):
            logging.info(f"ALIYUN-账号：{data.account_name} 云资源开始更新")
            get_aliyun_server_instance(data.server_platform_id, data.id, data.accesskey_id, data.accesskey_secret,
                                       region)
            logging.info(f"ALIYUN-账号：{data.account_name} 云资源更新完成")
            output = f"ALIYUN-账号：{data.account_name} 云资源更新完成"
            res = {
                'instancename': data.account_name,
                'output': output
            }
    elif platform_name == "AWS":
        for region in data.region.split(","):
            logging.info(f"AWS-账号：{data.account_name} 云资源开始更新")
            get_aws_server_instance(data.server_platform_id, data.id, data.accesskey_id, data.accesskey_secret, region)
            logging.info(f"AWS-账号：{data.account_name} 云资源更新完成")
            output = f"AWS-账号：{data.account_name} 云资源更新完成"
            res = {
                'instancename': data.account_name,
                'output': output
            }
    else:
        print("平台不匹配")
        res = {
            'instancename': data.account_name,
            'output': "平台不匹配"
        }
    return res





def AutoUpdateYunRes():
    all_account = models.AccountManagement.objects.all()
    results = []
    for account in all_account:
        account_id = account.id
        res = publicUpdateYunRes(account_id)
        results.append(res)
    # return "Cloud resources update success!"
    return results


class AccountManagementSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = AccountManagement
        fields = '__all__'

    def to_representation(self, instance):
        # 获取原始序列化数据
        ret = super().to_representation(instance)
        # 移除 accesskey_secret 字段
        ret.pop('accesskey_secret', None)
        return ret

class AccountManagementViewSet(CustomModelViewSet):
    queryset = AccountManagement.objects.all()
    serializer_class = AccountManagementSerializer

    # filter_fields = ["id", "account_name", "login_username", "accesskey_id"]

    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def update_cloud_res(self, request):
        pk = request.data.get("id")
        publicUpdateYunRes(pk)
        return HttpResponse("更新成功")

