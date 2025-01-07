import { request, downloadFile } from '@/api/service'
export const urlPrefix = '/api/monitors/ssl_monitors/'

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
/*
 * 导出
 * @param params
 */
export function exportData (params) {
  return downloadFile({
    url: urlPrefix + 'export_data/',
    params: params,
    method: 'get'
  })
}

export function updateMonitors () {
  return request({
    url: urlPrefix + 'ssl_monitors_update/',
    method: 'get'
  })
}

export function GetAbnormalList (query) {
  return request({
    url: urlPrefix + 'ssl_monitors_error/',
    method: 'get',
    params: { ...query }
  })
}

export function updateSSLStatus(obj) {
  return request({
    url: urlPrefix + 'updateStatus/',
    method: 'put',
    data: obj
  })
}
