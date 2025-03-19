<template>
  <div class="app-container">
    <router-view />
  </div>
</template>

<script setup>
// App根组件
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', Arial, sans-serif;
}

.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}
</style> 