import { request, downloadFile } from '@/api/service'
export const urlPrefix = '/api/cmdb/server_remote_account/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}

export function GetServerRemoteAccounDetail (obj) {
  return request({
    url: '/api/cmdb/server_remote_account/ser_remote_account_detail/',
    method: 'get',
    params: { obj }
  })
}

export function GetServerRemoteAccounExclude (obj) {
  return request({
    url: '/api/cmdb/server_remote_account/ser_remote_account_exclude/',
    method: 'get',
    params: { obj }
  })
}

export function UpdateServerRemoteAccount (obj, uri) {
  return request({
    url: `/api/cmdb/update_ser_remote_account/${uri}/`,
    method: 'post',
    data: obj
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
