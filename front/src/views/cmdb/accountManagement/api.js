import { request } from '@/api/service'
export const urlPrefix = '/api/cmdb/account_management/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}

export function AddObj (obj) {
  return request({
    url: urlPrefix,
    method: 'post',
    data: obj
  })
}

export function UpdateObj (obj) {
  return request({
    url: urlPrefix + obj.id + '/',
    method: 'put',
    data: obj
  })
}

export function DelObj (id) {
  return request({
    url: urlPrefix + id + '/',
    method: 'delete',
    data: { soft_delete: true }
  })
}

export function BatchDel (keys) {
  return request({
    url: urlPrefix + 'multiple_delete/',
    method: 'delete',
    data: { keys }
  })
}

export function UpdateYunRes (obj) {
  return request({
    url: urlPrefix + 'update_cloud_res/',
    method: 'put',
    data: obj
  })
}

// 获取平台列表
export function getPlatformList () {
  return request({
    url: '/api/cmdb/server_platform/',
    method: 'get'
  })
}

// 添加平台
export function addPlatform (data) {
  return request({
    url: '/api/cmdb/server_platform/',
    method: 'post',
    data
  })
}

// 更新平台
export function updatePlatform (data) {
  return request({
    url: `/api/cmdb/server_platform/${data.id}/`,
    method: 'put',
    data
  })
}

// 删除平台
export function deletePlatform (id) {
  return request({
    url: `/api/cmdb/server_platform/${id}/`,
    method: 'delete'
  })
}
