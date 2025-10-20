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
import ContentDownload from '../components/class_room/Content-download.vue';
import ContentUpload from '../components/class_room/Content-upload.vue';
import ContentInfo from '../components/info/Content-info.vue';
import ContentMonitoring from '../components/monitoring/Content-monitoring.vue';
import ContentReport from '../components/report/Content-report.vue';
import ContentAddStudent from '../components/student/Content-addStudent.vue';
import ContentStudent from '../components/student/Content-Student.vue';
import ContentAddTeacher from '../components/teacher/Content-addTeacher.vue';
import ContentTeacher from '../components/teacher/Content-teacher.vue';
import ContentClass from '../components/class_room/Content-class.vue';
import ContentLessonTool from '../components/tool/Content-lessonTool.vue';
import ContentYearTool from '../components/tool/Content-yearTool.vue';
import ContentSemesterTool from '../components/tool/Content-semesterTool.vue';
import ContentUser from '../components/user/Content-user.vue';
import ContentFolder from '../components/class_room/Content-folder.vue';
import ContentScheduleTool from '../components/tool/Content-scheduleTool.vue';
import axios from 'axios';
import { ref, onMounted, shallowRef } from 'vue';
import  useUserStore  from '../stores/user';
import ContentClassTool from '../components/tool/Content-classTool.vue';

const username = ref('')
const role = ref('')
const userStore = useUserStore()

const activeComponent = shallowRef(ContentReport)
function switchComponent(name) {
    const map = {
        ContentReport,
        ContentClassTool,
        ContentYearTool,
        ContentLessonTool,
        ContentTeacher,
        ContentAddTeacher,
        ContentStudent,
        ContentAddStudent,
        ContentInfo,
        ContentDownload,
        ContentUpload,
        ContentUser,
        ContentMonitoring,
        ContentClass,
        ContentSemesterTool,
        ContentFolder,
        ContentScheduleTool
    }
    activeComponent.value = map[name]
}

onMounted(() => {
    username.value = userStore.userInfo.username
    role.value = userStore.userInfo.role
    const timer = new Date(userStore.userInfo.expired_at)
    const remaining = timer - Date.now()
   
    if (remaining > 30000) {
        const delay = remaining - 30000
        setTimeout(() => {
            refreshToken()
        }, delay);
    } 
})

const refreshToken = async () => {
    const res = await axios.post('api/auth/refresh_token', {
        withCredentials: true
    })
    userStore.setUserInfo(res.data)
    const timer = new Date(userStore.userInfo.expired_at)
    let remaining = timer - Date.now()

    if (remaining > 30000) {
        const delay = remaining - 30000
        setTimeout(() => {
            refreshToken()
        }, delay)
    } else if (remaining > 0) {
        setTimeout(() => {
            refreshToken()
        }, 1000)
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