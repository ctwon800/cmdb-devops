import json
from container.utils.k8s_api import K8SClusterSelect
from django.http import JsonResponse
from rest_framework.views import APIView
from container.models import K8sCluster

class K8sNamespaceViewSet(APIView):

    def get(self, request, *args, **kwargs):
        cluster_name = request.query_params.get('cluster_name')

        if cluster_name is None or cluster_name is '':
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                             flat=True).first()


        cluster_select = K8SClusterSelect(cluster_name)
        my_data = cluster_select.namespace_list(cluster_name)
        message = {
            "code": 2000,
            "data": {
                "data": my_data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        givenname = data['givenname']
        sn = data['sn']
        mail = data['mail']
        return self.ldap_addUser(givenname, sn, mail)

    def put(self, request, *args, **kwargs):
        data = json.loads(request.body)
        uid = data['uid']
        password = data['password']
        print(password)
        return self.ldap_updateUserPassword(uid, password)

    def delete(self, request, *args, **kwargs):
        username = request.body.decode()
        # data = json.loads(request.body.decode())
        # print(data)
        # username = data['uid']
        print(username)
        return self.ldap_deleteUser(username)







# class K8sNodesInitSerializer(CustomModelSerializer):
#     """
#     初始化获取数信息(用于生成初始化json文件)
#     """
#
#     class Meta:
#         model = ServerPlatform
#         fields = ["server_platform"]
#         read_only_fields = ['id']
#
# class K8sNodesSerializer(CustomModelSerializer):
#     """
#     服务器管理-序列化器
#     """
#     class Meta:
#         model = ServerPlatform
#         fields = "__all__"

# class K8sNodesViewSet(CustomModelViewSet):
#     queryset = ServerPlatform.objects.all()
#     serializer_class = ServerPlatformSerializer



