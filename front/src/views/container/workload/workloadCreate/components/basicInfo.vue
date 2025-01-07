<template>
  <div>
    <el-form :model="basicInfoData" label-width="120px">
      <!-- 负载类型 -->
      <el-form-item label="工作负载类型" required>
        <el-select v-model="basicInfoData.workloadType" placeholder="请选择负载类型">
          <el-option v-for="item in workloadTypes" :key="item.value" :label="item.label" :value="item.value"></el-option>
        </el-select>
      </el-form-item>

      <!-- 工作负载名称 -->
      <el-form-item label="工作负载名称" required>
        <el-input v-model="basicInfoData.workloadName" placeholder="请输入工作负载名称"></el-input>
      </el-form-item>

      <!-- 注解 -->
      <el-form-item label="注解" :model="basicInfoData.annotations">
        <el-button type="primary" size="mini" @click="addAnnotation">+ 添加注解</el-button>
        <div v-for="(key, index) in annotationsKeys" :key="index" class="annotation">
          <el-input v-model="annotationsKeys[index]" placeholder="key" style="width: 300px; padding-left: 0px;"></el-input>
          <el-input v-model="basicInfoData.annotations[key]" placeholder="value" style="width: 500px; padding-left: 20px;"></el-input>
          <el-button
                style="margin-left: 20px;"
                type="danger"
                icon="el-icon-delete" circle
                @click="removeAnnotation(index)">
              </el-button>
        </div>
      </el-form-item>

      <!-- 标签 -->
      <el-form-item label="标签" :model="basicInfoData.labels">
        <el-button type="primary" size="mini" @click="addLabels">+ 添加标签</el-button>
        <div v-for="(key, index) in labelsKeys" :key="index" class="annotation">
          <el-input v-model="labelsKeys[index]" placeholder="key" style="width: 300px; padding-left: 0px;"></el-input>
          <el-input v-model="basicInfoData.labels[key]" placeholder="value" style="width: 500px; padding-left: 20px;"></el-input>
          <el-button
            style="margin-left: 20px;"
            type="danger"
            icon="el-icon-delete" circle
            @click="removeLabels(index)">
          </el-button>
        </div>
      </el-form-item>

      <!-- 副本数 -->
      <el-form-item label="副本数">
        <el-input-number v-model="basicInfoData.replicas" :min="1" :step="1"></el-input-number>
      </el-form-item>

    </el-form>
  </div>
</template>

<script>
export default {
  name: 'basicInfo',
  data() {
    return {
      // 初始化表单数据
      basicInfoData: {
        workloadType: '', // 负载类型
        workloadName: '', // 负载名称
        description: '', // 服务描述
        annotations: {}, // 注解
        labels: {}, // 标签
        replicas: 1 // 副本数
      },
      // 可选择的负载类型
      workloadTypes: [
        { value: 'Deployment', label: '无状态 (Deployment)' },
        { value: 'StatefulSet', label: '有状态 (StatefulSet)' },
        { value: 'DaemonSet', label: '守护进程集 (DaemonSet)' },
        { value: 'CronJob', label: '定时任务 (CronJob)' },
        { value: 'Job', label: '任务 (Job)' }
      ],
      annotationsKeys: [],
      labelsKeys: []
    }
  },
  watch: {
    // 监控workloadName的变化，自动添加和变更app：workloadName标签和注释
    'basicInfoData.workloadName'(newVal) {
      if (!this.basicInfoData.annotations.app) {
        // 添加 app: myname 注解
        this.basicInfoData.annotations.app = newVal
        this.annotationsKeys.push('app')
      } else {
        this.basicInfoData.annotations.app = newVal
      }
      if (!this.basicInfoData.labels.app) {
        // 添加 app: myname 注解
        this.basicInfoData.labels.app = newVal
        this.labelsKeys.push('app')
      } else {
        this.basicInfoData.labels.app = newVal
      }
    },
    basicInfoData: {
      handler(newVal) {
        this.$emit('input', newVal) // 触发父组件的更新
      },
      deep: true
    }
  },
  methods: {
    addAnnotation() {
      this.annotationsKeys.push('')
    },
    removeAnnotation(index) {
      const key = this.annotationsKeys[index]
      this.$delete(this.basicInfoData.annotations, key)
      this.annotationsKeys.splice(index, 1) // 从 keys 数组中删除
    },
    addLabels() {
      this.labelsKeys.push('')
    },
    removeLabels(index) {
      const key = this.labelsKeys[index]
      this.$delete(this.basicInfoData.labels, key)
      this.labelsKeys.splice(index, 1) // 从 keys 数组中删除
    },
    testSubmit() {
      console.log(this.basicInfoData)
    }
  }
}
</script>

<style scoped>
.annotation, .label {
  margin-bottom: 10px;
}
</style>
