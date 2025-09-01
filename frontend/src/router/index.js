import {createRouter, createWebHistory} from 'vue-router'
import Login from '../views/Login.vue'
import Dashboard from '../views/Dashboard.vue'
import Callback from '../views/Callback.vue'


const routes = [
    {path: '/', component: Login},
    {path: '/callback', component: Callback},
    {path: '/dashboard', component: Dashboard}
]

const router = createRouter({history: createWebHistory(), routes})

export default router