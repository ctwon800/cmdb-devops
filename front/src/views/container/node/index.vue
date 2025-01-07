<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @nodeDetail="nodeDetail"
      @nodeSchedule="nodeSchedule"
      @btnOrder="$message('按钮排序, order越小越靠前')"
      @nodeLabel="nodeLabel"
      @nodeDrain="nodeDrain"
      @nodeDelete="nodeDelete"
      @nodeTaint="nodeTaint"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <crud-toolbar
          :search.sync="crud.searchOptions.show"
          @refresh="doRefresh()"
          @columns-filter-changed="handleColumnsFilterChanged"
        />
      </div>
    </d2-crud-x>
    <el-dialog
      title="节点详情"
      :visible.sync="dialogNodeDetailVisible"
      width="80%"
      :modal-append-to-body="false"
    >
      <div v-if="Object.keys(nodeDetailData).length > 0" class="node-detail-dialog">
        <!-- 上半部分：显示 Pod 的总额度和使用量 -->
        <div class="pod-usage card">
          <div class="card-header">资源使用</div>
          <div class="card-body">
            <p><strong>容器组（已分配量/总额度）:</strong> {{ nodeDetailData.num_pods_running }} / {{ nodeDetailData.max_pods }}</p>
          </div>
          <div class="card-body">
            <p><strong>cpu（可分配额度/服务器总额度）:</strong> {{ nodeDetailData.cpu_allocatable_cores }} / {{ nodeDetailData.cpu_capacity_cores }}</p>
          </div>
          <div class="card-body">
            <p><strong>memory（可分配额度/服务器总额度，单位Mb）:</strong> {{ nodeDetailData.memory_allocatable_mb }} / {{ nodeDetailData.memory_capacity_mb }}</p>
          </div>
        </div>
        <!-- 下半部分：显示一个列表 -->
        <div class="pod-list card">
          <div class="card-header">容器组</div>
          <div class="card-body">
            <el-table :data="nodeDetailData.pod_list" style="width: 100%">
              <el-table-column prop="namespace" label="命名空间" />
              <el-table-column prop="pod_name" label="名称" />
              <el-table-column prop="status" label="状态" />
              <el-table-column prop="pod_ip" label="容器组ip" />
              <el-table-column prop="creation_time" label="创建时间" />
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button @click="expelPodAction(scope.row)" type="danger" size="small" icon="el-icon-delete">驱逐(平滑重启)</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogNodeDetailVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'调度配置 - ' + node_name"
      :visible.sync="dialogNodeScheduleVisible">
      <el-radio-group v-model="selectedNodeSchedule" style="justify-content: center; margin-top: 20px">
        <el-radio label="True">暂停调度</el-radio>
        <el-radio label="False">可调度</el-radio>
      </el-radio-group>
    <span slot="footer" class="dialog-footer">
      <el-button @click="submitNodeScheduleBotton" type="primary">提交</el-button>
      <el-button @click="dialogNodeScheduleVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'节点排水- ' + drainNodeName"
      :visible.sync="dialogNodeDrainVisible"
      width="30%">
      <span>请确定是否进行节点排水操作，确定的话会先暂停调度再进行排水。</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogNodeDrainVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitNodeDrainBotton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'节点移除- ' + deleteNodeName"
      :visible.sync="dialogNodeDeleteVisible"
      width="30%">
      <span>请确定是否进行节点移除操作，确定的话会先暂停调度排水最后移除节点。</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogNodeDeleteVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitNodeDeleteBotton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog :title="'节点标签管理 - ' + this.nodeNameLabel"
    :visible.sync="dialogNodeLablesVisible"
    width="60%">
      <el-table :data="nodeLabelData" style="width: 100%">
        <el-table-column prop="key" label="Key">
          <template slot-scope="scope">
            <el-input v-model="scope.row.key" placeholder="Key"></el-input>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Value">
          <template slot-scope="scope">
            <el-input v-model="scope.row.value" placeholder="Value"></el-input>
          </template>
        </el-table-column>
        <el-table-column label="删除">
          <template slot-scope="scope">
            <el-button @click="removeLabel(scope.$index)" type="danger" size="small">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" @click="addLabelRow">添加标签</el-button>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogNodeLablesVisible = false">取消</el-button>
        <el-button type="primary" @click="checkNodeLabelsChangeButton">保存</el-button>
      </div>
    </el-dialog>
    <el-dialog
      title="确认更新"
      :visible.sync="diffDialogVisible"
      width="80%"
      :modal-append-to-body="false"
    >
      <div>
        <CodeDiff
          :old-string=originalData
          :new-string=modifiedData
          output-format="side-by-side"
        />
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="submitNodeSaveLabels" type="primary">确认修改并提交</el-button>
        <el-button @click="diffDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="' 确定是否删除该  ' + label_key + '  标签'"
      :visible.sync="dialogNodelabelDeleteVisible"
      width="30%">
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogNodelabelDeleteVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitNodelabelDeletebutton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
    :title="'污点管理 - ' + this.nodeNameTaint"
    :visible.sync="dialogNodeTaintVisible">
      <span>请注意key和effect的值为必填项</span>
      <el-table :data="nodeTaintsData" style="width: 100%">
        <el-table-column prop="key" label="Key">
          <template slot-scope="scope">
            <el-input v-model="scope.row.key" placeholder="Key"></el-input>
          </template>
        </el-table-column>
        <el-table-column prop="value" label="Value">
          <template slot-scope="scope">
            <el-input v-model="scope.row.value" placeholder="Value"></el-input>
          </template>
        </el-table-column>
        <el-table-column label="Effect">
          <template slot-scope="scope">
            <el-select v-model="scope.row.effect" placeholder="Select effect">
              <el-option
                v-for="effect in effectOptions"
                :key="effect"
                :label="effect"
                :value="effect"
              ></el-option>
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="删除">
          <template slot-scope="scope">
            <el-button @click="removeTaintRow(scope.$index)" type="danger" size="small">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-button type="primary" @click="addTaintRow">添加污点</el-button>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogNodeTaintVisible = false">Cancel</el-button>
        <el-button type="primary" @click="submitNodeTaintsButton">Submit</el-button>
      </div>
    </el-dialog>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
import { CodeDiff } from 'v-code-diff'
// import { request } from '@/api/service'
export default {
  name: 'containers_node',
  mixins: [d2CrudPlus.crud],
  components: {
    CodeDiff
  },
  data () {
    return {
      dialogNodeDetailVisible: false, // 控制弹出框显示与隐藏
      nodeDetailData: {}, // 存储从接口返回的数据
      dialogNodeScheduleVisible: false,
      selectedNodeSchedule: null,
      node_name: '',
      dialogNodeDrainVisible: false,
      dialogNodeDeleteVisible: false,
      k8s_cluster_name: '123',
      dialogNodeLablesVisible: false,
      nodeLabelData: [],
      drainNodeName: '',
      deleteNodeName: '',
      nodeNameLabel: '',
      diffDialogVisible: false,
      originalData: '',
      modifiedData: '',
      clusterNameLabel: '',
      dialogNodelabelDeleteVisible: false,
      label_key: '',
      dialogNodeTaintVisible: false,
      nodeTaintsData: [],
      effectOptions: ['NoSchedule', 'NoExecute', 'PreferNoSchedule'],
      nodeNameTaint: ''
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
    getNamespaceList() {
      api.GetNamespace().then(res => {
        this.namespaceList = res.data.data
      })
    },
    nodeDetail({ row }) {
      const nodeName = row.node_name
      const clusterName = row.cluster_name
      this.clusterName = row.cluster_name
      api.GetNodeDetail(nodeName, clusterName).then(response => {
        this.nodeDetailData = response.data
        this.dialogNodeDetailVisible = true
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    expelPodAction(row) {
      row.cluster_name = this.clusterName
      console.log(row)
      api.NodeEvictionPod(row).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
      }).catch(error => {
        console.error('Error evicting pod:', error)
      })
    },
    nodeSchedule({ row }) {
      this.dialogNodeScheduleVisible = true
      this.selectedNodeSchedule = row.node_schedule
      this.cluster_name = row.cluster_name
      this.node_name = row.node_name
      this.default_node_schedule = this.selectedNodeSchedule
    },
    submitNodeScheduleBotton() {
      if (this.selectedNodeSchedule === this.default_node_schedule) {
        this.dialogNodeScheduleVisible = false
        return this.$message({
          showClose: true,
          message: '没有修改',
          type: 'success'
        })
      }
      const obj = {
        node_name: this.node_name,
        node_status: this.selectedNodeSchedule,
        cluster_name: this.cluster_name
      }
      console.log(this.selectedNodeSchedule)
      this.dialogNodeScheduleVisible = false
      api.NodeSetSchedule(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.doRefresh()
      }).catch(error => {
        console.error('Error set node schedule:', error)
      })
    },
    nodeDrain({ row }) {
      this.dialogNodeDrainVisible = true
      this.drainNodeName = row.node_name
      this.drainClusterName = row.cluster_name
    },
    submitNodeDrainBotton() {
      api.NodeDrain(this.drainNodeName, this.drainClusterName).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.dialogNodeDrainVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error set node drain:', error)
      })
    },
    nodeDelete({ row }) {
      this.dialogNodeDeleteVisible = true
      this.deleteNodeName = row.node_name
      this.deleteClusterName = row.cluster_name
    },
    submitNodeDeleteBotton() {
      api.NodeDelete(this.deleteNodeName, this.deleteClusterName).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.dialogNodeDeleteVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error set node delete:', error)
      })
    },
    nodeLabel({ row }) {
      const nodeName = row.node_name
      const clusterName = row.cluster_name
      this.nodeNameLabel = row.node_name
      this.clusterNameLabel = row.cluster_name
      api.GetNodeLabel(nodeName, clusterName).then(response => {
        this.nodeLabelData = Object.entries(response.data).map(([key, value]) => ({ key, value }))
        this.dialogNodeLablesVisible = true
        this.defaultNodeLabelsData = response.data
      }).catch(error => {
        console.error('Error fetching node label:', error)
      })
    },
    removeLabel(index) {
      // print(index)
      this.label_key = this.nodeLabelData[index].key
      console.log(this.label_key)
      this.dialogNodelabelDeleteVisible = true
      // this.nodeLabelData.splice(index, 1)
    },
    submitNodelabelDeletebutton() {
      const obj = {
        node_name: this.nodeNameLabel,
        cluster_name: this.clusterNameLabel,
        label_key: this.label_key
      }
      api.DeleteNodeLabel(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.dialogNodelabelDeleteVisible = false
        this.dialogNodeLablesVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error delete node label:', error)
      })
    },
    addLabelRow() {
      this.nodeLabelData.push({ key: '', value: '' })
    },
    checkNodeLabelsChangeButton() {
      this.diffDialogVisible = true
      this.originalData = JSON.stringify(this.defaultNodeLabelsData, null, 2)
      this.modifiedData = JSON.stringify(
        this.nodeLabelData.reduce((acc, { key, value }) => {
          acc[key] = value
          return acc
        }, {}), null, 2)
    },
    submitNodeSaveLabels() {
      const obj = {
        node_name: this.nodeNameLabel,
        cluster_name: this.clusterNameLabel,
        new_labels: this.modifiedData
      }
      api.UpdateNodeLabel(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.diffDialogVisible = false
        this.dialogNodeLablesVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update node label', error)
      })
    },
    nodeTaint({ row }) {
      const nodeName = row.node_name
      const clusterName = row.cluster_name
      this.nodeNameTaint = row.node_name
      this.clusterNameTaint = row.cluster_name
      api.GetNodeTaint(nodeName, clusterName).then(response => {
        this.nodeTaintsData = response.data
        this.dialogNodeTaintVisible = true
      }).catch(error => {
        console.error('Error fetching node label:', error)
      })
    },
    addTaintRow() {
      this.nodeTaintsData.push({ key: '', value: '', effect: '' })
    },
    removeTaintRow(index) {
      this.nodeTaintsData.splice(index, 1)
    },
    submitNodeTaintsButton() {
      const obj = {
        node_name: this.nodeNameTaint,
        cluster_name: this.clusterNameTaint,
        new_taints: this.nodeTaintsData
      }
      api.UpdateNodeTaint(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
        this.dialogNodeTaintVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update node taints:', error)
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
.node-detail-dialog {
  .pod-usage, .pod-list {
    margin: 20px 0;
  }
}

.card {
  background: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  &-header {
    font-size: 16px;
    font-weight: 600;
    padding: 10px 16px;
    background-color: #f5f7fa;
    border-bottom: 1px solid #ebeef5;
  }

  &-body {
    padding: 16px;
    font-size: 14px;
    line-height: 24px;
  }
}
</style>
