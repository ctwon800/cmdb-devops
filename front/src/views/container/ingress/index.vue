<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @ingressYaml="ingressYaml"
      @ingressDelete="ingressDelete"
      @ingressDetail="ingressDetail"
      @ingressEdit="ingressEdit"
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
            @click="createIngressButton"
          >创建</el-button>
          <el-button
            type="warning"
            size="small"
            icon="el-icon-edit"
            @click="createIngressYamlButton"
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
      <template slot="rulesSlot" slot-scope="scope">
        <div v-for="(value, index) in scope.row.rules" :key="index">
            {{ value.host }}
            <br/>
        </div>
      </template>
    </d2-crud-x>
    <el-dialog
      :title="ingressDetailData.name"
      :visible.sync="dialogIngressDetailVisible"
      width="80%"
      :modal-append-to-body="false"
    >
      <div v-if="Object.keys(ingressDetailData).length > 0" class="ingress-detail-dialog">
        <!-- 上半部分：显示 Pod 的总额度和使用量 -->
        <div class="card">
          <div class="card-header">基本信息</div>
          <div class="card-body">
            <table class="table table-bordered" style="width: 100%;">
              <tbody>
                <tr>
                  <td>
                    <span>名称:  </span>
                    <span>{{ ingressDetailData.name }}</span>
                  </td>
                  <td>
                    <span>命名空间:  </span>
                    <span>{{ ingressDetailData.namespace }}</span>
                  </td>
                </tr>
                <tr>
                  <td>
                    <span>负载均衡IP:  </span>
                    <span>{{ ingressDetailData.load_balancer }}</span>
                  </td>
                  <td>
                    <span>创建时间:   </span>
                    <span>{{ ingressDetailData.creation_timestamp }}</span>
                  </td>
                </tr>
                <tr>
                  <td  colspan="2">
                    <span>注解：</span>
                    <div v-for="(value, key) in ingressDetailData.annotations" :key="key"  style="padding-left: 20px;">
                      <template>
                        <span>{{ key }}:  {{ value }}</span>
                      </template>
                      </div>
                  </td>
                </tr>
                <tr>
                  <td colspan="2">
                    <span>路由: </span>
                    <span>
                      <div v-for="(rules, index) in ingressDetailData.rules" :key="index">
                        <table style="width: 100%; padding-left: 20px;">
                            <strong>域名：{{ rules.host }} </strong><br>
                            <strong>路由配置： </strong>
                            <!-- <div v-for="(paths, index) in rules.paths" :key="index"> -->
                              <table style="width: 100%; padding-left: 0px;">
                                <tr>
                                  <th style="text-align: left;">匹配类型</th>
                                  <th style="text-align: left;">路径映射</th>
                                  <th style="text-align: left;">后端服务</th>
                                  <th style="text-align: left;">后端服务端口</th>
                                </tr>
                                <tr v-for="(paths, index) in rules.paths" :key="index" style="padding-left: 40px;">
                                  <td>{{ paths.path_type }}</td>
                                  <td>{{ paths.path }}</td>
                                  <td>{{ paths.backend.service_name }}</td>
                                  <td>{{ paths.backend.service_port }}</td>
                                </tr>
                              </table>
                            <!-- </div> -->
                        </table>
                        <br>
                      </div>
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogIngressDetailVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'预览/编辑YAML - ' + yamlIngressName"
      :visible.sync="dialogIngressYamlVisible"
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
<code>{{ ingressYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button v-if="editMode" @click="checkIngressYamlBotton" type="primary">提交</el-button>
        <el-button @click="dialogIngressYamlVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认更新- ' + yamlIngressName"
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
        <el-button v-if="editMode" @click="submitIngressYamlBotton" type="primary">确认修改并提交</el-button>
        <el-button @click="diffDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认是否删除该Ingress - ' + deleteIngressName"
      :visible.sync="dialogIngressDeleteCheckVisible"
      width="40%">
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogIngressDeleteCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitIngressDeleteButton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="isEditing ? '修改应用路由' : '创建应用路由'"
      :visible.sync="dialogCreateIngressVisible"
      width="80%"
      @close="handleClose">
      <div>
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
          <span style="width: 120px;">名称：</span>
          <el-input v-model="ingressForm.name" placeholder="请输入Ingress名称" style="width: 300px; padding-left: 10px;"></el-input>
        </div>
        <div style="display: flex; align-items: center;">
          <span style="width: 120px;">Ingress Class:</span>
          <el-select v-model="ingressForm.ingress_class_name" placeholder="请选择Ingress类型" style="width: 300px; padding-left: 10px;">
            <el-option
              v-for="item in ingress_class_names"
              :key="item"
              :label="item"
              :value="item">
            </el-option>
          </el-select>
        </div>
        <div style="display: flex; align-items: center; margin-top: 10px;">
          <span style="width: 120px;">注解：</span>
          <div>
            <el-button type="primary" @click="addAnnotation" size="small" style="margin-left: 10px;">添加</el-button>
          </div>
        </div>
        <div style="margin-top: 10px; margin-left: 120px;">
          <div>
            <el-form :model="ingressForm.annotations">
              <div v-for="(key, index) in annotationsKeys" :key="index" class="annotation-row">
                <el-form-item>
                  <el-select v-model="annotationsKeys[index]" placeholder="请选择或输入注解键" @change="updatePlaceholder(index)" style="width: 400px; padding-top: 0px; padding-left: 10px;" clearable filterable allow-create>
                    <el-option
                      v-for="(value, index) in annotationsOptions"
                      :key="index"
                      :label="index"
                      :value="index">
                    </el-option>
                  </el-select>
                  <el-input v-model="ingressForm.annotations[key]" :placeholder="currentPlaceholders[index]" style="width: 300px; padding-left: 20px;" />
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
        <el-form :model="ingressForm.labels">
          <div v-for="(key, index) in labelKeys" :key="index" class="tag-row">
            <el-form-item style="display: flex; align-items: center; margin-bottom: 10px;">
              <el-input v-model="labelKeys[index]" placeholder="请输入标签键" style="width: 400px; padding-left: 10px;" />
              <el-input v-model="ingressForm.labels[key]" placeholder="请输入标签值" style="width: 300px; padding-left: 20px;" />
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
      <div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 10px;">
        <span style="width: 120px;">TLS：</span>
        <div>
          <el-button type="primary" @click="addTLS" size="small" style="margin-left: 10px;">添加</el-button>
        </div>
      </div>
      <div style="margin-top: 10px; margin-left: 120px;">
        <div v-for="(tls, tlsIndex) in ingressForm.tls" :key="tlsIndex">
          <el-input v-model="tls.host" placeholder="请输入域名" style="width: 300px; padding-left: 10px;"></el-input>
          <el-select v-model="tls.secret_name" placeholder="请选择TLS Secret" style="width: 300px; padding-left: 10px;">
            <el-option
              v-for="secret in tlsSecrets"
              :key="secret"
              :label="secret"
              :value="secret">
            </el-option>
          </el-select>
          <el-button v-if="ingressForm.tls.length > 0" type="danger" icon="el-icon-delete" circle style="margin-left: 10px;" @click="removeTLS(tlsIndex)"></el-button>
        </div>
      </div>
      <div style="display: flex; align-items: center; margin-bottom: 10px; margin-top: 10px;">
        <span style="width: 120px;">路由规则：</span>
        <div>
          <el-button type="primary" @click="addRule" size="small" style="margin-left: 10px;">添加</el-button>
        </div>
      </div>
      <div style="margin-top: 10px; margin-left: 120px;">
        <div v-for="(rule, ruleIndex) in ingressForm.rules" :key="ruleIndex">
          <el-card shadow="always" style="margin-bottom: 20px; position: relative;">
            <el-button
              v-if="ingressForm.rules.length > 1"
              type="danger"
              icon="el-icon-delete"
              circle
              style="position: absolute; top: 10px; right: 10px; z-index: 10;"
              @click="removeRule(ruleIndex)">
            </el-button>
            <el-form>
              <el-form-item label="">
                <el-input v-model="rule.host" placeholder="请输入域名" style="width: 300px; padding-left: 10px;"></el-input>
                <!-- <el-switch
                  v-model="rule.tlsEnabled"
                  active-text="TLS 启用"
                  inactive-text="TLS 禁用"
                  style="margin-left: 20px;"
                  @change="updateTlsList(ruleIndex)">
                </el-switch>
                  <el-select v-if="rule.tlsEnabled" placeholder="请选择TLS Secret" style="width: 300px; padding-left: 10px;">
                    <el-option
                      v-for="secret in tlsSecrets"
                      :key="secret"
                      :label="secret"
                      :value="secret">
                    </el-option>
                  </el-select> -->
              </el-form-item>
            </el-form>
            <el-button type="primary" @click="addRulePath(rule)" size="mini" style="display: flex; align-items: center; margin-bottom: 10px; margin-left: 40px;">添加路径映射</el-button>
            <div v-for="(path, pIndex) in rule.paths" :key="pIndex">
              <el-form>
                <el-form-item label="" style="display: flex; align-items: center; margin-bottom: 10px; margin-left: 40px;">
                  <el-select v-model="path.path_type" placeholder="选择路径映射类型" style="width: 200px; margin-right: 10px;" required>
                    <el-option label="前缀匹配" value="Prefix"></el-option>
                    <el-option label="精准匹配" value="Exact"></el-option>
                    <el-option label="由控制器提供方决定如何匹配" value="ImplementationSpecific"></el-option>
                  </el-select>
                  <el-input v-model="path.path" placeholder="请输入路径" style="width: 200px; margin-right: 10px;"></el-input>
                  <el-select v-model="path.backend.service_name" placeholder="请选择服务" style="width: 200px; margin-right: 10px;" @change="updateServicePorts(ruleIndex, pIndex)">
                  <el-option
                    v-for="service in services"
                    :key="service.service_name"
                    :label="service.service_name"
                    :value="service.service_name">
                  </el-option>
                </el-select>
                <el-select v-model="path.backend.service_port" placeholder="请选择端口" style="width: 150px;">
                  <el-option
                    v-for="port in service_ports"
                    :key="port.port"
                    :label="port.port"
                    :value="port.port">
                  </el-option>
                </el-select>
                <el-button v-if="rule.paths.length > 1" type="danger" icon="el-icon-delete" circle style="margin-left: 10px;" @click="removeRulePath(rule, pathIndex)"></el-button>
                </el-form-item>
              </el-form>
            </div>
          </el-card>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogCreateIngressVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitCreateIngressButton">提 交</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'创建YAML - '"
      :visible.sync="dialogCreateIngressYamlVisible"
      width="80%"
      class="d2p-code-dialog"
      >
      <div>
        <pre class="code-container" ref="codeContainer">
<code>{{ createIngressYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="submitIngressYamlButton" type="primary">提交</el-button>
        <el-button @click="dialogCreateIngressYamlVisible = false">关闭</el-button>
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
  name: 'containers_ingress',
  mixins: [d2CrudPlus.crud],
  components: {
    CodeDiff
  },
  data () {
    return {
      dialogIngressYamlVisible: false,
      editMode: false,
      yamlIngressName: '',
      yamlClusterName: '',
      yamlNamespace: '',
      ingressYamlData: '',
      defaultYamlIngressData: '',
      modifiedData: '',
      diffDialogVisible: false,
      dialogCreateIngressYamlVisible: false,
      originalData: '',
      dialogIngressDeleteCheckVisible: false,
      deleteIngressName: '',
      dialogIngressDetailVisible: false,
      ingressDetailData: {},
      dialogCreateIngressVisible: false,
      ingressForm: this.getDefaultIngressForm(),
      // ingressForm: {
      //   name: '',
      //   ingress_class_name: '',
      //   tlsEnabled: false,
      //   tls_secret: '',
      //   annotations: {},
      //   labels: {},
      //   rules: [
      //     {
      //       host: '',
      //       paths: [{
      //         path: '',
      //         backend: {
      //           service_name: '',
      //           service_port: ''
      //         }
      //       }],
      //       path_type: ''
      //     }
      //   ]
      // },
      ingress_class_names: [],
      k8s_cluster_name: '',
      selectedClusterName: '',
      selectedNamespace: '',
      annotationsOptions: [], // 从 API 获取的注解键列表
      annotationInput: '', // 用于输入自定义注解键的值
      selectedKey: '',
      currentPlaceholders: [''],
      tlsEnabled: false,
      tlsSecrets: [],
      // routingRules: [''],
      services: [],
      isEditing: false,
      testDialogVisible: false,
      labelKeys: [],
      annotationsKeys: [],
      service_ports: [],
      createIngressYamlData: ''
    }
  },
  mounted () {
  },
  methods: {
    getDefaultIngressForm() {
      return {
        name: '',
        ingress_class_name: '',
        annotations: {},
        labels: {},
        rules: [
          {
            host: '',
            paths: [{
              path: '',
              backend: {
                service_name: '',
                service_port: ''
              },
              path_type: ''
            }]
          }
        ],
        tls: []
      }
    },
    getCrudOptions () {
      // this.crud.searchOptions.form
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    handleClose() {
      this.dialogCreateIngressVisible = false
      this.ingressForm = this.getDefaultIngressForm()
      this.labelKeys = []
      this.annotationsKeys = []
      this.doRefresh()
    },
    ingressDetail({ row }) {
      this.dialogIngressDetailVisible = true
      const ingressName = row.name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetIngressDetail(ingressName, clusterName, namespace).then(response => {
        this.ingressDetailData = response.data.data
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    ingressYaml ({ row }) {
      this.dialogIngressYamlVisible = true
      this.editMode = false
      this.yamlIngressName = row.name
      this.yamlClusterName = row.cluster_name
      this.yamlNamespace = row.namespace
      console.log('1111')
      api.GetIngressYaml(this.yamlIngressName, this.yamlClusterName, this.yamlNamespace).then(response => {
        this.ingressYamlData = response.data.data
        this.defaultYamlIngressData = this.ingressYamlData
        this.$nextTick(() => {
          this.$refs.codeContainer.style.backgroundColor = 'white' // Reset background
          this.$refs.codeContainer.style.color = 'black'
          this.$refs.codeContainer.contentEditable = false // Disable editing
          this.$refs.codeContainer.innerText = this.defaultYamlIngressData
        })
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    checkIngressYamlBotton() {
      this.ingressYamlData = this.$refs.codeContainer.innerText
      this.originalData = this.defaultYamlIngressData
      this.modifiedData = this.ingressYamlData
      this.diffDialogVisible = true
    },
    submitIngressYamlBotton() {
      const obj = {
        ingress_name: this.yamlIngressName,
        cluster_name: this.yamlClusterName,
        namespace: this.yamlNamespace,
        yaml_data: this.modifiedData
      }
      api.IngressYamlUpdate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.diffDialogVisible = false
        this.dialogIngressYamlVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update ingress yaml:', error)
      })
    },
    toggleEditMode() {
      this.editMode = !this.editMode
      console.log(this.editMode)
      if (this.editMode) {
        this.defaultYamlIngressData = this.ingressYamlData
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true

        this.$refs.codeContainer.innerText = this.ingressYamlData
      } else {
        this.$refs.codeContainer.style.backgroundColor = 'white' // Reset background
        this.$refs.codeContainer.style.color = 'black'
        this.$refs.codeContainer.contentEditable = false // Disable editing
        this.ingressYamlData = this.defaultYamlIngressData
        this.$refs.codeContainer.innerText = this.defaultYamlIngressData
      }
    },
    ingressDelete({ row }) {
      this.deleteIngressName = row.name
      this.deleteClusterName = row.cluster_name
      this.deleteNamaspace = row.namespace
      this.dialogIngressDeleteCheckVisible = true
    },
    submitIngressDeleteButton({ row }) {
      api.IngressDelete({
        cluster_name: this.deleteClusterName,
        namespace: this.deleteNamaspace,
        ingress_name: this.deleteIngressName
      }).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
      })
      this.doRefresh()
      this.dialogIngressDeleteCheckVisible = false
    },
    createIngressButton() {
      this.isEditing = false
      this.dialogCreateIngressVisible = true
      console.log(this.selectedClusterName)
      console.log(this.selectedNamespace)
      api.GetIngressClass(this.selectedClusterName, this.selectedNamespace).then(response => {
        this.ingress_class_names = response.data.data
        if (this.ingress_class_names.length > 0) {
          this.ingressForm.ingress_class_name = this.ingress_class_names[0]
        }
      })
      api.GetIngressAnnotation().then(response => {
        this.annotationsOptions = response.data.data
        console.log(this.annotationsOptions)
      })
      this.tlsSecrets = []
      this.tlsEnabled = false
      api.GetServicePorts(this.selectedClusterName, this.selectedNamespace).then(response => {
        this.services = response.data.data
      })
      api.GetTlsSecretList(this.selectedClusterName, this.selectedNamespace).then(response => {
        this.tlsSecrets = response.data.data.map(secret => secret.secret_name)
      })
      if (this.isEditing) {
        console.log('11111111')
      } else {
        this.ingressForm = this.getDefaultIngressForm()
        console.log(this.ingressForm)
      }
    },
    updatePlaceholder(index) {
      const selectedKey = this.annotationsKeys[index]
      if (this.annotationsOptions[selectedKey]) {
        this.currentPlaceholders[index] = this.annotationsOptions[selectedKey]
        console.log(this.currentPlaceholders[index])
      } else {
        this.currentPlaceholders[index] = ''
        this.ingressForm.annotations[index].value = '' // 清空值
      }
    },
    addAnnotation() {
      // this.ingressForm.annotations.keys.push({ key: '', value: '' })
      // this.currentPlaceholders.push('')
      this.annotationsKeys.push("")
    },
    removeAnnotation(index) {
      // this.ingressForm.annotations.keys.splice(index, 1)
      // this.currentPlaceholders.splice(index, 1)
      const key = this.annotationsKeys[index]
      this.$delete(this.ingressForm.annotations, key)
      this.annotationsKeys.splice(index, 1)
    },
    submitCreateIngressButton() {
      console.log(this.ingressForm)
      console.log(this.selectedNamespace)
      console.log(this.selectedClusterName)
      console.log(this.isEditing)
      if (this.isEditing) {
        this.ingressForm.change_type = 'update'
      } else {
        this.ingressForm.change_type = 'create'
      }
      this.ingressForm.cluster_name = this.selectedClusterName
      this.ingressForm.namespace = this.selectedNamespace
      api.IngressChange(this.ingressForm).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogCreateIngressVisible = false
        this.doRefresh()
      })
    },
    addLabel() {
      // this.ingressForm.labels.push("")
      this.labelKeys.push("") // 只在 labelKeys 中添加空 key
    },
    removeLabel(index) {
      // this.ingressForm.labels.keys.splice(index, 1)
      const key = this.labelKeys[index]
      this.$delete(this.ingressForm.labels, key)
      this.labelKeys.splice(index, 1) // 从 keys 数组中删除
    },
    addRule() {
      this.ingressForm.rules.push(
        {
          host: '',
          paths: [{
            path: '',
            backend: {
              service_name: '',
              service_port: ''
            },
            path_type: ''
          }]
        }
      )
    },
    addRulePath(rule) {
      rule.paths.push({
        path: '',
        backend: {
          service_name: '',
          service_port: ''
        },
        path_type: ""
      })
    },
    addTLS() {
      this.ingressForm.tls.push({
        host: '',
        secret_name: ''
      })
    },
    removeTLS(tlsIndex) {
      this.ingressForm.tls.splice(tlsIndex, 1)
    },
    fetchTlsSecrets() {
      if (this.tlsEnabled) {
        api.GetTlsSecretList(this.selectedClusterName, this.selectedNamespace).then(response => {
          this.tlsSecrets = response.data.data
        })
      }
    },
    addRoutingRule() {
      this.ingressForm.routingRules.push({
        pathMappingType: '',
        path: '',
        serviceName: '',
        servicePort: '',
        availablePorts: []
      })
      // this.routeRuleForm.keys.push({ key: '', value: '' })
    },
    removeRulePath(rule, pathIndex) {
      rule.paths.splice(pathIndex, 1)
      // this.ingressForm.routingRules.splice(index, 1)
    },
    removeRule(ruleIndex) {
      this.ingressForm.rules.splice(ruleIndex, 1)
    },
    fetchServicePorts() {
      api.GetServicePorts(this.selectedClusterName, this.selectedNamespace).then(response => {
        this.services = response.data.data
      })
    },
    updateServicePorts(ruleIndex, pIndex) {
      const selectedService = this.services.find(service => service.service_name === this.ingressForm.rules[ruleIndex].paths[pIndex].backend.service_name)
      this.$set(this.ingressForm.rules[ruleIndex].paths[pIndex].backend, 'service_port', '')
      if (selectedService) {
        this.service_ports = selectedService.service_port
      } else {
        this.service_ports = []
      }
    },
    // changeIngressButton() {
    //   this.isEditing = true
    //   this.dialogCreateIngressVisible = true
    //   const ingressName = 'test-090909'
    //   const clusterName = 'daodou-test'
    //   const namespace = 'devops'
    //   api.GetIngressDetail(ingressName, clusterName, namespace).then(response => {
    //     this.ingressForm = response.data.data
    //     console.log(this.ingressForm)
    //     this.labelKeys = Object.keys(this.ingressForm.labels)
    //     this.annotationsKeys = Object.keys(this.ingressForm.annotations)
    //   })
    // },
    ingressEdit({ row }) {
      console.log('ingressEdit')
      this.isEditing = true
      this.dialogCreateIngressVisible = true
      const ingressName = row.name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetIngressDetail(ingressName, clusterName, namespace).then(response => {
        this.ingressForm = response.data.data
        console.log(this.ingressForm)
        this.labelKeys = Object.keys(this.ingressForm.labels)
        this.annotationsKeys = Object.keys(this.ingressForm.annotations)
      })
    },
    createIngressYamlButton() {
      this.dialogCreateIngressYamlVisible = true
      this.$nextTick(() => {
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true
        this.$refs.codeContainer.innerText = this.createIngressYamlData
      })
    },
    submitIngressYamlButton() {
      console.log(this.selectedClusterName)
      console.log(this.selectedNamespace)
      this.ingressYamlData = this.$refs.codeContainer.innerText
      const obj = {
        cluster_name: this.selectedClusterName,
        namespace: this.selectedNamespace,
        yaml_data: this.ingressYamlData
      }
      api.IngressYamlCreate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogCreateIngressYamlVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update ingress yaml:', error)
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

  .ingress-detail-dialog .card {
    border: 1px solid #ddd;
    border-radius: 0.25rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }
  .ingress-detail-dialog .card-header {
    font-weight: bold;
    background-color: #f7f7f7;
  }
  .ingress-detail-dialog .card-body {
    padding: 1rem;
  }
  .ingress-detail-dialog .info-item {
    padding: 0.5rem;
    border-bottom: 1px solid #ddd;
  }
  .ingress-detail-dialog .list-group-item {
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
