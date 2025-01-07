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
            @click="onExport"
            v-permission="'Export'"
            ><i class="el-icon-download" /> 导出
          </el-button>
          <importExcel
            api="api/cmdb/cmdb-server-instance/"
            v-permission="'Import'"
            >导入
          </importExcel>
          <el-button
            size="small"
            type="warning"
            @click="UpdateCloudCostClick"
            ><i class="el-icon-refresh" /> 手动更新
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
    <el-dialog title="手动更新云账号费用" :visible.sync="updateCloudCostFormVisible">
      <el-form ref="updateCloudCostForm" :model="updateCloudCostForm">
        <el-form-item label="平台" prop="server_platform_id">
          <el-select v-model="updateCloudCostForm.server_platform_id" clearable placeholder="请选择">
          <el-option
            v-for="item in server_platform_mess"
            :key="item.id"
            :label="item.server_platform"
            :value="item.id">
          </el-option>
        </el-select>
        </el-form-item>
        <el-form-item label="账号" prop="account_name_id">
          <el-select v-model="updateCloudCostForm.account_name_id" clearable placeholder="请选择">
            <el-option
              v-for="item in account_name_mess"
              :key="item.id"
              :label="item.account_name"
              :value="item.id">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="账单月份" prop="bill_cycle">
          <el-date-picker
            v-model="updateCloudCostForm.bill_cycle"
            type="monthrange"
            range-separator="至"
            start-placeholder="开始月份"
            end-placeholder="结束月份">
          </el-date-picker>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="updateCloudCostFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateCloudCost">确 定</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

export default {
  name: 'cmdb-cloud-cost',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogFormVisible: false,
      updateCloudCostFormVisible: false,
      server_platform: '',
      account_name: '',
      bill_cycle: '',
      server_platform_mess: [],
      account_name_mess: [],
      bill_cycle_mess: [],
      updateCloudCostForm: {
        server_platform_id: '',
        bill_cycle: '',
        account_name_id: ''
      }
    }
  },
  created() {
    this.fetchData()
  },
  methods: {
    fetchData() {
      this.loading = true
      const query = {}
      api.GetList(query)
    },
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
    UpdateCloudCostClick() {
      this.updateCloudCostFormVisible = true
      api.GetServerPlatform().then(res => {
        this.server_platform_mess = res.data.data
      })
      api.GetAccountName().then(res => {
        this.account_name_mess = res.data.data
      })
      api.GetMonthList().then(res => {
        this.bill_cycle_mess = res.data.data
      })
    },
    submitUpdateCloudCost () {
      this.$refs.updateCloudCostForm.validate((valid) => {
        if (!valid) {
          return
        }
        const params = Object.assign({}, this.updateCloudCostForm)
        console.log(params)
        api.UpdateCloudCost(params).then(res => {
          this.updateCloudCostFormVisible = false
          console.log(res)
          this.$message({
            message: res,
            showClose: true,
            duration: 5,
            type: 'success'
          })
          this.doRefresh()
          this.$refs.updateCloudCostForm.resetFields()
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
