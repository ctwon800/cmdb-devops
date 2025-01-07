<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @setAbnormal="handleSetAbnormal"
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
            @click="UpdateSSLMonitorClick"
            ><i class="el-icon-refresh" /> 手动更新证书信息
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="showAbnormalSSLMonitors"
          >
            <i class="el-icon-warning" /> 异常证书列表
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
    <el-dialog title="手动更新证书内容" :visible.sync="updateSSLMonitorFormVisible"
      v-loading="loading"
      element-loading-text="正在更新证书信息中，请稍等"
      element-loading-spinner="el-icon-loading"
      element-loading-background="rgba(0, 0, 0, 0.8)">
      <span>是否确定更新</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="updateSSLMonitorFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateSSLMonitor">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      title="异常证书列表"
      :visible.sync="abnormalSSLDialogVisible"
      width="80%">
      <el-table
        :data="abnormalSSLList"
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column
          prop="ssl_domain"
          label="证书名称"
          width="200">
        </el-table-column>
        <el-table-column
          prop="ssl_account"
          label="所属账号"
          width="145">
        </el-table-column>
        <el-table-column
          prop="ssl_expire_time"
          label="到期日期"
          width="150">
        </el-table-column>
        <el-table-column
          prop="ssl_expire_days"
          label="到期天数"
          width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.ssl_expire_days < 30 ? 'danger' : 'success'">
              {{ scope.row.ssl_expire_days }}天
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="ssl_status"
          label="状态"
          width="100">
          <template slot-scope="scope">
            <el-tag :type="scope.row.ssl_status === '正常' ? 'success' : 'danger'">
              {{ scope.row.ssl_status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          label="操作"
          width="150">
          <template slot-scope="scope">
            <el-button
              size="small"
              type="primary"
              @click="handleRemoveAbnormal(scope.row)">
              移除异常状态
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          @current-change="handleAbnormalSSLPageChange"
          :current-page="abnormalSSLPagination.currentPage"
          :page-size="abnormalSSLPagination.pageSize"
          :total="abnormalSSLPagination.total"
          layout="total, prev, pager, next">
        </el-pagination>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'cmdb-ssl-monitors',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      updateSSLMonitorFormVisible: false,
      abnormalSSLDialogVisible: false,
      abnormalSSLList: [],
      loading: false,
      abnormalSSLPagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
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
    UpdateSSLMonitorClick() {
      this.updateSSLMonitorFormVisible = true
    },
    submitUpdateSSLMonitor() {
      this.updateSSLMonitorFormVisible = false
      api.updateMonitors()
      this.$message({
        message: '后台正在执行中，请5分钟后再查看',
        showClose: true,
        duration: 5000,
        type: 'success'
      })
      this.doRefresh()
    },
    showAbnormalSSLMonitors() {
      this.abnormalSSLDialogVisible = true
      this.loadAbnormalSSLList(1)
    },
    loadAbnormalSSLList(page) {
      const query = {
        page: page,
        limit: this.abnormalSSLPagination.pageSize
      }
      api.GetAbnormalList(query).then((res) => {
        this.abnormalSSLList = res.data.data
        this.abnormalSSLPagination = {
          currentPage: res.data.page,
          pageSize: res.data.limit,
          total: res.data.total
        }
      })
    },
    handleAbnormalSSLPageChange(currentPage) {
      this.loadAbnormalSSLList(currentPage)
    },
    // handleDelete(row) {
    //   this.$confirm('确定删除此项吗?', '提示', {
    //     confirmButtonText: '确定',
    //     cancelButtonText: '取消',
    //     type: 'warning'
    //   }).then(() => {
    //     this.delRequest(row).then(() => {
    //       this.$message({
    //         type: 'success',
    //         message: '删除成功!'
    //       })
    //       this.doRefresh()
    //     })
    //   }).catch(() => {
    //     this.$message({
    //       type: 'info',
    //       message: '已取消删除'
    //     })
    //   })
    // },
    handleRemoveAbnormal(row) {
      this.$confirm('确认将该证书状态设置为正常吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.updateSSLStatus({ id: row.id }).then(() => {
          const index = this.abnormalSSLList.findIndex(item => item.id === row.id)
          if (index > -1) {
            this.abnormalSSLList.splice(index, 1)
          }
          this.$message({
            type: 'success',
            message: '状态已更新为正常！'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        })
      })
    },
    handleSetAbnormal({ row }) {
      this.$confirm('确认将该证书状态设置为异常吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.updateSSLStatus({ id: row.id }).then(() => {
          this.$message({
            type: 'success',
            message: '状态已更新为异常！'
          })
          this.loadAbnormalSSLList(this.abnormalSSLPagination.currentPage)
          this.doRefresh()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
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

<style lang="scss" scoped>
.pagination-container {
  margin-top: 15px;
  text-align: right;
}
</style>
