from kubernetes import client
import logging


def restart_pods(self, namespace, pod_name):
    v1 = client.CoreV1Api()
    # 删除 Pod
    v1.delete_namespaced_pod(name=pod_name, namespace=namespace, body=client.V1DeleteOptions())
    logging.info(f"Pod '{pod_name}' has been restarted.")


def eviction_pods(self, namespace, pod_name):
    v1 = client.CoreV1Api()

    # 创建 Eviction 对象
    eviction = client.V1Eviction(
        metadata=client.V1ObjectMeta(name=pod_name, namespace=namespace),
        delete_options=client.V1DeleteOptions()
    )

    # 驱逐 Pod
    v1.create_namespaced_pod_eviction(name=pod_name, namespace=namespace, body=eviction)
    logging.info(f"Pod '{pod_name}' has been evicted.")


def eviction_pod_or_restart_deployment(self, namespace, pod_name):
    v1 = client.CoreV1Api()
    apps_v1 = client.AppsV1Api()
    print("0923949234")
    # 获取 Pod 对象
    pod = v1.read_namespaced_pod(name=pod_name, namespace=namespace)
    # 获取 Pod 的标签
    pod_labels = pod.metadata.labels

    # 查找与 Pod 标签匹配的 Deployment
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
    # print(deployments)
    deployment = None
    for dep in deployments.items:
        if all(pod_labels.get(key) == value for key, value in dep.spec.selector.match_labels.items()):
            deployment = dep
            print(deployment)
            break
    if deployment:
        # 获取 Deployment 的副本数
        replicas = deployment.spec.replicas
        deployment_name = deployment.metadata.name

        if replicas == 1:
            # 重启 Deployment
            self.deployment_restart(namespace, deployment_name)
            logging.info(f"Deployment '{deployment_name}' has only one replica. Deployment restarting...")
            return "Deployment '{deployment_name}' has only one replica. Restarting..."
        else:
            self.eviction_pods(namespace, pod_name)
            logging.info(f"Evicting Pod '{pod_name}'...")
            return f"Evicting Pod '{pod_name}'..."