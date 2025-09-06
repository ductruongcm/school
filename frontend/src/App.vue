<script setup>
import routes from './router/index.js'
</script>

<template>
  <div class="layout">
    <div class="header">
      <div>Trường THPT BVD</div>
      <div class="topPopup"><TopPopup /></div>
    </div>
    <router-view />
  </div>
</template>
<script>
import TopPopup from './components/TopPopup.vue';

</script>
<style scoped>
.layout {
  background-color: black;
  color: white;
  min-height: 100vh;
}

.header {
  display: flex;
  position: relative;
  left: 15px;
  top: 15px
}

.topPopup {
  position: relative;
  left: 400px;
}
</style>
