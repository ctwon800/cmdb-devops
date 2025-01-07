from kubernetes import client
from datetime import datetime
import yaml
import pytz
import logging
from django.utils import timezone
from kubernetes.client import ApiException


def remove_none(data):
    if isinstance(data, dict):
        return {k: remove_none(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_none(item) for item in data if item is not None]
    else:
        return data

def trans_time_to_shanghai(timestamp):
    utc_tz = pytz.utc
    shanghai_tz = pytz.timezone('Asia/Shanghai')
    # 将UTC时间转换为上海时间
    time_shanghai_str = timestamp.replace(tzinfo=utc_tz).astimezone(shanghai_tz)
    time_shanghai = time_shanghai_str.strftime("%Y-%m-%d %H:%M:%S")
    return time_shanghai



def deployment_restart(self, namespace, deployment_name):
    v1 = client.AppsV1Api()
    # 获取 Deployment 对象
    deployment = v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
    # 更新 Deployment 的注释，触发重新创建 Pods
    deployment.spec.template.metadata.annotations = {"kubectl.kubernetes.io/restartedAt": str(time.time())}
    # 应用更新
    v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
    logging.info(f"Deployment '{deployment_name}' has been restarted.")
    return f"Deployment '{deployment_name}' has been restarted."


def deployment_list(self, namespace, cluster_name):
    apps_v1 = client.AppsV1Api()
    deployments = apps_v1.list_namespaced_deployment(namespace=namespace)
    deployments_messages = []
    for deployment in deployments.items:
        dep_name = deployment.metadata.name
        dep_replicas = deployment.spec.replicas
        dep_namespace = deployment.metadata.namespace
        dep_ready_replicas = deployment.status.ready_replicas
        dep_available_replicas = deployment.status.available_replicas
        dep_unavailable_replicas = deployment.status.unavailable_replicas
        dep_updated_replicas = deployment.status.updated_replicas
        dep_labels = deployment.spec.template.metadata.labels
        dep_container_replicas_detail = str(dep_available_replicas) + '/' + str(dep_replicas)
        dep_create_time = timezone.localtime(deployment.metadata.creation_timestamp).strftime(
            "%Y-%m-%d %H:%M:%S")
        dep_images = []
        for container in deployment.spec.template.spec.containers:
            dep_images.append(container.image)
        deployments_messages.append({
            "name": dep_name,
            "replicas": dep_replicas,
            "namespace": dep_namespace,
            "ready_replicas": dep_ready_replicas,
            "available_replicas": dep_available_replicas,
            "container_replicas_detail": dep_container_replicas_detail,
            "labels": dep_labels,
            "create_time": dep_create_time,
            "updated_replicas": dep_updated_replicas,
            "unavailable_replicas": dep_unavailable_replicas,
            "images": dep_images,
            "cluster_name": cluster_name,
        })
    return deployments_messages

def deployment_detail(self, namespace, deployment_name, cluster_name):

    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace, pretty=False)

    dep_name = deployment.metadata.name
    dep_replicas = deployment.spec.replicas
    dep_namespace = deployment.metadata.namespace
    dep_ready_replicas = deployment.status.ready_replicas
    dep_available_replicas = deployment.status.available_replicas
    dep_unavailable_replicas = deployment.status.unavailable_replicas
    dep_updated_replicas = deployment.status.updated_replicas
    dep_labels = deployment.spec.template.metadata.labels
    dep_selector = deployment.spec.selector.match_labels
    dep_container_replicas_detail = str(dep_available_replicas) + '/' + str(dep_replicas)
    dep_create_time = timezone.localtime(deployment.metadata.creation_timestamp).strftime(
        "%Y-%m-%d %H:%M:%S")
    dep_strategy_type = deployment.spec.strategy.type
    dep_strategy_rolling_update = deployment.spec.strategy.rolling_update
    dep_strategy_rolling_update_max_surge = dep_strategy_rolling_update.max_surge
    dep_strategy_rolling_update_max_unavailable = dep_strategy_rolling_update.max_unavailable
    dep_restart_policy = deployment.spec.template.spec.restart_policy
    dep_conditions = []
    for condition in deployment.status.conditions:
        dep_conditions_status = condition.status
        dep_conditions_last_transition_time = timezone.localtime(
            condition.last_transition_time).strftime("%Y-%m-%d %H:%M:%S")
        dep_conditions_message = condition.message
        dep_conditions_reason = condition.reason
        dep_conditions_type = condition.type
        dep_conditions.append({
            "conditions_type": dep_conditions_type,
            "conditions_status": dep_conditions_status,
            "conditions_last_transition_time": dep_conditions_last_transition_time,
            "conditions_message": dep_conditions_message,
            "conditions_reason": dep_conditions_reason,
        })
    dep_images = []
    for container in deployment.spec.template.spec.containers:
        dep_images.append(container.image)

    dep_containers = deployment.spec.template.spec.containers
    dep_containers_list = []
    for container in dep_containers:
        dep_container_name = container.name
        dep_container_image = container.image
        dep_container_image_pull_policy = container.image_pull_policy

        dep_containers_list.append({
            "name": dep_container_name,
            "image": dep_container_image,
            "image_pull_policy": dep_container_image_pull_policy,
        })

    dep_init_containers = deployment.spec.template.spec.init_containers
    dep_init_containers_list = []
    if dep_init_containers is not None:
        for init_container in dep_init_containers:
            dep_init_container_name = init_container.name
            dep_init_container_image = init_container.image
            dep_init_container_image_pull_policy = init_container.image_pull_policy

            dep_init_containers_list.append({
                "name": dep_init_container_name,
                "image": dep_init_container_image,
                "image_pull_policy": dep_init_container_image_pull_policy,
            })

    deployments_messages = {
        "name": dep_name,
        "replicas": dep_replicas,
        "namespace": dep_namespace,
        "ready_replicas": dep_ready_replicas,
        "available_replicas": dep_available_replicas,
        "container_replicas_detail": dep_container_replicas_detail,
        "labels": dep_labels,
        "create_time": dep_create_time,
        "updated_replicas": dep_updated_replicas,
        "unavailable_replicas": dep_unavailable_replicas,
        "images": dep_images,
        "cluster_name": cluster_name,
        "selector": dep_selector,
        "strategy_type": dep_strategy_type,
        "strategy_rolling_update_max_surge": dep_strategy_rolling_update_max_surge,
        "strategy_rolling_update_max_unavailable": dep_strategy_rolling_update_max_unavailable,
        "restart_policy": dep_restart_policy,
        "containers": dep_containers_list,
        "init_containers": dep_init_containers_list,
        "conditions": dep_conditions,
    }
    return deployments_messages


def deployment_detail_yaml(self, namespace, deployment_name):
    apps_v1 = client.AppsV1Api()
    deployment_detail = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace, pretty=False)
    deployment = deployment_detail.to_dict()

    metadata = deployment.get('metadata', {})
    if 'managed_fields' in metadata:
        del metadata['managed_fields']
    data = yaml.dump(deployment, default_flow_style=False)
    clean_data = yaml.safe_load(data)
    clean_data = remove_none(clean_data)
    yaml_data = yaml.dump(clean_data, default_flow_style=False)
    return yaml_data


def deployment_event(self, namespace, deployment_name):
    core_v1 = client.CoreV1Api()
    field_selector = f"involvedObject.kind=Deployment,involvedObject.name={deployment_name},involvedObject.namespace={namespace}"
    events = core_v1.list_namespaced_event(namespace=namespace, field_selector=field_selector)
    return events
    # for event in events.items:
    #     if event.involved_object.name == deployment_name:
    #         print(event)

def deployment_replicas(self, namespace, deployment_name, replicas_num):
    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace, pretty=False)
    deployment.spec.replicas = replicas_num
    try:
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        return f'修改replicas成功，replicas为{replicas_num}'
    except ApiException as e:
        logging.error(e)
        return f'修改replicas失败，失败的原因为{e}'

def deployment_yaml_update(self, namespace, deployment_name, yaml_data):
    apps_v1 = client.AppsV1Api()
    updated_deployment_yaml = yaml.safe_load(yaml_data)
    try:
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=updated_deployment_yaml)
        return f'修改deployment成功'
    except ApiException as e:
        logging.error(e)
        return f'修改deployment失败，失败的原因为{e}'

def deployment_image_update(self, namespace, deployment_name, container_name, image_name):
    apps_v1 = client.AppsV1Api()
    deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace, pretty=False)

    updated = False
    for container in deployment.spec.template.spec.containers:
        if container.name == container_name:
            container.image = image_name
            updated = True
            break

    if not updated:
        return f"Container '{container_name}' not found in Deployment '{deployment_name}'."

    try:
        apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=namespace, body=deployment)
        return f'修改image成功，image为{image_name}'
    except ApiException as e:
        logging.error(e)
        return f'修改image失败，失败的原因为{e}'
    except Exception as e:
        logging.error(e)
        return f'修改image失败，失败的原因为{e}'


def deployment_history_list(self, namespace, deployment_name, cluster_name):
    v1 = client.AppsV1Api()
    # 获取指定 Deployment 的当前配置
    try:
        deployment = v1.read_namespaced_deployment(namespace=namespace, name=deployment_name)
    except client.exceptions.ApiException as e:
        logging.error(f"Error getting deployment: {e}")
        return


    current_revision = deployment.metadata.annotations.get('deployment.kubernetes.io/revision')

    # 获取 Deployment 的标签选择器
    selector = deployment.spec.selector.match_labels
    label_selector = ','.join([f'{k}={v}' for k, v in selector.items()])

    # 获取 Deployment 的 ReplicaSets
    try:
        replicasets = v1.list_namespaced_replica_set(namespace, label_selector=label_selector)
        return replicasets, current_revision
    except client.exceptions.ApiException as e:
        logging.error(f"Error listing replica sets: {e}")
        return

def deployment_history_detail(self, namespace, deployment_name, cluster_name):
    replicasets, current_revision = self.deployment_history_list(namespace, deployment_name, cluster_name)
    history = []
    for rs in replicasets.items:
        revision = rs.metadata.annotations.get('deployment.kubernetes.io/revision')
        if revision == current_revision:
            continue
        history.append({
            'name': rs.metadata.name,
            'creation_timestamp': trans_time_to_shanghai(rs.metadata.creation_timestamp),
            'image': rs.spec.template.spec.containers[0].image,
            'namespace': rs.metadata.namespace,
            'deployment_name': deployment_name,
            'revision': revision,
            'cluster_name': cluster_name
        })

    sorted_history = sorted(history,
                                key=lambda x: datetime.strptime(x['creation_timestamp'], '%Y-%m-%d %H:%M:%S'),
                                reverse=True)
    return sorted_history


def deployment_rollback(self, namespace, deployment_name, cluster_name, revision):
    api_instance = client.AppsV1Api()
    # 获取指定的 revision 的 Deployment 模板
    replicasets, current_revision = self.deployment_history_list(namespace, deployment_name, cluster_name)
    for rs in replicasets.items:
        revision_history = rs.metadata.annotations.get('deployment.kubernetes.io/revision')
        if revision_history == revision:
            revision_spec_template = rs.spec.template

    # 将该 revision 的 spec.template 复制到当前的 Deployment 中
    deployment = api_instance.read_namespaced_deployment(
        name=deployment_name, namespace=namespace
    )
    deployment.spec.template = revision_spec_template

    # 更新 Deployment
    api_instance.replace_namespaced_deployment(
        name=deployment_name, namespace=namespace, body=deployment
    )
    logging.info(f"Deployment {deployment_name} rolled back to revision {revision}.")
    return f"Rolled back {deployment_name} to revision {revision}"

def deployment_delete(self, namespace, deployment_name):
    v1 = client.AppsV1Api()
    try:
        # 删除 Deployment
        api_response = v1.delete_namespaced_deployment(
            name=deployment_name,
            namespace=namespace
        )
        logging.info(f"Deployment {deployment_name} deleted. Status: {api_response.status}")
        return f"删除{deployment_name}成功"

    except ApiException as e:
        logging.error(f"Exception when deleting deployment: {e}")
        return f"Error deleting deployment: {e}"


def deployment_labels(self, namespace):
    v1 = client.AppsV1Api()
    # 获取该namespace下所有的Deployment的labels的信息和deployment的名称
    try:
        deployments = v1.list_namespaced_deployment(namespace)
        # labels_list = []
        # for deployment in deployments.items:
        #     labels = deployment.metadata.labels
        #     deployment_name = deployment.metadata.name
        #     labels_list.append({'labels': labels, 'deployment_name': deployment_name})
        #     logging.info(f"Deployment {deployment_name} labels: {labels}")
        # return labels_list
        deployment_info = {}
        for deployment in deployments.items:
            name = deployment.metadata.name
            selector = deployment.spec.selector.match_labels
            deployment_info[name] = selector

        return deployment_info

    except ApiException as e:
        logging.error(f"Exception when calling AppsV1Api->list_namespaced_deployment: {e}")
        return f"Error getting deployments: {e}"

def deployment_yaml_create(self, namespace, yaml_data):
    apps_v1 = client.AppsV1Api()
    deployment_yaml = yaml.safe_load(yaml_data)
    
    try:
        apps_v1.create_namespaced_deployment(
            namespace=namespace,
            body=deployment_yaml
        )
        return f'创建deployment成功'
    except ApiException as e:
        logging.error(e)
        return f'创建deployment失败，失败的原因为{e}'
    except Exception as e:
        logging.error(e)
        return f'创建deployment失败，失败的原因为{e}'