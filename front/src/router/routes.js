import layoutHeaderAside from '@/layout/header-aside'
import { checkPlugins } from '@/views/plugins/index.js'
// 由于懒加载页面太多的话会造成webpack热更新太慢，所以开发环境不使用懒加载，只有生产环境使用懒加载
const _import = require('@/libs/util.import.' + process.env.NODE_ENV)
const pluginImport = require('@/libs/util.import.plugin')
/**
 * 在主框架内显示
 */
const frameIn = [{
  path: '/',
  redirect: { name: 'index' },
  component: layoutHeaderAside,
  children: [
    // 控制台
    {
      path: 'index',
      name: 'index',
      meta: {
        auth: true
      },
      component: _import('dashboard/workbench/index')
    },
    {
      path: 'page1',
      name: 'page1',
      meta: {
        auth: true
      },
      component: _import('demo/page1/index')
    },
    {
      path: 'userInfo',
      name: 'userInfo',
      meta: {
        title: '个人信息',
        auth: true
      },
      component: () => import('@/layout/header-aside/components/header-user/userinfo')
    },
    // dashboard 工作台
    {
      path: 'workbench',
      name: 'workbench',
      meta: {
        title: '工作台',
        auth: true
      },
      component: _import('dashboard/workbench')
    },
    // 刷新页面 必须保留
    {
      path: 'refresh',
      name: 'refresh',
      hidden: true,
      component: _import('system/function/refresh')
    },
    // 页面重定向 必须保留
    {
      path: 'redirect/:route*',
      name: 'redirect',
      hidden: true,
      component: _import('system/function/redirect')
    }
  ]
}]

/**
 * 在主框架之外显示
 */
const frameOut = [
  // 登录
  {
    path: '/login',
    name: 'login',
    component: _import('system/login')
  },
  {
    path: '/sshConnect',
    name: 'sshConnect',
    component: _import('cmdb/ssh')
  },
  {
    path: '/remoteRecordVideo',
    name: 'remoteRecordVideo',
    component: _import('cmdb/remoteRecordVideo')
  }
]

/**
 * 第三方登录
 */
const oauth2PluginsType = checkPlugins('dvadmin-oauth2-web')
if (oauth2PluginsType) {
  frameOut.push({
    path: '/oauth2',
    name: 'login',
    component: oauth2PluginsType === 'local' ? _import('plugins/dvadmin-oauth2-web/src/login/index') : pluginImport('dvadmin-oauth2-web/src/login/index')
  })
}
/**
 * 租户申请注册
 */
const tenantsPluginsType = checkPlugins('dvadmin-tenants-web')
if (tenantsPluginsType) {
  frameOut.push({
    path: '/register',
    name: 'tenantsRegister',
    component: tenantsPluginsType === 'local' ? _import('plugins/dvadmin-tenants-web/src/register/index') : pluginImport('dvadmin-tenants-web/src/register/index')
  })
}
/**
 * 错误页面
 */
const errorPage = [{
  path: '/404',
  name: '404',
  component: _import('system/error/404')
}]

// 导出需要显示菜单的
export const frameInRoutes = frameIn
export const frameOutRoutes = frameOut

// 重新组织后导出
export default [
  ...frameIn,
  ...frameOut,
  ...errorPage
]
