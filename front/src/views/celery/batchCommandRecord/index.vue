<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @batchCommandResult="batchCommandResult"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <crud-toolbar
          :search.sync="crud.searchOptions.show"
          :compact.sync="crud.pageOptions.compact"
          :columns="crud.columns"
          @refresh="doRefresh()"
          @columns-filter-changed="handleColumnsFilterChanged"
        />
      </div>
    </d2-crud-x>

    <el-dialog
      title="执行结果"
      :visible.sync="dialogFormVisible"
      width="80%">
      <pre>{{ commandResult }}</pre>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogFormVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

export default {
  name: 'batchCommandRecord',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      dialogFormVisible: false,
      path_src: 'https://ice-service-test-hz.oss-cn-hangzhou.aliyuncs.com/tmp/20231220-173315-i-bp186s6hda2qiixu9k6r.cast',
      showVideo: false,
      isShow: false,
      commandResult: ''
    }
  },
  methods: {
    getCrudOptions () {
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    batchCommandResult({ row }) {
      try {
        let output = ''
        // 解析输入数据
        const results = typeof row.formatted_output === 'string'
          ? JSON.parse(row.formatted_output)
          : row.formatted_output || []

        results.forEach((item, index) => {
          if (!item) {
            output += '\n'
            return
          }

          const isString = typeof item === 'string'
          const isObject = item && typeof item === 'object'

          if (!isString && !isObject) return

          // 只在新服务器开始时添加分隔线
          const cleanedItem = isString ? item.replace(/^\n+/, '') : ''
          const isServerInfo = cleanedItem.includes('当前服务器')

          if (isServerInfo) {
            output += '\n----------------------------------------\n'
          }

          if (isString) {
            const isCommandStart = cleanedItem.includes('开始执行命令在服务器:')
            output += isServerInfo || isCommandStart
              ? cleanedItem
              : '\n  ' + cleanedItem

            console.log('cleanedItem', cleanedItem)
            return
          }

          // 处理对象类型（最终状态）
          output += '\n最终状态：' + (item.code === 200 ? '✅ 成功' : '❌ 失败')
          output += '\n消息：' + item.message
        })

        this.commandResult = output.trim() || '暂无执行结果'
        console.log('解析成功:', this.commandResult)
      } catch (e) {
        console.error('解析结果失败:', e)
        this.commandResult = typeof row.formatted_output === 'string'
          ? row.formatted_output
          : JSON.stringify(row.formatted_output, null, 2)
      }
      this.dialogFormVisible = true
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

.el-dialog__body pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  font-family: Monaco, Consolas, Courier, monospace;
  line-height: 1.5;
  color: #333;
}

.el-dialog__body pre {
  .success {
    color: #67C23A;
  }
  .error {
    color: #F56C6C;
  }
}
</style>
