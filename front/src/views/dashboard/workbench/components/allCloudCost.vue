<template>
  <el-card
    class="card-view"
    :style="{
      backgroundColor: randomColor(),
    }"
  >
    <div id="costChart" :style="{width: pxData.wpx+'px',height: pxData.hpx+'px'}"></div>
  </el-card>
</template>

<script>
import { request } from '@/api/service'

export default {
  sort: 20,
  title: '所有云账号费用',
  name: 'allCloudCost',
  icon: 'el-icon-s-data',
  description: '所有云账号费用',
  height: 28,
  width: 30,
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
  watch: {
    pxData: {
      handler () {
        // eslint-disable-next-line no-unused-expressions
        this.myChart?.resize({ width: this.pxData.wpx, height: this.pxData.hpx })
      },
      immediate: true,
      deep: true
    }
  },
  data () {
    this.myChart = null
    return {
      data: []
    }
  },
  mounted() {
    this.myChart = this.$echarts.init(document.getElementById('costChart'))
    this.initGet()
  },
  methods: {
    initGet () {
      request({
        url: '/api/system/datav/month_cost_count/'
      }).then((res) => {
        this.data = res.data
        this.drawChart(this.data)
      })
    },
    sortedDataList() {
      return this.data.sort((a, b) => b.total_price - a.total_price)
    },
    randomColor () {
      const color = ['#fffff']
      const ran = Math.floor(Math.random() * 4)
      return color[ran]
    },
    drawChart() {
      // 获取chart容器
      // const chartContainer = this.$refs.chart
      // // 初始化echarts实例
      // const myChart = echarts.init(chartContainer)
      // 构造x轴和y轴的数据
      const xAxisData = []
      const yAxisData = []
      this.data.forEach(item => {
        xAxisData.push(item.bill_cycle)
        yAxisData.push(item.total_price)
      })
      // 配置柱状图的选项
      const options = {
        title: {
          text: '前12个月所有云账号费用汇总',
          textStyle: {
            color: '#666666',
            fontSize: 14,
            fontWeight: '600'
          },
          left: 'center'
        },
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.8)',
          textStyle: {
            color: '#666'
          },
          axisPointer: {
            lineStyle: {
              color: '#999',
              type: 'dotted',
              width: 1
            }
          },
          formatter: params => {
            const param = params[0]
            return `<div style="padding: 8px;"><div style="color: #333;">${param.name}</div><div style="color: #FFA500;">${param.value} 元</div></div>`
          }
        },
        xAxis: {
          // type: 'category',
          data: xAxisData,
          boundaryGap: true,
          axisLine: {
            lineStyle: {
              color: '#aaa',
              width: 1
            }
          },
          axisLabel: {
            interval: 0,
            maxInterval: 1,
            rotate: 0,
            textStyle: {
              color: '#333',
              fontSize: 10
            }
          }
        },
        yAxis: {
          // type: 'value',
          axisLine: {
            lineStyle: {
              color: '#aaa',
              width: 1
            }
          },
          axisLabel: {
            textStyle: {
              color: '#333',
              fontSize: 12
            }
          },
          splitLine: {
            lineStyle: {
              color: '#ddd',
              type: 'dotted',
              width: 1
            }
          }
        },
        grid: {
          top: 40,
          left: 50,
          right: 65,
          bottom: 50
        },
        series: [{
          type: 'bar',
          data: yAxisData,
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(0, 128, 255, 1)'
                },
                {
                  offset: 1,
                  color: 'rgba(0, 128, 255, 0.2)'
                }
              ]
            }
          }
        }]
      }
      // 使用配置绘制柱状图
      this.myChart.setOption(options)
    }
  }
}
</script>

<style scoped lang="scss">
.card-view {
  //border-radius: 10px;
  color: $color-primary;
}

.el-card {
  height: 100%;
}
</style>
