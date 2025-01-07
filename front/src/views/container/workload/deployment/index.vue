<script src="../../service/api.js"></script>
<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <d2-crud-x
      ref="d2Crud"
      v-bind="_crudProps"
      v-on="_crudListeners"
      @deploymentDetail="deploymentDetail"
      @deploymentReplicas="deploymentReplicas"
      @deploymentEdit="deploymentEdit"
      @deploymentImageChange="deploymentImageChange"
      @deploymentHistoryVersion="deploymentHistoryVersion"
      @deploymentRestart="deploymentRestart"
      @deploymentDelete="deploymentDelete"
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
            @click="workloadCreateButton"
          >创建</el-button>
          <el-button
            type="warning"
            size="small"
            icon="el-icon-edit"
            @click="createDeploymentYamlButton"
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
      <template slot="imagesSlot" slot-scope="scope">
        <div v-for="(image, index) in scope.row.images" :key="index">
            {{ image }}
            <br/>
        </div>
      </template>
    </d2-crud-x>
    <el-dialog
      :title="deploymentDetailData.name"
      :visible.sync="dialogDeploymentDetailVisible"
      width="80%"
      :modal-append-to-body="false"
    >
      <div v-if="Object.keys(deploymentDetailData).length > 0" class="deployment-detail-dialog">
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
                    <span>{{ deploymentDetailData.name }}</span>
                  </td>
                  <td style="width: 50%;">
                    <span>命名空间:  </span>
                    <span>{{ deploymentDetailData.namespace }}</span>
                  </td>
                </tr>
                <tr>
                  <td style="width: 50%;">
                    <span>状态:  </span>
                    <span>{{ deploymentDetailData.container_replicas_detail }}，已准备 {{ deploymentDetailData.ready_replicas }} 个, 期望： {{ deploymentDetailData.replicas }} 个</span>
                  </td>
                  <td style="width: 50%;">
                    <span>创建时间:   </span>
                    <span>{{ deploymentDetailData.create_time }}</span>
                  </td>
                </tr>
                <tr>
                  <td style="width: 50%;">
                    <span>选择器:  </span>
                    <span class="selector-list">
                      <tr>
                        <div v-for="(value, key) in deploymentDetailData.selector"  :key="key">
                          <template>
                            <td>{{ key }}: {{ value }}</td>
                          </template>
                        </div>
                      </tr>
                    </span>
                  </td>
                  <td style="width: 50%;">
                    <span>labels: </span>
                    <span>
                      <tr>
                        <div v-for="(value, key) in deploymentDetailData.labels" :key="key">
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
                    <span>更新策略:  </span>
                    <span> {{ deploymentDetailData.strategy_type }} </span><br>
                    <template v-if="deploymentDetailData.strategy_type === 'RollingUpdate'">
                      <span>超过期望的Pod数量: {{ deploymentDetailData.strategy_rolling_update_max_surge }}</span><br>
                      <span>不可用Pod最大数量: {{ deploymentDetailData.strategy_rolling_update_max_surge }}</span>
                    </template>
                  </td>
                  <td style="width: 50%;">
                    <span>重启策略:   </span>
                    <span>{{ deploymentDetailData.restart_policy }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-if="deploymentDetailData.containers && deploymentDetailData.containers.length > 0" class="pod-list card">
          <div class="card-header">容器组</div>
          <div class="card-body">
            <el-table :data="deploymentDetailData.containers" style="width: 100%">
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="image" label="镜像" />
              <el-table-column prop="image_pull_policy" label="拉取策略" />
            </el-table>
          </div>
        </div>
        <div v-if="deploymentDetailData.init_containers && deploymentDetailData.init_containers.length > 0" class="pod-list card">
          <div class="card-header">初始化容器组</div>
          <div class="card-body">
            <el-table :data="deploymentDetailData.init_containers" style="width: 100%">
              <el-table-column prop="name" label="名称" />
              <el-table-column prop="image" label="镜像" />
              <el-table-column prop="image_pull_policy" label="拉取策略" />
            </el-table>
          </div>
        </div>
        <div v-if="deploymentDetailData.conditions && deploymentDetailData.conditions.length > 0" class="pod-list card">
          <div class="card-header">现状详情</div>
          <div class="card-body">
            <el-table :data="deploymentDetailData.conditions" style="width: 100%">
              <el-table-column prop="conditions_type" label="类型" />
              <el-table-column prop="conditions_status" label="状态" />
              <el-table-column prop="conditions_last_transition_time" label="更新时间" />
              <el-table-column prop="conditions_reason" label="原因" />
              <el-table-column prop="conditions_message" label="消息" />
            </el-table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentDetailVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="replicasDeploymentName + ' 副本数量调整'"
      :visible.sync="dialogDeploymentReplicasVisible"
      width="30%"
      >
      <template style="align-items: center; justify-content: center;" >
        <el-input-number v-model="replicasNum" @change="handleChange" :min="0" :max="50" label="副本数量" ></el-input-number>
      </template>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentReplicasVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeploymentReplicasBotton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'预览/编辑YAML - ' + editDeploymentName"
      :visible.sync="dialogDeploymentEditVisible"
      width="80%"
      class="d2p-code-dialog123"
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
<code>{{ deploymentYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button v-if="editMode" @click="checkDeploymentYamlBotton" type="primary">提交</el-button>
        <el-button @click="dialogDeploymentEditVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认更新- ' + editDeploymentName"
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
        <el-button v-if="editMode" @click="submitDeploymentYamlBotton" type="primary">确认修改并提交</el-button>
        <el-button @click="diffDialogVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="deploymentDetailData.name"
      :visible.sync="deploymentImageChangeVisible"
      width="80%"
      >
      <div v-if="Object.keys(deploymentDetailData).length > 0" class="deployment-detail-dialog">
        <div class="card">
          <div class="card-header">容器组</div>
          <div class="card-body">
            <el-table :data="deploymentDetailData.containers" style="width: 100%">
              <el-table-column prop="name" label="名称" />
              <!-- <el-table-column prop="image" label="镜像" /> -->
              <el-table-column label="镜像">
                <template slot-scope="scope">
                  {{ splitImage(scope.row.image).image }}
                </template>
              </el-table-column>
              <el-table-column label="当前版本">
                <template slot-scope="scope">
                  {{ splitImage(scope.row.image).tag }}
                </template>
              </el-table-column>
              <el-table-column label="新版本">
                <template slot-scope="scope">
                  <el-input v-model="scope.row.newImage" placeholder="请输入新的镜像" size="small">
                  </el-input>
                </template>
              </el-table-column>
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button @click="checkDeploymentChangImagebutton(scope.row, deploymentDetailData)" type="primary" size="small" icon="el-icon-edit">确认修改新镜像</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deploymentImageChangeVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      title="确认调整镜像版本"
      :visible.sync="dialogDeploymentImageChangeCheckVisible"
      width="30%">
      <span>将要调整 1 个容器的镜像版本，是否继续？</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentImageChangeCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeploymentChangImagebutton">确 定</el-button>
      </span>
    </el-dialog>
        <el-dialog
      :title="deploymentDetailData.name + '- 历史版本-回滚'"
      :visible.sync="deploymentHistoryVisible"
      width="80%"
      >
      <div v-if="Object.keys(deploymentHistoryData).length > 0" class="deployment-detail-dialog">
        <div class="card">
          <div class="card-header">历史版本记录</div>
          <div class="card-body">
            <el-table :data="deploymentHistoryData" style="width: 100%">
              <el-table-column prop="name" label="历史版本" />
              <!-- <el-table-column prop="image" label="镜像" /> -->
              <el-table-column prop="image" label="镜像" />
              <el-table-column prop="revision" label="历史版本号" />
              <el-table-column prop="creation_timestamp" label="创建时间" />
              <el-table-column label="操作">
                <template slot-scope="scope">
                  <el-button @click="checkDeploymentHistoryRolloutbutton(scope.row)" type="primary" size="small" icon="el-icon-edit">回滚到该版本</el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="deploymentHistoryVisible = false">关闭</el-button>
      </span>
    </el-dialog>
    <el-dialog
      title="确认是否要回滚该版本"
      :visible.sync="dialogDeploymentHistoryRolloutCheckVisible"
      width="60%">
      <span>即将回滚的镜像版本：{{ this.deploymentHistoryRow.image }}</span>
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentHistoryRolloutCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeploymentHistoryRolloutButton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认是否重启该deployment - ' + restartDeploymentName"
      :visible.sync="dialogDeploymentRestartCheckVisible"
      width="40%">
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentRestartCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeploymentRestartButton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'确认是否删除该deployment - ' + deleteDeploymentName"
      :visible.sync="dialogDeploymentDeleteCheckVisible"
      width="40%">
      <span slot="footer" class="dialog-footer">
        <el-button @click="dialogDeploymentDeleteCheckVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitDeploymentDeleteButton">确 定</el-button>
      </span>
    </el-dialog>
    <el-dialog
      :title="'创建YAML - '"
      :visible.sync="dialogCreateDeploymentYamlVisible"
      width="80%"
      class="d2p-code-dialog"
      >
      <div>
        <pre class="code-container" ref="codeContainer">
<code>{{ createDeploymentYamlData }}</code>
        </pre>
      </div>
      <span slot="footer" class="dialog-footer">
        <el-button @click="submitDeploymentYamlButton" type="primary">提交</el-button>
        <el-button @click="dialogCreateDeploymentYamlVisible = false">关闭</el-button>
      </span>
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
      dialogDeploymentDetailVisible: false, // 控制弹出框显示与隐藏
      deploymentDetailData: {},
      dialogDeploymentReplicasVisible: false,
      replicasNum: 1,
      dialogDeploymentEditVisible: false,
      replicasDeploymentName: '',
      deploymentName: '',
      deploymentYamlData: '',
      editMode: false,
      defaultDeploymentYamlData: '',
      diffDialogVisible: false,
      deploymentImageChangeVisible: false,
      originalData: '',
      modifiedData: '',
      editDeploymentName: '',
      dialogDeploymentImageChangeCheckVisible: false,
      deploymentHistoryVisible: false,
      deploymentHistoryData: '',
      dialogDeploymentHistoryRolloutCheckVisible: false,
      image: '',
      deploymentHistoryRow: '',
      dialogDeploymentRestartCheckVisible: false,
      restartDeploymentName: '',
      dialogDeploymentDeleteCheckVisible: false,
      deleteDeploymentName: '',
      selectedNamespace: '',
      selectedClusterName: '',
      dialogCreateDeploymentYamlVisible: false,
      createDeploymentYamlData: '',
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
    deploymentDetail({ row }) {
      this.dialogDeploymentDetailVisible = true
      const deploymentName = row.name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetDeploymentDetail(deploymentName, clusterName, namespace).then(response => {
        this.deploymentDetailData = response.data.data
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    deploymentReplicas({ row }) {
      this.dialogDeploymentReplicasVisible = true
      this.replicasDeploymentName = row.name
      this.replicasClusterName = row.cluster_name
      this.replicasNum = row.replicas
      this.replicasNamespace = row.namespace
    },
    submitDeploymentReplicasBotton() {
      const obj = {
        deployment_name: this.replicasDeploymentName,
        cluster_name: this.replicasClusterName,
        replicas: this.replicasNum,
        namespace: this.replicasNamespace
      }
      api.SetDeploymentReplicas(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data,
          type: 'success'
        })
      }).catch(error => {
        console.error('Error set deployment replicas:', error)
      })
      this.dialogDeploymentReplicasVisible = false
    },
    handleChange(value) {
      console.log(value)
    },
    deploymentEdit({ row }) {
      this.dialogDeploymentEditVisible = true
      this.editMode = false
      this.editDeploymentName = row.name
      this.editClusterName = row.cluster_name
      this.editNamespace = row.namespace
      api.GetDeploymentYaml(this.editDeploymentName, this.editClusterName, this.editNamespace).then(response => {
        this.deploymentYamlData = response.data.data
        this.defaultDeploymentYamlData = this.deploymentYamlData
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
      this.$refs.codeContainer.style.backgroundColor = '' // Reset background
      this.$refs.codeContainer.style.color = 'black'
      this.$refs.codeContainer.contentEditable = false // Disable editing
      this.$refs.codeContainer.innerText = this.defaultDeploymentYamlData
    },
    checkDeploymentYamlBotton() {
      this.deploymentYamlData = this.$refs.codeContainer.innerText
      this.originalData = this.defaultDeploymentYamlData
      this.modifiedData = this.deploymentYamlData
      this.diffDialogVisible = true
    },
    submitDeploymentYamlBotton() {
      const obj = {
        deployment_name: this.editDeploymentName,
        cluster_name: this.editClusterName,
        namespace: this.editNamespace,
        yaml_data: this.modifiedData
      }
      api.DeploymentYamlUpdate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.diffDialogVisible = false
        this.dialogDeploymentEditVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error update deployment yaml:', error)
      })
    },
    toggleEditMode() {
      this.editMode = !this.editMode
      console.log(this.editMode)
      if (this.editMode) {
        this.defaultDeploymentYamlData = this.deploymentYamlData
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true

        this.$refs.codeContainer.innerText = this.deploymentYamlData
      } else {
        this.$refs.codeContainer.style.backgroundColor = '' // Reset background
        this.$refs.codeContainer.style.color = 'black'
        this.$refs.codeContainer.contentEditable = false // Disable editing
        this.deploymentYamlData = this.defaultDeploymentYamlData
        this.$refs.codeContainer.innerText = this.defaultDeploymentYamlData
      }
    },
    deploymentImageChange({ row }) {
      this.deploymentImageChangeVisible = true
      const deploymentName = row.name
      const clusterName = row.cluster_name
      const namespace = row.namespace
      api.GetDeploymentDetail(deploymentName, clusterName, namespace).then(response => {
        this.deploymentDetailData = response.data.data
        this.setDefaultNewImage()
      }).catch(error => {
        console.error('Error fetching node detail:', error)
      })
    },
    splitImage(image) {
      const [img, tag] = image.split(':')
      return {
        image: img,
        tag: tag || 'latest'
      }
    },
    setDefaultNewImage() {
      this.deploymentDetailData.containers.forEach(container => {
        const { tag } = this.splitImage(container.image)
        this.$set(container, 'newImage', tag)
      })
    },
    checkDeploymentChangImagebutton(row, deploymentDetailData) {
      if (row.newImage.replace(/\s+/g, '') === this.splitImage(row.image).tag) {
        this.$message({
          message: '版本一致，不需要修改',
          type: 'info'
        })
        return
      }
      this.dialogDeploymentImageChangeCheckVisible = true
      this.row = row
      this.deploymentDetailData = deploymentDetailData
    },
    submitDeploymentChangImagebutton() {
      const row = this.row
      const deploymentDetailData = this.deploymentDetailData
      const obj = {
        deployment_name: deploymentDetailData.name,
        cluster_name: deploymentDetailData.cluster_name,
        namespace: deploymentDetailData.namespace,
        container_name: row.name,
        image: this.splitImage(row.image).image,
        newImage: row.newImage.replace(/\s+/g, '')
      }
      api.SetDeploymentImage(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogDeploymentImageChangeCheckVisible = false
        this.deploymentImageChangeVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error set deployment image:', error)
      })
    },
    deploymentHistoryVersion({ row }) {
      this.deploymentHistoryVisible = true
      this.historyDeploymentName = row.name
      this.historyClusterName = row.cluster_name
      this.historyNamespace = row.namespace
      api.GetDeploymentHistory(this.historyDeploymentName, this.historyClusterName, this.historyNamespace).then(response => {
        this.deploymentHistoryData = response.data.data
      }).catch(error => {
        console.error('Error get deployment history:', error)
      })
    },
    checkDeploymentHistoryRolloutbutton(row) {
      console.log('555')
      this.dialogDeploymentHistoryRolloutCheckVisible = true
      this.deploymentHistoryRow = row
    },
    submitDeploymentHistoryRolloutButton() {
      console.log(this.deploymentHistoryRow)
      const obj = {
        deployment_name: this.deploymentHistoryRow.deployment_name,
        cluster_name: this.deploymentHistoryRow.cluster_name,
        namespace: this.deploymentHistoryRow.namespace,
        revision: this.deploymentHistoryRow.revision
      }
      api.SetDeploymentHistoryVersion(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogDeploymentHistoryRolloutCheckVisible = false
        this.deploymentHistoryVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error set deployment history version:', error)
      })
    },
    deploymentRestart({ row }) {
      this.restartDeploymentName = row.name
      this.restartClusterName = row.cluster_name
      this.restartNamaspace = row.namespace
      this.dialogDeploymentRestartCheckVisible = true
    },
    submitDeploymentRestartButton({ row }) {
      api.DeploymentRestart({
        cluster_name: this.restartClusterName,
        namespace: this.restartNamaspace,
        deployment_name: this.restartDeploymentName
      }).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
      })
      this.dialogDeploymentRestartCheckVisible = false
    },
    deploymentDelete({ row }) {
      this.deleteDeploymentName = row.name
      this.deleteClusterName = row.cluster_name
      this.deleteNamaspace = row.namespace
      this.dialogDeploymentDeleteCheckVisible = true
    },
    submitDeploymentDeleteButton({ row }) {
      api.DeploymentDelete({
        cluster_name: this.deleteClusterName,
        namespace: this.deleteNamaspace,
        deployment_name: this.deleteDeploymentName
      }).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
      })
      this.dialogDeploymentDeleteCheckVisible = false
      this.doRefresh()
    },
    workloadCreateButton() {
      console.log('123')
      console.log(this.selectedNamespace)
      console.log(this.selectedClusterName)
      const namespace = this.selectedNamespace
      const clusterName = this.selectedClusterName
      // const params = {
      //   cluster_name: this.selectedClusterName,
      //   namespace: this.selectedNamespace
      // }
      this.$router.push({
        name: 'workloadCreate',
        query: {
          namespace,
          clusterName
        }
      })
    },
    createDeploymentYamlButton() {
      this.dialogCreateDeploymentYamlVisible = true
      this.$nextTick(() => {
        this.$refs.codeContainer.style.backgroundColor = 'black'
        this.$refs.codeContainer.style.color = 'white'
        this.$refs.codeContainer.contentEditable = true
        this.$refs.codeContainer.innerText = this.createDeploymentYamlData
      })
    },
    submitDeploymentYamlButton() {
      this.deploymentYamlData = this.$refs.codeContainer.innerText
      const obj = {
        cluster_name: this.selectedClusterName,
        namespace: this.selectedNamespace,
        yaml_data: this.deploymentYamlData
      }
      api.DeploymentYamlCreate(obj).then(response => {
        this.$message({
          showClose: true,
          message: response.data.data,
          type: 'success'
        })
        this.dialogCreateDeploymentYamlVisible = false
        this.doRefresh()
      }).catch(error => {
        console.error('Error create deployment yaml:', error)
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

  .deployment-detail-dialog .card {
    border: 1px solid #ddd;
    border-radius: 0.25rem;
    box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  }
  .deployment-detail-dialog .card-header {
    font-weight: bold;
    background-color: #f7f7f7;
  }
  .deployment-detail-dialog .card-body {
    padding: 1rem;
  }
  .deployment-detail-dialog .info-item {
    padding: 0.5rem;
    border-bottom: 1px solid #ddd;
  }
  .deployment-detail-dialog .list-group-item {
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

.diff {
  display: flex;
  &-container {
    display: flex;
    justify-content: space-between;
  }
  &-column {
    width: 48%;
    border: 1px solid #ccc;
    padding: 10px;
    box-sizing: border-box;
  }
  &-add {
    background-color: #e6ffed;
    color: #22863a;
  }
  &-removed {
    background-color: #ffeef0;
    color: #b31d28;
  }
  &-unchanged {
    background-color: #f1f8ff;
  }

  &-empty {
    background-color: #fff;
  }
}
  .diff-container {
    display: flex;
    justify-content: space-between;
  }

  .card-text {
    background-color: #e6ffed;
    color: #22863a;
    // }
  }

.card-text.diff-added{
  background-color: #e6ffed;
  color: #22863a;
}

  .diff-removed {
    background-color: #ffeef0;
    color: #b31d28;
  }

  .diff-unchanged {
    background-color: #f1f8ff;
  }

  .diff-empty {
    background-color: #fff;
  }
}

.d2p-code-dialog .code-container-wrapper {
  background-color: #000000;
  color: #ffffff;
  padding: 20px;
  border-radius: 8px;
}

.d2p-code-dialog .code-container {
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #ffffff;
  background-color: #000000;
  padding: 15px;
  border-radius: 5px;
  overflow-y: auto;
  height: calc(1.2em * 20); // 设置为20行高度
  font-family: monospace;
}

.d2p-code-dialog code {
  color: #ffffff;
}
</style>
