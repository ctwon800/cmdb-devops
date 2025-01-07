from kubernetes import client
import logging
from django.utils import timezone
import yaml
from kubernetes.client import ApiException


def pvc_list(self, namespace, cluster_name):
    v1 = client.CoreV1Api()
    pvc_list = []
    pvc_list_data = v1.list_namespaced_persistent_volume_claim(namespace)
    for pvc in pvc_list_data.items:
        pvc_list.append({
            "pvc_name": pvc.metadata.name,
            "pvc_labels": pvc.metadata.labels,
            "pvc_annotations": pvc.metadata.annotations,
            "pvc_storage_class": pvc.spec.storage_class_name,
            "pvc_access_modes": pvc.spec.access_modes,
            "pvc_volume_name": pvc.spec.volume_name,
            "pvc_capacity": pvc.status.capacity,
            "pvc_phase": pvc.status.phase,
            "pvc_creation_timestamp": timezone.localtime(pvc.metadata.creation_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "namespace": namespace,
            "cluster_name": cluster_name
        })
    return pvc_list