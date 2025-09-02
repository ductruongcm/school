<template>
    <div>
        <div>{{ username }}</div>
        <div>{{ role }}</div>
    </div>
</template>
<script setup>
import axios from 'axios';
import {useRouter} from 'vue-router';
import { ref, onMounted } from 'vue';
const router = useRouter()

const username = ref('')
const role = ref('')

const fetchUserInfo = async() => {
    const res = await axios.get('http://localhost:5000/api/auth/user_info', {withCredentials: true})
    return res.data
}

const refrestToken = async() => {
    const res = await axios.get('http://localhost:5000/api/auth/refresh_token', {withCredentials: true})
    return res.data
}
 
onMounted(async () => {
    try{
        const userInfo = await fetchUserInfo()
        username.value = userInfo.username
        role.value = userInfo.role
    } catch (err) {
        try{
            const userInfo = await refrestToken()
            username.value = userInfo.username
            role.value = userInfo.role
        } catch (err) {
            router.push('/')
        }        
    }
})


</script>