<script setup>
import TopPopup from './components/TopPopup.vue';
import { ref, provide, onMounted } from 'vue';

const year = ref('2025 - 2026')
provide('year', year)

</script>

<template>
  <div class="layout">
    <div class="header">
      <div>Trường THPT BVD</div>
      <div>Niên khóa {{ year }}</div> 
      <div class="topPopup"><TopPopup /></div>
    </div>
    <router-view />
  </div>
</template>

<style scoped>
.layout {
  background-color: black;
  color: white;
  min-height: 100vh;
}

.header {
  /* display: flex; */
  position: relative;
  left: 15px;
  top: 15px
}

.topPopup {
  position: relative;
  left: 400px;
}
</style>
