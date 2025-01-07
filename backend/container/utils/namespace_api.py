from kubernetes import client
import logging
from container.models import K8sCluster

def namespace_list(self, cluster_name):
    v1 = client.CoreV1Api()
    namespaces = v1.list_namespace()
    namespace_exclude_list = K8sCluster.objects.get(k8s_cluster_name=cluster_name).k8s_exclude_namespace.split(",")

    namespace_messages = []

    for namespace in namespaces.items:
        if namespace_exclude_list:
            if namespace.metadata.name in namespace_exclude_list:
                logging.info(f"Namespace '{namespace.metadata.name}' is excluded.")
                continue
            else:
                logging.info(f"Namespace '{namespace.metadata.name}' is not excluded.")
                namespace_messages.append({
                    "namespace": namespace.metadata.name,
                    "status": namespace.status.phase
                })
        else:
            namespace_messages.append({
                "namespace": namespace.metadata.name,
                "status": namespace.status.phase
            })
    return namespace_messages