import { request } from '@/api/service'
export const urlPrefix = '/api/container/node/'

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

export function GetNodeDetail (nodeName, clusterName) {
  return request({
    url: '/api/container/node/node_detail/',
    method: 'get',
    params: {
      node_name: nodeName,
      cluster_name: clusterName
    }
  })
}

export function NodeEvictionPod (obj) {
  return request({
    url: '/api/container/node/node_eviction/',
    method: 'post',
    data: obj
  })
}

export function NodeSetSchedule (obj) {
  return request({
    url: urlPrefix,
    method: 'put',
    data: obj
  })
}

export function NodeDrain (drainNodeName, drainClusterName) {
  return request({
    url: '/api/container/node/node_drain/',
    method: 'get',
    params: {
      node_name: drainNodeName,
      cluster_name: drainClusterName
    }
  })
}

export function NodeDelete (deleteNodeName, deleteClusterName) {
  return request({
    url: urlPrefix,
    method: 'delete',
    params: {
      node_name: deleteNodeName,
      cluster_name: deleteClusterName
    }
  })
}

export function GetNodeLabel (nodeName, clusterName) {
  return request({
    url: '/api/container/node/node_label/',
    method: 'get',
    params: {
      node_name: nodeName,
      cluster_name: clusterName
    }
  })
}

export function UpdateNodeLabel (obj) {
  return request({
    url: '/api/container/node/update_node_label/',
    method: 'put',
    data: obj
  })
}

export function DeleteNodeLabel (obj) {
  return request({
    url: '/api/container/node/node_label_delete/',
    method: 'delete',
    data: obj
  })
}

export function GetNodeTaint (nodeName, clusterName) {
  return request({
    url: '/api/container/node/node_taint/',
    method: 'get',
    params: {
      node_name: nodeName,
      cluster_name: clusterName
    }
  })
}

export function UpdateNodeTaint (obj) {
  return request({
    url: '/api/container/node/node_taint_update/',
    method: 'put',
    data: obj
  })
}

export function DeleteNodeTaint (obj) {
  return request({
    url: '/api/container/node/node_taint_delete/',
    method: 'delete',
    data: obj
  })
}
