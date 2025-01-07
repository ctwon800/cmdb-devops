<template>
  <div>
    <el-row>
      <el-col :span="5">
        <!-- 左侧容器列表 -->
        <el-button type="warning" size="mini" @click="addContainer('init')">添加初始化容器</el-button>
        <el-button type="primary" size="mini" @click="addContainer('work')">添加工作容器</el-button>
        <div v-for="(container, index) in containerInfoData" :key="index" class="container-list">
          <el-tag
            :type="container.type === 'init' ? 'warning' : 'primary'"
            closable
            @close="removeContainer(index)"
            @click="selectContainer(index)">
            {{ container.type === 'init' ? '初始化容器' : '工作容器' }}: {{ container.name || '' }}
          </el-tag>
        </div>
      </el-col>
      <el-col :span="19">
        <!-- 右侧表单 -->
        <div v-if="selectedContainerIndex !== null">
          <el-form :model="containerInfoData[selectedContainerIndex]" label-width="120px">
            <!-- 容器名称 -->
            <el-form-item label="名称" required>
              <el-input v-model="containerInfoData[selectedContainerIndex].name" placeholder="请输入容器名称"></el-input>
            </el-form-item>
            <!-- 镜像 -->
            <el-form-item label="容器镜像" required>
              <el-input v-model="containerInfoData[selectedContainerIndex].image" placeholder="请输入容器镜像" style="width: 70%"></el-input>
              <span style="margin-left: 10px; width: 10%">镜像密钥 </span>
              <el-select v-model="containerInfoData[selectedContainerIndex].imagePullSecret" clearable placeholder="请选择拉取密钥" style="width: 20%">
                <el-option v-for="item in imageSecrets" :key="item" :value="item">
                </el-option>
              </el-select>
            </el-form-item>
            <!-- 镜像拉取策略 -->
            <el-form-item label="镜像拉取策略" required>
              <el-radio-group v-model="containerInfoData[selectedContainerIndex].imagePullPolicy">
                <el-radio label="Always">始终拉取</el-radio>
                <el-radio label="IfNotPresent">本地不存在时拉取</el-radio>
                <el-radio label="Never">从不拉取</el-radio>
              </el-radio-group>
              <!--镜像仓库密钥 -->
            </el-form-item>
            <el-form-item label="命令/参数">
              <el-checkbox v-model="isCommandChecked" @change="handleCheckboxCommandChange"></el-checkbox>
              <div v-if="isCommandChecked" style="padding-top: 0px; display: flex; flex-direction: column; gap: 10px;">
                <el-input v-model="containerInfoData[selectedContainerIndex].workingDir" placeholder="请输入工作目录">
                  <template slot="prepend">
                    <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                      <span>工作目录</span>
                    </div>
                  </template>
                </el-input>
                <el-input v-model="containerInfoData[selectedContainerIndex].command" placeholder="请输入命令">
                  <template slot="prepend">
                    <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                      <span>命令</span>
                    </div>
                  </template>
                </el-input>
                <el-input v-model="containerInfoData[selectedContainerIndex].args" placeholder="请输入参数">
                  <template slot="prepend">
                    <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                      <span>参数</span>
                    </div>
                  </template>
                </el-input>
              </div>
            </el-form-item>
            <!-- 环境变量 -->
            <el-form-item label="环境变量">
              <el-checkbox v-model="isEnvChecked" @change="handleCheckboxEnvChange"></el-checkbox>
              <div v-if="isEnvChecked" style="margin-top: 10px;">
                <el-button type="primary" size="mini" @click="addEnvVariable(selectedContainerIndex)">添加环境变量</el-button>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <span style="width: 33%;">变量名</span>
                  <span style="width: 33%">变量值</span>
                  <span style="width: 33%">操作</span>
                </div>
                <div v-for="(env, index) in containerInfoData[selectedContainerIndex].env" :key="index" class="env-item"  style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                  <el-input v-model="env.name" placeholder="变量名" style="width: 33%;"></el-input>
                  <el-input v-model="env.value" placeholder="变量值" style="width: 33%;"></el-input>
                  <div style="margin-left: 10px; width: 33%">
                    <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeEnvVariable(index, selectedContainerIndex)"></el-button>
                  </div>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="端口">
              <el-checkbox v-model="isPortsChecked" @change="handleCheckboxPortsChange"></el-checkbox>
              <div v-if="isPortsChecked" style="margin-top: 10px;">
                <el-button type="primary" size="mini" @click="addPortVariable(selectedContainerIndex)">新增端口</el-button>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <span style="width: 25%;">名称</span>
                  <span style="width: 25%">端口</span>
                  <span style="width: 25%">协议</span>
                  <span style="width: 25%">操作</span>
                </div>
                <div v-for="(port, index) in containerInfoData[selectedContainerIndex].ports" :key="index" style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                  <el-input v-model="port.name" placeholder="请输入名称" style="width: 25%;"></el-input>
                  <el-input v-model="port.number" placeholder="请输入端口号" style="width: 25%;"></el-input>
                  <el-select v-model="port.protocol" placeholder="选择协议" style="width: 25%;">
                    <el-option label="TCP" value="TCP"></el-option>
                    <el-option label="UDP" value="UDP"></el-option>
                  </el-select>
                  <div style="margin-left: 20px; width: 25%">
                    <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removePortVariable(index, selectedContainerIndex)"></el-button>
                  </div>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="资源请求/限制">
              <el-checkbox v-model="isResourceChecked" @change="handleCheckboxResourceChange"></el-checkbox>
              <div v-if="isResourceChecked" style="margin-top: 10px;">
                <div>
                  <span>CPU限制</span>
                  <el-input v-model="containerInfoData[selectedContainerIndex].resources.limits.cpu" placeholder="0.5" style="width: 200px; padding-left: 20px;">
                    <template slot="append">
                      <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                        <span>Core</span>
                      </div>
                    </template>
                  </el-input>
                  <span style="margin-left: 40px;">内存限制</span>
                  <el-input v-model="containerInfoData[selectedContainerIndex].resources.limits.memory" placeholder="1024" style="width: 200px; padding-left: 20px;">
                    <template slot="append">
                      <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                        <span>MiB</span>
                      </div>
                    </template>
                  </el-input>
                </div>
                <div style="margin-top: 10px;">
                  <span>CPU请求</span>
                  <el-input v-model="containerInfoData[selectedContainerIndex].resources.requests.cpu" placeholder="0.5" style="width: 200px; padding-left: 20px;">
                    <template slot="append">
                      <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                        <span>Core</span>
                      </div>
                    </template>
                  </el-input>
                  <span style="margin-left: 40px;">内存请求</span>
                  <el-input v-model="containerInfoData[selectedContainerIndex].resources.requests.memory" placeholder="1024" style="width: 200px; padding-left: 20px;">
                    <template slot="append">
                      <div style="display: flex; align-items: center; width: 70px; justify-content: center;">
                        <span>MiB</span>
                      </div>
                    </template>
                  </el-input>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="健康检测">
              <el-checkbox v-model="isHealthCheckEnabled" @change="handleHealthCheckToggle"></el-checkbox>
              <div v-if="isHealthCheckEnabled">
                <el-checkbox v-model="isLivenessProbeChecked" @change="handleProbeCheckboxChange('livenessProbe')">存活探针</el-checkbox>
                <el-checkbox v-model="isReadinessProbeChecked" @change="handleProbeCheckboxChange('readinessProbe')">就绪探针</el-checkbox>
                <el-checkbox v-model="isStartupProbeChecked" @change="handleProbeCheckboxChange('startupProbe')">启动探针</el-checkbox>
                <div v-if="isLivenessProbeChecked">
                  <health-check
                    v-model="containerInfoData[selectedContainerIndex].livenessProbe"
                    probeType="liveness"
                    @change="(data) => handleHealthCheckChange('livenessProbe', data)">
                  </health-check>
                </div>
                <div v-if="isReadinessProbeChecked">
                  <health-check
                    v-model="containerInfoData[selectedContainerIndex].readinessProbe"
                    probeType="readiness"
                    @change="(data) => handleHealthCheckChange('readinessProbe', data)">
                  </health-check>
                </div>
                <div v-if="isStartupProbeChecked">
                  <health-check
                    v-model="containerInfoData[selectedContainerIndex].startupProbe"
                    probeType="startup"
                    @change="(data) => handleHealthCheckChange('startupProbe', data)">
                  </health-check>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="特权容器">
              <el-checkbox
                v-model="containerInfoData[selectedContainerIndex].securityContext.privileged"
                @change="handlePrivilegedChange">
              </el-checkbox>
              <div style="color: #909399; font-size: 12px; margin-top: 5px;">
                特权容器可以访问宿主机的设备和进程,请谨慎使用
              </div>
            </el-form-item>
            <!-- 修改存储卷表单项 -->
            <el-form-item label="存储卷">
              <el-checkbox v-model="isVolumeChecked" @change="handleCheckboxVolumeChange"></el-checkbox>
              <div v-if="isVolumeChecked" style="margin-top: 10px;">
                <el-button type="primary" size="mini" @click="addVolumeMount(selectedContainerIndex)">添加存储卷</el-button>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                  <span style="width: 15%;">存储卷类型</span>
                  <span style="width: 15%">名称</span>
                  <span style="width: 15%">挂载源</span>
                  <span style="width: 15%">容器路径</span>
                  <span style="width: 15%">子路径</span>
                  <span style="width: 15%">只读</span>
                  <span style="width: 10%">操作</span>
                </div>
                <div v-for="(volume, index) in containerInfoData[selectedContainerIndex].volumeMounts"
                     :key="index"
                     style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                  <el-select v-model="volume.type" style="width: 15%;" placeholder="选择类型" @change="(val) => handleVolumeTypeChange(val, index)">
                    <el-option label="临时目录" value="emptyDir"></el-option>
                    <el-option label="主机目录" value="hostPath"></el-option>
                    <el-option label="配置项" value="configMap"></el-option>
                    <el-option label="保密字典" value="secret"></el-option>
                    <el-option label="存储声明" value="persistentVolumeClaim"></el-option>
                  </el-select>
                  <el-input v-model="volume.name" placeholder="volume名称" style="width: 15%;"></el-input>

                  <!-- 根据不同类型显示不同的源配置 -->
                  <template v-if="volume.type === 'hostPath'">
                    <el-input v-model="volume.hostPath.path" placeholder="主机路径" style="width: 15%;"></el-input>
                  </template>
                  <template v-else-if="volume.type === 'configMap'">
                    <el-select v-model="volume.configMap.name" style="width: 15%;" placeholder="选择配置项">
                      <el-option v-for="cm in configMapList" :key="cm" :label="cm" :value="cm"></el-option>
                    </el-select>
                  </template>
                  <template v-else-if="volume.type === 'secret'">
                    <el-select v-model="volume.secret.secretName" style="width: 15%;" placeholder="选择保密字典">
                      <el-option v-for="secret in secretList" :key="secret" :label="secret" :value="secret"></el-option>
                    </el-select>
                  </template>
                  <template v-else-if="volume.type === 'persistentVolumeClaim'">
                    <el-select v-model="volume.persistentVolumeClaim.claimName" style="width: 15%;" placeholder="选择存储声明">
                      <el-option v-for="pvc in pvcList" :key="pvc" :label="pvc" :value="pvc"></el-option>
                    </el-select>
                  </template>
                  <template v-else>
                    <div style="width: 15%;">-</div>
                  </template>

                  <el-input v-model="volume.mountPath" placeholder="容器内路径" style="width: 15%;"></el-input>
                  <el-input v-model="volume.subPath" placeholder="子路径(可选)" style="width: 15%;"></el-input>
                  <el-checkbox v-model="volume.readOnly" style="width: 15%;"></el-checkbox>
                  <div style="width: 10%">
                    <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeVolumeMount(index, selectedContainerIndex)"></el-button>
                  </div>
                </div>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import * as api from "@/views/container/workload/workloadCreate/api"
import HealthCheck from './HealthCheck.vue'

export default {
  name: 'containerInfo',
  props: {
    value: {
      type: Array,
      default: () => []
    },
    namespace: {
      type: String,
      required: true
    },
    clusterName: {
      type: String,
      required: true
    }
  },
  mounted() {
    console.log('Namespace:', this.namespace)
    console.log('Cluster Name:', this.clusterName)
    api.GetImagePullSecretList(this.namespace, this.clusterName).then(res => {
      console.log('获取secret的值：', res.data.data)
      this.imageSecrets = res.data.data
    })
  },
  data() {
    return {
      containerInfoData: this.value,
      selectedContainerIndex: null,
      imageSecrets: [],
      isCommandChecked: false,
      isPortsChecked: false,
      isEnvChecked: false,
      isResourceChecked: false,
      isHealthCheckEnabled: false,
      isLivenessProbeChecked: false,
      isReadinessProbeChecked: false,
      isStartupProbeChecked: false,
      isVolumeChecked: false,
      pvcList: [],
      configMapList: [],
      secretList: []
    }
  },
  watch: {
    containerInfoData: {
      handler(newVal) {
        this.$emit('input', newVal)
      },
      deep: true
    },
    'containerInfoData[selectedContainerIndex].volumeMounts': {
      handler(newVal) {
        this.pvcList = newVal.filter(volume => volume.type === 'persistentVolumeClaim').map(volume => volume.name)
        this.configMapList = newVal.filter(volume => volume.type === 'configMap').map(volume => volume.name)
        this.secretList = newVal.filter(volume => volume.type === 'secret').map(volume => volume.name)
      },
      deep: true
    }
  },
  methods: {
    addContainer(type) {
      this.containerInfoData.push({
        name: '',
        image: '',
        imagePullPolicy: 'Always',
        imagePullSecret: '',
        env: [],
        replicas: 1,
        workingDir: '',
        command: '',
        args: '',
        type: type,
        ports: [],
        resources: {
          limits: {
            cpu: '',
            memory: ''
          },
          requests: {
            cpu: '',
            memory: ''
          }
        },
        livenessProbe: {},
        readinessProbe: {},
        startupProbe: {},
        securityContext: {
          privileged: false
        },
        volumeMounts: []
      })
      this.selectedContainerIndex = this.containerInfoData.length - 1
    },
    removeContainer(index) {
      this.containerInfoData.splice(index, 1)
      if (this.selectedContainerIndex === index) {
        this.selectedContainerIndex = null
      } else if (this.selectedContainerIndex > index) {
        this.selectedContainerIndex--
      }
    },
    selectContainer(index) {
      console.log("Selected container index:", index)
      this.selectedContainerIndex = index
    },
    addEnvVariable(index) {
      this.containerInfoData[index].env.push({ name: '', value: '' })
    },
    removeEnvVariable(index, selectedContainerIndex) {
      this.containerInfoData[selectedContainerIndex].env.splice(index, 1)
    },
    handleCheckboxCommandChange(value) {
      if (!value) {
        this.containerInfoData[this.selectedContainerIndex].workingDir = ''
        this.containerInfoData[this.selectedContainerIndex].command = ''
        this.containerInfoData[this.selectedContainerIndex].args = ''
      }
    },
    handleCheckboxEnvChange(value) {
      if (!value) {
        this.containerInfoData[this.selectedContainerIndex].env = []
      }
    },
    addPortVariable(selectedContainerIndex) {
      this.containerInfoData[selectedContainerIndex].ports.push({ name: '', number: '', protocol: 'TCP' })
    },
    removePortVariable(index, selectedContainerIndex) {
      this.containerInfoData[selectedContainerIndex].ports.splice(index, 1)
    },
    handleCheckboxPortsChange(value) {
      if (!value) {
        this.containerInfoData[this.selectedContainerIndex].ports = []
      }
    },
    handleCheckboxResourceChange(value) {
      if (!value) {
        this.containerInfoData[this.selectedContainerIndex].resources = {
          limits: {
            cpu: '',
            memory: ''
          },
          requests: {
            cpu: '',
            memory: ''
          }
        }
      }
    },
    handleHealthCheckToggle(value) {
      if (!value) {
        this.isLivenessProbeChecked = false
        this.isReadinessProbeChecked = false
        this.isStartupProbeChecked = false
        this.containerInfoData[this.selectedContainerIndex].livenessProbe = null
        this.containerInfoData[this.selectedContainerIndex].readinessProbe = null
        this.containerInfoData[this.selectedContainerIndex].startupProbe = null
      }
    },
    handleProbeCheckboxChange(probeType) {
      if (this[`is${probeType.charAt(0).toUpperCase() + probeType.slice(1)}Checked`]) {
        this.$set(
          this.containerInfoData[this.selectedContainerIndex],
          probeType,
          this.initProbeData()
        )
      } else {
        this.$set(
          this.containerInfoData[this.selectedContainerIndex],
          probeType,
          null
        )
      }
    },
    initProbeData() {
      return {
        enabled: true,
        type: 'http',
        http: {
          protocol: 'HTTP',
          path: '',
          port: '',
          headerName: '',
          headerValue: '',
          initialDelaySeconds: 20,
          periodSeconds: 3,
          timeoutSeconds: 3,
          successThreshold: 1,
          failureThreshold: 5
        },
        tcp: {
          port: '',
          initialDelaySeconds: 20,
          periodSeconds: 3,
          timeoutSeconds: 3,
          successThreshold: 1,
          failureThreshold: 5
        },
        command: {
          command: '',
          args: '',
          initialDelaySeconds: 20,
          periodSeconds: 3,
          timeoutSeconds: 3,
          successThreshold: 1,
          failureThreshold: 5
        }
      }
    },
    handleHealthCheckChange(probeType, probeData) {
      this.$set(
        this.containerInfoData[this.selectedContainerIndex],
        probeType,
        JSON.parse(JSON.stringify(probeData))
      )
    },
    handlePrivilegedChange(value) {
      if (value) {
        this.$set(this.containerInfoData[this.selectedContainerIndex], 'securityContext', {
          privileged: true
        })
      } else {
        this.$set(this.containerInfoData[this.selectedContainerIndex], 'securityContext', {})
      }
    },
    // 获取存储声明列表
    getPvcList() {
      api.GetPvcList(this.namespace, this.clusterName).then(res => {
        this.pvcData = res.data.data || []
        this.pvcList = this.pvcData.map(item => item.pvc_name)
      })
    },

    // 获取配置项列表
    getConfigMapList() {
      api.GetConfigMapList(this.namespace, this.clusterName).then(res => {
        this.configMapData = res.data.data || []
        this.configMapList = this.configMapData.map(item => item.configmap_name)
      })
    },

    // 获取保密字典列表
    getSecretList() {
      api.GetSecretList(this.namespace, this.clusterName).then(res => {
        this.secretData = res.data.data || []
        this.secretList = this.secretData.map(item => item.secret_name)
      })
    },
    generateRandomId() {
    // 生成5位随机数字字母组合
      const characters = 'abcdefghijklmnopqrstuvwxyz0123456789'
      let result = ''
      for (let i = 0; i < 5; i++) {
        result += characters.charAt(Math.floor(Math.random() * characters.length))
      }
      return result
    },
    addVolumeMount(selectedContainerIndex) {
      const newVolume = {
        type: '',
        name: `volume-${this.generateRandomId()}`,
        mountPath: '',
        subPath: '',
        readOnly: false,
        // 不同类型的具体配置
        hostPath: {
          path: '',
          type: ''
        },
        configMap: {
          name: '',
          defaultMode: 420,
          items: []
        },
        secret: {
          secretName: '',
          defaultMode: 420,
          items: []
        },
        persistentVolumeClaim: {
          claimName: ''
        }
      }
      this.containerInfoData[selectedContainerIndex].volumeMounts.push(newVolume)
    },
    removeVolumeMount(index, selectedContainerIndex) {
      this.containerInfoData[selectedContainerIndex].volumeMounts.splice(index, 1)
    },
    handleCheckboxVolumeChange(value) {
      if (!value) {
        this.containerInfoData[this.selectedContainerIndex].volumeMounts = []
      }
      if (value) {
        this.getPvcList()
        this.getConfigMapList()
        this.getSecretList()
      }
    },
    handleVolumeTypeChange(type, index) {
      // 重置对应类型的特定字段
      const volume = this.containerInfoData[this.selectedContainerIndex].volumeMounts[index]
      if (type === 'emptyDir') {
        volume.emptyDir = {}
      } else if (type === 'hostPath') {
        volume.hostPath = { path: '', type: '' }
      } else if (type === 'configMap') {
        volume.configMap = { name: '', defaultMode: 420, items: [] }
      } else if (type === 'secret') {
        volume.secret = { secretName: '', defaultMode: 420, items: [] }
      } else if (type === 'persistentVolumeClaim') {
        volume.persistentVolumeClaim = { claimName: '' }
      }
    }
  },
  components: {
    HealthCheck
  }
}
</script>

<style scoped>
.container-list {
  margin-top: 10px;
}
.env-item {
  margin-bottom: 10px;
}
.container-name {
  margin-top: 5px;
}
.is-warning {
  background-color: #f6f4e6;
}
.is-primary {
  background-color: #e6f5ff;
}
</style>
