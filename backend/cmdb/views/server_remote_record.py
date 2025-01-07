from cmdb.models import ServerRemoteRecord

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer



class ServerRemoteRecordSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = ServerRemoteRecord
        fields = "__all__"

class ServerRemoteRecordViewSet(CustomModelViewSet):
    queryset = ServerRemoteRecord.objects.all().order_by('-id')
    serializer_class = ServerRemoteRecordSerializer




