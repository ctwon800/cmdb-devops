<template>
  <div style="" class="*">
    <div ref="xterm" class="terminal"  :style="styleVar" ></div>
  </div>
</template>

<script>
import 'xterm/css/xterm.css'
import { Terminal } from 'xterm'
import { FitAddon } from 'xterm-addon-fit'

export default {
  name: 'xterm',
  props: {
    ip: { type: String }, // 通过父组件传递登录ip
    height: {
      type: Number, // xterm显示屏幕，高度
      default: 100
    }
  },
  data() {
    return {
      term: null,
      socket: null,
      recorder: null,
      recording: false,
      videoBlob: null
    }
  },
  computed: { // 动态设置xterm显示屏幕高度
    styleVar() {
      return {
        '--terminal-height': this.height + 'vh'
      }
    }
  },
  mounted() { // 初始化链接
    this.init()
    this.initSocket()
  },
  beforeDestroy() { // 退出销毁链接
    this.socket.close()
    this.term.dispose()
  },
  methods: {
    init() { // 初始化Terminal
      // windows.addE
      // this.ip = this.$route.query.remoteIp
      this.instanceId = this.$route.query.instanceId
      this.username = this.$route.query.username
      this.term = new Terminal({
        fontSize: 16,
        rows: this.rows,
        convertEol: true, // 启用时，光标将设置为下一行的开头
        rendererType: 'canvas', // 渲染类型
        cursorBlink: true, // 光标闪烁
        cursorStyle: 'block', // 光标样式 underline
        scrollback: 300,
        tabStopWidth: 4,
        theme: {
          background: '#060101', // 背景色
          foreground: '#ECECEC',
          cursor: 'help' // 设置光标
        }
      })
    },
    initSocket() { // 初始化Websocket
      const fitPlugin = new FitAddon()
      this.term.loadAddon(fitPlugin)
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const usernameInstanceId = this.username + '&' + this.instanceId
      // const baseURL = util.baseURL()
      // this.socket = new WebSocket(`${protocol}//${window.location.host}/socket/ws/ssh/${this.ip}`)
      // this.socket = new WebSocket(`${protocol}//${baseURL}/socket/ws/ssh/${this.ip}`)
      this.socket = new WebSocket(`${protocol}//${window.location.host}/socket/ws/ssh/${usernameInstanceId}`)
      this.socket.onmessage = e => {
        const reader = new window.FileReader()
        reader.onload = () => this.term.write(reader.result)
        reader.readAsText(e.data)
      }

      this.socket.onopen = () => {
        this.term.open(this.$refs.xterm)
        // this.term.loadWebfontAndOpen(this.$refs.xterm)
        this.term.focus()
        fitPlugin.fit()
      }

      this.socket.onclose = e => {
        if (e.code === 1000) { // 结束标记
          window.location.href = 'about:blank'
          window.close()
        } else {
          setTimeout(() => this.term.write('\r\nConnection is closed.\r\n'), 200)
        }
      }

      this.term.onData(data => this.socket.send(JSON.stringify({ data })))
      this.term.onResize(({ cols, rows }) => {
        this.socket.send(JSON.stringify({ resize: [cols, rows] }))
      })

      window.onresize = () => fitPlugin.fit()
    }
  }
}
</script>
<style scoped lang="scss">
.terminal {
  display: flex;
  width: 100%;
  min-height: var(--terminal-height);
  color: red;
}
.terminal > div {
  flex: 1;
}
</style>
