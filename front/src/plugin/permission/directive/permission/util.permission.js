
import store from '@/store'
import router from '@/router'
export default {
  hasPermissions (value) {
    if (process.env.VUE_APP_PM_ENABLED) {
      const path = router.history.current.path// 当前路由
      let needList = []
      if (typeof value === 'string') {
        needList.push(path + ':' + value)
      } else if (value && value instanceof Array && value.length > 0) {
        needList = needList.concat(path + ':' + value)
      }
      if (needList.length === 0) {
        throw new Error('need permissions! Like v-permission="usersphere:user:view" ')
      }
      const userPermissionList = store.getters['d2admin/permission/permissionList']
      return userPermissionList.some(permission => {
        return needList.includes(permission)
      })
    }
    return true
  }
}
