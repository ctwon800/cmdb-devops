from kubernetes import client
import logging
from django.utils import timezone
import yaml
from kubernetes.client import ApiException


def sercret_list(self, namespace, cluster_name):
    v1 = client.CoreV1Api()
    secrets = v1.list_namespaced_secret(namespace)
    secrets_list = []
    # print(secrets)
    for secret in secrets.items:
        secrets_list.append({
            "secret_name": secret.metadata.name,
            "secret_type": secret.type,
            "secret_labels": secret.metadata.labels,
            "secret_annotations": secret.metadata.annotations,
            "secret_data": secret.data,
            "secret_creation_timestamp": timezone.localtime(secret.metadata.creation_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "cluster_name": cluster_name,
            "namespace": namespace
        })
    return secrets_list

def image_secret(self, namespace):
    v1 = client.CoreV1Api()
    secrets = v1.list_namespaced_secret(namespace)
    return [secret.metadata.name for secret in secrets.items if secret.type == 'kubernetes.io/dockerconfigjson']
