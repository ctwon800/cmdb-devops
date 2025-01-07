import { request, downloadFile } from '@/api/service'
export const urlPrefix = '/api/cmdb/cloud_cost/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}

export function GetServerPlatform () {
  return request({
    url: '/api/cmdb/server_platform/',
    method: 'get'
  })
}

export function GetAccountName () {
  return request({
    url: '/api/cmdb/account_management/',
    method: 'get'
  })
}

export function GetAccountMonthCost (obj) {
  return request({
    url: '/api/cmdb/cloud_cost/get_all_account_month_count/',
    params: { obj },
    method: 'get'
  })
}

export function GetMonthList () {
  return request({
    url: '/api/cmdb/cloud_cost/get_month_list/',
    method: 'get'
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

export function UpdateCloudCost (obj) {
  return request({
    url: urlPrefix + 'get_month_count/',
    method: 'put',
    data: obj
  })
}
