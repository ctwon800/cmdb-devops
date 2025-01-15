from cmdb.models import ServerRemoteAccount, ServerInstance
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.json_response import DetailResponse
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
import logging

class ServerRemoteAccountSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    # remark = serializers.CharField(max_length=255, allow_blank=True)
    class Meta:
        model = ServerRemoteAccount
        fields = "__all__"
        # fields = ['remote_name']
    def to_representation(self, instance):
        # 获取原始序列化数据
        ret = super().to_representation(instance)
        # 移除 remote_password 字段
        ret.pop('remote_password', None)
        ret.pop('remote_private_key', None)
        return ret

class ServerRemoteAccountViewSet(CustomModelViewSet):
    queryset = ServerRemoteAccount.objects.all()
    serializer_class = ServerRemoteAccountSerializer


    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def ser_remote_account(self, request):
        """
        查询所有没有绑定远程账号的服务器信息
        :param request:
        :return:
        """
        server_no_remote_account = ServerInstance.objects.values_list('instancename', flat=True)
        data = {
            'server_no_remote_account': server_no_remote_account,
        }
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def ser_remote_account_exclude(self, request):
        """
        查询未绑定账号和绑定指定账号的服务器信息
        :param request:
        :return:
        """
        remote_account_id = request.GET.get("obj")
        # 使用Q对象组合两个查询条件
        servers = ServerInstance.objects.filter(
            Q(remote_auth_id__isnull=True) | Q(remote_auth_id=remote_account_id)
        ).values_list('instancename', flat=True)
        
        data = {
            'remote_account_detail_exclude': list(servers)
        }
        return DetailResponse(data=data, msg="获取成功")



    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def ser_remote_account_detail(self, request):
        remote_account_id = request.GET.get("obj")
        remote_account_detail = ServerInstance.objects.filter(remote_auth_id=remote_account_id).values_list('instancename', flat=True)
        logging.info(f'已绑定账号的服务器 f{remote_account_detail}')
        data = {
            'remote_account_detail': remote_account_detail
        }
        return DetailResponse(data=data, msg="获取成功")

    # @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def update_ser_remote_account(self, request, my_id=None):
        myid = my_id
        data = json.loads(request.body.decode())
        
        # 获取当前已绑定该账号的所有服务器
        current_bound_servers = ServerInstance.objects.filter(
            remote_auth_id=myid
        ).values_list('instancename', flat=True)
        
        # 将要解绑的服务器（在current_bound_servers中但不在data中的服务器）
        servers_to_unbind = set(current_bound_servers) - set(data)
        if servers_to_unbind:
            logging.info(f'以下服务器将解除账号绑定: {servers_to_unbind}')
            ServerInstance.objects.filter(
                instancename__in=servers_to_unbind
            ).update(remote_auth_id=None)
        
        # 更新或绑定data中的服务器
        for server_name in data:
            logging.info(f'服务器 {server_name} 开始更新并绑定账号 {myid}')
            ServerInstance.objects.filter(
                instancename=server_name
            ).update(remote_auth_id=myid)
            
        return DetailResponse(msg="更新完成")