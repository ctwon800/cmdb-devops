import { request } from '@/api/service'
export const urlPrefix = '/api/celery/task/'

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

export function RunTasks (obj) {
  return request({
    url: urlPrefix + 'run_tasks/',
    method: 'put',
    data: obj
  })
}

export function GetGroupList() {
  return request({
    url: '/api/cmdb/server_group/',
    method: 'get'
  })
}

export function ServerGroupAdd(obj) {
  return request({
    url: '/api/cmdb/server_group/',
    method: 'post',
    data: obj
  })
}

export function ServerGroupUpdate(obj) {
  return request({
    url: '/api/cmdb/server_group/' + obj.id + '/',
    method: 'put',
    data: obj
  })
}

export function ServerGroupDelete(id) {
  return request({
    url: '/api/cmdb/server_group/' + id + '/',
    method: 'delete'
  })
}

export function ServerGroupManage(id) {
  return request({
    url: '/api/cmdb/server_group/' + id + '/manage/',
    method: 'post'
  })
}

export function ServerGroupList(id) {
  return request({
    url: '/api/cmdb/server_group/' + id + '/servers_list/',
    method: 'get'
  })
}

export function ServerAllList(obj) {
  return request({
    url: '/api/cmdb/server_instance/get_instances_exclude_group/',
    method: 'get',
    params: obj
  })
}

export function AddServersToGroup(obj) {
  return request({
    url: '/api/cmdb/server_group/add_servers/',
    method: 'post',
    data: obj
  })
}

export function ServerRemove(obj) {
  return request({
    url: '/api/cmdb/server_group/remove_server/',
    method: 'post',
    data: obj
  })
}

export function GetTaskOutput(id) {
  return request({
    url: urlPrefix + id + '/get_task_output/',
    method: 'get'
  })
}

export function ExecuteAnsibleTask(obj) {
  return request({
    url: urlPrefix + 'execute_ansible_task/',
    method: 'post',
    data: obj
  })
}
