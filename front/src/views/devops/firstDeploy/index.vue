<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
       <template slot="header">测试页面1</template>
    <!-- <d2-crud-x
      ref="d2Crud"
    >
      <div slot="header">
        <h1>hello world</h1>
      </div>
    </d2-crud-x> -->
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'devops-first-deploy',
  mixins: [d2CrudPlus.crud],
  data () {
    return {}
  },
  methods: {
    getCrudOptions () {
      return crudOptions(this)
    },
    pageRequest (query) {
      query.lazy = true
      return api.GetList(query)
    }
    // addRequest (row) {
    //   d2CrudPlus.util.dict.clear()
    //   this.$store.dispatch('d2admin/dept/load')
    //   return api.createObj(row)
    // },
    // updateRequest (row) {
    //   d2CrudPlus.util.dict.clear()
    //   this.$store.dispatch('d2admin/dept/load')
    //   return api.UpdateObj(row)
    // },
    // delRequest (row) {
    //   d2CrudPlus.util.dict.clear()
    //   this.$store.dispatch('d2admin/dept/load')
    //   return api.DelObj(row.id)
    // },
    // 授权
    // createPermission (scope) {
    //   this.$router.push({
    //     name: 'menuButton',
    //     query: { id: scope.row.id, name: scope.row.name }
    //   })
    // },
  }
}
</script>

<style lang="scss">
.yxtInput {
  .el-form-item__label {
    color: #49a1ff;
  }
}
</style>
