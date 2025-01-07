import { request } from '@/api/service'
export const urlPrefix = '/api/cmdb/server_remote_record/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}
