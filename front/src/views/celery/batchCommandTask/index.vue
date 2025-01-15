<template>
  <d2-container>
    <div class="ansible-container">
      <!-- 左侧服务器列表区域 -->
      <div class="server-list">
        <!-- 添加服务器组管理按钮 -->
        <div class="group-manage-header">
          <el-button type="primary" size="small" @click="showGroupDialog">
            服务器组管理
          </el-button>
        </div>

        <el-tree
          :data="serversGroup"
          @check="handleCheckChange"
          show-checkbox
          node-key="id"
          :props="defaultProps">
        </el-tree>
      </div>

      <!-- 右侧任务执行区域 -->
      <div class="task-execution">
        <div class="task-config">
          <el-form :model="taskForm" label-width="80px">
            <el-form-item label="执行命令">
              <el-input type="textarea" v-model="taskForm.command"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="executeTask">执行</el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 任务输出区域 -->
        <div class="task-output">
          <pre v-html="taskOutput" class="resizable-output"></pre>
        </div>
      </div>
    </div>

    <!-- 添加服务器组管理对话框 -->
    <el-dialog title="服务器组管理" :visible.sync="groupDialogVisible" width="600px" @closed="handleGroupDialogClose">
      <div class="group-dialog-content">
        <div class="group-list">
          <div class="group-list-header">
            <el-button type="primary" size="small" @click="addNewGroup">
              新建服务器组
            </el-button>
          </div>
          <el-table :data="groupList" style="width: 100%">
            <el-table-column prop="group_name" label="组名称"></el-table-column>
            <el-table-column label="操作" width="300">
              <template slot-scope="scope">
                <el-button size="mini" @click="editGroup(scope.row)">编辑</el-button>
                <el-button size="mini" type="primary" @click="manageServers(scope.row)">管理服务器</el-button>
                <el-button size="mini" type="danger" @click="deleteGroup(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>
    </el-dialog>

    <!-- 添加服务器管理对话框 -->
    <el-dialog :title="currentGroup.group_name + ' - 服务器管理'" :visible.sync="serverDialogVisible" width="80%">
      <div class="server-dialog-content">
        <el-button type="primary" size="small" @click="addNewServer">
          添加服务器
        </el-button>
        <el-table :data="currentGroupServers" style="width: 100%">
          <el-table-column prop="instancename" label="服务器名称" width="200"></el-table-column>
          <el-table-column prop="hostname" label="主机名" width="200"></el-table-column>
          <el-table-column prop="instanceid" label="服务器ID"></el-table-column>
          <el-table-column prop="public_ip" label="公网ip"></el-table-column>
          <el-table-column prop="primary_ip" label="内网ip"></el-table-column>
          <el-table-column label="操作">
            <template slot-scope="scope">
              <!-- <el-button size="mini" @click="editServer(scope.row)">编辑</el-button> -->
              <el-button size="mini" type="danger" @click="removeServer(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>

    <!-- 添加新建服务器组对话框 -->
    <el-dialog :title="dialogType === 'add' ? '新建服务器组' : '修改服务器组'" :visible.sync="addGroupDialogVisible" width="400px">
      <el-form :model="newGroupForm" :rules="groupFormRules" ref="newGroupForm" label-width="80px">
        <el-form-item label="组名称" prop="group_name">
          <el-input v-model="newGroupForm.group_name" placeholder="请输入服务器组名称"></el-input>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="addGroupDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitNewGroup">确 定</el-button>
      </div>
    </el-dialog>

    <!-- 添加选择服务器对话框 -->
    <el-dialog title="选择服务器" :visible.sync="selectServerDialogVisible" width="80%">
      <div class="server-select-content">
        <div class="search-bar" style="margin-bottom: 20px; display: flex; align-items: center;">
          <el-input
            v-model="searchQuery"
            placeholder="请输入搜索关键词"
            style="width: 300px"
            @keyup.enter.native="handleSearchConfirm"
            clearable>
            <el-button
              slot="append"
              icon="el-icon-search"
              @click="handleSearchConfirm"
              type="primary">
              搜索
            </el-button>
          </el-input>
        </div>
        <el-table
          :data="filteredServers.slice((currentPage-1)*pageSize, currentPage*pageSize)"
          style="width: 100%"
          @selection-change="handleSelectionChange">
          <el-table-column type="selection" width="55"></el-table-column>
          <el-table-column prop="instancename" label="服务器名称" width="200"></el-table-column>
          <el-table-column prop="hostname" label="主机名" width="200"></el-table-column>
          <el-table-column prop="instanceid" label="服务器ID"></el-table-column>
          <el-table-column prop="public_ip" label="公网ip"></el-table-column>
          <el-table-column prop="primary_ip" label="内网ip"></el-table-column>
        </el-table>
        <div class="pagination" style="margin-top: 20px; text-align: right">
          <el-pagination
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
            :current-page="currentPage"
            :page-sizes="[10, 20, 50, 100]"
            :page-size="pageSize"
            layout="total, sizes, prev, pager, next, jumper"
            :total="filteredServers.length">
          </el-pagination>
        </div>
      </div>
      <div slot="footer" class="dialog-footer">
        <el-button @click="selectServerDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitSelectedServers">确 定</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import util from '@/libs/util.js'
export default {
  name: 'ansibleTasks',
  data () {
    return {
      activeTab: 'serversGroup',
      serversGroup: [], // 树形结构数据
      defaultProps: {
        children: 'children',
        label: 'label'
      },
      taskForm: {
        module: '',
        command: ''
      },
      moduleOptions: [
        { label: 'shell', value: 'shell' },
        { label: 'copy', value: 'copy' },
        { label: 'file', value: 'file' }
      ],
      taskOutput: '',
      websocket: null,
      groupDialogVisible: false,
      serverDialogVisible: false,
      groupList: [],
      currentGroup: {},
      currentGroupServers: [],
      addGroupDialogVisible: false,
      newGroupForm: {
        group_name: ''
      },
      groupFormRules: {
        group_name: [
          { required: true, message: '请输入组名称', trigger: 'blur' },
          { min: 2, max: 20, message: '长度在 2 到 20 个字符', trigger: 'blur' }
        ]
      },
      dialogType: 'add', // 用于区分新增还是修改
      currentGroupId: null, // 存储当前编辑的组ID
      selectServerDialogVisible: false, // 选择服务器对话框显示状态
      allServers: [], // 所有可选服务器列表
      selectedServers: [], // 已选择的服务器
      searchQuery: '', // 搜索关键词
      currentPage: 1, // 当前页码
      pageSize: 10, // 每页显示条数
      selectedNodes: [] // 存储选中的节点
    }
  },
  created() {
    // 组件创建时加载数据
    this.loadGroups()
  },
  computed: {
    filteredServers() {
      if (!this.searchQuery) {
        return this.allServers
      }
      const query = this.searchQuery.toLowerCase()
      return this.allServers.filter(server => {
        return Object.values(server).some(value =>
          String(value).toLowerCase().includes(query)
        )
      })
    }
  },
  methods: {
    // handleServerGroupSelect(data) {
    //   if (data.isServer) {
    //     // 处理服务器节点点击
    //     console.log('选中服务器:', data.serverData)
    //     this.currentGroup = data.serverData
    //     this.serverDialogVisible = true
    //   } else if (data.isGroup) {
    //     // 处理组节点点击
    //     console.log('选中组:', data)
    //   }
    // },
    executeTask() {
      const selectedServers = this.getSelectedServers()
      if (!selectedServers || selectedServers.length === 0) {
        this.$message.warning('请选择至少一台服务器')
        return
      }

      const command = this.taskForm.command
      if (!command) {
        this.$message.warning('请输入执行命令')
        return
      }

      this.taskOutput = ''

      const requestData = {
        servers: selectedServers.map(server => server.id),
        command: command
      }

      // 发送任务请求
      api.ExecuteAnsibleTask(requestData)
        .then(response => {
          console.log(response)
          if (response.data.task_id) {
            // 获取到任务ID后建立WebSocket连接
            console.log(response.data)
            console.log(response.data.task_id)
            this.connectWebSocket(response.data.task_id)
          } else {
            this.$message.error('未获取到任务ID')
          }
        })
        .catch(error => {
          console.error('Request error:', error)
          this.$message.error('任务执行失败：' + (error.response?.data?.message || error.message))
        })
    },

    connectWebSocket(taskId) {
      // 关闭之前的连接
      if (this.websocket) {
        this.websocket.close()
      }

      // 建立新的WebSocket连接
      // const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const wsUrl = util.baseURL() + 'ws/ansible/' + taskId + '/'

      this.websocket = new WebSocket(wsUrl)

      this.websocket.onopen = () => {
        console.log('WebSocket连接已建立')
      }

      this.websocket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          console.log('收到消息:', message)

          switch (message.type) {
            case 'task_output':
              // 处理命令输出
              if (message.data.code === 200) {
                this.taskOutput += message.data.data + '\n'
                // 自动滚动到底部
                this.$nextTick(() => {
                  const outputElement = document.querySelector('.task-output')
                  if (outputElement) {
                    outputElement.scrollTop = outputElement.scrollHeight
                  }
                })
              }
              break
            case 'task_error':
              // 处理错误信息
              this.$message.error(message.data.message)
              this.taskOutput += `错误: ${message.data.message}\n`
              break
            case 'task_complete':
              // 处理任务完成
              this.$message.success(message.data.message)
              this.websocket.close()
              break
          }
        } catch (error) {
          console.error('解析消息失败:', error)
          this.taskOutput += `解析消息失败: ${error.message}\n`
        }
      }

      this.websocket.onerror = (error) => {
        console.error('WebSocket错误:', error)
        this.$message.error('WebSocket连接错误')
        this.taskOutput += 'WebSocket连接错误\n'
      }

      this.websocket.onclose = () => {
        console.log('WebSocket连接已关闭')
      }
    },
    // 显示组管理对话框
    showGroupDialog() {
      this.groupDialogVisible = true
      api.GetGroupList().then(res => {
        this.groupList = res.data.data
      })
    },

    // 加载组和服务器数据
    loadGroups() {
      api.GetGroupList().then(res => {
        const groups = res.data.data
        // 转换数据为树形结构
        this.serversGroup = groups.map(group => {
          return {
            id: group.id,
            label: group.group_name,
            children: [], // 初始化空的子节点数组
            isGroup: true // 标记这是一个组节点
          }
        })

        // 为每个组加载服务器
        this.serversGroup.forEach(group => {
          this.loadGroupServers(group)
        })
      })
    },

    // 加载组内服务器
    loadGroupServers(group) {
      api.ServerGroupList(group.id).then(res => {
        // 转换服务器数据为树节点格式
        const servers = res.data.data.map(server => ({
          id: server.id,
          label: server.instancename,
          isServer: true, // 标记这是一个服务器节点
          serverData: server // 保存完整的服务器数据
        }))

        // 更新组节点的children
        const groupIndex = this.serversGroup.findIndex(g => g.id === group.id)
        if (groupIndex !== -1) {
          this.$set(this.serversGroup[groupIndex], 'children', servers)
        }
      })
    },

    // 添加新组
    addNewGroup() {
      this.dialogType = 'add'
      this.currentGroupId = null
      this.addGroupDialogVisible = true
      this.newGroupForm.group_name = ''
      if (this.$refs.newGroupForm) {
        this.$refs.newGroupForm.clearValidate()
      }
    },

    // 提交表单
    submitNewGroup() {
      this.$refs.newGroupForm.validate(valid => {
        if (valid) {
          const submitData = {
            group_name: this.newGroupForm.group_name
          }
          const request = this.dialogType === 'add'
            ? api.ServerGroupAdd(submitData)
            : api.ServerGroupUpdate({ ...submitData, id: this.currentGroupId })

          request.then(res => {
            this.$message.success(this.dialogType === 'add' ? '添加成功' : '修改成功')
            this.addGroupDialogVisible = false
            // 重新加载组列表
            this.loadGroups()
            // 如果组管理对话框是打开的，也更新组管理对话框中的列表
            if (this.groupDialogVisible) {
              api.GetGroupList().then(res => {
                this.groupList = res.data.data
              })
            }
          }).catch(err => {
            this.$message.error((this.dialogType === 'add' ? '添加' : '修改') + '失败：' + err.message)
          })
        }
      })
    },

    // 编辑组
    editGroup(group) {
      this.dialogType = 'edit'
      this.currentGroupId = group.id
      this.addGroupDialogVisible = true
      this.newGroupForm.group_name = group.group_name
      if (this.$refs.newGroupForm) {
        this.$refs.newGroupForm.clearValidate()
      }
    },

    // 删除组
    deleteGroup(group) {
      this.$confirm('确认删除该服务器组吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.ServerGroupDelete(group.id).then(res => {
          this.$message.success('删除成功')
          this.loadGroups()
          if (this.groupDialogVisible) {
            api.GetGroupList().then(res => {
              this.groupList = res.data.data
            })
          }
        }).catch(err => {
          this.$message.error('删除失败：' + err.message)
        })
      }).catch(() => {
        this.$message.info('已取消删除')
      })
    },

    // 管理服务器
    manageServers(group) {
      this.currentGroup = group
      this.serverDialogVisible = true
      // this.loadGroupServers(group.id)
      api.ServerGroupList(group.id).then(res => {
        this.currentGroupServers = res.data.data
      })
    },

    // 添加新服务器
    addNewServer() {
      this.selectServerDialogVisible = true
      this.selectedServers = [] // 重置选中的服务器
      this.searchQuery = '' // 重置搜索关键词
      this.currentPage = 1 // 重置页码到第一页
      // 获取所有可选服务器，添加组ID和搜索关键字参数
      api.ServerAllList({
        group_id: this.currentGroup.id
      }).then(res => {
        if (res.data.data) {
          this.allServers = res.data.data
        } else {
          this.$message.warning('未获取到服务器数据')
          this.allServers = []
        }
      }).catch(err => {
        this.$message.error('获取服务器列表失败：' + err.message)
      })
    },

    // 编辑服务器
    editServer(server) {
      // TODO: 实现编辑服务器的逻辑
    },

    // 删除服务器
    removeServer(server) {
      this.$confirm('确认从该组中移除此服务器吗?', '提示', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        api.ServerRemove({
          group_id: this.currentGroup.id,
          server_id: server.id
        }).then(res => {
          this.$message.success('从组内移除服务器成功')
          this.manageServers(this.currentGroup)
        }).catch(err => {
          this.$message.error('移除服务器失败：' + err.message)
        })
      }).catch(() => {
        this.$message.info('已取消移除')
      })
    },

    // 处理服务器选择变化
    handleSelectionChange(selection) {
      this.selectedServers = selection
      console.log('已选择的服务器：', selection) // 添加日志便于调试
    },

    // 提交选中的服务器
    submitSelectedServers() {
      if (this.selectedServers.length === 0) {
        this.$message.warning('请至少选择一个服务器')
        return
      }

      const serverIds = this.selectedServers.map(server => server.id)
      api.AddServersToGroup({
        group_id: this.currentGroup.id,
        server_ids: serverIds
      }).then(res => {
        this.$message.success('添加服务器成功')
        this.selectServerDialogVisible = false
        // 重新加载当前组的服务器列表
        this.manageServers(this.currentGroup)
      }).catch(err => {
        this.$message.error('添加服务器失败：' + err.message)
      })
    },

    // 添加分页相关方法
    handleSizeChange(val) {
      this.pageSize = val
      this.currentPage = 1
    },

    handleCurrentChange(val) {
      this.currentPage = val
    },

    handleSearchConfirm() {
      // 当搜索关键字变化时重新请求服务器列表
      api.ServerAllList({
        group_id: this.currentGroup.id,
        search: this.searchQuery
      }).then(res => {
        if (res.data.data) {
          this.allServers = res.data.data
        }
      })
    },

    // 处理节点选中状态变化
    handleCheckChange(data, checked) {
      // checked.checkedNodes 包含所有选中的节点
      // checked.checkedKeys 包含所有选中节点的 key
      // checked.halfCheckedNodes 包含半选中的节点
      // checked.halfCheckedKeys 包含半选中节点的 key

      // 过滤出选中的服务器节点
      this.selectedNodes = checked.checkedNodes.filter(node => node.isServer).map(node => node.serverData)
      console.log('选中的服务器：', this.selectedNodes)
    },

    // 获取当前选中的所有服务器
    getSelectedServers() {
      return this.selectedNodes
    },

    // 处理组管理对话框关闭
    handleGroupDialogClose() {
      // 重新加载组和服务器数据
      this.loadGroups()
    }
  },
  beforeDestroy() {
    if (this.websocket) {
      this.websocket.close()
    }
  }
}
</script>

<style scoped>
.ansible-container {
  display: flex;
  height: 100%;
}

.server-list {
  width: 300px;
  border-right: 1px solid #dcdfe6;
  padding: 20px;
}

.task-execution {
  flex: 1;
  padding: 20px;
  display: flex;
  flex-direction: column;
}

.task-config {
  margin-bottom: 20px;
}

/* .task-output {
  flex: 1;
  background: #1e1e1e;
  color: #fff;
  padding: 10px;
  overflow-y: auto;
}

.task-output pre {
  margin: 0;
  white-space: pre-wrap;
} */

.group-manage-header {
  margin-bottom: 15px;
  padding: 10px;
  border-bottom: 1px solid #dcdfe6;
  text-align: left;
  position: sticky;
  top: 0;
  background-color: #fff;
  z-index: 1;
}

.group-dialog-content,
.server-dialog-content {
  padding: 10px;
}

.group-list-header {
  margin-bottom: 15px;
}

.search-bar .el-input-group__append {
  padding: 0;
  border: none;
  background-color: transparent;
}

.search-bar .el-input-group__append button {
  border: 1px solid #409EFF;
  border-left: none;
  height: 100%;
  margin: 0;
}

.search-bar .el-input__inner {
  border-right: none;
}

/* 添加一些自定义样式来优化显示效果 */
.el-tree-node__content {
  height: 32px;
}

.el-tree-node.is-current > .el-tree-node__content {
  background-color: #f5f7fa;
}
.task-output {
  /* margin: 10px 0; */
  .resizable-output {
    min-height: 100px;
    max-height: 500px;
    overflow-y: auto;
    padding: 10px;
    background: #1e1e1e;
    color: #fff;
    border-radius: 4px;
    white-space: pre-wrap;
    word-wrap: break-word;
    resize: vertical;
  }
}
</style>
