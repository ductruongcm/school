<template>
    <div class="setPassword">
        <form @submit.prevent="handleSubmit">
            <div>Xin chào {{ name }}! Hãy thiết lập mật khẩu để đăng nhập</div>
            <label>Password</label> <br>
            <input type="password" v-model="password" required> <br>
            <label>Re-type password</label> <br>
            <input type="password" v-model="rePassword" required> <br>
        
            <button type="submit">Xác nhận</button>
            <button type="reset">Nhập lại từ đầu</button>
        </form>
        <div>{{ message }}</div>
    </div>

</template>
<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import router from '../router'

const name = ref('')
const password = ref('')
const rePassword = ref('')
const token = new URLSearchParams(window.location.search).get('token')
const userId = ref('')
const message = ref('')

const fetchUserInfo = async () => {
    try{
        const payload = {token: token}
        const res = await axios.post('api/auth/tmp_token', payload, {
            headers: {'Content-Type': 'application/json'}
        })
        userId.value = res.data.data.id
        name.value = res.data.data.username
    } catch (e) {
        router.push('/')
    }
}

onMounted(() => {
    if (!token) {
        router.push('/')
    }
    fetchUserInfo()
})

const handleSubmit = async () => {
    const payload = {
        password: password.value,
        repassword: rePassword.value,
        token: token
    }

    try {
        await axios.post(`/api/users/${userId.value}/password`, payload, {
        headers: {"Content-Type": "application/json"}
        })
        
        router.push('/')
        
    } catch (error) {
        if (error.response && error.response.status === 400 || 422 || 500) {
            message.value = error.response.data.msg
        } else {
            message.value = 'có lỗi xảy ra!!'
        }        
    }
}

</script>
<style scoped>
.setPassword {
    position: relative;
    justify-items: center;
    top: 8em;
}
</style>