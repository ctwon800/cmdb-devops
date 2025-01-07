import { request } from '@/api/service'
export const urlPrefix = '/api/container/service/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}

export function GetNamespace (query) {
  return request({
    url: '/api/container/namespace/',
    method: 'get',
    params: { ...query }
  })
}

export function GetServiceDetail (serviceName, clusterName, namespace) {
  return request({
    url: '/api/container/service/svc_detail/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      service_name: serviceName
    }
  })
}

export function GetServiceYaml (yamlServiceName, yamlClusterName, yamlNamespace) {
  return request({
    url: '/api/container/service/svc_yaml/',
    method: 'get',
    params: {
      cluster_name: yamlClusterName,
      namespace: yamlNamespace,
      service_name: yamlServiceName
    }
  })
}

export function ServiceYamlUpdate (obj) {
  return request({
    url: '/api/container/service/svc_yaml_update/',
    method: 'put',
    data: obj
  })
}

export function ServiceDelete (obj) {
  return request({
    url: '/api/container/service/svc_delete/',
    method: 'delete',
    data: obj
  })
}

export function GetDepLabels (selectedClusterName, selectedNamespace) {
  return request({
    url: '/api/container/deployment/dep_labels/',
    method: 'get',
    params: {
      cluster_name: selectedClusterName,
      namespace: selectedNamespace
    }
  })
}

export function ServiceChange (obj) {
  return request({
    url: '/api/container/service/',
    method: 'put',
    data: obj
  })
}

export function ServiceYamlCreate (obj) {
  return request({
    url: '/api/container/service/svc_yaml_create/',
    method: 'post',
    data: obj
  })
}
