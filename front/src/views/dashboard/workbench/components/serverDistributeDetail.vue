<template>
  <el-card class="card-view" shadow="always"
           :style="{backgroundColor:randomColor(),color: config?.fontColor?.value}">
    <div style="display:flex;flex: 1; flex-wrap: wrap;justify-content: space-between; margin-top: 10px;"
         :style="{color: config?.fontColor?.value}">
      <div style="flex: 1; min-width: 180px;max-width:180px;height: 80px; display: flex;">
        <el-col :span="4" class="lightgreen-box">
          <div class="underline">
            <i class="el-icon-s-platform"></i>
          </div>
        </el-col>
        <el-col :span="20" class="orange-box">
          <div class="enroll-time">
            <div class="enroll-number"><h3>{{ data.aliyun_server_total || 0 }}</h3>
            </div>
            <div class="enroll-text">阿里云服务器总数
            </div>
          </div>
        </el-col>
      </div>
      <div style="flex: 1;min-width: 180px;max-width:180px;height: 80px; display: flex;">
        <el-col :span="4" class="lightgreen-box">
          <div class="underline">
            <i class="el-icon-s-platform"></i>
          </div>
        </el-col>
        <el-col :span="20" class="orange-box">
          <div class="enroll-time">
            <div class="enroll-number"><h3>{{ data.aws_server_total || 0 }}</h3>
            </div>
            <div class="enroll-text">AWS服务器总数
            </div>
          </div>
        </el-col>
      </div>
      <div style="flex: 1;min-width: 180px;max-width:180px;height: 80px; display: flex;">
        <el-col :span="4" class="lightgreen-box">
          <div class="underline">
            <i class="el-icon-s-platform"></i>
          </div>
        </el-col>
        <el-col :span="20" class="orange-box">
          <div class="enroll-time">
            <div class="enroll-number"><h3>{{ data.other_server_total || 0 }}</h3>
            </div>
            <div class="enroll-text">其他
            </div>
          </div>
        </el-col>
      </div>
    </div>
  </el-card>
</template>

<script>
import { request } from '@/api/service'

export default {
  sort: 5,
  title: '服务器分布情况',
  name: 'serverDistributeDetail',
  icon: 'el-icon-s-platform',
  description: '服务器分布情况',
  height: 18,
  width: 20,
  isResizable: true,
  config: {
    color: {
      label: '背景颜色',
      type: 'color',
      value: '',
      placeholder: '颜色为空则随机变换颜色'
    },
    fontColor: {
      label: '字体颜色',
      type: 'color',
      value: '',
      placeholder: '请选择字体颜色'
    }
  },
  props: {
    config: {
      type: Object,
      required: false
    }
  },
  data () {
    return {
      data: {}
    }
  },
  mounted () {
    this.initGet()
  },
  methods: {
    initGet () {
      request({
        url: '/api/system/datav/server_distribute_detail/'
      }).then((res) => {
        this.data = res.data
      })
    },
    // 生成一个随机整数
    randomColor () {
      const color = [
        '#fffff'
      ]
      const ran = Math.floor(Math.random() * 4)
      return color[ran]
    }
  }
}
</script>

<style scoped lang="scss">
.card-view {
  // border-radius: 10px;
  color: $color-primary;
}
.enroll-number{
  color: $color-primary;
}
h3 {
  margin: 0;
}
.lightgreen-box {
  border-bottom: 2px solid;
  height: 60px;
  margin-bottom: 10px;
}

.underline i {
  font-size: 30px;
}

.orange-box {
  height: 60px;
  color: black;
  border-bottom: 2px solid rgb(242, 242, 242);
}

.enroll-time {
  margin-left: 10px;
}

.enroll-text {
  color: rgb(138, 138, 138);
}

.el-card {
  height: 100%;
}
</style>
