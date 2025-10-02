import {createRouter, createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import SetPassword from '../views/SetPassword.vue'
import Dashboard from '../views/Dashboard.vue'
import Sidebar from '../components/Sidebar.vue'
import MainContent from '../components/MainContent.vue'
import useUserStore  from '../stores/user'
import ContentClass from '../components/class_room/Content-class.vue'
import ContentDownload from '../components/class_room/Content-download.vue'
import ContentUpload from '../components/class_room/Content-upload.vue'
import ContentInfo from '../components/info/Content-info.vue'
import ContentMonitoring from '../components/monitoring/Content-monitoring.vue'
import ContentReport from '../components/report/Content-report.vue'
import ContentAddStudent from '../components/student/Content-addStudent.vue'
import ContentStudent from '../components/student/Content-Student.vue'
import ContentAddTeacher from '../components/teacher/Content-addTeacher.vue'
import ContentTeacher from '../components/teacher/Content-teacher.vue'
import ContentClassTool from '../components/tool/Content-classTool.vue'
import ContentLessonTool from '../components/tool/Content-lessonTool.vue'
import ContentYearTool from '../components/tool/Content-yearTool.vue'
import ContentUser from '../components/user/Content-user.vue'


const routes = [
    {path: '/', component: Login},
    {path: '/register', component: Register},
    {path: '/setpassword', component: SetPassword},
    {path: '/dashboard', component: Dashboard, Children: [
        {path: 'sidebar', component: Sidebar},
        {path: 'mainContent', component: MainContent, Children: [
            {path: 'report', component: ContentReport},
            {path: 'info', component: ContentInfo},
            {path: 'class', component: ContentClass},
            {path: 'student', component: ContentStudent},
            {path: 'teacher', component: ContentTeacher},
            {path: 'lessonTool', component: ContentLessonTool},
            {path: 'yearTool', component: ContentYearTool},
            {path: 'classTool', component: ContentClassTool},
            {path: 'addStudent', component: ContentAddStudent},
            {path: 'addTeacher', component: ContentAddTeacher},
            {path: 'download', component: ContentDownload},
            {path: 'upload', component: ContentUpload},
            {path: 'user', component: ContentUser},
            {path: 'monitoring', component: ContentMonitoring}
        ]}
    ]}
]

const router = createRouter({history: createWebHistory(), routes})

const publicPages = ['/', '/register', '/setpassword']

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