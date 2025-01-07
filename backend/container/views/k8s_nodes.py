import json
import logging

from rest_framework.viewsets import ViewSet

from container.utils.k8s_api import K8SClusterSelect
from django.http import JsonResponse
from django.core.paginator import Paginator
from rest_framework.decorators import action


class K8sNodeViewSet(ViewSet):

    def list(self, request, *args, **kwargs):
        k8s_cluster_name = request.GET.get('k8s_cluster_name')
        try:
            cluster_select = K8SClusterSelect(k8s_cluster_name)
            my_data = cluster_select.node_list()
        except Exception as e:
            logging.error(e)
            message = {
                "code": 4000,
                "data": "",
                # "msg": "集群数据获取失败，请检查集群的配置信息"
                "msg": e
            }
            return JsonResponse(message, safe=False)


        node_name_filter = request.GET.get('node_name')
        if node_name_filter:
            my_data = [node for node in my_data if node_name_filter in node['node_name']]

        # 获取前端传来的limit参数，默认为2
        total = len(my_data)
        page_size = int(request.GET.get('limit', 20))
        page_number = int(request.GET.get('page'))
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
        node_name = data['node_name']
        status = data['node_status']
        k8s_cluster_name = data['cluster_name']

        cluster_select = K8SClusterSelect(k8s_cluster_name)

        result = cluster_select.node_schedule_status(node_name, status)
        message = {
            "code": 2000,
            "data": result,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    def delete(self, request, *args, **kwargs):
        node_name = request.GET.get('node_name')
        cluster_name = request.GET.get('cluster_name')

        cluster_select = K8SClusterSelect(cluster_name)

        data = cluster_select.node_delete(node_name)
        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def node_detail(self, request, *args, **kwargs):
        node_name = request.GET.get('node_name')
        cluster_name = request.GET.get('cluster_name')

        cluster_select = K8SClusterSelect(cluster_name)

        node_data = cluster_select.node_detail(node_name)
        message = {
            "code": 2000,
            "data": node_data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['post'], detail=False)
    def node_eviction(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        pod_name = data['pod_name']
        namespace = data['namespace']
        cluster_name = data['cluster_name']
        logging.info(f"Pod '{pod_name}' start evicted.")
        cluster_select = K8SClusterSelect(cluster_name)
        result = cluster_select.eviction_pod_or_restart_deployment(namespace, pod_name)
        print(result)
        message = {
            "code": 2000,
            "data": result,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def node_drain(self, request, *args, **kwargs):

        node_name = request.GET.get('node_name')
        cluster_name = request.GET.get('cluster_name')

        cluster_select = K8SClusterSelect(cluster_name)

        data = cluster_select.node_drain(node_name)
        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def node_label(self, request, *args, **kwargs):

        node_name = request.GET.get('node_name')
        cluster_name = request.GET.get('cluster_name')
        cluster_select = K8SClusterSelect(cluster_name)

        data = cluster_select.node_label(node_name)

        # data_lis = "123"
        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['put'], detail=False)
    def node_label_update(self, request, *args, **kwargs):

        data = json.loads(request.body.decode())
        node_name = data['node_name']
        cluster_name = data['cluster_name']
        new_labels = data['new_labels']

        cluster_select = K8SClusterSelect(cluster_name)

        # Assuming cluster_select has a method to update the node label
        data = cluster_select.node_label_update(node_name, new_labels)

        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)

    @action(methods=['delete'], detail=False)
    def node_label_delete(self, request, *args, **kwargs):

        data = json.loads(request.body.decode())
        node_name = data['node_name']
        cluster_name = data['cluster_name']
        label_key = data['label_key']

        cluster_select = K8SClusterSelect(cluster_name)

        # Assuming cluster_select has a method to update the node label
        data = cluster_select.node_label_delete(node_name, label_key)

        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def node_taint(self, request, *args, **kwargs):

        node_name = request.GET.get('node_name')
        cluster_name = request.GET.get('cluster_name')
        cluster_select = K8SClusterSelect(cluster_name)

        data = cluster_select.node_taint(node_name)

        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)


    @action(methods=['put'], detail=False)
    def node_taint_update(self, request, *args, **kwargs):

        data = json.loads(request.body.decode())
        node_name = data['node_name']
        cluster_name = data['cluster_name']
        new_taints = data['new_taints']

        cluster_select = K8SClusterSelect(cluster_name)

        data = cluster_select.node_taint_update(node_name, new_taints)

        message = {
            "code": 2000,
            "data": data,
            "msg": "success"
        }
        return JsonResponse(message, safe=False)