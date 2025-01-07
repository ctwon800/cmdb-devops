<template>
  <el-card shadow="always" class="card-view">
    <div>
      <el-date-picker
        v-model="billTime"
        type="month"
        align="left"
        placeholder="选择月" style="width: 120px">
      </el-date-picker>
      <div id="monthCostChart" :style="{width: pxData.wpx+'px',height: pxData.hpx+'px'}"></div>
    </div>
    <!-- <div ref="chart" style="width: 400px; height: 210px;"> -->
    <!-- </div> -->
  </el-card>
</template>

<script>
import { GetAccountMonthCost } from '@/views/cmdb/cloudCost/api'
import moment from 'moment'

export default {
  sort: 19,
  title: '云账号月费用',
  name: 'monthCostDistribute',
  icon: 'el-icon-coin',
  description: '云账号月费用',
  height: 28,
  width: 18,
  isResizable: true,
  props: {
    pxData: {
      type: Object,
      require: false,
      default: () => ({
        wpx: 0,
        hpx: 0
      })
    }
  },
  data () {
    return {
      billTime: moment().subtract(1, 'month').toDate(),
      monthList: [{
        bill_cycle: ''
      }]
    }
  },
  watch: {
    billTime(newparms) {
      // 调用接口获取数据
      console.log(newparms)
      this.getAccountMonthCostList(newparms).then(res => {
        this.chatData = res.data.data
        this.renderChart()
      })
        .catch((error) => {
          console.error(error)
        })
    },
    pxData: {
      handler () {
        // eslint-disable-next-line no-unused-expressions
        this.myChart?.resize({ width: this.pxData.wpx, height: this.pxData.hpx })
      },
      immediate: true,
      deep: true
    }
  },
  mounted() {
    this.myChart = this.$echarts.init(document.getElementById('monthCostChart'))
    this.initGet()
  },
  methods: {
    initGet () {
      this.getAccountMonthCostList(this.billTime).then(res => {
        this.chatData = res.data.data
        this.renderChart()
      })
        .catch((error) => {
          console.error(error)
        })
    },
    getAccountMonthCostList(param) {
      return GetAccountMonthCost(param)
    },
    randomColor () {
      const color = ['#fffff']
      const ran = Math.floor(Math.random() * 4)
      return color[ran]
    },
    renderChart() {
      const data = this.chatData
      // const chart = echarts.init(this.$refs.chart)
      const option = {
        title: {
          text: '当前月份云账号费用饼状图',
          textStyle: {
            color: '#666666',
            fontSize: 14,
            fontWeight: '600'
          },
          left: 'center',
          top: 0
        },
        grid: {
          top: 0
          // left: 50,
          // right: 65,
          // bottom: 50
        },
        series: [
          {
            name: '数据',
            type: 'pie',
            radius: '30%',
            center: ['50%', '50%'],
            label: {
              position: 'outside',
              show: true,
              formatter: '{b} {c}元'
            },
            emphasis: {
              label: {
                position: 'inside',
                show: true,
                formatter: '{d}%'
              }
            },
            // tooltips: {
            //   trigger: 'item'
            // },
            data: data.map(item => ({
              name: item.account_name,
              value: item.cost
            })),
            itemStyle: {
              emphasis: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: 'rgba(0, 0, 0, 0.5)'
              }
            }
          }]
      }
      this.myChart.setOption(option)
    }
  }
}
</script>

<style scoped lang="scss">
.card-view {
  color: $color-primary;
}

.el-card {
  height: 100%;
}
</style>
