from container.models import K8sCluster

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.serializers import CustomModelSerializer
from rest_framework.decorators import action
from django.http import JsonResponse



class K8sClusterSerializer(CustomModelSerializer):
    """
    服务器管理-序列化器
    """
    class Meta:
        model = K8sCluster
        fields = "__all__"

    def to_representation(self, instance):
        # 获取原始序列化数据
        ret = super().to_representation(instance)
        # 移除 k8s_cluster_config 字段
        ret.pop('k8s_cluster_config', None)
        return ret

class K8sClusterViewSet(CustomModelViewSet):
    queryset = K8sCluster.objects.all()
    serializer_class = K8sClusterSerializer


    @action(methods=['GET'], detail=False)
    def default_cluster(self, request):
        my_data = K8sCluster.objects.filter(k8s_cluster_is_default=True).values('k8s_cluster_name').first()
        print(my_data)
        message = {
            "code": 2000,
            "data": {
                "data": my_data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)






