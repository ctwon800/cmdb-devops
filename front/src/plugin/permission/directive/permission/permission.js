
import permissionUtil from './util.permission'
export default {
  inserted (el, binding, vnode) {
    const { value } = binding
    const hasPermission = permissionUtil.hasPermissions(value)
    if (process.env.VUE_APP_PM_ENABLED) {
      if (!hasPermission) {
        el.parentNode && el.parentNode.removeChild(el)
      }
    }
  }
}
