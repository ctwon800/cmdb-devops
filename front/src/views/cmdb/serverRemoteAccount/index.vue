<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @serverAssociate="serverAssociate"
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
      title="关联服务器"
      :visible.sync="dialogServerRemoteVisible"
      width="80%">
      <el-transfer
        :key="dialogServerRemoteVisible"
        filterable
        v-model="value"
        :data="transferData"
        :titles="['未关联服务器', '已关联服务器']"
        :format="{
          noChecked: '${total}',
          hasChecked: '${checked}/${total}'
        }">
      </el-transfer>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogServerRemoteVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitServerRemote">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
// import { request } from '@/api/service'
export default {
  name: 'cmdb-server-remote-account',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogServerRemoteVisible: false,
      transferData: [],
      value: [],
      returnData: [],
      my_id: ''
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
    serverAssociate({ row }) {
      this.my_id = row.id
      this.dialogServerRemoteVisible = true
      this.transferData = []
      this.value = []
      // 获取所有可选服务器
      api.GetServerRemoteAccounExclude(row.id).then((res) => {
        this.transferData = res.data.remote_account_detail_exclude.map((item, index) => ({
          key: index,
          label: item, // 根据实际数据结构选择合适的显示字段
          disabled: false
        }))
        // 获取已关联的服务器
        api.GetServerRemoteAccounDetail(row.id).then(res => {
          // this.value = res.data.remote_account_detail
          const selectedServers = res.data.remote_account_detail
          this.value = this.transferData
            .filter(item => selectedServers.includes(item.label))
            .map(item => item.key)
        })
      })
    },
    onExport () {
      const that = this
      this.$confirm('是否确认导出所有数据项?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(function () {
        const query = that.getSearch().getForm()
        return api.exportData({ ...query })
      })
    },
    submitServerRemote () {
      // 根据选中的索引获取对应的服务器标签
      const updateData = this.value.map(index => {
        const selectedItem = this.transferData.find(item => item.key === index)
        return selectedItem.label
      })
      console.log(updateData)
      this.dialogServerRemoteVisible = false
      api.UpdateServerRemoteAccount(updateData, this.my_id).then(res => {
        this.$message({
          message: '更新完成',
          duration: 3000,
          type: 'success'
        })
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
.el-transfer-panel {
  width: auto;
}
</style>
