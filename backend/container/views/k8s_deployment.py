import json
import logging

from container.utils.k8s_api import K8SClusterSelect
from django.http import JsonResponse
from django.core.paginator import Paginator
from container.models import K8sCluster
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action


class K8sDeploymentViewSet(ViewSet):

    @action(methods=['get'], detail=False)
    def dep_list(self, request, *args, **kwargs):
        namespace = request.GET.get('namespace')
        search_name = request.GET.get('name')
        if namespace is None:
            namespace = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_default_namespace", flat=True).first()
        cluster_name = request.GET.get('cluster_name')
        if cluster_name is None:
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name", flat=True).first()


        cluster_select = K8SClusterSelect(cluster_name)

        deploymemt_list_data = cluster_select.deployment_list(namespace, cluster_name)

        if search_name:
            search_deployment_list_data = []
            for i in deploymemt_list_data:
                if search_name:
                    if search_name in i["name"]:
                        search_deployment_list_data.append(i)
            deplpyment_data = search_deployment_list_data
        else:
            deplpyment_data = deploymemt_list_data


        total = len(deplpyment_data)
        # 获取前端传来的limit参数，默认为2
        page_size = int(request.GET.get('limit', 20))
        page_number = int(request.GET.get('page'))
        paginator = Paginator(deplpyment_data, page_size)
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


    @action(methods=['get'], detail=False)
    def dep_detail(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        deployment_name = request.GET.get('deployment_name')
        cluster_select = K8SClusterSelect(cluster_name)
        deployment_data = cluster_select.deployment_detail(namespace, deployment_name, cluster_name)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_data
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)


    @action(methods=['put'], detail=False)
    def dep_replicas(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']
        replicas = data['replicas']

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_replicas(namespace, deployment_name, replicas)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def dep_yaml(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        deployment_name = request.GET.get('deployment_name')
        cluster_select = K8SClusterSelect(cluster_name)
        deployment_yaml = cluster_select.deployment_detail_yaml(namespace, deployment_name)
        # print(deployment_data)
        # deployment_yaml = "ok\nmy\ntest"

        message = {
            "code": 2000,
            "data": {
                "data": deployment_yaml
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['put'], detail=False)
    def dep_yaml_update(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']
        yaml_data = data['yaml_data']

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_yaml_update(namespace, deployment_name, yaml_data)

        # deployment_messages = "ok"
        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['put'], detail=False)
    def dep_image_update(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']
        image = data['image']
        tag = data['newImage']
        if tag == "":
            tag = "latest"
        container_name = data['container_name']
        image_name = image + ":" + tag

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_image_update(namespace, deployment_name, container_name, image_name)
        logging.info(deployment_messages)
        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['get'], detail=False)
    def dep_history(self, request, *args, **kwargs):
        cluster_name = request.GET.get('cluster_name')
        namespace = request.GET.get('namespace')
        deployment_name = request.GET.get('deployment_name')
        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_history_detail(namespace, deployment_name, cluster_name)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['put'], detail=False)
    def dep_history_rollback(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']
        revision = data['revision']

        # print(revision, cluster_name, namespace, deployment_name)

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_rollback(namespace, deployment_name, cluster_name, revision)
        logging.info(deployment_messages)
        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['post'], detail=False)
    def dep_restart(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_restart(namespace, deployment_name)
        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['delete'], detail=False)
    def dep_delete(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        deployment_name = data['deployment_name']

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_delete(namespace, deployment_name)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)


    @action(methods=['get'], detail=False)
    def dep_labels(self, request, *args, **kwargs):
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
        deployment_messages = cluster_select.deployment_labels(namespace)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }

        return JsonResponse(message, safe=False)

    @action(methods=['post'], detail=False)
    def dep_yaml_create(self, request, *args, **kwargs):
        data = json.loads(request.body.decode())
        cluster_name = data['cluster_name']
        namespace = data['namespace']
        yaml_data = data['yaml_data']
        
        if cluster_name is None or cluster_name == '':
            cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name",
                                                                                             flat=True).first()

            if namespace is None or namespace == '':
                namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()
        if namespace is None or namespace == '':
            namespace = K8sCluster.objects.filter(k8s_cluster_name=cluster_name).values_list("k8s_default_namespace",
                                                                                           flat=True).first()

        cluster_select = K8SClusterSelect(cluster_name)
        deployment_messages = cluster_select.deployment_yaml_create(namespace, yaml_data)

        message = {
            "code": 2000,
            "data": {
                "data": deployment_messages
            },
            "msg": "success"
        }
        return JsonResponse(message, safe=False)