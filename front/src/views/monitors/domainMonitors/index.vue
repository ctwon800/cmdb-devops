<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <el-button-group>
          <el-button
            size="small"
            v-permission="'Create'"
            type="primary"
            @click="addRow"
          >
            <i class="el-icon-plus" /> 新增
          </el-button>
          <el-button size="small" type="danger" @click="batchDelete">
            <i class="el-icon-delete"></i> 批量删除
          </el-button>
          <el-button
            size="small"
            type="warning"
            @click="UpdateDomainMonitorClick"
            ><i class="el-icon-refresh" /> 手动更新域名信息
          </el-button>
        </el-button-group>
        <crud-toolbar
          :search.sync="crud.searchOptions.show"
          :compact.sync="crud.pageOptions.compact"
          :columns="crud.columns"
          @refresh="doRefresh()"
          @columns-filter-changed="handleColumnsFilterChanged"
        />
      </div>
      <span slot="PaginationPrefixSlot" class="prefix">
        <el-button
          class="square"
          size="mini"
          title="批量删除"
          @click="batchDelete"
          icon="el-icon-delete"
          :disabled="!multipleSelection || multipleSelection.length == 0"
        />
      </span>
    </d2-crud-x>
    <el-dialog title="手动更新域名信息" :visible.sync="updateDomainMonitorFormVisible"
      v-loading="loading"
      element-loading-text="正在更新域名信息中，请稍等"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)"
      >
      <span>是否确定更新</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="updateDomainMonitorFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateDomainMonitor">确 定</el-button>

      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'cmdb-domain-monitors',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      updateDomainMonitorFormVisible: false,
      loading: false
    }
  },
  methods: {
    getCrudOptions () {
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    addRequest (row) {
      return api.AddObj(row)
    },
    updateRequest (row) {
      return api.UpdateObj(row)
    },
    delRequest (row) {
      return api.DelObj(row.id)
    },
    batchDelRequest (ids) {
      return api.BatchDel(ids)
    },
    UpdateDomainMonitorClick() {
      this.updateDomainMonitorFormVisible = true
    },
    submitUpdateDomainMonitor() {
      api.updateMonitors()
      this.updateDomainMonitorFormVisible = false
      this.$message({
        message: '后台正在执行中，请5分钟后再查看',
        showClose: true,
        duration: 5000,
        type: 'success'
      })
      this.doRefresh()
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
.el-transfer-panel {
  width: auto
}
</style>
