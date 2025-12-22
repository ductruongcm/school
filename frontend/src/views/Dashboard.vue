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
import ContentAssignStudent from '../components/student/Content-assignStudent.vue';
import ContentAddTeacher from '../components/teacher/Content-addTeacher.vue';
import ContentTeacher from '../components/teacher/Content-teacher.vue';
import ContentClass from '../components/class_room/Content-class.vue';
import ContentLessonTool from '../components/tool/Content-lessonTool.vue';
import ContentYearTool from '../components/tool/Content-yearTool.vue';
import ContentSemesterTool from '../components/tool/Content-semesterTool.vue';
import ContentUser from '../components/user/Content-user.vue';
import ContentScheduleTool from '../components/tool/Content-scheduleTool.vue';
import axios from 'axios';
import { ref, onMounted, shallowRef } from 'vue';
import { useUserStore } from '../stores/user';
import ContentClassTool from '../components/tool/Content-classTool.vue';
import ContentStudent from '../components/class_room/Content-student.vue';
import ContentScoreTool from '../components/tool/Content-scoreTool.vue';
import ContentYearSummary from '../components/class_room/Content-YearSummary.vue';
import ContentPeriodSummary from '../components/class_room/Content-PeriodSummary.vue';
import ContentActivitylog from '../components/monitoring/Content-activitylog.vue';
import ContentApproveStudent from '../components/student/Content-approveStudent.vue';
import ContentStudentMain from '../components/report/Content-studentMain.vue';
import ContentStudentSchedule from '../components/report/Content-StudentSchedule.vue';
import ContentMainSchedule from '../components/report/Content-MainSchedule.vue';
import ContentAttendence from '../components/class_room/Content-attendence.vue';
import Content_weakStudents from '../components/class_room/Content_weakStudents.vue';
import ContentSummaryResult from '../components/class_room/Content-SummaryResult.vue';
import ContentRetest from '../components/Retest/Content-Retest.vue';
import ContentDailyReport from '../components/report/Content-DailyReport.vue';
import ContentTeacherSchedule from '../components/report/Content-TeacherSchedule.vue';
import { watch } from 'vue';
const username = ref('')
const role = ref('')
const userStore = useUserStore()

const roleComponentMap = {
  admin: ContentReport,
  Student: ContentStudentSchedule,
  Teacher: ContentTeacherSchedule
}

const activeComponent = shallowRef(null)

watch(
  () => userStore.userInfo.role,
  (role) => {
    if (!activeComponent.value && role) {
      activeComponent.value = roleComponentMap[role]
    }
  },
  { immediate: true }
)


function switchComponent(name) {
    const map = {
        ContentReport,
        ContentClassTool,
        ContentYearTool,
        ContentLessonTool,
        ContentTeacher,
        ContentAddTeacher,
        ContentAssignStudent,
        ContentAddStudent,
        ContentInfo,
        ContentDownload,
        ContentUpload,
        ContentUser,
        ContentMonitoring,
        ContentClass,
        ContentSemesterTool,
        ContentStudentMain,
        ContentScheduleTool,
        ContentStudent,
        ContentScoreTool,
        ContentYearSummary,
        ContentPeriodSummary,
        ContentActivitylog,
        ContentApproveStudent,
        ContentStudentSchedule,
        ContentMainSchedule,
        ContentAttendence, 
        Content_weakStudents,
        ContentSummaryResult,
        ContentRetest,
        ContentDailyReport,
        ContentTeacherSchedule
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