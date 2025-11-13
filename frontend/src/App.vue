<script setup>
import TopPopup from './components/TopPopup.vue';
import { ref, computed, onMounted } from 'vue';
import useUserStore from './stores/user';
import { userYearStore } from './stores/yearStore';
import axios from 'axios';
import { useSemesterStore } from './stores/semesterStore';

const userStore = useUserStore()
const semesterStore = useSemesterStore()
const username = computed(() => userStore.userInfo?.username ?? '')
const role = computed(() => userStore.userInfo?.role ?? '')
const yearUse = userYearStore()
const yearSearch = ref('')
const yearList = ref([])

const fetchYear = async () => {
  const res = await axios.get('http://127.0.0.1:5000/api/academic/years', {
    params: {
      year: yearSearch.value,
      is_active: true
    }
  })
  yearList.value = res.data.data
  yearUse.setYear(yearList.value[0])
}

const semesterSearch = ref('')
const semesterList = ref([])
const fetchSemester = async () => {
  const res = await axios.get('http://127.0.0.1:5000/api/academic/semesters', {
    withCredentials: true, 
    params: {
      semester: semesterSearch.value,
      is_active: true
    }
  })
  semesterList.value = res.data.data
  semesterStore.setSemester(semesterList.value[0])
}

onMounted(async () => {
  await Promise.all([
    fetchYear(),
    fetchSemester()
  ])
})

function logout() {
  axios.get('api/user/logout')
  userStore.clearUser()
  window.location.href = '/'
}

</script>

<template>
  <div>
    <div class="header">
      <div>
        <div>Trường THPT BVD</div>
        <div v-for="year in yearList" :key="year.id" :value="year.id">Niên khóa {{ year.year }}</div> 
        <div v-for="semester in semesterList" :key="semester.semester_id" :value="semester.semester_id">{{ semester.semester }}</div>
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
