import json
import logging
from typing import Dict

from container.utils.k8s_api import K8SClusterSelect
from django.http import JsonResponse
from django.core.paginator import Paginator
from container.models import K8sCluster
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action



class K8sWorkloadViewSet(ViewSet):
    """K8s 工作负载管理视图集"""
    
    @action(methods=['post'], detail=False)
    def create_workload(self, request, *args, **kwargs):
        """创建 K8s 工作负载"""
        try:
            data = json.loads(request.body)
            
            # 处理集群和命名空间
            cluster_name = data.get('cluster_name')
            namespace = data.get('namespace')
            
            if not cluster_name:
                cluster_name = K8sCluster.objects.filter(
                    k8s_cluster_is_default=True
                ).values_list("k8s_cluster_name", flat=True).first()
            
            if not namespace:
                namespace = K8sCluster.objects.filter(
                    k8s_cluster_name=cluster_name
                ).values_list("k8s_default_namespace", flat=True).first()

            # 验证必要参数
            self._validate_workload_params(data)
            
            # 构建资源配置
            basic_info = data.get('basicInfoData', {})
            workload_manifest = {
                'apiVersion': self._get_api_version(basic_info['workloadType']),
                'kind': basic_info['workloadType'],
                'metadata': {
                    'name': basic_info['workloadName'],
                    'namespace': namespace,
                    'labels': basic_info.get('labels', {}),
                    'annotations': basic_info.get('annotations', {})
                },
                'spec': {
                    'replicas': basic_info.get('replicas', 1),
                    'selector': {
                        'matchLabels': basic_info.get('labels', {})
                    },
                    'template': {
                        'metadata': {
                            'labels': basic_info.get('labels', {})
                        },
                        'spec': self._build_pod_spec(
                            data.get('containerInfoData', []),
                            data.get('advancedConfigData', {})
                        )
                    }
                }
            }

            # 添加更新策略
            advanced_config = data.get('advancedConfigData', {})
            if 'updateStrategy' in advanced_config:
                workload_manifest['spec']['strategy'] = advanced_config['updateStrategy']

            # 处理Service和Ingress
            service_route_data = data.get('serviceRouteData', {})
            manifests = {'workload': workload_manifest}
            
            if service_route_data.get('service', {}).get('enabled'):
                manifests['service'] = self._build_service_manifest(
                    service_route_data['service'], 
                    namespace
                )
            
            if service_route_data.get('route', {}).get('enabled'):
                manifests['ingress'] = self._build_ingress_manifest(
                    service_route_data['route'], 
                    namespace
                )

            # 创建资源
            cluster_api = K8SClusterSelect(cluster_name)
            result = cluster_api.create_workload(namespace, manifests)
            
            print(result)

            message = {
                "code": 2000,
                "data": result,
                "msg": "success"
            }
            return JsonResponse(message, safe=False)

            
        except ValueError as e:
            logging.error(f"请求参数无效: {str(e)}")
            return JsonResponse({
                'code': 400,
                'message': f'参数错误: {str(e)}',
                'data': None
            })
        except Exception as e:
            logging.error(f"创建工作负载失败: {str(e)}")
            return JsonResponse({
                'code': 500,
                'message': f'创建失败: {str(e)}',
                'data': None
            })

    def _validate_workload_params(self, data: Dict):
        """验证工作负载参数"""
        basic_info = data.get('basicInfoData', {})
        if not basic_info.get('workloadName'):
            raise ValueError("工作负载名称不能为空")
        if not basic_info.get('workloadType'):
            raise ValueError("工作负载类型不能为空")

    def _get_api_version(self, workload_type: str) -> str:
        """获取资源的 API 版本"""
        api_versions = {
            'Deployment': 'apps/v1',
            'StatefulSet': 'apps/v1',
            'DaemonSet': 'apps/v1',
            'Job': 'batch/v1',
            'CronJob': 'batch/v1'
        }
        return api_versions.get(workload_type, 'apps/v1')

    def _build_pod_spec(self, containers_data, advanced_config):
        """构建Pod规格"""
        if not containers_data:
            return None
            
        containers = []
        volumes = []
        
        for container in containers_data:
            if not isinstance(container, dict):
                continue
                
            container_def = {
                'name': container.get('name', ''),
                'image': container.get('image', ''),
                'imagePullPolicy': container.get('imagePullPolicy', 'IfNotPresent'),
                'workingDir': container.get('workingDir'),
                'securityContext': container.get('securityContext', {}),
            }
            
            # 添加命令和参数
            if container.get('command'):
                container_def['command'] = container['command'].split()
            if container.get('args'):
                container_def['args'] = container['args'].split()
                
            # 添加环境变量
            if container.get('env'):
                container_def['env'] = [
                    {'name': env['name'], 'value': env['value']} 
                    for env in container['env']
                ]
                
            # 添加端口
            if container.get('ports'):
                container_def['ports'] = [
                    {
                        'name': port.get('name', f'port-{i}'),
                        'containerPort': int(port['number']),
                        'protocol': port['protocol']
                    }
                    for i, port in enumerate(container['ports'])
                ]
                
            # 处理资源限制
            if container.get('resources'):
                resources = container['resources']
                container_def['resources'] = {
                    'limits': {},
                    'requests': {}
                }
                
                # 处理资源限制
                if resources.get('limits'):
                    limits = resources['limits']
                    if limits.get('cpu'):
                        container_def['resources']['limits']['cpu'] = self._format_cpu_value(limits['cpu'])
                    if limits.get('memory'):
                        container_def['resources']['limits']['memory'] = self._format_memory_value(limits['memory'])
                
                # 处理资源请求
                if resources.get('requests'):
                    requests = resources['requests']
                    if requests.get('cpu'):
                        container_def['resources']['requests']['cpu'] = self._format_cpu_value(requests['cpu'])
                    if requests.get('memory'):
                        container_def['resources']['requests']['memory'] = self._format_memory_value(requests['memory'])
                
                # 如果limits或requests为空，则删除它们
                if not container_def['resources']['limits']:
                    del container_def['resources']['limits']
                if not container_def['resources']['requests']:
                    del container_def['resources']['requests']
                if not container_def['resources']:
                    del container_def['resources']
                
            # 添加探针
            liveness_probe = container.get('livenessProbe')
            if isinstance(liveness_probe, dict) and liveness_probe.get('enabled'):
                probe_result = self._build_probe(liveness_probe)
                if probe_result:
                    container_def['livenessProbe'] = probe_result
                    
            readiness_probe = container.get('readinessProbe')
            if isinstance(readiness_probe, dict) and readiness_probe.get('enabled'):
                probe_result = self._build_probe(readiness_probe)
                if probe_result:
                    container_def['readinessProbe'] = probe_result
                    
            startup_probe = container.get('startupProbe')
            if isinstance(startup_probe, dict) and startup_probe.get('enabled'):
                probe_result = self._build_probe(startup_probe)
                if probe_result:
                    container_def['startupProbe'] = probe_result

            # 添加卷挂载
            if container.get('volumeMounts'):
                container_mounts = []
                volume_configs = []
                
                for volume_config in container['volumeMounts']:
                    volume, volume_mount = self._build_volume_and_mount(volume_config)
                    if volume and volume_mount:
                        container_mounts.append(volume_mount)
                        # 检查是否已存在相同名称的卷
                        if not any(v['name'] == volume['name'] for v in volumes):
                            volumes.append(volume)
                
                if container_mounts:
                    container_def['volumeMounts'] = container_mounts

            containers.append(container_def)
        
        pod_spec = {
            'containers': containers,
            'volumes': volumes,
            'imagePullSecrets': [{'name': containers_data[0].get('imagePullSecret')}]
        }
        
        # 添加亲和性和容忍
        if advanced_config:
            if advanced_config.get('nodeAffinity'):
                pod_spec['affinity'] = pod_spec.get('affinity', {})
                pod_spec['affinity']['nodeAffinity'] = self._build_node_affinity(
                    advanced_config['nodeAffinity']
                )
                
            if advanced_config.get('podAffinity'):
                pod_spec['affinity'] = pod_spec.get('affinity', {})
                pod_spec['affinity']['podAffinity'] = self._build_pod_affinity(
                    advanced_config['podAffinity']
                )
                
            if advanced_config.get('tolerations'):
                pod_spec['tolerations'] = advanced_config['tolerations']
            
        return pod_spec

    def _build_probe(self, probe_config):
        """构建探针配置"""
        if not probe_config or not isinstance(probe_config, dict):
            return None
            
        if not probe_config.get('enabled'):
            return None
            
        probe = {}
        common_config = {}
        
        probe_type = probe_config.get('type')
        
        if probe_type == 'http':
            http_config = probe_config.get('http', {})
            if not http_config:  # 检查http配置是否存在
                return None
                
            probe['httpGet'] = {
                'path': http_config.get('path', '/'),
                'port': int(http_config.get('port', 80)),
                'scheme': http_config.get('protocol', 'HTTP')
            }
            if http_config.get('headerName') and http_config.get('headerValue'):
                probe['httpGet']['httpHeaders'] = [{
                    'name': http_config['headerName'],
                    'value': http_config['headerValue']
                }]
            common_config = http_config
            
        elif probe_type == 'tcp':
            tcp_config = probe_config.get('tcp', {})
            if not tcp_config:  # 检查tcp配置是否存在
                return None
                
            probe['tcpSocket'] = {
                'port': int(tcp_config.get('port', 80))
            }
            common_config = tcp_config
            
        elif probe_type == 'exec':
            exec_config = probe_config.get('exec', {})
            if not exec_config:  # 检查exec配置是否存在
                return None
                
            command = exec_config.get('command')
            if not command:  # 检查command是否存在
                return None
                
            if isinstance(command, str):
                command = command.split()
            elif not isinstance(command, list):
                return None
                
            probe['exec'] = {
                'command': command
            }
            common_config = exec_config
        else:
            return None

        # 添加通用的探针参数，使用安全的默认值
        probe.update({
            'initialDelaySeconds': int(common_config.get('initialDelaySeconds', 0)),
            'periodSeconds': int(common_config.get('periodSeconds', 10)),
            'timeoutSeconds': int(common_config.get('timeoutSeconds', 1)),
            'successThreshold': int(common_config.get('successThreshold', 1)),
            'failureThreshold': int(common_config.get('failureThreshold', 3))
        })
        
        return probe

    def _build_service_manifest(self, service_data, namespace):
        """构建Service配置"""
        return {
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': service_data['name'],
                'namespace': namespace,
                'labels': service_data.get('label', {})
            },
            'spec': {
                'type': service_data['service_type'],
                'selector': service_data['selector'],
                'ports': [{
                    'name': port['port_name'],
                    'port': int(port['service_port']),
                    'targetPort': int(port['container_port']),
                    'protocol': port['protocol'],
                    **(({'nodePort': int(port['node_port'])} 
                        if port.get('node_port') and service_data['service_type'] == 'NodePort' 
                        else {}))
                } for port in service_data['portMaps']]
            }
        }

    def _build_ingress_manifest(self, route_data, namespace):
        """构建Ingress配置"""
        ingress_manifest = {
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': route_data['name'],
                'namespace': namespace,
                'labels': route_data.get('labels', {})
            },
            'spec': {
                'rules': [{
                    'host': rule['host'],
                    'http': {
                        'paths': [{
                            'path': path['path'],
                            'pathType': 'Prefix',
                            'backend': {
                                'service': {
                                    'name': path['service_name'],
                                    'port': {
                                        'number': int(path['service_port'])
                                    }
                                }
                            }
                        } for path in rule['paths']]
                    }
                } for rule in route_data['rules']]
            }
        }

        # 添加 TLS 配置
        if route_data.get('tls'):
            ingress_manifest['spec']['tls'] = route_data['tls']

        return ingress_manifest

    def _build_node_affinity(self, node_affinity_rules):
        """
        构建节点亲和性配置
        
        Args:
            node_affinity_rules: 节点亲和性规则列表
            示例: [
                {
                    'type': 'required',  # 或 'preferred'
                    'operator': 'In',    # In, NotIn, Exists, DoesNotExist, Gt, Lt
                    'key': 'node-label-key',
                    'values': 'node-label-value'  # 可以是单个值或逗号分隔的多个值
                }
            ]
        """
        node_affinity = {}
        required_terms = []
        preferred_terms = []

        for rule in node_affinity_rules:
            match_expression = {
                'key': rule['key'],
                'operator': rule['operator']
            }
            
            # 处理不同的操作符
            if rule['operator'] not in ['Exists', 'DoesNotExist']:
                # 将值字符串转换为列表
                values = rule['values'].split(',') if isinstance(rule['values'], str) else [rule['values']]
                match_expression['values'] = values

            term = {
                'matchExpressions': [match_expression]
            }

            if rule['type'] == 'required':
                required_terms.append(term)
            else:  # preferred
                preferred_terms.append({
                    'weight': 1,  # 可以根据需要调整权重
                    'preference': term
                })

        # 添加必需的亲和性规则
        if required_terms:
            node_affinity['requiredDuringSchedulingIgnoredDuringExecution'] = {
                'nodeSelectorTerms': required_terms
            }

        # 添加首选的亲和性规则
        if preferred_terms:
            node_affinity['preferredDuringSchedulingIgnoredDuringExecution'] = preferred_terms

        return node_affinity

    def _build_pod_affinity(self, pod_affinity_rules):
        """
        构建Pod亲和性配置
        
        Args:
            pod_affinity_rules: Pod亲和性规则列表
            示例: [
                {
                    'type': 'affinity',      # 或 'anti-affinity'
                    'level': 'required',      # 或 'preferred'
                    'labelKey': 'app',
                    'labelValue': 'nginx',
                    'namespace': 'default',
                    'topologyKey': 'kubernetes.io/hostname'  # 可选
                }
            ]
        """
        pod_affinity_config = {}
        required_affinity = []
        preferred_affinity = []
        required_anti_affinity = []
        preferred_anti_affinity = []

        for rule in pod_affinity_rules:
            # 构建标签选择器
            label_selector = {
                'matchExpressions': [{
                    'key': rule['labelKey'],
                    'operator': 'In',
                    'values': [rule['labelValue']]
                }]
            }

            # 构建亲和性条件
            term = {
                'labelSelector': label_selector,
                'namespaces': [rule['namespace']] if rule.get('namespace') else None,
                'topologyKey': rule.get('topologyKey', 'kubernetes.io/hostname')
            }
            
            # 移除None值的字段
            term = {k: v for k, v in term.items() if v is not None}

            # 根据类型和级别分配规则
            if rule['type'] == 'affinity':
                if rule['level'] == 'required':
                    required_affinity.append(term)
                else:  # preferred
                    preferred_affinity.append({
                        'weight': 1,
                        'podAffinityTerm': term
                    })
            else:  # anti-affinity
                if rule['level'] == 'required':
                    required_anti_affinity.append(term)
                else:  # preferred
                    preferred_anti_affinity.append({
                        'weight': 1,
                        'podAffinityTerm': term
                    })

        # 构建最终的亲和性配置
        if required_affinity:
            pod_affinity_config['requiredDuringSchedulingIgnoredDuringExecution'] = required_affinity
        if preferred_affinity:
            pod_affinity_config['preferredDuringSchedulingIgnoredDuringExecution'] = preferred_affinity

        # 构建反亲和性配置
        pod_anti_affinity = {}
        if required_anti_affinity:
            pod_anti_affinity['requiredDuringSchedulingIgnoredDuringExecution'] = required_anti_affinity
        if preferred_anti_affinity:
            pod_anti_affinity['preferredDuringSchedulingIgnoredDuringExecution'] = preferred_anti_affinity

        # 返回完整的亲和性配置
        result = {}
        if pod_affinity_config:
            result['podAffinity'] = pod_affinity_config
        if pod_anti_affinity:
            result['podAntiAffinity'] = pod_anti_affinity

        return result

    def _format_cpu_value(self, cpu_value: str) -> str:
        """
        格式化CPU值
        
        Args:
            cpu_value: CPU值（可以是数字或带单位的字符串）
        
        Returns:
            格式化后的CPU值
        """
        if not cpu_value:
            return None
            
        try:
            # 如果是纯数字，直接返回
            float(cpu_value)
            return cpu_value
        except ValueError:
            # 如果包含单位，确保格式正确
            if cpu_value.endswith('m'):
                try:
                    int(cpu_value[:-1])
                    return cpu_value
                except ValueError:
                    pass
        
        # 默认转换为核心数
        try:
            cores = float(cpu_value)
            if cores < 1:
                return f"{int(cores * 1000)}m"
            return str(cores)
        except ValueError:
            return None

    def _format_memory_value(self, memory_value: str) -> str:
        """
        格式化内存值
        
        Args:
            memory_value: 内存值（可以是数字或带单位的字符串）
        
        Returns:
            格式化后的内存值
        """
        if not memory_value:
            return None
            
        try:
            # 直接返回数值加Mi单位
            value = str(int(float(memory_value)))
            return f"{value}Mi"
        except ValueError:
            return None

    def _build_volume_and_mount(self, volume_config):
        """构建存储卷和挂载点配置"""
        volume = {}
        volume_mount = {}
        common_config = {}  # 初始化默认值
        
        volume_type = volume_config.get('type')
        
        if volume_type == 'emptyDir':
            volume['emptyDir'] = {}
            common_config = volume_config
            
        elif volume_type == 'hostPath':
            host_path_config = volume_config.get('hostPath', {})
            volume['hostPath'] = {
                'path': host_path_config.get('path', ''),
                'type': host_path_config.get('type', '')
            }
            common_config = volume_config
            
        elif volume_type == 'configMap':
            config_map = volume_config.get('configMap', {})
            volume['configMap'] = {
                'name': config_map.get('name', ''),
                'defaultMode': int(config_map.get('defaultMode', 420))
            }
            if config_map.get('items'):
                volume['configMap']['items'] = config_map['items']
            common_config = volume_config
            
        elif volume_type == 'secret':
            secret = volume_config.get('secret', {})
            volume['secret'] = {
                'secretName': secret.get('secretName', ''),
                'defaultMode': int(secret.get('defaultMode', 420))
            }
            if secret.get('items'):
                volume['secret']['items'] = secret['items']
            common_config = volume_config
            
        elif volume_type == 'persistentVolumeClaim':
            pvc = volume_config.get('persistentVolumeClaim', {})
            volume['persistentVolumeClaim'] = {
                'claimName': pvc.get('claimName', '')
            }
            common_config = volume_config
        else:
            return None, None  # 如果类型无效，返回None
        
        # 构建挂载点配置
        volume_mount = {
            'name': volume_config.get('name', ''),
            'mountPath': volume_config.get('mountPath', ''),
            'subPath': volume_config.get('subPath', ''),
            'readOnly': volume_config.get('readOnly', False)
        }
        
        # 设置卷名称
        volume['name'] = volume_config.get('name', '')
        
        return volume, volume_mount
