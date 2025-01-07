<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @ResetLdapUserPassword="ResetLdapUserPassword"
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
      title="密码重置"
      :visible.sync="dialogFormVisible"
      :close-on-click-modal="false"
      width="30%"
    >
      <el-form :model="resetPwdForm" ref="resetPwdForm">
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="resetPwdForm.password"
            type="password"
            show-password
            clearable
            autocomplete="off"
          ></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">取 消</el-button>
        <el-button type="primary" @click="resetPwdSubmit">重 置</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

export default {
  name: 'devops-ldap-management',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      resetPwdForm: {
        uid: null,
        password: null
      },
      dialogFormVisible: false
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
      return api.addLdapUser(row).then(res => {
        this.$message({
          message: res,
          showClose: true,
          duration: 5000,
          type: 'success'
        })
        this.doRefresh()
      })
      // console.log('123')
      // return api.addLdapUser(row)
    },
    delRequest (row) {
      return api.deleteLdapUser(row.uid)
    },
    ResetLdapUserPassword ({ row }) {
      this.dialogFormVisible = true
      this.resetPwdForm.uid = row.uid
    },
    resetPwdSubmit () {
      const that = this
      that.$refs.resetPwdForm.validate((valid) => {
        if (valid) {
          const params = {
            uid: that.resetPwdForm.uid,
            password: that.resetPwdForm.password
          }
          api.updateLdapUserPwd(params).then((res) => {
            that.dialogFormVisible = false
            that.resetPwdForm = {
              uid: null,
              password: null
            }
            that.$message.success('修改成功')
          })
        } else {
          that.$message.error('表单校验失败，请检查')
        }
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
