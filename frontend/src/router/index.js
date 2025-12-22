import {createRouter, createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import SetPassword from '../views/SetPassword.vue'
import ChangePassword from '../views/ChangePassword.vue'
import Dashboard from '../views/Dashboard.vue'
import Sidebar from '../components/Sidebar.vue'
import MainContent from '../components/MainContent.vue'
import { useUserStore } from '../stores/user'
import ContentClass from '../components/class_room/Content-class.vue'
import ContentDownload from '../components/class_room/Content-download.vue'
import ContentUpload from '../components/class_room/Content-upload.vue'
import ContentInfo from '../components/info/Content-info.vue'
import ContentMonitoring from '../components/monitoring/Content-monitoring.vue'
import ContentReport from '../components/report/Content-report.vue'
import ContentAddStudent from '../components/student/Content-addStudent.vue'
import ContentAssignStudent from '../components/student/Content-assignStudent.vue'
import ContentAddTeacher from '../components/teacher/Content-addTeacher.vue'
import ContentTeacher from '../components/teacher/Content-teacher.vue'
import ContentClassTool from '../components/tool/Content-classTool.vue'
import ContentLessonTool from '../components/tool/Content-lessonTool.vue'
import ContentYearTool from '../components/tool/Content-yearTool.vue'
import ContentUser from '../components/user/Content-user.vue'
import ContentSemesterTool from '../components/tool/Content-semesterTool.vue'
import ContentScheduleTool from '../components/tool/Content-scheduleTool.vue'
import ContentStudent from '../components/class_room/Content-student.vue'
import ContentScoreTool from '../components/tool/Content-scoreTool.vue'
import ContentPeriodSummary from '../components/class_room/Content-PeriodSummary.vue'
import ContentYearSummary from '../components/class_room/Content-YearSummary.vue'
import ContentActivitylog from '../components/monitoring/Content-activitylog.vue'
import ContentApproveStudent from '../components/student/Content-approveStudent.vue'
import ContentStudentMain from '../components/report/Content-studentMain.vue'
import ContentStudentSchedule from '../components/report/Content-StudentSchedule.vue'
import ContentMainSchedule from '../components/report/Content-MainSchedule.vue'
import ContentAttendence from '../components/class_room/Content-attendence.vue'
import Content_weakStudents from '../components/class_room/Content_weakStudents.vue'
import ContentSummaryResult from '../components/class_room/Content-SummaryResult.vue'
import ContentRetest from '../components/Retest/Content-Retest.vue'
import ContentDailyReport from '../components/report/Content-DailyReport.vue'

const routes = [
    {path: '/', component: Login},
    {path: '/setpassword', component: SetPassword},
    {path: '/changepassword', component: ChangePassword},
    {path: '/dashboard', component: Dashboard, Children: [
        {path: 'sidebar', component: Sidebar},
        {path: 'mainContent', component: MainContent, Children: [
            {path: 'report', component: ContentReport},
            {path: 'info', component: ContentInfo},
            {path: 'class', component: ContentClass},
            {path: 'assignStudent', component: ContentAssignStudent},
            {path: 'teacher', component: ContentTeacher},
            {path: 'lessonTool', component: ContentLessonTool},
            {path: 'yearTool', component: ContentYearTool},
            {path: 'classTool', component: ContentClassTool},
            {path: 'addStudent', component: ContentAddStudent},
            {path: 'addTeacher', component: ContentAddTeacher},
            {path: 'download', component: ContentDownload},
            {path: 'upload', component: ContentUpload},
            {path: 'user', component: ContentUser},
            {path: 'monitoring', component: ContentMonitoring},
            {path: 'semesterTool', component: ContentSemesterTool},
            {path: 'scheduleTool', component: ContentScheduleTool},
            {path: 'student', component: ContentStudent},
            {path: 'scoreTool', component: ContentScoreTool},
            {path: 'periodsummary', component: ContentPeriodSummary},
            {path: 'yearsummary', component: ContentYearSummary},
            {path: 'activitylog', component: ContentActivitylog},
            {path: 'approveStudent', component: ContentApproveStudent},
            {path: 'studentMain', component: ContentStudentMain},
            {path: 'studentSchedule', component: ContentStudentSchedule},
            {path: 'mainSchedule', component: ContentMainSchedule},
            {path: 'attendence', component: ContentAttendence},
            {path: 'weakStudents', component: Content_weakStudents},
            {path: 'summaryResult', component: ContentSummaryResult},
            {path: 'retest', component: ContentRetest},
            {path: 'dailyReport', component: ContentDailyReport}
        ]}
    ]}
]

const router = createRouter({history: createWebHistory(), routes})

const publicPages = ['/']

router.beforeEach(async (to, form, next) => {
    const userStore = useUserStore()
    const authRequired = !publicPages.includes(to.path)

    if (authRequired && !userStore.userInfo) {
        return next('/')
    } else if (authRequired && new Date(userStore.userInfo.expired_at) < Date.now()) {
        userStore.clearUser()
        return next('/')
    } else {
    next()
    }
})

export default router