from kubernetes import client
import logging
from django.utils import timezone
import yaml
from kubernetes.client import ApiException
from yaml.representer import Representer





def represent_preserve_scalar(self, data):
    '''
        使用自定义序列化来确保多行字符串按正确格式处理。这需要使用自定义的 representer 处理 YAML 序列化
        例如有的ingress的数据中有 换行符， | 类似下面的数据
        metadata:
          annotations:
            nginx.ingress.kubernetes.io/configuration-snippet: |
              rewrite ^/api/(.*)$ /$1 break;
              rewrite ^/api123/(.*)$ /$1 break;
        主要是来处理这种 | 换行的情况，如果不进行处理，在开始的时候读取会变成下面的格式
         {'annotations': {'nginx.ingress.kubernetes.io/configuration-snippet': 'rewrite '
                                                                                           '^/api/(.*)$ '
                                                                                           '/$1 '
                                                                                           'break;\n',
                                      'nginx.ingress.kubernetes.io/force-ssl-redirect': 'true'}
    '''


    if isinstance(data, str) and '\n' in data:
        return self.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return self.represent_scalar('tag:yaml.org,2002:str', data)

Representer.add_representer(str, represent_preserve_scalar)

def ingress_list(self, namespace, cluster_name):
    v1 = client.NetworkingV1Api()
    ingresses = v1.list_namespaced_ingress(namespace=namespace)
    ingress_list = []
    for ingress in ingresses.items:
        ingress_info = {
            "name": ingress.metadata.name,
            "namespace": ingress.metadata.namespace,
            "creation_timestamp": ingress.metadata.creation_timestamp,
            "cluster_name": cluster_name,
            "namespace": namespace,
            # "annotations": ingress.metadata.annotations,
            "rules": [{
                "host": rule.host,
                # "paths": [{
                #     "path": path.path,
                #     "backend": {
                #         "service_name": path.backend.service.name,
                #         "service_port": path.backend.service.port.number
                #     }
                # } for path in rule.http.paths]
            } for rule in ingress.spec.rules]
        }
        ingress_list.append(ingress_info)
    return ingress_list


def ingress_detail(self, namespace, ingress_name, cluster_name):
    v1 = client.NetworkingV1Api()
    ingress = v1.read_namespaced_ingress(name=ingress_name, namespace=namespace)
    # print(ingress)
    ingress_detail = {
        "name": ingress.metadata.name,
        "namespace": ingress.metadata.namespace,
        "creation_timestamp": ingress.metadata.creation_timestamp,
        "cluster_name": cluster_name,
        "namespace": namespace,
        "labels": ingress.metadata.labels if ingress.metadata.labels else {},
        "annotations": ingress.metadata.annotations,
        "ingress_class_name": ingress.spec.ingress_class_name if ingress.spec.ingress_class_name else "",
        "rules": [{
            "host": rule.host,
            "paths": [{
                "path": path.path,
                "backend": {
                    "service_name": path.backend.service.name,
                    "service_port": path.backend.service.port.number
                },
                "path_type": path.path_type if path.path_type else ""
            } for path in rule.http.paths]
        } for rule in ingress.spec.rules],
        "tls": [{
            "host": tls.hosts[0],
            "secret_name": tls.secret_name
        } for tls in ingress.spec.tls] if ingress.spec.tls else [],
        "load_balancer": ingress.status.load_balancer.ingress[0].ip if ingress.status.load_balancer else ""
    }
    return ingress_detail

def fix_multiline_annotations(annotations):
    for key, value in annotations.items():
        if '\n' in value:
            annotations[key] = value.replace('\n', '\n ')
    return annotations


def ingress_yaml(self, namespace, ingress_name):
    v1 = client.NetworkingV1Api()
    ingress = v1.read_namespaced_ingress(name=ingress_name, namespace=namespace)
    print(ingress.metadata.annotations)
    # 将 ingress 对象序列化为字典
    ingress_dict = client.ApiClient().sanitize_for_serialization(ingress)
    # print(ingress_dict)
    metadata = ingress_dict.get('metadata', {})
    status = ingress_dict.get('status', {})
    if 'managedFields' in metadata:
        del metadata['managedFields']
    # if 'annotations' in metadata:
    #     del metadata['annotations']
    if status:
        del status['loadBalancer']

    # 将字典转换为 YAML 格式
    ingress_yaml = yaml.dump(ingress_dict, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return ingress_yaml


def ingress_yaml_update(self, namespace, ingress_name, yaml_data):
    apps_v1 = client.NetworkingV1Api()
    updated_ingress_yaml = yaml.safe_load(yaml_data)
    try:
        apps_v1.patch_namespaced_ingress(name=ingress_name, namespace=namespace, body=updated_ingress_yaml)
        return f'修改deployment成功'
    except ApiException as e:
        logging.error(e)
        return f'修改deployment失败，失败的原因为{e}'


def ing_yaml_create(self, namespace, yaml_data):
    apps_v1 = client.NetworkingV1Api()
    updated_ingress_yaml = yaml.safe_load(yaml_data)
    try:
        apps_v1.create_namespaced_ingress( namespace=namespace, body=updated_ingress_yaml)
        return f'创建ingress成功'
    except ApiException as e:
        logging.error(e)
        return f'创建ingress失败，失败的原因为{e}'



def ingress_delete(self, namespace, ingress_name):
    v1 = client.NetworkingV1Api()
    try:
        # 删除 ingress
        response = v1.delete_namespaced_ingress(
            name=ingress_name,
            namespace=namespace
        )
        logging.info(f"ingress '{ingress_name}' deleted successfully.")
        return f"ingress '{ingress_name}' deleted successfully."
    except client.exceptions.ApiException as e:
        if e.status == 404:
            logging.info(f"ingress '{ingress_name}' not found.")
            return f"ingress '{ingress_name}' not found."
        else:
            logging.info(f"Failed to delete ingress: {e}")
            return f"Failed to delete ingress: {e}"

def ingress_class(self):
    v1 = client.NetworkingV1Api()
    try:
        # 获取 Ingress Classes 列表
        ingress_classes = v1.list_ingress_class()
        ingress_class_list = []
        for ingress_class in ingress_classes.items:
            ingress_class_name = ingress_class.metadata.name
            ingress_class_list.append(ingress_class_name)
        return ingress_class_list
    except client.exceptions.ApiException as e:
        logging.info(f"Exception when calling NetworkingV1Api->list_ingress_class: {e}")
        return f"Exception when calling NetworkingV1Api->list_ingress_class: {e}"


def ingress_tls_secret(self, namespace):
    v1 = client.CoreV1Api()
    secrets = v1.list_namespaced_secret(namespace=namespace)
    return [secret.metadata.name for secret in secrets.items if secret.type == 'kubernetes.io/tls']

def ingress_change(self, namespace, ingress_data):
    v1 = client.NetworkingV1Api()

    # 构建 Ingress 规范
    ingress_spec = client.V1IngressSpec(
        rules=[
            client.V1IngressRule(
                host=rule['host'],
                http=client.V1HTTPIngressRuleValue(
                    paths=[
                        client.V1HTTPIngressPath(
                            path=path['path'],
                            path_type=path['path_type'],
                            backend=client.V1IngressBackend(
                                service=client.V1IngressServiceBackend(
                                    name=path['backend']['service_name'],
                                    port=client.V1ServiceBackendPort(number=path['backend']['service_port'])
                                )
                            )
                        ) for path in rule['paths']
                    ]
                )
            ) for rule in ingress_data['rules']
        ],
        tls=[
            client.V1IngressTLS(
                hosts=[tls['host']],
                secret_name=tls['secret_name']
            ) for tls in ingress_data.get('tls', [])
        ]
    )

    # 构建 Ingress 对象
    ingress_metadata = client.V1ObjectMeta(
        name=ingress_data['name'],
        annotations=ingress_data.get('annotations', {}),
        labels=ingress_data.get('labels', {})
    )

    ingress_body = client.V1Ingress(
        metadata=ingress_metadata,
        spec=ingress_spec
    )

    print(ingress_body)
    if ingress_data.get('change_type') == 'create':
        # 调用 API 创建 Ingress
        try:
            api_response = v1.create_namespaced_ingress(
                namespace=namespace,
                body=ingress_body
            )
            print("Ingress created. Status='%s'" % api_response.metadata.name)
            return "Ingress created. Status='%s'" % api_response.metadata.name

        except client.ApiException as e:
            return "Exception when creating ingress: %s\n" % e.reason
            print("Exception when creating ingress: %s\n" % e)
    elif ingress_data.get('change_type') == 'update':
        try:
            api_response = v1.patch_namespaced_ingress(
                name=ingress_data['name'],
                namespace=namespace,
                body=ingress_body
            )
            print("Ingress updated. Status='%s'" % api_response.metadata.name)
            return "Ingress updated. Status='%s'" % api_response.metadata.name
        except client.ApiException as e:
            return "Exception when updating ingress: %s\n" % e.reason

    # 调用 API 创建 Ingress
    try:
        api_response = v1.create_namespaced_ingress(
            namespace=namespace,
            body=ingress_body
        )
        print("Ingress created. Status='%s'" % api_response.metadata.name)
        return "Ingress created. Status='%s'" % api_response.metadata.name

    except client.ApiException as e:
        return "Exception when creating ingress: %s\n" % e.reason
        # print("Exception when creating ingress: %s\n" % e)


def ingress_all_namespace_domain(self):
    """
    获取k8s集群中所有ingress的域名
    """
    try:
        # 创建API客户端
        v1 = client.NetworkingV1Api()
        
        # 获取所有命名空间的ingress
        ingress_list = v1.list_ingress_for_all_namespaces()
        
        # 存储所有域名
        domains = []
        
        # 遍历ingress获取域名,只获取配置了TLS的域名
        for ingress in ingress_list.items:
            # 只获取配置了TLS的域名
            if ingress.spec.tls:
                for tls in ingress.spec.tls:
                    if tls.hosts:
                        domains.extend(tls.hosts)
        # 去重
        domains = list(set(domains))
        logging.info(f"从k8s集群获取到的域名列表: {domains}")
        
        return domains
        
    except Exception as e:
        logging.error(f"获取k8s集群域名失败: {str(e)}")
        return []
