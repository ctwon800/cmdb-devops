import yaml
from kubernetes import client, config
import logging
from container.models import K8sCluster
import base64
from container.utils import node_api, deployment_api, namespace_api, pod_api, service_api, ingress_api, secret_api, configmap_api, pvc_api, workload_api

class K8sApiMain():
    def __init__(self, k8s_cluster_name: str):
        """初始化 K8s API 客户端"""
        try:
            self.cluster_name = k8s_cluster_name
            cluster = K8sCluster.objects.get(k8s_cluster_name=k8s_cluster_name)
            decoded_config = base64.b64decode(cluster.k8s_cluster_config).decode('utf-8')
            config_dict = yaml.safe_load(decoded_config)
            
            # 初始化客户端
            config.load_kube_config_from_dict(config_dict=config_dict)
            self.core_api = client.CoreV1Api()
            self.apps_api = client.AppsV1Api()
            self.networking_api = client.NetworkingV1Api()
            self.batch_api = client.BatchV1Api()
            
            # 加载API模块
            self._load_api_modules()
            
        except Exception as e:
            logging.error(f"初始化 K8s API 客户端失败: {str(e)}")
            raise

    def _load_api_modules(self):
        """加载所有 API 模块"""
        api_modules = [
            node_api, deployment_api, namespace_api, pod_api,
            service_api, ingress_api, secret_api, configmap_api,
            pvc_api, workload_api
        ]
        
        for module in api_modules:
            try:
                self.load_methods_from_module(module)
            except Exception as e:
                logging.error(f"加载模块 {module.__name__} 失败: {str(e)}")

    def load_methods_from_module(self, module):
        for attr_name in dir(module):
            # if callable(getattr(module, attr_name)):
            #     # 动态将方法绑定到实例
            #     setattr(self, attr_name, getattr(module, attr_name))
            method = getattr(module, attr_name)
            if callable(method):
                try:
                    bound_method = method.__get__(self, self.__class__)
                    setattr(self, attr_name, bound_method)
                except Exception as e:
                    pass
                    # print(f"Error binding method {attr_name} from {module.__name__}: {str(e)}")
            else:
                pass
                # print(f"Skipped non-callable attribute: {attr_name}")
    def check_data_exists(self, data):
        if data is not None:
            data_list = [data_item.to_dict() for data_item in data]
        else:
            data_list = []
        return data_list

    def check_list_in_list_exists(self, data):
        if data is not None:
            health_data = []
            health_data.append(data)
        else:
            health_data = None
        return health_data



class K8SClusterSelect(K8sApiMain):
    def __init__(self, k8s_cluster_name, *args, **kwargs):
        if k8s_cluster_name is None or k8s_cluster_name == "":
            logging.info("k8s_cluster_name is not exist")
            k8s_cluster_name = K8sCluster.objects.filter(k8s_cluster_is_default=True).values_list("k8s_cluster_name", flat=True).first()
            logging.info(f"k8s_cluster_name default is {k8s_cluster_name}")
        super().__init__(k8s_cluster_name, *args, **kwargs)