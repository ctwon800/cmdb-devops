<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @tasksResults="tasksResults"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <el-button-group>
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
      title="执行结果"
      :visible.sync="dialogVisible"
      width="60%">
      <div v-for="item in outputData" :key="item.instancename" class="output-container">
        <p class="instancename">{{ item.instancename }}</p>
        <pre class="output">{{ formatOutput(item.output) }}</pre>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

export default {
  name: 'celery-results',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogVisible: false,
      tasksResult: '',
      outputData: [],
      output: ''
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
    delRequest (row) {
      return api.DelObj(row.id)
    },
    batchDelRequest (ids) {
      return api.BatchDel(ids)
    },
    tasksResults({ row }) {
      this.dialogVisible = true
      this.outputData = row.result
    },
    formatOutput(output) {
      console.log(output)
      if (!output) {
        return ''// 如果 output 为 undefined 或 null，则返回空字符串
      }
      return output.replace(/\\u([0-9a-fA-F]{4})/g, (match, grp) => String.fromCharCode(parseInt(grp, 16)))
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

.output-container {
  margin-bottom: 20px;
}

.instancename {
  font-weight: bold;
  margin-bottom: 10px;
}

.output {
  background-color: #f7f7f7;
  padding: 10px;
  border-radius: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

</style>
