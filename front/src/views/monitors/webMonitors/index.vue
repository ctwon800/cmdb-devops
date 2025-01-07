<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @SetUnmonitor="handleSetUnmonitor"
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
            type="primary"
            @click="addRow"
          >
            <i class="el-icon-plus" /> 新增
          </el-button>
          <el-button size="small" type="danger" @click="batchDelete">
            <i class="el-icon-delete"></i> 批量删除
          </el-button>
          <el-button size="small" type="warning" @click="batchSetUnmonitor">
            <i class="el-icon-warning" /> 批量设置不监控
          </el-button>
          <el-button
            size="small"
            type="danger"
            @click="showUnmonitorWebMonitors"
          >
            <i class="el-icon-warning" /> 不监控列表
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
      title="不监控列表"
      :visible.sync="unmonitorWebDialogVisible"
      width="80%">
      <div class="search-box">
        <el-input
          v-model="searchQuery"
          placeholder="请输入网站地址搜索"
          prefix-icon="el-icon-search"
          clearable
          @keyup.enter.native="handleSearch"
          @clear="handleClear"
        >
          <el-button
            slot="append"
            icon="el-icon-search"
            @click="handleSearch">
            查询
          </el-button>
        </el-input>
      </div>
      <el-table
        :data="unmonitorWebList"
        style="width: 100%"
        border
        v-loading="loading">
        <el-table-column
          prop="web_uri"
          label="web站点"
          width="200">
        </el-table-column>
        <el-table-column
          prop="web_account"
          label="所属账号"
          width="145">
        </el-table-column>
        <el-table-column
          prop="web_status"
          label="网站状态"
          width="150">
        </el-table-column>
        <el-table-column
          label="操作"
          width="150">
          <template slot-scope="scope">
            <el-button
              size="small"
              type="primary"
              @click="handleRemoveUnmonitor(scope.row)">
              移除不监控列表
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      <div class="pagination-container">
        <el-pagination
          @current-change="handleUnmonitorWebPageChange"
          :current-page="unmonitorWebPagination.currentPage"
          :page-size="unmonitorWebPagination.pageSize"
          :total="unmonitorWebPagination.total"
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
  name: 'cmdb-web-monitors',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      unmonitorWebDialogVisible: false,
      unmonitorWebList: [],
      loading: false,
      unmonitorWebPagination: {
        currentPage: 1,
        pageSize: 10,
        total: 0
      },
      searchQuery: ''
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
    showUnmonitorWebMonitors() {
      this.unmonitorWebDialogVisible = true
      this.searchQuery = ''
      this.loadUnmonitorWebList(1)
    },
    loadUnmonitorWebList(page) {
      const query = {
        page: page,
        limit: this.unmonitorWebPagination.pageSize,
        search: this.searchQuery
      }
      api.GetUnmonitorList(query).then((res) => {
        this.unmonitorWebList = res.data.data
        this.unmonitorWebPagination = {
          currentPage: res.data.page,
          pageSize: res.data.limit,
          total: res.data.total
        }
      })
    },
    handleUnmonitorWebPageChange(currentPage) {
      this.loadUnmonitorWebList(currentPage)
    },
    handleRemoveUnmonitor(row) {
      this.$confirm('确认将该web站点状态设置为监控吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.updateWebCheckEnable({ id: row.id }).then(() => {
          const index = this.unmonitorWebList.findIndex(item => item.id === row.id)
          if (index > -1) {
            this.unmonitorWebList.splice(index, 1)
          }
          this.$message({
            type: 'success',
            message: '状态已更新为监控！'
          })
          this.doRefresh()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        })
      })
    },
    handleSetUnmonitor({ row }) {
      this.$confirm('确认将该web站点设置为不监控吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.updateWebCheckEnable({ id: row.id }).then(() => {
          this.$message({
            type: 'success',
            message: '状态已更新为不监控！'
          })
          this.doRefresh()
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        })
      })
    },
    batchSetUnmonitor() {
      if (!this.multipleSelection || this.multipleSelection.length === 0) {
        this.$message({
          type: 'warning',
          message: '请选择要设置的web站点'
        })
        return
      }

      this.$confirm('确认将选中的web站点设置为不监控吗？', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        const promises = this.multipleSelection.map(row => {
          return api.updateWebCheckEnable({ id: row.id })
        })
        Promise.all(promises).then(() => {
          this.$message({
            type: 'success',
            message: '批量设置不监控成功！'
          })
          this.doRefresh()
        }).catch(() => {
          this.$message({
            type: 'error',
            message: '批量设置不监控失败'
          })
        })
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        })
      })
    },
    handleSearch() {
      this.unmonitorWebPagination.currentPage = 1
      this.loadUnmonitorWebList(1)
    },
    handleClear() {
      this.searchQuery = ''
      this.loadUnmonitorWebList(1)
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
.search-box {
  margin-bottom: 20px;
}
</style>
