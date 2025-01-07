<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @recordVideo="recordVideo"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <crud-toolbar
          :search.sync="crud.searchOptions.show"
          :compact.sync="crud.pageOptions.compact"
          :columns="crud.columns"
          @refresh="doRefresh()"
          @columns-filter-changed="handleColumnsFilterChanged"
        />
      </div>
    </d2-crud-x>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

export default {
  name: 'cmdb-remote-record',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogFormVisible: false,
      path_src: 'https://ice-service-test-hz.oss-cn-hangzhou.aliyuncs.com/tmp/20231220-173315-i-bp186s6hda2qiixu9k6r.cast',
      showVideo: false,
      isShow: false
    }
  },
  methods: {
    getCrudOptions () {
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    recordVideo({ row }) {
      const host = window.location.host
      const protocol = window.location.protocol
      console.log(row.record_filepath)
      const videoSrc = protocol + '//' + host + '/' + row.record_filepath
      console.log(videoSrc)
      const pathHerf = this.$router.resolve({
        path: '/remoteRecordVideo',
        query: {
          recordVideoPath: videoSrc
        }
      })
      window.open(pathHerf.href, '_blank')
    }
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
