<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @serviceEdit="serviceEdit"
      @serviceYaml="serviceYaml"
      @serviceDelete="serviceDelete"
      @serviceDetail="serviceDetail"
      @btnOrder="$message('按钮排序，order越小越靠前')"
    >
      <div slot="header">
        <crud-search
          ref="search"
          :options="crud.searchOptions"
          @submit="handleSearch"
        />
        <el-button-group>
          <el-button
            type="primary"
            size="small"
            icon="el-icon-plus"
            @click="createServiceButton"
          >创建</el-button>
          <el-button
            type="warning"
            size="small"
            icon="el-icon-edit"
            @click="createServiceYamlButton"
          >YAML</el-button>
        </el-button-group>
        <crud-toolbar
          :search.sync="crud.searchOptions.show"
          :compact.sync="crud.pageOptions.compact"
          :columns="crud.columns"
          @refresh="doRefresh()"
          @columns-filter-changed="handleColumnsFilterChanged"
        />
      </div>
      <template slot="service_portSlot" slot-scope="scope">
        <div v-for="(value, index) in scope.row.service_port" :key="index">
            {{ value.port }}  {{ value.node_port }}  {{ value.protocol }}
            <br/>
        </div>
      </template>
    </d2-crud-x>
    <el-dialog
      :title="serviceDetailData.name"
      :visible.sync="dialogServiceDetailVisible"
      width="80%"
      :modal-append-to-body="false"
    >
      <div v-if="Object.keys(serviceDetailData).length > 0" class="service-detail-dialog">
        <!-- 上半部分：显示 Pod 的总额度和使用量 -->
        <div class="card">
          <div class="card-header">基本信息</div>
          <div class="card-body">
            <table class="table table-bordered">
              <tbody>
                <!-- 第一行 -->
                <tr>
                  <td style="width: 50%;">
                    <span>名称:  </span>
                    <span>{{ serviceDetailData.name }}</span>
                  </td>
                  <td style="width: 50%;">
                    <span>命名空间:  </span>
                    <span>{{ serviceDetailData.namespace }}</span>
                  </td>
                </tr>
                <tr>
                  <td style="width: 50%;">
                    <span>服务类型:  </span>
                    <span>{{ serviceDetailData.type }}</span>
                  </td>
                  <td style="width: 50%;">
                    <span>创建时间:   </span>
                    <span>{{ serviceDetailData.creat_time }}</span>
                  </td>
                </tr>
                <tr>
                  <td style="width: 50%;">
                    <span>选择器:  </span>
                    <span class="selector-list">
                      <tr>
                        <div v-for="(value, key) in serviceDetailData.selector"  :key="key">
                          <template>
                            <td>{{ key }}: {{ value }}</td>
                          </template>
                        </div>
                      </tr>
                    </span>
                  </td>
                  <td style="width: 50%;">
                    <span>标签: </span>
                    <span>
                      <tr>
                        <div v-for="(value, key) in serviceDetailData.label" :key="key">
                        <template>
                          <td>{{ key }}: {{ value }}</td>
                        </template>
                        </div>
                      </tr>
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style="width: 50%;">
                    <span>端口: </span>
                    <span>
                      <div v-for="(port, index) in serviceDetailData.port" :key="index">
                        <table>
                          <tr v-if="port.name">
                            <td>名称: {{ port.name }}</td>
                          </tr>
                          <tr v-if="port.protocol">
                            <td>协议: {{ port.protocol }}</td>
                          </tr>
                          <tr v-if="port.port">
                            <td>端口: {{ port.port }}</td>
                          </tr>
                          <tr v-if="port.target_port">
                            <td>目标端口: {{ port.target_port }}</td>
                          </tr>
                          <tr v-if="port.node_port">
                            <td>节点端口: {{ port.node_port }}</td>
                          </tr>
                        </table>
                        <br>
                      </div>
                    </span>
                  </td>
                  <td style="width: 50%;">
                    <span>服务IP:   </span>
                    <span>{{ serviceDetailData.cluster_ip }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentDetailVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'预览/编辑YAML - ' + yamlServiceName"
      :visible.sync="dialogServiceYamlVisible"
      width="80%"
      class="d2p-code-dialog"
      >
      <div>
        <el-button
        slot="title"
        @click="toggleEditMode"
        type="primary"
        style="position: absolute; top: 10px; right: 10px;"
        >
          {{ editMode ? '取消' : '编辑' }}
        </el-button>
        <pre class="code-container" ref="codeContainer">
<code>{{ serviceYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button v-if="editMode" @click="checkServiceYamlBotton" type="primary">提交</el-button>
        <el-button @click="dialogServiceYamlVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认更新- ' + yamlServiceName"
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
        <el-button v-if="editMode" @click="submitServiceYamlBotton" type="primary">确认修改并提交</el-button>
        <el-button @click="diffDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认是否删除该service - ' + deleteServiceName"
      :visible.sync="dialogServiceDeleteCheckVisible"
      width="40%">
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogServiceDeleteCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitServiceDeleteButton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="isEditing ? '修改服务' : '创建服务'"
      :visible.sync="dialogCreateServiceVisible"
      width="80%"
      @close="handleCloseCreateServcice">
      <div>
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
          <span style="width: 120px;">名称：</span>
          <el-input v-model="serviceForm.name" placeholder="请输入Service名称" style="width: 300px; padding-left: 10px;"></el-input>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
          <span style="width: 120px;">注解：</span>
          <div>
            <el-button type="primary" @click="addAnnotation" size="small" style="margin-left: 10px;">添加</el-button>
          </div>
        </div>
        <div style="margin-top: 10px; margin-left: 120px;">
          <div>
            <el-form :model="serviceForm.annotations">
              <div v-for="(key, index) in annotationsKeys" :key="index" class="annotation-row">
                <el-form-item>
                  <el-input v-model="annotationsKeys[index]" placeholder="请输入注解值键" style="width: 400px; padding-left: 10px;" />
                  <el-input v-model="serviceForm.annotations[key]" :placeholder="请输入注解值" style="width: 300px; padding-left: 20px;" />
                  <el-button
                  style="margin-left: 20px;"
                  type="danger"
                  icon="el-icon-delete" circle
                  @click="removeAnnotation(index)">
                  </el-button>
                </el-form-item>
              </div>
            </el-form>
          </div>
        </div>
      </div>
      <div style="display: flex; align-items: center; margin-top: 10px;">
          <span style="width: 120px;">标签：</span>
          <div>
            <el-button type="primary" @click="addLabel" size="small" style="margin-left: 10px;">添加</el-button>
          </div>
      </div>
      <div style="margin-top: 10px; margin-left: 120px;">
        <el-form :model="serviceForm.label">
          <div v-for="(key, index) in labelKeys" :key="index" class="tag-row">
            <el-form-item style="display: flex; align-items: center; margin-bottom: 10px;">
              <el-input v-model="labelKeys[index]" placeholder="请输入标签键" style="width: 400px; padding-left: 10px;" />
              <el-input v-model="serviceForm.label[key]" placeholder="请输入标签值" style="width: 300px; padding-left: 20px;" />
              <el-button
                style="margin-left: 20px;"
                type="danger"
                icon="el-icon-delete" circle
                @click="removeLabel(index)">
              </el-button>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <div style="display: flex; align-items: center;">
        <span style="width: 120px;">服务类型：</span>
        <el-select v-model="serviceForm.service_type" placeholder="请选择服务类型" style="width: 300px; padding-left: 10px;">
          <el-option label="ClusterIP" value="ClusterIP"></el-option>
          <el-option label="NodePort" value="NodePort"></el-option>
        </el-select>
      </div>
      <div style="display: flex; align-items: center; margin-top: 10px;">
          <span style="width: 120px;">服务选择器：</span>
          <div>
            <el-button type="primary" @click="addSelector" size="small" style="margin-left: 10px;">添加</el-button>
            <el-button type="primary" @click="insertWorkloadLabels" size="small" style="margin-left: 10px;">引入工作负载标签</el-button>
          </div>
      </div>
      <div style="margin-top: 10px; margin-left: 120px;">
        <el-form :model="serviceForm.selector">
          <div v-for="(key, index) in selectorKeys" :key="index" class="tag-row">
            <el-form-item style="display: flex; align-items: center; margin-bottom: 10px;">
              <el-input v-model="selectorKeys[index]" placeholder="请输入标签键" style="width: 400px; padding-left: 10px;" />
              <el-input v-model="serviceForm.selector[key]" placeholder="请输入标签值" style="width: 300px; padding-left: 20px;" />
              <el-button
                style="margin-left: 20px;"
                type="danger"
                icon="el-icon-delete" circle
                @click="removeSelector(index)">
              </el-button>
            </el-form-item>
          </div>
        </el-form>
      </div>
      <div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 10px;">
        <span style="width: 120px;">端口映射：</span>
        <div>
          <el-button type="primary" @click="addPortMaps(serviceForm.portMaps)" size="small" style="margin-left: 10px;">添加</el-button>
        </div>
      </div>
      <div style="margin-top: 10px; margin-left: 120px;">
        <div v-for="(portMap, portMapIndex) in serviceForm.portMaps" :key="portMapIndex">
          <el-form>
            <el-form-item label="" style="display: flex; align-items: center; margin-bottom: 10px; margin-left: 40px;">
              <el-input v-model="portMap.name" placeholder="服务名称" style="width: 150px; margin-right: 0px;"></el-input>
              <el-select v-model="portMap.protocol" placeholder="请选择协议" style="width: 100px; padding-left: 10px;">
                <el-option label="TCP" value="TCP"></el-option>
                <el-option label="UDP" value="UDP"></el-option>
              </el-select>
              <el-input v-model="portMap.port" placeholder="服务端口" style="width: 150px; margin-right: 10px; padding-left: 10px;"></el-input>
              <el-input v-model="portMap.target_port" placeholder="容器端口" style="width: 150px; margin-right: 10px;"></el-input>
              <el-input v-if="serviceForm.service_type === 'NodePort'" v-model="portMap.node_port" placeholder="NodePort端口" style="width: 100px; margin-right: 10px;"></el-input>
              <el-button v-if="serviceForm.portMaps.length > 1" type="danger" icon="el-icon-delete" circle style="margin-left: 10px;" @click="removePortMaps(serviceForm.portMaps, portMapIndex)"></el-button>
            </el-form-item>
          </el-form>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogCreateServiceVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitCreateServiceButton">提 交</el-button>
      </span>
    </el-dialog>
    <el-dialog title="选择器" :visible.sync="dialogWorkloadSelectorVisible" width="500px">
      <el-form>
        <el-form-item label="workloadName">
          <el-select v-model="workloadSelector" placeholder="请选择">
            <el-option v-for="(selectors, workload) in workloadSelectorOptions" :key="workload" :label="workload" :value="workload">
            </el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="Selectors">
          <el-tag v-for="(value, key) in workloadSelectorOptions[workloadSelector]" :key="key">{{ key }}: {{ value }}</el-tag>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click="dialogWorkloadSelectorVisible = false">取消</el-button>
        <el-button type="primary" @click="insertSelectorsSubmit">确认</el-button>
      </div>
    </el-dialog>
    <el-dialog
      :title="'创建YAML - '"
      :visible.sync="dialogCreateServiceYamlVisible"
      width="80%"
      class="d2p-code-dialog"
      >
      <div>
        <pre class="code-container" ref="codeContainer">
<code>{{ createServiceYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="submitServiceYamlButton" type="primary">提交</el-button>
        <el-button @click="dialogCreateServiceYamlVisible = false">关闭</el-button>
      </span>
    </el-dialog>
  </d2-container>
</template>
<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
import { CodeDiff } from 'v-code-diff'

export default {
  name: 'containers_service',
  mixins: [d2CrudPlus.crud],
  components: {
    CodeDiff
  },
  data () {
    return {
      dialogServiceYamlVisible: false,
      editMode: false,
      yamlServiceName: '',
      yamlClusterName: '',
      yamlNamespace: '',
      selectedClusterName: '',
      selectedNamespace: '',
      serviceYamlData: '',
      defaultYamlServiceData: '',
      modifiedData: '',
      diffDialogVisible: false,
      originalData: '',
      dialogServiceDeleteCheckVisible: false,
      deleteServiceName: '',
      dialogServiceDetailVisible: false,
      serviceDetailData: {},
      dialogCreateServiceVisible: false,
      isEdit: false,
      serviceForm: {
        name: '',
        annotations: {},
        label: {},
        service_type: '',
        selector: {},
        portMaps: [{
          name: '',
          port: '',
          target_port: '',
          protocol: '',
          node_port: ''
        }]
      },
      labelKeys: [],
      selectorKeys: [],
      annotationsKeys: [],
      isEditing: false,
      annotationsOptions: [],
      currentPlaceholders: [''],
      selectedKey: '',
      service_type: ['ClusterIP', 'NodePort'],
      dialogWorkloadSelectorVisible: false,
      workloadSelector: '',
      workloadSelectorOptions: {},
      mySelectorKeys: [],
      dialogCreateServiceYamlVisible: false,
      createServiceYamlData: ''
    }
  },
  mounted () {
  },
  methods: {
    getCrudOptions () {
      // this.crud.searchOptions.form
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    serviceDetail({ row }) {
      this.dialogServiceDetailVisible = true
      const serviceName = row.service_name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetServiceDetail(serviceName, clusterName, namespace).then(response => {
        this.serviceDetailData = response.data.data
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    serviceYaml ({ row }) {
      this.dialogServiceYamlVisible = true
      this.editMode = false
      this.yamlServiceName = row.service_name
      this.yamlClusterName = row.cluster_name
      this.yamlNamespace = row.namespace
      console.log('1111')
      api.GetServiceYaml(this.yamlServiceName, this.yamlClusterName, this.yamlNamespace).then(response => {
        this.serviceYamlData = response.data.data
        this.defaultYamlServiceData = this.serviceYamlData
        this.$nextTick(() => {
          this.$refs.codeContainer.style.backgroundColor = 'white' // Reset background
          this.$refs.codeContainer.style.color = 'black'
          this.$refs.codeContainer.contentEditable = false // Disable editing
          this.$refs.codeContainer.innerText = this.defaultYamlServiceData
        })
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    checkServiceYamlBotton() {
      this.serviceYamlData = this.$refs.codeContainer.innerText
      this.originalData = this.defaultYamlServiceData
      this.modifiedData = this.serviceYamlData
      this.diffDialogVisible = true
    },
    submitServiceYamlBotton() {
      const obj = {
        service_name: this.yamlServiceName,
        cluster_name: this.yamlClusterName,
        namespace: this.yamlNamespace,
        yaml_data: this.modifiedData
      }
      api.ServiceYamlUpdate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.diffDialogVisible = false
        this.dialogServiceYamlVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update service yaml:', error)
      })
    },
    toggleEditMode() {
      this.editMode = !this.editMode
      console.log(this.editMode)
      if (this.editMode) {
        this.defaultYamlServiceData = this.serviceYamlData
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true

        this.$refs.codeContainer.innerText = this.serviceYamlData
      } else {
        this.$refs.codeContainer.style.backgroundColor = '' // Reset background
        this.$refs.codeContainer.style.color = 'black'
        this.$refs.codeContainer.contentEditable = false // Disable editing
        this.serviceYamlData = this.defaultYamlServiceData
        this.$refs.codeContainer.innerText = this.defaultYamlServiceData
      }
    },
    serviceDelete({ row }) {
      this.deleteServiceName = row.service_name
      this.deleteClusterName = row.cluster_name
      this.deleteNamaspace = row.namespace
      this.dialogServiceDeleteCheckVisible = true
    },
    submitServiceDeleteButton({ row }) {
      api.ServiceDelete({
        cluster_name: this.deleteClusterName,
        namespace: this.deleteNamaspace,
        service_name: this.deleteServiceName
      }).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
      })
      this.dialogServiceDeleteCheckVisible = false
      this.doRefresh()
    },
    createServiceButton() {
      this.isEditing = false
      this.dialogCreateServiceVisible = true
      this.serviceForm.service_type = 'ClusterIP'
    },
    handleCloseCreateServcice() {
      this.serviceForm = {
        name: '',
        annotations: {},
        label: {},
        service_type: '',
        selector: {},
        portMaps: [{
          name: '',
          port: '',
          target_port: '',
          protocol: '',
          node_port: ''
        }]
      }
    },
    addAnnotation() {
      this.annotationsKeys.push("")
    },
    removeAnnotation(index) {
      const key = this.annotationsKeys[index]
      this.$delete(this.serviceForm.annotations, key)
      this.annotationsKeys.splice(index, 1)
    },
    addLabel() {
      this.labelKeys.push("") // 只在 labelKeys 中添加空 key
    },
    removeLabel(index) {
      const key = this.labelKeys[index]
      this.$delete(this.serviceForm.label, key)
      this.labelKeys.splice(index, 1) // 从 keys 数组中删除
    },
    addSelector() {
      this.selectorKeys.push("") // 只在 labelKeys 中添加空 key
    },
    removeSelector(index) {
      const key = this.selectorKeys[index]
      this.$delete(this.serviceForm.selector, key)
      this.selectorKeys.splice(index, 1) // 从 keys 数组中删除
    },
    insertWorkloadLabels() {
      console.log('123')
      console.log(this.selectedNamespace)
      console.log(this.selectedClusterName)
      this.dialogWorkloadSelectorVisible = true
      api.GetDepLabels(this.selectedClusterName, this.selectedNamespace).then(response => {
        this.workloadSelectorOptions = response.data.data
      })
    },
    insertSelectorsSubmit() {
      console.log('123')
      const mySelectorKeys = this.workloadSelectorOptions[this.workloadSelector]
      this.dialogWorkloadSelectorVisible = false
      if (this.mySelectorKeys) {
        Object.keys(mySelectorKeys).forEach((key) => {
          this.selectorKeys.push(key)
          this.$set(this.serviceForm.selector, key, mySelectorKeys[key])
        })
      }
      this.dialogWorkloadSelectorVisible = false
    },
    addPortMaps(portMaps) {
      console.log('222')
      portMaps.push({
        port_name: '',
        service_port: '',
        container_port: '',
        protocol: ''
      })
    },
    removePortMaps(portMaps, portMapIndex) {
      console.log('123')
      portMaps.splice(portMapIndex, 1)
    },
    submitCreateServiceButton() {
      if (this.isEditing) {
        this.serviceForm.change_type = 'update'
      } else {
        this.serviceForm.change_type = 'create'
      }
      this.serviceForm.cluster_name = this.selectedClusterName
      this.serviceForm.namespace = this.selectedNamespace
      api.ServiceChange(this.serviceForm).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogCreateServiceVisible = false
        this.doRefresh()
      })
    },
    createServiceYamlButton() {
      console.log('123')
      this.dialogCreateServiceYamlVisible = true
      this.$nextTick(() => {
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true
        this.$refs.codeContainer.innerText = this.createServiceYamlData
      })
    },
    submitServiceYamlButton() {
      console.log(this.selectedClusterName)
      console.log(this.selectedNamespace)
      this.serviceYamlData = this.$refs.codeContainer.innerText
      const obj = {
        cluster_name: this.selectedClusterName,
        namespace: this.selectedNamespace,
        yaml_data: this.serviceYamlData
      }
      api.ServiceYamlCreate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogCreateServiceYamlVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update service yaml:', error)
      })
    },
    serviceEdit({ row }) {
      this.isEditing = true
      this.dialogCreateServiceVisible = true
      const serviceName = row.service_name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetServiceDetail(serviceName, clusterName, namespace).then(response => {
        this.serviceForm = response.data.data
        this.serviceForm.service_type = response.data.data.type
        this.serviceForm.portMaps = response.data.data.port
        this.serviceForm.annotations = response.data.data.annotations
        this.annotationsKeys = Object.keys(response.data.data.annotations)
        this.labelKeys = Object.keys(response.data.data.label)
        this.selectorKeys = Object.keys(response.data.data.selector)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.yxtInput {
  .el-form-item__label {
    color: #49a1ff;
  }
}

.d2p-code-dialog .code-container-wrapper {
  background-color: #000000; /* 设置背景颜色为黑色 */
  color: #ffffff; /* 设置字体颜色为白色 */
  padding: 20px;
  border-radius: 8px;
}

.d2p-code-dialog .code-container {
  white-space: pre-wrap; /* 自动换行 */
  word-wrap: break-word; /* 长单词换行 */
  color: #ffffff; /* 代码字体颜色 */
  background-color: #000000; /* 代码容器背景颜色 */
  padding: 15px;
  border-radius: 5px;
  overflow-y: auto;
  height: calc(1.2em * 20);
  // max-height: 500px; /* 控制高度，防止内容太长 */
  font-family: monospace; /* 使用等宽字体 */
}

.d2p-code-dialog code {
  color: #ffffff; /* 确保 <code> 标签内字体也是白色 */
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
    overflow-y: auto;
    font-size: 14px;
    line-height: 24px;
  }

  .service-detail-dialog .card {
    border: 1px solid #ddd;
    border-radius: 0.25rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }
  .service-detail-dialog .card-header {
    font-weight: bold;
    background-color: #f7f7f7;
  }
  .service-detail-dialog .card-body {
    padding: 1rem;
  }
  .service-detail-dialog .info-item {
    padding: 0.5rem;
    border-bottom: 1px solid #ddd;
  }
  .service-detail-dialog .list-group-item {
    border: none;
    padding: 0.5rem;
  }
  .table {
    width: 100%;
    border-collapse: collapse; /* 边框重叠 */
  }
  .table-bordered {
    border: 1px solid #ddd; /* 添加表格边框 */
  }
  .table td, .table th {
    border: 1px solid #ddd; /* 添加单元格边框 */
    padding: 8px;
  }
  .selector-list {
    list-style-type: none; /* 去掉列表项的默认符号 */
    padding: 0; /* 去掉列表的 padding */
  }

  .code-container {
      position: relative;
      overflow: auto;
      max-height: 400px; /* Adjust max height as needed */
      overflow-y: auto;
      overflow-x: auto;
      white-space: pre-wrap;
      padding: 1em;
      line-height: 1.5;
      counter-reset: line;
  }

.code-container {
      position: relative;
      overflow: auto;
      max-height: 400px; /* Adjust max height as needed */
      overflow-y: auto;
      overflow-x: auto;
      white-space: pre-wrap;
      padding: 1em;
      line-height: 1.5;
      counter-reset: line;
  }
}
</style>
