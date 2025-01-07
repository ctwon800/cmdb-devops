
import { request } from '@/api/service'
export const urlPrefix = '/api/devops/ldap/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: query
  })
}

export function addLdapUser (params) {
  return request({
    url: urlPrefix,
    method: 'post',
    data: params
  })
}

export function updateLdapUserPwd (params) {
  return request({
    url: urlPrefix,
    method: 'put',
    data: params
  })
}

export function deleteLdapUser (params) {
  return request({
    url: urlPrefix,
    method: 'delete',
    data: params
  })
}
