<template>
    <div class="content">
        <div class="sidebar"><sidebar @change="switchComponent"/></div>
        <div></div>
        <div class="mainContent"><MainContent :activeComponent="activeComponent"/></div>
    </div>

</template>
<script setup>
import Sidebar from '../components/Sidebar.vue';
import MainContent from '../components/MainContent.vue';
import ContentClass from '../components/Content-class.vue';
import ContentReport from '../components/Content-report.vue';
import ContentStudent from '../components/Content-student.vue';
import ContentTeacher from '../components/Content-teacher.vue';
import ContentToolClass from '../components/Content-toolClass.vue';
import ContentToolInfo from '../components/Content-toolInfo.vue';
import ContentToolStudent from '../components/Content-toolStudent.vue';
import ContentToolTeacher from '../components/Content-toolTeacher.vue';
import ContentDownload from '../components/Content-download.vue';
import ContentUpload from '../components/Content-upload.vue';
import ContentUser from '../components/Content-user.vue';
import ContentMonitoring from '../components/Content-monitoring.vue';
import axios from 'axios';
import { ref, onMounted, shallowRef } from 'vue';
import  useUserStore  from '../stores/user';


const username = ref('')
const role = ref('')
const userStore = useUserStore()

onMounted( async () => {
    username.value = userStore.userInfo.username
    role.value = userStore.userInfo.role
    
})

const activeComponent = shallowRef(ContentReport)
function switchComponent(name) {
    const map = {
        ContentReport,
        ContentClass,
        ContentTeacher,
        ContentStudent,
        ContentToolClass,
        ContentToolInfo,
        ContentToolStudent,
        ContentToolTeacher,
        ContentDownload,
        ContentUpload,
        ContentUser,
        ContentMonitoring
    }
    activeComponent.value = map[name]
}

onMounted(() => {
    const timer = new Date(userStore.userInfo.expired_at)
    const remaining = timer - Date.now()
    
    if (remaining > 30000) {
        const delay = remaining - 30000
        setTimeout(() => {
            refreshToken()
        }, delay);
    } 
})

async function refreshToken() {
    const userStore = useUserStore()
    const res = await axios.get('api/auth/refresh_token', { withCredentials: true })
    userStore.setUserInfo(res.data)
    const timer = new Date(userStore.userInfo.expired_at)
    let remaining = timer - Date.now()

    if (remaining > 30000) { 
        const delay = remaining - 30000
        setTimeout(() => {
            refreshToken()
         }, delay);
    } 
    else if (remaining > 0) {
        setTimeout(() => {
            refreshToken()
        }, 1000);
    }
}

</script>
<style scoped>
.content {
    
    margin: 0 auto;
    display: grid;
    grid-template-columns: 15% 3% 83%;
}

.mainContent {
    position: relative;
    width: 100%;
    top: 4em;
    justify-items: center;
}
.sidebar {
    position: relative;
    width: 100%;
    top: 2em;
    left: 1em;
    cursor: pointer;
}
.logout {
    cursor: pointer;
}
</style>