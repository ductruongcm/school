import {createRouter, createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Dashboard from '../views/Dashboard.vue'
import ContentClass from '../components/Content-class.vue'
import ContentStudent from '../components/Content-student.vue'
import ContentTeacher from '../components/Content-teacher.vue'
import ContentReport from '../components/Content-report.vue'
import ContentToolClass from '../components/Content-toolClass.vue'
import ContentToolInfo from '../components/Content-toolInfo.vue'
import ContentToolStudent from '../components/Content-toolStudent.vue'
import ContentToolTeacher from '../components/Content-toolTeacher.vue'
import Sidebar from '../components/Sidebar.vue'
import MainContent from '../components/MainContent.vue'
import  useUserStore  from '../stores/user'
import axios from '../stores/axios'

const routes = [
    {path: '/', component: Login},
    {path: '/register', component: Register},
    {path: '/dashboard', component: Dashboard, Children: [
        {path: 'sidebar', component: Sidebar},
        {path: 'mainContent', component: MainContent, Children: [
            {path: 'class', component: ContentClass},
            {path: 'student', component: ContentStudent},
            {path: 'teacher', component: ContentTeacher},
            {path: 'report', component: ContentReport},
            {path: 'classtool', component: ContentToolClass},
            {path: 'studentool', component: ContentToolStudent},
            {path: 'teachertool', component: ContentToolTeacher},
            {path: 'Infotool', component: ContentToolInfo}
        ]}
    ]}
]

const router = createRouter({history: createWebHistory(), routes})

const publicPages = ['/', '/register']

router.beforeEach(async (to, form, next) => {
    const userStore = useUserStore()
    const authRequired = !publicPages.includes(to.path)

    if (authRequired && !userStore.userInfo) {
            return next('/')
    }
    next()
})

export default router