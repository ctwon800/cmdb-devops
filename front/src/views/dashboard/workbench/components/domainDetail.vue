<template>
  <el-card class="card-view" shadow="always"
           :style="{backgroundColor:randomColor(),color: config?.fontColor?.value}">
    <div class="card-content" :style="{color: config?.fontColor?.value, flexWrap: 'nowrap'}">
      <div class="monitor-box" :style="{flex: '1 1 calc(33.33% - 10px)', minWidth: '180px', maxWidth: '300px', margin: '10px'}">
        <el-col :span="4">
          <div class="underline">
            <i class="el-icon-sunrise-1"></i>
          </div>
        </el-col>
        <el-col :span="20">
          <div class="enroll-time">
            <div class="enroll-text">监控域名数</div>
            <div class="enroll-number-domain_count"><h3>{{ data.domain_total || 0 }}</h3></div>
          </div>
        </el-col>
      </div>
      <div class="monitor-box" :style="{flex: '1 1 calc(33.33% - 10px)', minWidth: '180px', maxWidth: '300px', margin: '10px'}">
        <el-col :span="4">
          <div class="underline">
            <i class="el-icon-sunrise-1"></i>
          </div>
        </el-col>
        <el-col :span="20">
          <div class="enroll-time">
            <div class="enroll-text">即将到期域名</div>
            <div class="enroll-number"><h3>{{ data.domain_expiring_soon_name || 0 }}</h3></div>
            <div class="enroll-text">即将到期天数</div>
            <div class="enroll-number-day">
              <h3 :style="{color: data.domain_expiring_soon_days < 31 ? 'red' : ''}">{{ data.domain_expiring_soon_days || 0 }}</h3>
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
  sort: 6,
  title: '域名一览',
  name: 'domainDetail',
  icon: 'el-icon-s-cooperation',
  description: '域名一览情况',
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
        url: '/api/system/datav/domain_detail/'
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
  font-size: 18px;
  margin-left: 0px;
  margin-top: 2px;
  margin-bottom: 10px;
}
.enroll-number-day{
  color: $color-primary;
  font-size: 25px;
  margin-left: 30px;
  margin-top: 2px;
  margin-bottom: 10px;
}
.enroll-number-domain_count{
  color: $color-primary;
  font-size: 25px;
  margin-top: 10px;
  margin-left: 30px;
  margin-bottom: 10px;
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
  height: 80px;
  color: black;
  border-bottom: 2px solid rgb(242, 242, 242);
}

.enroll-time {
  margin-left: 10px;
}

.enroll-text {
  color: rgb(138, 138, 138);
  margin-left: 10px;
}

.el-card {
  height: 100%;
}
</style>
