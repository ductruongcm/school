<script setup>
import TopPopup from './components/TopPopup.vue';
import { ref, provide, onMounted } from 'vue';
import userUseStore from './stores/user.js'
import router from './router/index.js';
import axios from 'axios';

const year = ref('2025 - 2026')
provide('year', year)

function refreshToken(remaining) {
  const userStore = userUseStore()
  if (remaining > 0) {
    setTimeout(async () => {
      const res = await axios.get('/api/auth/refresh_token', { withCredentials: true })
      userStore.setUserInfo(res.data)
      remaining = userStore.tokenExpiresAt - 800000
      refreshToken(remaining)
    }, remaining );
  }
}

onMounted(() => {
  const userStore = userUseStore()
  
  let remaining = userStore.tokenExpiresAt - 800000
  if (remaining > 0) {
    setTimeout(() => {
      try {
        refreshToken(remaining)

      } catch (e) {
        userStore.clearUser()
        router.push('/')
      }
    }, remaining);
  }    
})

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
