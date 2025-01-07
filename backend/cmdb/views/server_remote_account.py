from cmdb.models import ServerRemoteAccount, ServerInstance
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.json_response import DetailResponse
from rest_framework import serializers
from django.views.decorators.csrf import csrf_exempt
import json

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
        查询所有没有绑定远程账号的服务器信息
        :param request:
        :return:
        """
        remote_account_id = request.GET.get("obj")
        remote_account_detail_exclude = ServerInstance.objects.filter(remote_auth_id__isnull=False).exclude(remote_auth_id=remote_account_id).values_list('instancename', flat=True)
        data = {
            'remote_account_detail_exclude': remote_account_detail_exclude
        }
        return DetailResponse(data=data, msg="获取成功")



    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def ser_remote_account_detail(self, request):
        remote_account_id = request.GET.get("obj")
        remote_account_detail = ServerInstance.objects.filter(remote_auth_id=remote_account_id).values_list('instancename', flat=True)
        data = {
            'remote_account_detail': remote_account_detail
        }
        return DetailResponse(data=data, msg="获取成功")

    # @csrf_exempt
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def update_ser_remote_account(self, request, my_id=None):
        myid = my_id
        db_records = ServerInstance.objects.filter(remote_auth_id=myid).values_list('instancename', flat=True)
        print(db_records)
        data = json.loads(request.body.decode())
        print(data)
        db_records_to_change = []
        for db_record in db_records:
            print(db_record)
            if db_record not in [recode['label'] for recode in data]:
                db_records_to_change.append(db_record)
        print("123")
        print(db_records_to_change)
        for record in db_records_to_change:
            ServerInstance.objects.filter(instancename=record).update(remote_auth_id=None)
        for recode in data:
            print(recode)
            print("开始更新该条记录")
            instance_name = recode['label']
            print(instance_name)
            ServerInstance.objects.filter(instancename=instance_name).update(remote_auth_id=myid)
        #
        # for i in data:
        #     print(i)
        #     print(i['label'])
        # for db_record in db_records:
        # a = 0
        # for a  data.lenth:
        #     print(i)
        # 213
        # remote_account_detail = ServerInstance.objects.filter(remote_auth_id=remote_account_id).values_list('instancename', flat=True)
        # data = {
        #     'remote_account_detail': remote_account_detail
        # }
        return DetailResponse(msg="更新完成")