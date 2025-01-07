import { request } from '@/api/service'
export const urlPrefix = '/api/container/ingress/'

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

export function GetIngressDetail (ingressName, clusterName, namespace) {
  return request({
    url: '/api/container/ingress/ing_detail/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      ingress_name: ingressName
    }
  })
}

export function GetIngressYaml (yamlIngressName, yamlClusterName, yamlNamespace) {
  return request({
    url: '/api/container/ingress/ing_yaml/',
    method: 'get',
    params: {
      cluster_name: yamlClusterName,
      namespace: yamlNamespace,
      ingress_name: yamlIngressName
    }
  })
}

export function IngressYamlUpdate (obj) {
  return request({
    url: '/api/container/ingress/ing_yaml_update/',
    method: 'put',
    data: obj
  })
}

export function IngressDelete (obj) {
  return request({
    url: '/api/container/ingress/ing_delete/',
    method: 'delete',
    data: obj
  })
}

export function GetIngressClass (selectedClusterName) {
  return request({
    url: '/api/container/ingress/ing_class/',
    method: 'get',
    params: {
      cluster_name: selectedClusterName
    }
  })
}

export function GetIngressAnnotation () {
  return request({
    url: '/api/container/ingress/ing_annotation/',
    method: 'get',
    params: {}
  })
}

export function GetTlsSecretList (selectedClusterName, selectedNamespace) {
  return request({
    url: '/api/container/secret/',
    method: 'get',
    params: {
      cluster_name: selectedClusterName,
      namespace: selectedNamespace,
      secret_type: 'kubernetes.io/tls'
    }
  })
}

export function GetServicePorts (selectedClusterName, selectedNamespace) {
  return request({
    url: '/api/container/service/',
    method: 'get',
    params: {
      cluster_name: selectedClusterName,
      namespace: selectedNamespace,
      limit: 100
    }
  })
}

export function IngressChange (obj) {
  return request({
    url: '/api/container/ingress/',
    method: 'put',
    data: obj
  })
}

export function IngressYamlCreate (obj) {
  return request({
    url: '/api/container/ingress/ing_yaml_create/',
    method: 'post',
    data: obj
  })
}
