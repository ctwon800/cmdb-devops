import json
import os

from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.viewsets import ViewSet

from application import settings
from container.utils.k8s_api import K8SClusterSelect
import logging
from container.models import K8sCluster
from rest_framework.decorators import action


class K8sIngressViewSet(ViewSet):

    def list(self, request, *args, **kwargs):
        k8s_cluster_name = request.GET.get('k8s_cluster_name')
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        if namespace is None:
            namespace = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_default_namespace",
                                                                                           flat=True).first()
        if cluster_name is None:
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                              flat=True).first()
        try:
            cluster_select = K8SClusterSelect(cluster_name)
            my_data = cluster_select.ingress_list(namespace, cluster_name)
        except Exception as e:
            logging.error(e)
            message = {
                "code": 4000,
                "data": "",
                # "msg": "集群数据获取失败，请检查集群的配置信息"
                "msg": e
            }
            return JsonResponse(message, safe=False)
        ingress_name_filter = request.GET.get('name')
        if ingress_name_filter:
            my_data = [ingress for ingress in my_data if ingress_name_filter in ingress['name']]

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
        # ingress_name = data['ingress_name']
        # status = data['ingress_status']
        # k8s_cluster_name = data['cluster_name']
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

        ingress_data = data
        cluster_select = K8SClusterSelect(cluster_name)

        data1 = cluster_select.ingress_change(namespace, ingress_data)
        print(data1)
        data = 'ok'
        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['post'], detail=False)
    def ing_yaml_create(self, request, *args, **kwargs):
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
        data = cluster_select.ing_yaml_create(namespace, yaml_data)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def ing_detail(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        ingress_name = request.GET.get('ingress_name')
        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.ingress_detail(namespace, ingress_name, cluster_name)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def ing_yaml(self, request, *args, **kwargs):
        ingress_name = request.GET.get('ingress_name')
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        cluster_select = K8SClusterSelect(cluster_name)
        ingress_yaml = cluster_select.ingress_yaml(namespace, ingress_name)
        # print(ingress_yaml.metadata.annotations)
        message = {
            "code": 2000,
            "data": {
                "data": ingress_yaml
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['put'], detail=False)
    def ing_yaml_update(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        ingress_name = data['ingress_name']
        yaml_data = data['yaml_data']

        print(yaml_data)
        print(cluster_name)

        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.ingress_yaml_update(namespace, ingress_name, yaml_data)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['delete'], detail=False)
    def ing_delete(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        ingress_name = data['ingress_name']

        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.ingress_delete(namespace, ingress_name)

        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def ing_class(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.ingress_class()
        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def ing_annotation(self, request, *args, **kwargs):
        file_path = os.path.join(settings.BASE_DIR, 'container', 'utils', 'nginx-ingress-annotations.txt')

        with open(file_path, 'r', encoding='utf-8') as file:
            # 加载 JSON 数据
            data = json.load(file)
        # data = json.dumps(data, indent=4, ensure_ascii=False)
        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def ing_tls_secret(self, request, *args, **kwargs):
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
        data = cluster_select.ingress_tls_secret(namespace)
        message = {
            "code": 2000,
            "data": {
                "data": data
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    # @action(methods=['get'], detail=False)
def ing_all_namespace_domain(cluster_name):
    # cluster_name = request.GET.get('cluster_name')
    try:
        cluster_select = K8SClusterSelect(cluster_name)
        data = cluster_select.ingress_all_namespace_domain()
    except Exception as e:
        logging.error(e)
        data = []

    return data
    # message = {
    #     "code": 2000,
    #     "data": {
    #         "data": data
    #     },
    #     "msg": "success"
    # }
    # return JsonResponse(message, safe=False)
