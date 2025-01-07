from kubernetes import client
import logging
from django.utils import timezone
import yaml
from kubernetes.client import ApiException


def configmapp_list(self, namespace, cluster_name):
    v1 = client.CoreV1Api()
    configmaps = v1.list_namespaced_config_map(namespace)
    configmap_list = []
    for configmap in configmaps.items:
        configmap_list.append({
            "configmap_name": configmap.metadata.name,
            "configmap_labels": configmap.metadata.labels,
            "configmap_annotations": configmap.metadata.annotations,
            "configmap_data": configmap.data,
            "configmap_creation_timestamp": timezone.localtime(configmap.metadata.creation_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "namespace": namespace,
            "cluster_name": cluster_name
        })
    return configmap_list