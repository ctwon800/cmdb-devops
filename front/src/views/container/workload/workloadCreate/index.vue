<template>
  <d2-container>
    <div>
      <el-header>
        <div class="yxt-flex-between">
          <div>
            <el-tag>创建工作负载</el-tag>
          </div>
          <div>
            <el-button-group>
              <el-button
                type="primary"
                size="small"
                icon="el-icon-folder-add"
                @click="workloadCancelButton"
              >
                取消
              </el-button>
              <el-button
                size="small"
                type="warning"
                icon="el-icon-edit-outline"
                @click="workloadSubmitButton"
              >
                保存
              </el-button>
            </el-button-group>
          </div>
        </div>
      </el-header>
    </div>
    <el-tabs type="border-card" v-model="editableTabsValue">
      <el-tab-pane label="基本信息" name="basicInfo">
        <basicInfo
          v-model="formData.basicInfoData"
          :namespace="namespace"
          :clusterName="clusterName"
        ></basicInfo>
      </el-tab-pane>
      <el-tab-pane label="容器信息" name="containerInfo">
        <containerInfo
          v-model="formData.containerInfoData"
          :namespace="namespace"
          :clusterName="clusterName"
        ></containerInfo>
      </el-tab-pane>
      <el-tab-pane label="高级配置" name="advancedConfig">
        <advancedConfig
          v-model="formData.advancedConfigData"
          :namespace="namespace"
          :clusterName="clusterName"
        ></advancedConfig>
      </el-tab-pane>
      <el-tab-pane label="服务/应用路由" name="serviceRoute">
        <serviceRoute
          v-model="formData.serviceRouteData"
          :namespace="namespace"
          :clusterName="clusterName"
          :workloadName="formData.basicInfoData.workloadName"
          :basicInfoData="formData.basicInfoData"
        ></serviceRoute>
      </el-tab-pane>
    </el-tabs>
  </d2-container>
</template>

<script>
import basicInfo from '@/views/container/workload/workloadCreate/components/basicInfo'
import * as api from './api'
import containerInfo from '@/views/container/workload/workloadCreate/components/containerInfo'
import advancedConfig from '@/views/container/workload/workloadCreate/components/advancedConfig'
import serviceRoute from '@/views/container/workload/workloadCreate/components/serviceRoute'
export default {
  name: 'workloadCreate',
  components: {
    basicInfo,
    containerInfo,
    advancedConfig,
    serviceRoute
  },
  data () {
    return {
      formData: {
        basicInfoData: {},
        containerInfoData: [],
        advancedConfigData: {},
        serviceRouteData: {},
        namespace: '',
        clusterName: ''
      },
      editableTabsValue: 'basicInfo',
      namespace: this.namespace,
      clusterName: this.clusterName
    }
  },
  watch: {
    // 添加这个 watch 来监听 basicInfoData 的变化
    'formData.basicInfoData': {
      handler(newVal) {
        console.log('basicInfoData changed:', newVal)
      },
      deep: true
    }
  },
  created() {
    this.namespace = this.$route.query.namespace
    this.clusterName = this.$route.query.clusterName
    console.log('0090909')
    console.log(this.namespace, this.clusterName)
  },
  methods: {
    workloadCancelButton() {
      this.$router.push({ name: 'deployment' })
    },
    workloadSubmitButton() {
      api.createWorkload(this.formData).then(response => {
        // 处理消息对象
        let message = response.data
        if (typeof message === 'object') {
          // 如果是对象，将所有消息组合成字符串
          message = Object.values(message).join(',')
        }
        console.log(message)
        this.$message({
          showClose: true,
          message: message,
          type: 'success'
        })
        // 跳转到 deployment 页面
        this.$router.push({ name: 'deployment' })
      })
    }
  }
}
</script>

<style scoped>

</style>
