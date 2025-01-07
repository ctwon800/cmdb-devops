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
          <el-button
            type="primary"
            size="small"
            icon="el-icon-s-tools"
            @click="platformManager"
          >平台管理</el-button>
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
      width="30%">
      <span>请确定是否手动更新云资源，目前仅支持更新云主机，云资源会每天自动定时更新。</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogUpdateVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitUpdateYunresource">确 定</el-button>
      </span>
    </el-dialog>
    <!-- 添加平台管理对话框 -->
    <el-dialog
      title="平台管理"
      :visible.sync="platformDialogVisible"
      width="50%">
      <div class="platform-manager">
        <div class="operation-bar">
          <el-button type="primary" size="small" @click="addPlatform">
            <i class="el-icon-plus"></i> 新增平台
          </el-button>
        </div>
        <el-table :data="platformList" style="width: 100%">
          <el-table-column prop="id" label="id"></el-table-column>
          <el-table-column prop="server_platform" label="平台名称"></el-table-column>
          <el-table-column label="操作" width="150">
            <template slot-scope="scope">
              <el-button type="text" @click="editPlatform(scope.row)">编辑</el-button>
              <el-button type="text" style="color: #F56C6C" @click="deletePlatform(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
    <!-- 平台编辑对话框 -->
    <el-dialog
      :title="platformForm.id ? '编辑平台' : '新增平台'"
      :visible.sync="platformFormVisible"
      width="30%">
      <el-form :model="platformForm" ref="platformForm" label-width="80px">
        <el-form-item label="平台名称" prop="server_platform">
          <el-input v-model="platformForm.server_platform"></el-input>
        </el-form-item>
      </el-form>
      <span slot="footer" class="dialog-footer">
        <el-button @click="platformFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitPlatform">确 定</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'cmdb-account-management',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogUpdateVisible: false,
      platformDialogVisible: false,
      platformFormVisible: false,
      platformList: [],
      platformForm: {
        id: null,
        server_platform: ''
      }
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
    },
    platformManager () {
      this.platformDialogVisible = true
      // api.getPlatformList().then(response => {
      //   this.platformList = response.data.data
      // }).catch(error => {
      //   console.error('Error fetching node detail:', error)
      // })
      this.mygetPlatformList()
    },
    async mygetPlatformList() {
      try {
        const res = await api.getPlatformList()
        this.platformList = res.data.data
      } catch (error) {
        this.$message.error('获取平台列表失败')
      }
    },
    addPlatform() {
      this.platformForm = {
        id: null,
        server_platform: ''
      }
      this.platformFormVisible = true
    },
    editPlatform(row) {
      this.platformForm = { ...row }
      this.platformFormVisible = true
    },
    async deletePlatform(row) {
      try {
        await this.$confirm('确认删除该平台?', '提示', {
          type: 'warning'
        })
        await api.deletePlatform(row.id)
        this.$message.success('删除成功')
      } catch (error) {
        if (error !== 'cancel') {
          this.$message.error('删除失败')
        }
      }
      this.mygetPlatformList()
    },
    async submitPlatform() {
      try {
        if (this.platformForm.id) {
          await api.updatePlatform(this.platformForm)
          this.$message.success('更新成功')
        } else {
          await api.addPlatform(this.platformForm)
          this.$message.success('添加成功')
        }
        this.mygetPlatformList()
        this.platformFormVisible = false
      } catch (error) {
        this.$message.error(this.platformForm.id ? '更新失败' : '添加失败')
      }
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
.platform-manager {
  .operation-bar {
    margin-bottom: 15px;
  }
}
</style>
