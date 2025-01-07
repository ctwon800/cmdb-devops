import json

import pytz
from kubernetes import client
import logging
from kubernetes.client import ApiException


def node_list(self):
    v1 = client.CoreV1Api()
    nodes = v1.list_node()
    node_messages = []
    for node in nodes.items:
        if node.spec.unschedulable == True:
            node_schedule = 'True'
        else:
            node_schedule = 'False'
        node_name = node.metadata.name
        conditions = node.status.conditions
        for condition in conditions:
            if condition.type == 'Ready' and condition.status == 'True':
                node_status = 'Ready'
                break
        else:
            node_status = 'NotReady'
        for add in node.status.addresses:
            if add.type == 'InternalIP':
                node_ip = add.address
        kubectl_version = node.status.node_info.kubelet_version
        container_runtime_version = node.status.node_info.container_runtime_version
        node_message = {
            "cluster_name": self.cluster_name,
            "node_name": node_name,
            "node_status": node_status,
            "node_schedule": node_schedule,
            "node_ip": node_ip,
            "kubectl_version": kubectl_version,
            "container_runtime_version": container_runtime_version
        }
        node_messages.append(node_message)
    return node_messages


def node_detail(self, node_name):
        v1 = client.CoreV1Api()

        # 获取在指定节点上运行的所有 Pod
        pods = v1.list_pod_for_all_namespaces(field_selector=f'spec.nodeName={node_name}')
        pods_message = []
        for pod in pods.items:
            pod_name = pod.metadata.name
            namespace = pod.metadata.namespace
            pod_ip = pod.status.pod_ip
            creation_time = pod.metadata.creation_timestamp
            phase = pod.status.phase
            creation_time_utc = pod.metadata.creation_timestamp
            # 转成可读格式
            utc_tz = pytz.utc
            shanghai_tz = pytz.timezone('Asia/Shanghai')
            # 将UTC时间转换为上海时间
            creation_time_shanghai = creation_time_utc.replace(tzinfo=utc_tz).astimezone(shanghai_tz)
            creation_time_str = creation_time_shanghai.strftime("%Y-%m-%d %H:%M:%S")

            pods_message.append({
                "pod_name": pod_name,
                "namespace": namespace,
                "pod_ip": pod_ip,
                "creation_time": creation_time_str,
                "status": phase
            })


        # 获取节点的信息
        node = v1.read_node(node_name)
        allocatable = node.status.allocatable
        capacity = node.status.capacity

        # 转换并打印容量信息
        cpu_capacity_cores = int(capacity['cpu'])
        memory_capacity_bytes = int(capacity['memory'].replace('Ki', '')) * 1024  # Convert Ki to bytes
        memory_capacity_mb = memory_capacity_bytes // (1024 * 1024)  # Convert bytes to MB


        # 转换并打印可分配资源信息
        cpu_allocatable_cores = int(allocatable['cpu'].replace('m', '')) / 1000  # Convert millicores to cores
        memory_allocatable_bytes = int(allocatable['memory'].replace('Ki', '')) * 1024  # Convert Ki to bytes
        memory_allocatable_mb = memory_allocatable_bytes // (1024 * 1024)  # Convert bytes to MB


        # 获取节点上运行的容器组数量
        num_pods_running = len(pods.items)

        # 打印运行的容器组数量
        logging.info(f"\nNumber of Pods running on node {node_name}: {num_pods_running}")

        # 获取节点最大能够容纳的 Pod 数量
        max_pods = int(allocatable.get('pods', 0))
        logging.info(f"Maximum number of Pods that can be scheduled on node {node_name}: {max_pods}")

        node_message = {
            "node_name": node_name,
            "pod_list": pods_message,
            "cpu_capacity_cores": cpu_capacity_cores,
            "memory_capacity_mb": memory_capacity_mb,
            "cpu_allocatable_cores": cpu_allocatable_cores,
            "memory_allocatable_mb": memory_allocatable_mb,
            "num_pods_running": num_pods_running,
            "max_pods": max_pods
        }
        return node_message

def node_schedule_status(self, node_name, status):
    v1 = client.CoreV1Api()
    if status == 'False':
        status = False
    elif status == 'True':
        status = True
    body = {
        "spec": {
            "unschedulable": status
        }
    }
    response = v1.patch_node(node_name, body)
    # 读取修改后response返回node的unschedulable属性
    check_node_unschedulable = response.spec.unschedulable
    if status is False:
        if check_node_unschedulable is None:
            return "修改成功"
        else:
            return "修改失败"
    elif status is True:
        if check_node_unschedulable is True:
            return "修改成功"
        else:
            return "修改失败"


def node_drain(self, node_name):
    # 创建 CoreV1Api 实例
    v1 = client.CoreV1Api()

    # 判断节点的调度状态。
    node = v1.read_node(node_name)
    if not node.spec.unschedulable:
        node_body = {
            "spec": {
                "unschedulable": True
            }
        }
        logging.info(f"Node {node_name} set schedule is unschedulable")
        v1.patch_node(node_name, node_body)

    pods = v1.list_pod_for_all_namespaces(field_selector=f"spec.nodeName={node_name}")
    for pod in pods.items:
        if pod.metadata.owner_references and pod.metadata.owner_references[0].kind == "DaemonSet":
            continue

        body = client.V1DeleteOptions(
            grace_period_seconds=0
        )
        try:
            v1.delete_namespaced_pod(pod.metadata.name, pod.metadata.namespace, body=body)
            logging.info(f"Evicted Pod: {pod.metadata.name} from Namespace: {pod.metadata.namespace}")
        except client.exceptions.ApiException as e:
            if e.status == 404:
                logging.info(f"Pod not found: {pod.metadata.name}")
            else:
                raise
    return "Node drain successfully"

def node_delete(self, node_name):
    # 先排空节点
    logging.info(f"Node {node_name} drain")
    logging.info(self.node_drain(node_name))
    v1 = client.CoreV1Api()
    v1.delete_node(node_name)
    logging.info(f"Node {node_name} deleted successfully")
    return f"Node {node_name} deleted successfully"


def node_label(self, node_name):
    v1 = client.CoreV1Api()
    node_info = v1.read_node(name=node_name)
    labels = node_info.metadata.labels
    return labels

def node_label_update(self, node_name, new_labels):

    v1 = client.CoreV1Api()
    # 将字符串转换为字典
    try:
        new_labels = json.loads(new_labels)
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing new_labels: {e}")
        return f"Error parsing new_labels: {e}"

    node = v1.read_node(name=node_name)
    try:
        # 更新 labels
        node.metadata.labels.update(new_labels)
    except Exception as e:
        logging.error(f"Error updating labels: {e}")
        return f"Error updating labels: {e}"
    try:
        v1.patch_node(name=node_name, body={"metadata": {"labels": node.metadata.labels}})
        return "Node label updated successfully"
    except ApiException as e:
        return f"Error updating node label: {e}"

def node_label_delete(self, node_name, label_key):
    v1 = client.CoreV1Api()
    node = v1.read_node(name=node_name)
    # 检查标签是否存在
    if label_key not in node.metadata.labels:
        return f"Label '{label_key}' not found on node '{node_name}'"
    try:
        # 删除指定标签
        node.metadata.labels.pop(label_key)
    except Exception as e:
        logging.error(f"Error deleting label: {e}")
        return f"Error deleting label: {e}"
    try:
        v1.replace_node(name=node_name, body=node)
        return "Node label deleted successfully"
    except ApiException as e:
        return f"Error deleting node label: {e}"


def node_taint(self, node_name):
    v1 = client.CoreV1Api()
    node_info = v1.read_node(name=node_name)
    taints = node_info.spec.taints

    # 将 taints 转换为可序列化的格式
    taints_list = []
    if taints:
        for taint in taints:
            taints_list.append({
                "key": taint.key,
                "value": taint.value,
                "effect": taint.effect,
                "time_added": taint.time_added.isoformat() if taint.time_added else None,
            })

    return taints_list

def add_or_update_taint(taints_list, taint_dict):
    """
    添加新的污点或更新现有污点。
    """
    for existing_taint in taints_list:
        if existing_taint.key == taint_dict["key"]:
            # 更新现有污点的值
            existing_taint.value = taint_dict["value"]
            existing_taint.effect = taint_dict["effect"]
            logging.info(f"更新污点: {taint_dict['key']}={taint_dict['value']}:{taint_dict['effect']}")
            return
    # 添加新污点
    new_taint = client.V1Taint(
        key=taint_dict["key"],
        value=taint_dict["value"],
        effect=taint_dict["effect"]
    )
    taints_list.append(new_taint)
    logging.info(f"添加新污点: {taint_dict['key']}={taint_dict['value']}:{taint_dict['effect']}")



def node_taint_update(self, node_name, new_taints):
    v1 = client.CoreV1Api()
    try:
        # 获取节点对象
        node = v1.read_node(name=node_name)
        # 获取当前污点列表，如果不存在则初始化为空列表
        taints = node.spec.taints if node.spec.taints is not None else []
        # 打印当前污点列表
        logging.info("当前污点列表:")
        for taint in taints:
            logging.info(f"- Key: {taint.key}, Value: {taint.value}, Effect: {taint.effect}")

        # 处理 new_taints
        for taint in new_taints:
            key, value, effect = taint["key"], taint["value"], taint["effect"]

            if not key or not effect:
                # 忽略无效污点（key 或 effect 为空）
                continue
            # 如果 value 不为空，添加或更新污点
            add_or_update_taint(taints, taint)


        # 判断new_taints中所有的key是否都在taints中，如果taints中有的key在new_taints中没有，则taints中对应的key等内容删除
        for taint in taints:
            if taint.key not in [t["key"] for t in new_taints]:
                # 如果taints中的key不在new_taints中，则删除该污点
                taints.remove(taint)
                logging.info(f"删除污点: {taint.key}={taint.value}:{taint.effect}")
        # 更新节点的污点列表
        body = {
            "spec": {
                "taints": taints
            }
        }
        # 提交更新到 Kubernetes 集群
        updated_node = v1.patch_node(name=node_name, body=body)
        logging.info(f"\n节点 {node_name} 的污点已成功更新。")
        # 打印更新后的污点列表
        logging.info("更新后的污点列表:")
        if updated_node.spec.taints:
            for taint in updated_node.spec.taints:
                logging.info(f"- Key: {taint.key}, Value: {taint.value}, Effect: {taint.effect}")
        else:
            logging.info("该节点没有污点。")
    except ApiException as e:
        logging.info(f"Exception when updating node taints: {e}")

