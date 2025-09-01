<template>
    <div>
        <div>{{ username }}</div>
        <div>{{ role }}</div>
    </div>
</template>
<script setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';

const username = ref('')
const role = ref('')
// role.value = 'tùm lum tùm la'

onMounted( async () => {
    const res = await axios.get('http://localhost:5000/api/auth/user_info', {withCredentials: true})
    const userInfo = res.data
    username.value = userInfo.username
    role.value = userInfo.role
})

</script>