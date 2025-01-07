import json
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.viewsets import ViewSet
from container.utils.k8s_api import K8SClusterSelect
import logging
from container.models import K8sCluster
from rest_framework.decorators import action

class K8sServiceViewSet(ViewSet):

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


        # if namespace is None:
        #     namespace = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_default_namespace", flat=True).first()
        # if cluster_name is None:
        #     cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name", flat=True).first()
        

        try:
            cluster_select = K8SClusterSelect(k8s_cluster_name)
            my_data = cluster_select.service_list(namespace, cluster_name)
        except Exception as e:
            logging.error(e)
            message = {
                "code": 4000,
                "data": "",
                # "msg": "集群数据获取失败，请检查集群的配置信息"
                "msg": e
            }
            return JsonResponse(message, safe=False)


        service_name_filter = request.GET.get('service_name')
        if service_name_filter:
            my_data = [service for service in my_data if service_name_filter in service['service_name']]

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
        print(data)
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        if cluster_name is None or cluster_name is '':
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                             flat=True).first()

            if namespace is None or namespace is '':
                namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()
        if namespace is None or namespace is '':
            namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()

        service_form = data
        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.service_create_or_change(namespace, service_form)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def svc_detail(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        service_name = request.GET.get('service_name')
        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.service_detail(namespace, service_name, cluster_name)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def svc_yaml(self, request, *args, **kwargs):
        service_name = request.GET.get('service_name')
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        cluster_select = K8SClusterSelect(cluster_name)
        service_yaml = cluster_select.service_yaml(namespace, service_name)


        message = {
            "code": 2000,
            "data": {
                "data": service_yaml
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['post'], detail=False)
    def svc_yaml_create(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        yaml_data = data['yaml_data']
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
        data = cluster_select.service_yaml_create(namespace, yaml_data)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['put'], detail=False)
    def svc_yaml_update(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        service_name = data['service_name']
        yaml_data = data['yaml_data']

        print(yaml_data)
        print(cluster_name)

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.service_yaml_update(namespace, service_name, yaml_data)

        # deployment_messages = "ok"
        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['delete'], detail=False)
    def svc_delete(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        service_name = data['service_name']

        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.service_delete(namespace, service_name)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)