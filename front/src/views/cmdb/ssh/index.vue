<template>
    <div>
      <SSH :ip="ip" :height="100" :width="100" style="font-family: none;"/>
    </div>
</template>

<script>

// import '@/components'

export default {
  name: 'sshConnect',
  components: {
    SSH: () => import('@/components/SSH')
  },
  data() {
    return {
      ip: ''
    }
  },
  mounted() {
    console.log('989898')
    // var urlParams = new URLSearchParams(window.location.search)
    // var myIp = urlParams.get('remoteIp')
    const remoteIp = this.$router.query.remoteIp
    console.log(remoteIp)
    this.ip = this.$route.query.ip
  }
}
</script>
