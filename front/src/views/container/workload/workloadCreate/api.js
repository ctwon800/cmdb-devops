import { request } from '@/api/service'
export const urlPrefix = '/api/system/system_config/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: query
  })
}

export function GetImagePullSecretList (namespace, clusterName) {
  return request({
    url: '/api/container/secret/image_secret/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace
    }
  })
}

export function GetPvcList (namespace, clusterName) {
  return request({
    url: '/api/container/pvc/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace
    }
  })
}

export function GetConfigMapList (namespace, clusterName) {
  return request({
    url: '/api/container/configmap/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace
    }
  })
}

export function GetSecretList (namespace, clusterName) {
  return request({
    url: '/api/container/secret/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace
    }
  })
}

export function GetNamespaceList (clusterName) {
  return request({
    url: '/api/container/namespace/',
    method: 'get',
    params: { cluster_name: clusterName }
  })
}

export function createWorkload(data) {
  return request({
    url: '/api/container/workload/create_workload/',
    method: 'post',
    data: data
  })
}

export function GetTlsSecretList (clusterName, namespace) {
  return request({
    url: '/api/container/secret/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      secret_type: 'kubernetes.io/tls'
    }
  })
}
