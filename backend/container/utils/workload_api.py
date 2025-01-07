from kubernetes import client
from kubernetes.client import ApiException
from typing import Dict, Optional
import logging



def create_workload(self, namespace: str, manifests: Dict) -> Dict:
    """
    创建 Kubernetes 工作负载及相关资源

    Args:
        namespace: 目标命名空间
        manifests: 包含 workload、service、ingress 的资源配置

    Returns:
        Dict: 创建的资源结果
    """
    results = {}
    
    # 工作负载类型与对应的创建方法映射
    workload_mapping = {
        'Deployment': self.apps_api.create_namespaced_deployment,
        'StatefulSet': self.apps_api.create_namespaced_stateful_set,
        'DaemonSet': self.apps_api.create_namespaced_daemon_set,
        'Job': self.batch_api.create_namespaced_job,
        'CronJob': self.batch_api.create_namespaced_cron_job
    }

    # 创建工作负载
    if manifests.get('workload'):
        try:
            workload = manifests['workload']
            kind = workload.get('kind')
            if kind not in workload_mapping:
                raise ValueError(f"不支持的工作负载类型: {kind}")
            
            logging.info(f"正在创建 {kind}, namespace={namespace}")
            create_func = workload_mapping[kind]
            _ = create_func(
                namespace=namespace,
                body=workload
            )
            results['workload'] = f"{kind} 创建成功"
            logging.info(f"{kind} 创建成功")
        except ApiException as e:
            error_msg = f"创建工作负载失败: {str(e)}"
            logging.error(error_msg)
            raise ApiException(error_msg)
        except Exception as e:
            error_msg = f"创建工作负载时发生未知错误: {str(e)}"
            logging.error(error_msg)
            raise

    # 创建 Service
    if manifests.get('service'):
        try:
            logging.info(f"正在创建 Service, namespace={namespace}")
            _ = self.core_api.create_namespaced_service(
                namespace=namespace,
                body=manifests['service']
            )
            results['service'] = "Service 创建成功"
            logging.info("Service 创建成功")
        except ApiException as e:
            error_msg = f"创建 Service 失败: {str(e)}"
            logging.error(error_msg)
            raise ApiException(error_msg)
        except Exception as e:
            error_msg = f"创建 Service 时发生未知错误: {str(e)}"
            logging.error(error_msg)
            raise

    # 创建 Ingress
    if manifests.get('ingress'):
        try:
            logging.info(f"正在创建 Ingress, namespace={namespace}")
            _ = self.networking_api.create_namespaced_ingress(
                namespace=namespace,
                body=manifests['ingress']
            )
            results['ingress'] = "Ingress 创建成功"
            logging.info("Ingress 创建成功")
        except ApiException as e:
            error_msg = f"创建 Ingress 失败: {str(e)}"
            logging.error(error_msg)
            raise ApiException(error_msg)
        except Exception as e:
            error_msg = f"创建 Ingress 时发生未知错误: {str(e)}"
            logging.error(error_msg)
            raise

    return results
