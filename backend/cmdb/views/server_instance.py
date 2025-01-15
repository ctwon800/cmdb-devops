from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import pytz
from datetime import datetime
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action

from cmdb import models
from cmdb.utils.aliyun_ecs import get_aliyun_server_instance
from cmdb.utils.aws_ec2 import get_aws_server_instance
from cmdb.models import ServerInstance, ServerPlatform, AccountManagement
import json
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer


class ServerInstanceSerializer(CustomModelSerializer, serializers.Serializer):
    """
    服务器管理-序列化器
    """
    # exprire_time = serializers.CharField(max_length=255, allow_null=True)


    # def validate_exprire_time(self, value):
    #     print("222")
    #     if value is None or value == '':
    #         # 如果字段值为空，重新赋值为常量
    #         value = '111'
    #     return value


    class Meta:
        model = ServerInstance
        fields = "__all__"

class ExportServerInstanceSerializer(CustomModelSerializer):
    class Meta:
        model = ServerInstance
        fields = "__all__"

class ImportServerInstanceSerializer(CustomModelSerializer):
    class Meta:
        model = ServerInstance
        fields = "__all__"
        # exclude = (
        #     "post",
        #     "user_permissions",
        #     "groups",
        #     "is_superuser",
        #     "date_joined",
        # )

class ServerInstanceViewSet(CustomModelViewSet):
    queryset = ServerInstance.objects.all()
    serializer_class = ServerInstanceSerializer
    search_fields = ['instanceid', 'instancename']
    # 导出
    export_field_label = {
        "cloud_platform": "云平台",
        "account_name": "账号名",
        "instanceid": "实例id",
        "instancename": "实例名称",
        "instancetype": "实例类型",
        "hostname": "主机名称",
        "regionid": "区域",
        "zoneid": "实例可用区",
        "osname": "OS",
        "ostype": "os类型",
        "cpu": "cpu",
        "memory": "memory",
        "public_ip": "公网ip",
        "primary_ip": "内网ip",
        "status": "运行状态",
        "create_time": "创建时间",
        "exprire_time": "过期时间",
        "start_time": "启动时间"
    }
    export_serializer_class = ExportServerInstanceSerializer

    # 导入
    import_field_dict = {
        "cloud_platform": "云平台",
        "account_name": "账号名",
        "instanceid": "实例id",
        "instancename": "实例名称",
        "instancetype": "实例类型",
        "hostname": "主机名称",
        "regionid": "区域",
        "zoneid": "实例可用区",
        "osname": "OS",
        "ostype": "os类型",
        "cpu": "cpu",
        "memory": "memory",
        "public_ip": "公网ip",
        "primary_ip": "内网ip",
        "status": "运行状态",
        "create_time": "创建时间",
        "exprire_time": "过期时间",
        "start_time": "启动时间"
    }
    import_serializer_class = ImportServerInstanceSerializer

    @action(methods=['GET'], detail=False)
    def GetServerInstance(self, request):
        get_aliyun_server_instance()
        get_aws_server_instance()
        return HttpResponse("更新成功")

    @action(methods=['GET'], detail=False)
    def test_in(self, request):
        print("123")
        ser_obj = models.ServerPlatform.objects.filter(pk=1).first()
        acc_obj = models.AccountManagement.objects.filter(pk=1).first()
        print(type(ser_obj))
        ins = models.ServerInstance.objects.create(instanceid="tt", instancename="pwer", server_platform=ser_obj,
                                                   account_name=acc_obj)
        print(ins, type(ins))


    @action(methods=['GET'], detail=False)
    def get_instance_simple(self, request):
        search_data = request.GET.get('search')
        if search_data:
            instance_data = models.ServerInstance.objects.filter(
                Q(instanceid__icontains=search_data) |
                Q(instancename__icontains=search_data)
            )
        else:
            instance_data = models.ServerInstance.objects.all()
        instance_list = instance_data.values_list('instanceid', 'instancename')
        instances = []
        for instance in instance_list:
            instance_item = {
                "instanceid": instance[0],
                "instancename": instance[1]
            }
            instances.append(instance_item)

        message = {
            "code": 2000,
            "data": {
                "data": instances
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def get_instances_exclude_group(self, request):
        """获取不在指定组内的所有服务器"""
        group_id = request.GET.get('group_id')
        if not group_id:
            message = {
                "code": 4000,
                "msg": "缺少group_id参数",
                "data": None
            }
            return JsonResponse(message)
        
        # 检查组是否存在
        if not models.ServersGroup.objects.filter(id=group_id).exists():
            message = {
                "code": 4000,
                "msg": "指定的组不存在",
                "data": None
            }
            return JsonResponse(message)
            
        # 如果组存在但没有服务器，直接返回所有服务器
        group = models.ServersGroup.objects.get(id=group_id)
        if not group.server_instances.exists():
            instances = models.ServerInstance.objects.all().values('id', 'instanceid', 'instancename')
        else:
            # 获取指定组内的所有服务器ID
            group_instances = group.server_instances.all().values_list('id', flat=True)
            # 排除这些服务器
            instances = models.ServerInstance.objects.exclude(
                id__in=group_instances
            ).values('id', 'instancename', 'instanceid', 'hostname', 'public_ip', 'primary_ip')
        
        message = {
            "code": 2000,
            "msg": "success",
            "data": {
                "data": list(instances)
            }
        }
        return JsonResponse(message)


# if __name__ == '__main__':
#     test_in()