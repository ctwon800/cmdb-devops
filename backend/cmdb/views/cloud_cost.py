from django.http import HttpResponse, JsonResponse
import pytz
from datetime import datetime, timedelta
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from io import StringIO

from cmdb import models
from cmdb.utils.aliyun_ecs import get_aliyun_month_count
from cmdb.utils.aws_ec2 import get_aws_month_bill
from cmdb.models import ServerInstance, ServerPlatform, AccountManagement, CloudCost
import json

from dvadmin.utils.json_response import DetailResponse
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer


# 将选择月份时区转换为上海并输出月份范围列表
def time_transform(start_time, end_time):
    start_time_default = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    end_time_default = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S.%fZ')
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    start_time_shanghai = start_time_default.replace(tzinfo=pytz.utc).astimezone(shanghai_tz)
    end_time_shanghai = end_time_default.replace(tzinfo=pytz.utc).astimezone(shanghai_tz)
    current_datetime = start_time_shanghai
    months = []
    while current_datetime <= end_time_shanghai:
        months.append(current_datetime.strftime('%Y-%m'))
        current_datetime += timedelta(days=30)
    return months

# 手动更新云账号的费用账号
def publicUpdateCloudCost(account_name_id, BillingCycle):
    data = models.AccountManagement.objects.get(id=account_name_id)
    platform = models.ServerPlatform.objects.get(id=data.server_platform_id)
    platform_name = platform.server_platform
    if platform_name == "ALIYUN":
        logging.info(f"ALIYUN-账号：{data.account_name} 云资源开始更新")
        get_aliyun_month_count(data.server_platform_id, data.id, data.accesskey_id, data.accesskey_secret,
                                   BillingCycle)
        logging.info(f"ALIYUN-账号：{data.account_name} 云资源更新完成")
        output = f"ALIYUN-：{data.account_name} cost update successfully."
    elif platform_name == "AWS":
        logging.info(f"AWS-账号：{data.account_name} 云资源开始更新")
        get_aws_month_bill(data.server_platform_id, data.id, data.accesskey_id, data.accesskey_secret,
                               BillingCycle)
        logging.info(f"AWS-账号：{data.account_name} 云资源更新完成")
        output = f"AWS-：{data.account_name} cost update successfully."
    else:
        print("平台不匹配")
        output = "平台不匹配"
    res = {
        'instancename': data.account_name,
        'output': output
    }
    return res

#   自动更新云账号费用账单
def AutoUpdateCloudCost():
    all_account = models.AccountManagement.objects.all()
    now_time = datetime.now()
    last_month_time = now_time.replace(month=now_time.month - 1)
    last_month = last_month_time.strftime('%Y-%m')
    for account in all_account:
        account_id = account.id
        res = publicUpdateCloudCost(account_id, last_month)
    return res



class CloudCostSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = CloudCost
        fields = "__all__"


class CloudCostViewSet(CustomModelViewSet):
    queryset = CloudCost.objects.all()
    serializer_class = CloudCostSerializer

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_month_list(self, request):
        month_list = CloudCost.objects.values_list('bill_cycle', flat=True).distinct().order_by('-bill_cycle')[:12]
        a = []
        for i in month_list:
            fa = {"bill_cycle": i}
            a.append(fa)
        b = {
            "data": {
                "data": a
            }
        }
        return JsonResponse(b, safe=False)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_all_account_month_count(self, request):
        bill_cycle_default_time = request.GET.get("obj")
        if bill_cycle_default_time:
            bill_cycle_default = datetime.strptime(bill_cycle_default_time, '%Y-%m-%dT%H:%M:%S.%fZ')
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            start_time_shanghai = bill_cycle_default.replace(tzinfo=pytz.utc).astimezone(shanghai_tz)
            bill_cycle = start_time_shanghai.strftime('%Y-%m')
            cost_month_cloud_list = CloudCost.objects.filter(bill_cycle=bill_cycle)
            data = []
            for i in cost_month_cloud_list:
                account_name = AccountManagement.objects.get(id=i.account_name_id).account_name
                cost = i.cost
                a = {
                    "account_name": account_name,
                    "cost": cost
                }
                data.append(a)
            return DetailResponse(data={"data": data}, msg="获取成功")
        else:
            return DetailResponse(msg="饼状图月份不能清空")


    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def get_month_count(self, request):
        account_name_id = request.data.get("account_name_id")
        bill_cycle_start = request.data.get("bill_cycle")[0]
        bill_cycle_end = request.data.get("bill_cycle")[1]
        bill_cycle_list = time_transform(bill_cycle_start, bill_cycle_end)
        for bill_cycle_item in bill_cycle_list:
            logging.info(f"正在更新 {account_name_id}, {bill_cycle_item}的费用账号")
            publicUpdateCloudCost(account_name_id, bill_cycle_item)
        return HttpResponse("更新成功")

    @action(methods=['PUT'], detail=False, permission_classes=[IsAuthenticated])
    def update_cloud_cost(self, request):
        account_name_id = request.data.get("id")
        bill_cycle = request.data.get("bill_cycle")
        publicUpdateCloudCost(account_name_id, bill_cycle)
        return HttpResponse("更新成功")


