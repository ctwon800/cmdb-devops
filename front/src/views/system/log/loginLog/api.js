
import { request } from '@/api/service'

export const urlPrefix = '/api/system/login_log/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: query
  })
}
