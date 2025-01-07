<template>
  <div>
    <div class="probes-container">
      <div class="probe-section">
        <span style="font-size: 14px; font-weight: 500; color: #606266; margin-bottom: 10px; display: inline-block;">{{ probeTypeLabel }}</span>
        <div>
          <el-tabs v-model="localProbeData.type" type="border-card" @tab-click="handleTabChange">
            <el-tab-pane label="HTTP请求" name="http" style="margin-top: 10px; width: 50%">
              <el-form :model="localProbeData.http" v-if="localProbeData.type === 'http'">
                <el-form-item label="协议">
                  <el-select
                    v-model="localProbeData.http.protocol"
                    placeholder="选择协议"
                    style="width: 100%"
                    @change="handleFieldChange">
                    <el-option label="HTTP" value="HTTP"></el-option>
                    <el-option label="HTTPS" value="HTTPS"></el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="路径">
                  <el-input
                    v-model="localProbeData.http.path"
                    placeholder="请输入路径"
                    @input="handleFieldChange">
                  </el-input>
                </el-form-item>
                <el-form-item label="端口">
                  <el-input v-model="localProbeData.http.port" placeholder="请输入端口" @input="handleFieldChange"></el-input>
                </el-form-item>
                <el-form-item label="请求头">
                  <el-input v-model="localProbeData.http.headerName" placeholder="请输入请求头名称" @input="handleFieldChange" style="margin-bottom: 10px;"></el-input>
                  <el-input v-model="localProbeData.http.headerValue" placeholder="请输入请求头值" @input="handleFieldChange"></el-input>
                </el-form-item>
                <el-form-item label="初始延迟(秒)">
                  <el-input-number v-model="localProbeData.http.initialDelaySeconds" :min="0" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="检测间隔(秒)">
                  <el-input-number v-model="localProbeData.http.periodSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="localProbeData.http.timeoutSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="成功阈值">
                  <el-input-number v-model="localProbeData.http.successThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="失败阈值">
                  <el-input-number v-model="localProbeData.http.failureThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="TCP连接" name="tcp" style="margin-top: 10px; width: 50%">
              <el-form :model="localProbeData.tcp" v-if="localProbeData.type === 'tcp'">
                <el-form-item label="端口">
                  <el-input v-model="localProbeData.tcp.port" placeholder="请输入端口" @input="handleFieldChange"></el-input>
                </el-form-item>
                <el-form-item label="初始延迟(秒)">
                  <el-input-number v-model="localProbeData.tcp.initialDelaySeconds" :min="0" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="检测间隔(秒)">
                  <el-input-number v-model="localProbeData.tcp.periodSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="localProbeData.tcp.timeoutSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="成功阈值">
                  <el-input-number v-model="localProbeData.tcp.successThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="失败阈值">
                  <el-input-number v-model="localProbeData.tcp.failureThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
              </el-form>
            </el-tab-pane>
            <el-tab-pane label="命令行" name="exec" style="margin-top: 10px; width: 50%">
              <el-form :model="localProbeData.exec" v-if="localProbeData.type === 'exec'">
                <el-form-item label="命令">
                  <el-input v-model="localProbeData.exec.command" placeholder="请输入命令" @input="handleFieldChange"></el-input>
                </el-form-item>
                <el-form-item label="初始延迟(秒)">
                  <el-input-number v-model="localProbeData.exec.initialDelaySeconds" :min="0" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="检测间隔(秒)">
                  <el-input-number v-model="localProbeData.exec.periodSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="超时时间(秒)">
                  <el-input-number v-model="localProbeData.exec.timeoutSeconds" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="成功阈值">
                  <el-input-number v-model="localProbeData.exec.successThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
                <el-form-item label="失败阈值">
                  <el-input-number v-model="localProbeData.exec.failureThreshold" :min="1" @change="handleFieldChange"></el-input-number>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HealthCheck',
  props: {
    value: {
      type: Object,
      default: () => ({})
    },
    probeType: {
      type: String,
      required: true,
      validator: function(value) {
        return ['liveness', 'startup', 'readiness'].indexOf(value) !== -1
      }
    }
  },
  computed: {
    probeTypeLabel() {
      const typeMap = {
        liveness: '存活检查',
        startup: '启动检查',
        readiness: '就绪检查'
      }
      return typeMap[this.probeType] || ''
    }
  },
  data() {
    return {
      localProbeData: this.initializeData(),
      updateTimer: null
    }
  },
  methods: {
    initializeData() {
      if (!this.value || Object.keys(this.value).length === 0) {
        return this.getDefaultData()
      }
      return this.mergeData(this.getDefaultData(), this.value)
    },

    getDefaultData() {
      const defaultProbeSettings = {
        initialDelaySeconds: 20,
        periodSeconds: 3,
        timeoutSeconds: 3,
        successThreshold: 1,
        failureThreshold: 5
      }

      return {
        enabled: true,
        type: 'http',
        http: {
          protocol: 'HTTP',
          path: '',
          port: '',
          headerName: '',
          headerValue: '',
          ...defaultProbeSettings
        },
        tcp: {
          port: '',
          ...defaultProbeSettings
        },
        exec: {
          command: '',
          ...defaultProbeSettings
        }
      }
    },

    handleTabChange(tab) {
      const newType = tab.name
      this.resetOtherTypesData(newType)
      this.localProbeData.type = newType
      this.handleFieldChange()
    },

    resetOtherTypesData(currentType) {
      const defaultSettings = {
        initialDelaySeconds: 20,
        periodSeconds: 3,
        timeoutSeconds: 3,
        successThreshold: 1,
        failureThreshold: 5
      }

      if (currentType !== 'http') {
        this.localProbeData.http = {
          protocol: 'HTTP',
          path: '',
          port: '',
          headerName: '',
          headerValue: '',
          ...defaultSettings
        }
      }

      if (currentType !== 'tcp') {
        this.localProbeData.tcp = {
          port: '',
          ...defaultSettings
        }
      }

      if (currentType !== 'exec') {
        this.localProbeData.exec = {
          command: '',
          ...defaultSettings
        }
      }
    },

    handleFieldChange() {
      if (this.updateTimer) {
        clearTimeout(this.updateTimer)
      }
      this.updateTimer = setTimeout(() => {
        const updatedData = {
          enabled: true,
          type: this.localProbeData.type,
          [this.localProbeData.type]: this.localProbeData[this.localProbeData.type]
        }
        this.$emit('input', updatedData)
        this.$emit('change', updatedData)
      }, 300)
    },

    mergeData(defaultData, valueData) {
      if (!valueData || Object.keys(valueData).length === 0) {
        return defaultData
      }

      const mergedData = {
        ...defaultData,
        enabled: valueData.enabled ?? true,
        type: valueData.type || 'http'
      }

      mergedData[valueData.type] = {
        ...defaultData[valueData.type],
        ...(valueData[valueData.type] || {})
      }

      return mergedData
    },

    resetData() {
      this.localProbeData = this.getDefaultData()
      this.handleFieldChange()
    }
  },
  watch: {
    value: {
      handler(newVal) {
        if (!newVal || Object.keys(newVal).length === 0) {
          this.resetData()
        } else {
          this.localProbeData = this.mergeData(this.getDefaultData(), newVal)
        }
      },
      deep: true
    }
  },
  beforeDestroy() {
    if (this.updateTimer) {
      clearTimeout(this.updateTimer)
    }
  }
}
</script>

<style scoped>
.probes-container {
  margin-top: 10px;
}

.probe-section {
  margin-bottom: 20px;
  border: 1px solid #EBEEF5;
  padding: 15px;
  border-radius: 4px;
}

.probe-section:last-child {
  margin-bottom: 0;
}
</style>
