import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.viewsets import ViewSet
from container.utils.k8s_api import K8SClusterSelect
import logging
from container.models import K8sCluster
from rest_framework.decorators import action

class K8sSecretViewSet(ViewSet):

    def list(self, request, *args, **kwargs):
        k8s_cluster_name = request.GET.get('k8s_cluster_name')
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')

        if cluster_name is None or cluster_name is '':
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                             flat=True).first()

            if namespace is None or namespace is '':
                namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()
        if namespace is None or namespace is '':
            namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()


        try:
            cluster_select = K8SClusterSelect(k8s_cluster_name)
            my_data = cluster_select.sercret_list(namespace, cluster_name)
        except Exception as e:
            logging.error(e)
            message = {
                "code": 4000,
                "data": "",
                # "msg": "集群数据获取失败，请检查集群的配置信息"
                "msg": e
            }
            return JsonResponse(message, safe=False)


        secret_name_filter = request.GET.get('secret_name')
        if secret_name_filter:
            my_data = [secret for secret in my_data if secret_name_filter in secret['secret_name']]

        secret_type_filter = request.GET.get('secret_type')
        if secret_type_filter:
            my_data = [secret for secret in my_data if secret_type_filter in secret['secret_type']]

        # 获取前端传来的limit参数，默认为2
        total = len(my_data)
        page_size = int(request.GET.get('limit', 20))
        page_number = int(request.GET.get('page', 1))
        paginator = Paginator(my_data, page_size)
        page_obj = paginator.get_page(page_number)
        is_next = page_obj.has_next()
        is_previous = page_obj.has_previous()
        data_list = list(page_obj)

        message = {
            "code": 2000,
            "data": {
                "page": page_number,
                "total": total,
                "is_next": is_next,
                "is_previous": is_previous,
                "limit": page_size,
                "data": data_list
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)




    def put(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        service_name = data['service_name']
        status = data['service_status']
        k8s_cluster_name = data['cluster_name']

        cluster_select = K8SClusterSelect(k8s_cluster_name)

        result = cluster_select.service_schedule_status(service_name, status)
        message = {
            "code": 2000,
            "data": result,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def image_secret(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')

        if cluster_name is None or cluster_name is '':
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                             flat=True).first()

            if namespace is None or namespace is '':
                namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()
        if namespace is None or namespace is '':
            namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()


        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.image_secret(namespace)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)
