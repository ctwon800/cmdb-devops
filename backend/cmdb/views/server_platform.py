from cmdb.models import ServerPlatform

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer

class ServerPlatformInitSerializer(CustomModelSerializer):
    """
    初始化获取数信息(用于生成初始化json文件)
    """

    class Meta:
        model = ServerPlatform
        fields = ["server_platform"]
        read_only_fields = ['id']

class ServerPlatformSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = ServerPlatform
        fields = "__all__"

class ServerPlatformViewSet(CustomModelViewSet):
    queryset = ServerPlatform.objects.all()
    serializer_class = ServerPlatformSerializer



