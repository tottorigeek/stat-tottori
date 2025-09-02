<template>
  <div id="app">
    <header>
      <h1>鳥取県統計プロジェクト</h1>
    </header>
    <main>
      <HelloWorld />
    </main>
  </div>
</template>

<script>
import HelloWorld from './components/HelloWorld.vue'

export default {
  name: 'App',
  components: {
    HelloWorld
  }
}
</script>

<style>
#app {
  font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

header h1 {
  color: #42b883;
  margin-bottom: 30px;
}
</style>