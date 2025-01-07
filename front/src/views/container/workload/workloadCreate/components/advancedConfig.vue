<template>
  <div>
    <el-form label-width="120px" size="small">
      <!-- 升级策略 -->
      <el-form-item label="升级策略">
        <el-checkbox
          v-model="checkboxStatus.updateStrategy"
          @change="handleUpdateStrategyChange">
          配置升级策略
        </el-checkbox>

        <div v-if="checkboxStatus.updateStrategy" style="margin-top: 10px;">
          <el-form-item label="策略类型" label-width="120px">
            <el-select
              v-model="localData.updateStrategy.type"
              placeholder="请选择升级策略">
              <el-option label="滚动更新" value="RollingUpdate"></el-option>
              <el-option label="重新创建" value="Recreate"></el-option>
            </el-select>
          </el-form-item>

          <template v-if="localData.updateStrategy.type === 'RollingUpdate'">
            <el-form-item label="最大超出副本数" label-width="120px">
              <el-input v-model="localData.updateStrategy.rollingUpdate.maxSurge" placeholder="最大超出副本数" style="width: 200px;">
              </el-input>
            </el-form-item>
            <el-form-item label="最大不可用数" label-width="120px">
              <el-input v-model="localData.updateStrategy.rollingUpdate.maxUnavailable" placeholder="最大不可用数" style="width: 200px;">
              </el-input>
            </el-form-item>
          </template>
        </div>
      </el-form-item>

      <!-- 节点亲和性 -->
      <el-form-item label="节点亲和性">
        <el-checkbox
          v-model="checkboxStatus.nodeAffinity"
          @change="handleNodeAffinityChange">
          启用节点亲和性
        </el-checkbox>
        <div v-if="checkboxStatus.nodeAffinity" style="margin-top: 10px;">
          <el-button type="primary" size="mini" @click="addNodeAffinity">添加规则</el-button>
          <div v-for="(rule, index) in localData.nodeAffinity" :key="'node-'+index">
            <div style="display: flex; align-items: center; margin: 10px 0;">
              <el-select v-model="rule.type" style="width: 150px; margin-right: 10px;">
                <el-option label="必须满足" value="required"></el-option>
                <el-option label="尽量满足" value="preferred"></el-option>
              </el-select>
              <el-select v-model="rule.operator" style="width: 150px; margin-right: 10px;">
                <el-option label="存在" value="Exists"></el-option>
                <el-option label="不存在" value="DoesNotExist"></el-option>
                <el-option label="在列表中" value="In"></el-option>
                <el-option label="不在列表中" value="NotIn"></el-option>
              </el-select>
              <el-input v-model="rule.key" placeholder="键" style="width: 150px; margin-right: 10px;"></el-input>
              <el-input
                v-if="['In', 'NotIn'].includes(rule.operator)"
                v-model="rule.values"
                placeholder="值(多个用逗号分隔)"
                style="width: 200px; margin-right: 10px;">
              </el-input>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeNodeAffinity(index)"></el-button>
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- Pod亲和性 -->
      <el-form-item label="Pod亲和性">
        <el-checkbox
          v-model="checkboxStatus.podAffinity"
          @change="handlePodAffinityChange">
          启用Pod亲和性
        </el-checkbox>
        <div v-if="checkboxStatus.podAffinity" style="margin-top: 10px;">
          <el-button type="primary" size="mini" @click="addPodAffinity">添加规则</el-button>
          <div v-for="(rule, index) in localData.podAffinity" :key="'pod-'+index">
            <div style="display: flex; align-items: center; margin: 10px 0;">
              <el-select v-model="rule.type" style="width: 150px; margin-right: 10px;">
                <el-option label="亲和" value="affinity"></el-option>
                <el-option label="反亲和" value="antiAffinity"></el-option>
              </el-select>
              <el-select v-model="rule.level" style="width: 150px; margin-right: 10px;">
                <el-option label="必须满足" value="required"></el-option>
                <el-option label="尽量满足" value="preferred"></el-option>
              </el-select>
              <el-input v-model="rule.labelKey" placeholder="标签键" style="width: 150px; margin-right: 10px;"></el-input>
              <el-input v-model="rule.labelValue" placeholder="标签值" style="width: 150px; margin-right: 10px;"></el-input>
              <el-select v-model="rule.namespace" style="width: 150px; margin-right: 10px;">
                <el-option
                  v-for="ns in namespaceList"
                  :key="ns"
                  :label="ns"
                  :value="ns">
                </el-option>
              </el-select>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removePodAffinity(index)"></el-button>
            </div>
          </div>
        </div>
      </el-form-item>

      <!-- 容忍 -->
      <el-form-item label="容忍">
        <el-checkbox
          v-model="checkboxStatus.tolerations"
          @change="handleTolerationsChange">
          启用容忍
        </el-checkbox>
        <div v-if="checkboxStatus.tolerations" style="margin-top: 10px;">
          <el-button type="primary" size="mini" @click="addToleration">添加容忍</el-button>
          <div v-for="(toleration, index) in localData.tolerations" :key="'tol-'+index">
            <div style="display: flex; align-items: center; margin: 10px 0;">
              <el-input v-model="toleration.key" placeholder="键" style="width: 150px; margin-right: 10px;"></el-input>
              <el-select v-model="toleration.operator" style="width: 150px; margin-right: 10px;">
                <el-option label="等于" value="Equal"></el-option>
                <el-option label="存在" value="Exists"></el-option>
              </el-select>
              <el-input
                v-if="toleration.operator === 'Equal'"
                v-model="toleration.value"
                placeholder="值"
                style="width: 150px; margin-right: 10px;">
              </el-input>
              <el-select v-model="toleration.effect" style="width: 150px; margin-right: 10px;">
                <el-option label="不调度" value="NoSchedule"></el-option>
                <el-option label="尽量不调度" value="PreferNoSchedule"></el-option>
                <el-option label="不执行" value="NoExecute"></el-option>
              </el-select>
              <el-button type="danger" size="mini" icon="el-icon-delete" circle @click="removeToleration(index)"></el-button>
            </div>
          </div>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script>
import * as api from "@/views/container/workload/workloadCreate/api"

export default {
  name: 'advancedConfig',
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
    }
  },
  data() {
    return {
      localData: {
        updateStrategy: {
        },
        nodeAffinity: [],
        podAffinity: [],
        tolerations: []
      },
      checkboxStatus: {
        updateStrategy: false,
        nodeAffinity: false,
        podAffinity: false,
        tolerations: false
      },
      namespaceList: []
    }
  },
  watch: {
    localData: {
      handler(newVal) {
      // 创建一个深拷贝的 localData
        const dataToEmit = JSON.parse(JSON.stringify(newVal))

        // 如果 updateStrategy 类型是 Recreate，删除 rollingUpdate
        if (dataToEmit.updateStrategy.type === 'Recreate') {
          delete dataToEmit.updateStrategy.rollingUpdate
        }

        // 触发 input 事件，传递处理后的数据
        this.$emit('input', dataToEmit)
      },
      immediate: true,
      deep: true
    }
  },
  created() {
    this.getNamespaceList()
  },
  methods: {
    // 处理升级策略复选框变化
    handleUpdateStrategyChange(value) {
      if (!value) {
        this.localData.updateStrategy = {}
      } else {
        this.localData.updateStrategy = {
          type: 'RollingUpdate',
          rollingUpdate: {
            maxSurge: '25%',
            maxUnavailable: '25%'
          }
        }
      }
    },

    // 获取命名空间列表
    getNamespaceList() {
      api.GetNamespaceList(this.clusterName).then(res => {
        // this.namespaceList = res.data.data || []
        this.namespaceData = res.data.data || []
        this.namespaceList = this.namespaceData.map(item => item.namespace)
      })
    },

    // 节点亲和性相关方法
    handleNodeAffinityChange(value) {
      if (value) {
        // 如果勾选，添加一个默认规则
        if (!this.localData.nodeAffinity || !this.localData.nodeAffinity.length) {
          this.localData.nodeAffinity = [{
            type: 'required',
            operator: 'In',
            key: '',
            values: ''
          }]
        }
      } else {
        // 如果取消勾选，清空规则
        this.localData.nodeAffinity = []
      }
    },
    addNodeAffinity() {
      this.localData.nodeAffinity.push({
        type: 'required',
        operator: 'In',
        key: '',
        values: ''
      })
    },
    removeNodeAffinity(index) {
      this.localData.nodeAffinity.splice(index, 1)
    },

    // Pod亲和性相关方法
    handlePodAffinityChange(value) {
      if (value) {
        if (!this.localData.podAffinity || !this.localData.podAffinity.length) {
          this.localData.podAffinity = [{
            type: 'affinity',
            level: 'required',
            labelKey: '',
            labelValue: '',
            namespace: this.namespace
          }]
        }
      } else {
        this.localData.podAffinity = []
      }
    },
    addPodAffinity() {
      this.localData.podAffinity.push({
        type: 'affinity',
        level: 'required',
        labelKey: '',
        labelValue: '',
        namespace: this.namespace
      })
    },
    removePodAffinity(index) {
      this.localData.podAffinity.splice(index, 1)
    },

    // 容忍相关方法
    handleTolerationsChange(value) {
      if (value) {
        if (!this.localData.tolerations || !this.localData.tolerations.length) {
          this.localData.tolerations = [{
            key: '',
            operator: 'Equal',
            value: '',
            effect: 'NoSchedule'
          }]
        }
      } else {
        this.localData.tolerations = []
      }
    },
    addToleration() {
      this.localData.tolerations.push({
        key: '',
        operator: 'Equal',
        value: '',
        effect: 'NoSchedule'
      })
    },
    removeToleration(index) {
      this.localData.tolerations.splice(index, 1)
    }
  }
}
</script>

<style scoped>
.tips {
  color: #909399;
  font-size: 12px;
  margin-left: 10px;
}

.el-form-item {
  margin-bottom: 18px;
}

/* 嵌套的表单项样式 */
.el-form-item .el-form-item {
  margin-bottom: 12px;
  margin-left: 20px;
}
</style>
