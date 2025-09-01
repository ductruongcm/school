<template>
    <div>Đang xác thực...</div>
</template>
<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
const router = useRouter()

onMounted(async () => {
    try {
        const res = await axios.get('http://localhost:5000/api/auth/user_info', {withCredentials: true})
        const userInfo = res.data
        const username = userInfo.username
        router.push(`/dashboard?username=${username}`)
    } catch (err) {
        router.push('/')
    }    
})

</script>