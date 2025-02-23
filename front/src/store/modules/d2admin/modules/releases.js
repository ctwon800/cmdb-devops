
import util from '@/libs/util.js'

export default {
  namespaced: true,
  mutations: {
    /**
     * @description 显示版本信息
     * @param {Object} state state
     */
    versionShow () {
      util.log.capsule('D2Admin', `v${process.env.VUE_APP_VERSION}`)
      // console.log('DVAdmin(Gitee)：https://gitee.com/liqianglog/django-vue-admin')
      // console.log('演示地址：https://demo.django-vue-admin.com')
      // console.log('社区地址：https://bbs.django-vue-admin.com')
      // console.log('文档地址：https://www.django-vue-admin.com')
      // console.log('前端配置文档地址：https://d2.pub/zh/doc/d2-crud-v2')
      // console.log('请不要吝啬您的 star，谢谢 ~')
    }
  }
}
