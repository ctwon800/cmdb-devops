import { request } from '@/api/service'
export const urlPrefix = '/api/container/deployment/'

export function GetList (query) {
  return request({
    url: urlPrefix + 'dep_list/',
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

export function GetDeploymentDetail (deploymentName, clusterName, namespace) {
  return request({
    url: '/api/container/deployment/dep_detail/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      deployment_name: deploymentName
    }
  })
}

export function SetDeploymentReplicas (obj) {
  return request({
    url: '/api/container/deployment/dep_replicas/',
    method: 'put',
    data: obj
  })
}

export function GetDeploymentYaml (deploymentName, clusterName, namespace) {
  return request({
    url: '/api/container/deployment/dep_yaml/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      deployment_name: deploymentName
    }
  })
}

export function DeploymentYamlUpdate (obj) {
  return request({
    url: '/api/container/deployment/dep_yaml_update/',
    method: 'put',
    data: obj
  })
}

export function SetDeploymentImage (obj) {
  return request({
    url: '/api/container/deployment/dep_image_update/',
    method: 'put',
    data: obj
  })
}

export function GetDeploymentHistory (deploymentName, clusterName, namespace) {
  return request({
    // url: '/api/container/deployment_history/',
    url: '/api/container/deployment/dep_history/',
    method: 'get',
    params: {
      cluster_name: clusterName,
      namespace: namespace,
      deployment_name: deploymentName
    }
  })
}

export function SetDeploymentHistoryVersion (obj) {
  return request({
    url: '/api/container/deployment/dep_history_rollback/',
    method: 'put',
    data: obj
  })
}

export function DeploymentRestart (obj) {
  return request({
    url: '/api/container/deployment/dep_restart/',
    method: 'post',
    data: obj
  })
}

export function DeploymentDelete (obj) {
  return request({
    url: '/api/container/deployment/dep_delete/',
    method: 'delete',
    data: obj
  })
}

export function DeploymentYamlCreate (obj) {
  return request({
    url: '/api/container/deployment/dep_yaml_create/',
    method: 'post',
    data: obj
  })
}
