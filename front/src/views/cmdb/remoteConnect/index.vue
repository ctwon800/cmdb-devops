<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @updateYunresource="updateYunresource"
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
    <el-dialog
      title="更新云资源"
      :visible.sync="dialogUpdateVisible"
      width="30%"
      :before-close="handleClose">
      <span>请确定是否手动更新云资源，目前仅支持更新云主机，云资源会每天自动定时更新。</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogUpdateVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateYunresource">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'cmdb-remote-connect',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogUpdateVisible: false
    }
  },
  methods: {
    getCrudOptions () {
      // this.crud.searchOptions.form
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
    updateYunresource({ row }) {
      this.dialogUpdateVisible = true
      this.yunResId = row.id
      console.log(row.id)
    },
    submitUpdateYunresource() {
      // console.log(that.account_name)
      console.log(this.yunResId)
      const params = {
        id: this.yunResId
      }
      api.UpdateYunRes(params).then((res) => {
        this.dialogUpdateVisible = false
        this.$message.success('更新成功')
      })
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
