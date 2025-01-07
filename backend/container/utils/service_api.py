from kubernetes import client
import logging
from django.utils import timezone
import yaml
from kubernetes.client import ApiException


def service_list(self, namespace, cluster_name):
    v1 = client.CoreV1Api()
    services = v1.list_namespaced_service(namespace)
    services_list = []
    for service in services.items:
        services_list.append({
            "service_name": service.metadata.name,
            "service_type": service.spec.type,
            "service_port": [port.to_dict() for port in service.spec.ports],
            "service_cluster_ip": service.spec.cluster_ip,
            "service_creat_time": timezone.localtime(service.metadata.creation_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
            "service_namespace": service.metadata.namespace,
            "cluster_name": cluster_name,
            "namespace": namespace
        })
    return services_list



def service_detail(self, namespace, service_name, cluster_name):
    v1 = client.CoreV1Api()
    service = v1.read_namespaced_service(name=service_name, namespace=namespace)
    service_detail = {
        "name": service.metadata.name,
        "type": service.spec.type,
        "port": [port.to_dict() for port in service.spec.ports],
        "cluster_ip": service.spec.cluster_ip,
        "creat_time": timezone.localtime(service.metadata.creation_timestamp).strftime("%Y-%m-%d %H:%M:%S"),
        "namespace": service.metadata.namespace,
        "cluster_name": cluster_name,
        "namespace": namespace,
        "label": service.metadata.labels if service.metadata.labels else "",
        "selector": service.spec.selector if service.spec.selector else "",
        "annotations": service.metadata.annotations if service.metadata.annotations else ""
    }
    return service_detail

def service_yaml(self, namespace, service_name):
    v1 = client.CoreV1Api()
    service = v1.read_namespaced_service(name=service_name, namespace=namespace)

    # 将 Service 对象序列化为字典
    service_dict = client.ApiClient().sanitize_for_serialization(service)

    metadata = service_dict.get('metadata', {})
    if 'managedFields' in metadata:
        del metadata['managedFields']
    if 'annotations' in metadata:
        del metadata['annotations']

    # 将字典转换为 YAML 格式
    service_yaml = yaml.dump(service_dict, default_flow_style=False)

    return service_yaml


def service_yaml_create(self, namespace, yaml_data):
    apps_v1 = client.CoreV1Api()
    updated_service_yaml = yaml.safe_load(yaml_data)
    try:
        apps_v1.create_namespaced_service( namespace=namespace, body=updated_service_yaml)
        return f'创建ingress成功'
    except ApiException as e:
        logging.error(e)
        return f'创建ingress失败，失败的原因为{e}'


def service_yaml_update(self, namespace, service_name, yaml_data):
    apps_v1 = client.CoreV1Api()
    updated_service_yaml = yaml.safe_load(yaml_data)
    try:
        apps_v1.patch_namespaced_service(name=service_name, namespace=namespace, body=updated_service_yaml)
        return f'修改deployment成功'
    except ApiException as e:
        logging.error(e)
        return f'修改deployment失败，失败的原因为{e}'


def service_delete(self, namespace, service_name):
    v1 = client.CoreV1Api()
    try:
        # 删除 Service
        response = v1.delete_namespaced_service(
            name=service_name,
            namespace=namespace
        )
        logging.info(f"Service '{service_name}' deleted successfully.")
        return f"Service '{service_name}' deleted successfully."
    except client.exceptions.ApiException as e:
        if e.status == 404:
            logging.info(f"Service '{service_name}' not found.")
            return f"Service '{service_name}' not found."
        else:
            logging.info(f"Failed to delete service: {e}")
            return f"Failed to delete service: {e}"

    service_name = service_form['name']

    # 端口映射处理
    ports = []
    for port_map in service_form['port_maps']:
        port = client.V1ServicePort(
            name=port_map['port_name'],
            port=int(port_map['service_port']),
            target_port=int(port_map['container_port']),
            protocol=port_map['protocol'],
        )
        # 如果是 NodePort 类型，添加 nodePort
        if service_form['service_type'] == 'NodePort' and 'node_port' in port_map and port_map['node_port']:
            port.node_port = int(port_map['node_port'])

        ports.append(port)

    # 构建 Service Spec
    spec = client.V1ServiceSpec(
        type=service_form['service_type'],
        selector=service_form['selectors'],
        ports=ports
    )

    # 构建 Service 对象
    service = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=service_name,
            labels=service_form['labels'],
            annotations=service_form['annotations']
        ),
        spec=spec
    )

    try:
        # 尝试获取现有的 Service 进行更新
        existing_service = v1.read_namespaced_service(service_name, namespace)
        service.metadata.resource_version = existing_service.metadata.resource_version  # 保留 resource_version
        v1.replace_namespaced_service(service_name, namespace, service)
        print(f"Service '{service_name}' updated successfully.")
    except ApiException as e:
        if e.status == 404:
            # 如果 Service 不存在，则创建新的
            v1.create_namespaced_service(namespace, service)
            print(f"Service '{service_name}' created successfully.")
        else:
            print(f"Failed to create or update service: {e}")

    service_name = service_form['name']

    # 端口映射处理
    ports = []
    for port_map in service_form['port_maps']:
        port = client.V1ServicePort(
            name=port_map['port_name'],
            port=int(port_map['service_port']),
            target_port=int(port_map['container_port']),
            protocol=port_map['protocol'],
        )
        # 如果是 NodePort 类型，添加 nodePort
        if service_form['service_type'] == 'NodePort' and 'node_port' in port_map and port_map['node_port']:
            port.node_port = int(port_map['node_port'])

        ports.append(port)

    # 构建 Service Spec
    spec = client.V1ServiceSpec(
        type=service_form['service_type'],
        selector=service_form['service_selectors'],
        ports=ports
    )

    # 构建 Service 对象
    service = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=service_name,
            labels=service_form['labels'],
            annotations=service_form['annotations']
        ),
        spec=spec
    )

    try:
        # 尝试获取现有的 Service 进行更新
        existing_service = v1.read_namespaced_service(service_name, namespace)
        service.metadata.resource_version = existing_service.metadata.resource_version  # 保留 resource_version
        v1.replace_namespaced_service(service_name, namespace, service)
        print(f"Service '{service_name}' updated successfully.")
    except ApiException as e:
        if e.status == 404:
            # 如果 Service 不存在，则创建新的
            v1.create_namespaced_service(namespace, service)
            print(f"Service '{service_name}' created successfully.")
        else:
            print(f"Failed to create or update service: {e}")


def service_create_or_change(self, namespace, service_form):
    v1 = client.CoreV1Api()
    service_name = service_form['name']

    # 端口映射处理
    ports = []
    for port_map in service_form['portMaps']:
        port = client.V1ServicePort(
            name=port_map['name'],
            port=int(port_map['port']),
            target_port=int(port_map['target_port']),
            protocol=port_map['protocol'],
        )
        # 如果是 NodePort 类型，添加 nodePort
        if service_form['service_type'] == 'NodePort' and 'node_port' in port_map and port_map['node_port']:
            port.node_port = int(port_map['node_port'])

        ports.append(port)

    if service_form['label'] == '':
        service_form['label'] = {}
    if service_form['annotations'] == '':
        service_form['annotations'] = {}
    if service_form['selector'] == '':
        service_form['selector'] = {}

    # 构建 Service Spec
    spec = client.V1ServiceSpec(
        type=service_form['service_type'],
        selector=service_form['selector'],
        ports=ports
    )



    # 构建 Service 对象
    service = client.V1Service(
        metadata=client.V1ObjectMeta(
            name=service_name,
            labels=service_form['label'],
            annotations=service_form['annotations']
        ),
        spec=spec
    )

    # print(service)
    if service_form.get('change_type') == 'create':
        try:
            v1.create_namespaced_service(namespace, service)
            return f"Service '{service_name}' created successfully."
        except ApiException as e:
            logging.error(e)
            return f"Failed to create service: {e}"

    elif service_form.get('change_type') == 'update':
        # print(service)
        try:
            existing_service = v1.read_namespaced_service(service_name, namespace)
            service.metadata.resource_version = existing_service.metadata.resource_version  # 保留 resource_version
            v1.replace_namespaced_service(service_name, namespace, service)
            return f"Service '{service_name}' updated successfully."
        except ApiException as e:
            logging.error(e)
            return f"Failed to update service: {e}"
