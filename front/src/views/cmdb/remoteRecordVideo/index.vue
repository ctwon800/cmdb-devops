<template>
    <div id="asciinemaPlayer"></div>
</template>

<script>

import * as AsciinemaPlayer from 'asciinema-player'
import 'asciinema-player/dist/bundle/asciinema-player.css'

export default {
  name: 'remoteRecordVideo',
  mounted() {
    this.recordVideoPath = this.$route.query.recordVideoPath
    AsciinemaPlayer.create(this.recordVideoPath, document.getElementById('asciinemaPlayer'), {
      loop: true,
      theme: 'solarized-dark',
      autoPlay: true,
      speed: 1,
      cols: 196,
      rows: 43
    })
  }
}
</script>

<style lang="scss">
</style>
