<template>
    <div class="userInfo">
        <div>{{ username }}</div>
        <div>{{ role }}</div>
        <div @click="logout" class="logout">Log out</div>
    </div>

    <div class="content">
        <div class="sidebar"><sidebar @change="switchComponent"/></div>
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
import { shallowRef } from 'vue';
import axios from 'axios';
import {useRouter} from 'vue-router';
import { ref, onMounted } from 'vue';
import  useUserStore  from '../stores/user';

const username = ref('')
const role = ref('')
const userStore = useUserStore()

onMounted( async () => {
    username.value = userStore.userInfo.username
    role.value = userStore.userInfo.role
})

const logout = async () => {
    axios.get('api/auth/logout', {withCredentials: true})
    userStore.clearUser()
    window.location.href = '/'
} 

const activeComponent = shallowRef(ContentClass)
function switchComponent(name) {
    const map = {
        ContentClass,
        ContentTeacher,
        ContentStudent,
        ContentReport,
        ContentToolClass,
        ContentToolInfo,
        ContentToolStudent,
        ContentToolTeacher
    }
    activeComponent.value = map[name]
}

   




</script>
<style scoped>
.userInfo {
    position: absolute;
    right: 25px;
}
.content {
    display: flex
}

.mainContent {
    position: relative;
    left: 45em;
    top: 4em;
}
.sidebar {
    position: relative;
    left: 2em;
    top: 4em
}
.logout {
    cursor: pointer;
}
</style>