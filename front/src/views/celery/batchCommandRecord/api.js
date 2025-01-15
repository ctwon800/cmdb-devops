import { request } from '@/api/service'
export const urlPrefix = '/api/celery/batch_command_record/'

export function GetList (query) {
  return request({
    url: urlPrefix,
    method: 'get',
    params: { ...query }
  })
}
