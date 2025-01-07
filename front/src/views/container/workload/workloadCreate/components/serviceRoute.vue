<template>
  <div>
    <el-form label-width="120px" size="small">
      <!-- 服务 -->
      <el-form-item label="服务">
        <el-checkbox
          v-model="checkboxStatus.service"
          @change="handleServiceChange">
          启用服务
        </el-checkbox>
        <div v-if="checkboxStatus.service" style="margin-top: 10px;">
          <!-- 服务名称 -->
          <el-form-item label="服务名称">
            <el-input v-model="serviceData.name" :placeholder="`请输入服务名称，默认: ${defaultServiceName}`"></el-input>
          </el-form-item>

          <!-- 服务类型 -->
          <el-form-item label="服务类型">
            <el-select v-model="serviceData.service_type" placeholder="请选择服务类型" style="width: 100%">
              <el-option label="ClusterIP" value="ClusterIP"></el-option>
              <el-option label="NodePort" value="NodePort"></el-option>
            </el-select>
          </el-form-item>

          <!-- 标签 -->
          <el-form-item label="标签">
            <el-button type="primary" size="mini" @click="addServiceLabel">添加</el-button>
            <div v-for="(key, index) in serviceLabelKeys" :key="'label-'+index" style="margin-top: 10px;">
              <el-input v-model="serviceLabelKeys[index]" placeholder="标签键" style="width: 40%; margin-right: 10px;"></el-input>
              <el-input v-model="serviceData.label[key]" placeholder="标签值" style="width: 40%; margin-right: 10px;"></el-input>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeServiceLabel(index)"></el-button>
            </div>
          </el-form-item>

          <!-- 选择器 -->
          <el-form-item label="选择器">
            <el-button type="primary" size="mini" @click="addServiceSelector">添加</el-button>
            <div v-for="(key, index) in serviceSelectorKeys" :key="'selector-'+index" style="margin-top: 10px;">
              <el-input v-model="serviceSelectorKeys[index]" placeholder="选择器键" style="width: 40%; margin-right: 10px;"></el-input>
              <el-input v-model="serviceData.selector[key]" placeholder="选择器值" style="width: 40%; margin-right: 10px;"></el-input>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeServiceSelector(index)"></el-button>
            </div>
          </el-form-item>

          <!-- 端口映射 -->
          <el-form-item label="端口映射">
            <el-button type="primary" size="mini" @click="addServicePort">添加端口</el-button>
            <div v-for="(port, index) in serviceData.portMaps" :key="'port-'+index" style="margin-top: 10px;">
              <el-input v-model="port.port_name" placeholder="端口名称" style="width: 15%; margin-right: 10px;"></el-input>
              <el-input v-model="port.service_port" placeholder="服务端口" style="width: 15%; margin-right: 10px;"></el-input>
              <el-input v-model="port.container_port" placeholder="容器端口" style="width: 15%; margin-right: 10px;"></el-input>
              <!-- NodePort类型时显示节点端口输入框 -->
              <el-input
                v-if="serviceData.service_type === 'NodePort'"
                v-model="port.node_port"
                placeholder="节点端口"
                style="width: 15%; margin-right: 10px;">
              </el-input>
              <el-select v-model="port.protocol" placeholder="协议" style="width: 15%; margin-right: 10px;">
                <el-option label="TCP" value="TCP"></el-option>
                <el-option label="UDP" value="UDP"></el-option>
              </el-select>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeServicePort(index)"></el-button>
            </div>
          </el-form-item>
        </div>
      </el-form-item>

      <!-- 路由配置 -->
      <el-form-item label="路由">
        <el-checkbox
          v-model="checkboxStatus.route"
          @change="handleRouteChange">
          启用路由
        </el-checkbox>
        <div v-if="checkboxStatus.route" style="margin-top: 10px;">
          <!-- 路由名称 -->
          <el-form-item label="路由名称">
            <el-input v-model="routeData.name" :placeholder="`请输入路由名称，默认: ${defaultRouteName}`"></el-input>
          </el-form-item>

          <!-- 路由标签 -->
          <el-form-item label="标签">
            <el-button type="primary" size="mini" @click="addRouteLabel">添加</el-button>
            <div v-for="(key, index) in routeLabelKeys" :key="'route-label-'+index" style="margin-top: 10px;">
              <el-input v-model="routeLabelKeys[index]" placeholder="标签键" style="width: 40%; margin-right: 10px;"></el-input>
              <el-input v-model="routeData.labels[key]" placeholder="标签值" style="width: 40%; margin-right: 10px;"></el-input>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeRouteLabel(index)"></el-button>
            </div>
          </el-form-item>

          <!-- 路由规则 -->
          <el-form-item label="规则">
            <el-button type="primary" size="mini" @click="addRouteRule">添加规则</el-button>
            <div v-for="(rule, index) in routeData.rules" :key="'rule-'+index" style="margin-top: 10px;">
              <!-- 域名和HTTPS设置 -->
              <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <el-input
                  v-model="rule.host"
                  placeholder="域名"
                  style="width: 60%; margin-right: 10px;">
                </el-input>
                <el-switch
                  v-model="rule.enableHttps"
                  active-text="HTTPS"
                  @change="(val) => handleHttpsChange(val, index)">
                </el-switch>
                <el-select
                  v-if="rule.enableHttps"
                  v-model="rule.tlsSecretName"
                  placeholder="选择证书"
                  style="width: 30%; margin-left: 10px;"
                  @change="updateTlsConfig">
                  <el-option
                    v-for="cert in certificates"
                    :key="cert.name"
                    :label="cert.name"
                    :value="cert.name">
                  </el-option>
                </el-select>
              </div>

              <!-- 路径规则 -->
              <div v-for="(path, pathIndex) in rule.paths" :key="'path-'+pathIndex" style="margin-bottom: 10px;">
                <el-input v-model="path.path" placeholder="路径 (例如: /api)" style="width: 30%; margin-right: 10px;"></el-input>
                <el-select
                  v-model="path.service_name"
                  placeholder="选择服务"
                  style="width: 20%; margin-right: 10px;"
                  :disabled="checkboxStatus.service">
                  <el-option
                    :label="serviceData.name"
                    :value="serviceData.name"
                    v-if="checkboxStatus.service">
                  </el-option>
                </el-select>
                <el-select
                  v-model="path.service_port"
                  placeholder="选择端口"
                  style="width: 20%; margin-right: 10px;"
                  :disabled="checkboxStatus.service">
                  <template v-if="checkboxStatus.service">
                    <el-option
                      v-for="port in serviceData.portMaps"
                      :key="port.service_port"
                      :label="port.service_port"
                      :value="port.service_port">
                    </el-option>
                  </template>
                </el-select>
                <el-button
                  type="danger"
                  size="mini"
                  icon="el-icon-delete"
                  circle
                  @click="removeRoutePath(index, pathIndex)">
                </el-button>
                <el-button
                  type="primary"
                  size="mini"
                  @click="addRoutePath(index)"
                  style="margin-left: 10px;">
                  添加路径
                </el-button>
              </div>
              <el-button
                type="danger"
                size="mini"
                @click="removeRouteRule(index)"
                style="margin-top: 10px;">
                删除规则
              </el-button>
            </div>
          </el-form-item>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import * as api from "@/views/container/workload/workloadCreate/api"
export default {
  name: 'serviceRoute',
  props: {
    value: {
      type: Object,
      default: () => ({})
    },
    namespace: {
      type: String,
      default: ''
    },
    clusterName: {
      type: String,
      default: ''
    },
    workloadName: {
      type: String,
      default: ''
    },
    basicInfoData: {
      type: Object,
      default: () => ({})
    }
  },
  data() {
    return {
      checkboxStatus: {
        service: false,
        route: false
      },
      serviceData: {
        name: '',
        service_type: 'ClusterIP',
        label: {},
        selector: {},
        portMaps: []
      },
      serviceLabelKeys: [],
      serviceSelectorKeys: [],
      routeData: {
        name: '',
        labels: {},
        rules: [],
        tls: []
      },
      routeLabelKeys: [],
      certificates: []
    }
  },
  computed: {
    defaultServiceName() {
      return this.workloadName ? `${this.workloadName}-svc` : ''
    },
    defaultRouteName() {
      return `${this.workloadName}-ingress`
    }
  },
  watch: {
    checkboxStatus: {
      handler(newVal) {
        this.updateParentData()
      },
      deep: true
    },
    serviceData: {
      handler(newVal) {
        if (this.checkboxStatus.route && this.checkboxStatus.service) {
          this.updateRouteServiceInfo()
        }
      },
      deep: true
    },
    routeData: {
      handler(newVal) {
        this.updateParentData()
      },
      deep: true
    },
    workloadName: {
      handler(newVal) {
        if (newVal && this.checkboxStatus.service) {
          this.serviceData.name = `${newVal}-svc`
        }
      },
      immediate: true
    }
  },
  methods: {
    updateParentData() {
      const data = {
        service: {
          enabled: this.checkboxStatus.service,
          ...this.serviceData
        },
        route: {
          enabled: this.checkboxStatus.route,
          ...this.routeData
        }
      }
      this.$emit('input', data)
    },
    handleServiceChange(value) {
      if (!value) {
        this.serviceData = {
          name: '',
          service_type: 'ClusterIP',
          label: {},
          selector: {},
          portMaps: []
        }
        this.serviceLabelKeys = []
        this.serviceSelectorKeys = []
      } else {
        if (this.workloadName) {
          this.serviceData.name = this.defaultServiceName
        }
        if (this.basicInfoData.labels) {
          this.updateServiceLabelsAndSelectors(this.basicInfoData.labels)
        }
        this.addServicePort()
      }
      this.updateParentData()
    },
    addServiceLabel() {
      this.serviceLabelKeys.push('')
      this.updateParentData()
    },
    removeServiceLabel(index) {
      const key = this.serviceLabelKeys[index]
      this.$delete(this.serviceData.label, key)
      this.serviceLabelKeys.splice(index, 1)
      this.updateParentData()
    },
    addServiceSelector() {
      this.serviceSelectorKeys.push('')
    },
    removeServiceSelector(index) {
      const key = this.serviceSelectorKeys[index]
      this.$delete(this.serviceData.selector, key)
      this.serviceSelectorKeys.splice(index, 1)
    },
    addServicePort() {
      this.serviceData.portMaps.push({
        port_name: '',
        service_port: '',
        container_port: '',
        node_port: '',
        protocol: 'TCP'
      })
      this.updateParentData()
    },
    removeServicePort(index) {
      this.serviceData.portMaps.splice(index, 1)
      this.updateParentData()
    },
    handleRouteChange(value) {
      if (!value) {
        this.routeData = {
          name: '',
          labels: {},
          rules: [],
          tls: []
        }
        this.routeLabelKeys = []
      } else {
        this.routeData.name = this.defaultRouteName
        try {
          // 调用获取证书列表的 API
          api.GetTlsSecretList(this.clusterName, this.namespace).then(response => {
            this.certificates = response.data.data.map(name => ({
              name: name.secret_name,
              value: name.secret_name
            }))
          })
        } catch (error) {
          console.error('获取证书列表失败:', error)
        }
        // 继承 basicInfo 的标签
        if (this.basicInfoData.labels) {
          this.updateRouteLabels(this.basicInfoData.labels)
        }
        // 添加默认规则
        this.addRouteRule()
      }
      this.updateParentData()
    },
    updateServiceLabelsAndSelectors(labels) {
      this.serviceData.label = {}
      this.serviceData.selector = {}
      this.serviceLabelKeys = []
      this.serviceSelectorKeys = []
      Object.entries(labels).forEach(([key, value]) => {
        this.serviceLabelKeys.push(key)
        this.$set(this.serviceData.label, key, value)
        this.serviceSelectorKeys.push(key)
        this.$set(this.serviceData.selector, key, value)
      })
    },
    handleServiceTypeChange(value) {
      if (value === 'NodePort') {
        this.serviceData.portMaps.forEach(port => {
          if (!port.node_port) {
            port.node_port = ''
          }
        })
      }
    },
    // 路由标签相关方法
    addRouteLabel() {
      this.routeLabelKeys.push('')
      this.updateParentData()
    },
    removeRouteLabel(index) {
      const key = this.routeLabelKeys[index]
      this.$delete(this.routeData.labels, key)
      this.routeLabelKeys.splice(index, 1)
      this.updateParentData()
    },

    // 路由规则相关方法
    addRouteRule() {
      this.routeData.rules.push({
        host: '',
        enableHttps: false,
        tlsSecretName: '',
        paths: [{
          path: '/',
          service_name: this.checkboxStatus.service ? this.serviceData.name : '',
          service_port: this.checkboxStatus.service && this.serviceData.portMaps.length > 0
            ? this.serviceData.portMaps[0].service_port
            : ''
        }]
      })
      this.updateParentData()
    },
    removeRouteRule(index) {
      this.routeData.rules.splice(index, 1)
      this.updateParentData()
    },
    addRoutePath(ruleIndex) {
      this.routeData.rules[ruleIndex].paths.push({
        path: '/',
        service_name: this.checkboxStatus.service ? this.serviceData.name : '',
        service_port: this.checkboxStatus.service && this.serviceData.portMaps.length > 0
          ? this.serviceData.portMaps[0].service_port
          : ''
      })
      this.updateParentData()
    },
    removeRoutePath(ruleIndex, pathIndex) {
      this.routeData.rules[ruleIndex].paths.splice(pathIndex, 1)
      this.updateParentData()
    },

    // 更新路由标签
    updateRouteLabels(labels) {
      this.routeData.labels = {}
      this.routeLabelKeys = []
      Object.entries(labels).forEach(([key, value]) => {
        this.routeLabelKeys.push(key)
        this.$set(this.routeData.labels, key, value)
      })
    },

    // 监听服务变化，更新路由规则中的服务信息
    updateRouteServiceInfo() {
      this.routeData.rules.forEach(rule => {
        rule.paths.forEach(path => {
          path.service_name = this.serviceData.name
          path.service_port = this.serviceData.portMaps.find(port => port.service_port === path.service_port).service_port
        })
      })
      this.updateParentData()
    },

    handleHttpsChange(val, ruleIndex) {
      const rule = this.routeData.rules[ruleIndex]
      if (val) {
        // 启用 HTTPS 时，确保 TLS 配置存在
        if (!rule.tlsSecretName) {
          rule.tlsSecretName = ''
        }
      } else {
        // 禁用 HTTPS 时，清除 TLS 配置
        rule.tlsSecretName = ''
        this.updateTlsConfig()
      }
    },

    updateTlsConfig() {
      // 重新生成 TLS 配置
      this.routeData.tls = this.routeData.rules
        .filter(rule => rule.enableHttps && rule.tlsSecretName)
        .reduce((acc, rule) => {
          const existingTls = acc.find(t => t.secretName === rule.tlsSecretName)
          if (existingTls) {
            existingTls.hosts.push(rule.host)
          } else {
            acc.push({
              hosts: [rule.host],
              secretName: rule.tlsSecretName
            })
          }
          return acc
        }, [])
      this.updateParentData()
    }
  }
}
</script>

<style scoped>
.el-form-item {
  margin-bottom: 18px;
}
/* 可以添加一些过渡动画 */
.port-input-enter-active, .port-input-leave-active {
  transition: all 0.3s;
}
.port-input-enter, .port-input-leave-to {
  opacity: 0;
  transform: translateX(10px);
}
</style>
