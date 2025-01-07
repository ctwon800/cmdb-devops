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
        filterable
        props: row.id
        v-model="value"
        :render-content="renderFunc"
        :data="transferData"
        :titles="['Source', 'Target']"
        :format="{
          noChecked: '${total}',
          hasChecked: '${checked}/${total}'
        }"
        @change="handleChange"
        style="el-transfer-panel:350px">
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
import { request } from '@/api/service'
export default {
  name: 'cmdb-server-remote-account',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogServerRemoteVisible: false,
      transferData: [],
      value: [],
      returnData: [],
      my_id: '',
      // valueData: [],
      renderFunc(h, option) {
        return <span>{ option.label }</span>
      }
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
      api.GetServerRemoteAccounExclude(row.id).then((res) => {
        this.returnDataExclude = res.data.remote_account_detail_exclude
      })
      request({
        url: '/api/cmdb/server_remote_account/ser_remote_account/'
      }).then((res) => {
        this.returnData = res.data.server_no_remote_account
        const data = []
        console.log(this.returnData)
        const generateData = _ => {
          for (let i = 0; i < this.returnData.length; i++) {
            const trueOrFalse = _ => {
              for (let m = 0; m < this.returnDataExclude.length; m++) {
                if (this.returnData[i] === this.returnDataExclude[m]) {
                  return true
                } else {
                  return false
                }
              }
            }
            data.push({
              key: i,
              label: this.returnData[i],
              disabled: trueOrFalse()
              // disabled: i % 4 === 0
            })
          }
          console.log('909090')
          console.log(data)
          return data
        }
        this.transferData = generateData()
      })
      api.GetServerRemoteAccounDetail(row.id).then(res => {
        this.my_value = res.data.remote_account_detail
        console.log(this.my_value)
        const valueData = _ => {
          const data = []
          for (let i = 0; i < this.my_value.length; i++) {
            for (let m = 0; m < this.returnData.length; m++) {
              if (this.my_value[i] === this.returnData[m]) {
                data.push(m)
              }
            }
          }
          console.log(data)
          return data
        }
        this.value = valueData()
        console.log('1111')
        console.log(this.value)
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
    handleChange(value, direction, movedKeys) {
      console.log(value, direction, movedKeys)
    },
    submitServerRemote () {
      const updateData = []
      for (const item of this.value) {
        console.log(item)
        updateData.push(this.transferData[item])
      }
      this.dialogServerRemoteVisible = false
      // console.log(updateData)
      api.UpdateServerRemoteAccount(updateData, this.my_id).then(res => {
        console.log(res)
        this.$message({
          message: '更新完成',
          duration: 5,
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
  width: auto
}
</style>
