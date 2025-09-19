<script setup>
import TopPopup from './components/TopPopup.vue';
import { ref, provide, computed } from 'vue';
import useUserStore from './stores/user';

const userStore = useUserStore()

const username = computed(() => userStore.userInfo?.username ?? '')
const role = computed(() => userStore.userInfo?.role ?? '')

const year = ref('2025 - 2026')
provide('year', year)

function logout() {
  userStore.clearUser()
  window.location.href = '/'
}

</script>

<template>
  <div>
    <div class="header">
      <div>
        <div>Trường THPT BVD</div>
        <div>Niên khóa {{ year }}</div> 
      </div>
      <div class="topPopup"><TopPopup /></div>
      <div v-if="userStore.userInfo" class="userInfo">
        <div>{{ username }}</div>
        <div>{{ role }}</div>
        <div @click="logout" style="cursor: pointer;">Log out</div>
      </div>
    </div>
    <router-view />
  </div>
</template>

<style scoped>

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

.userInfo {
  position: absolute;
  right: 30px;
}
</style>
