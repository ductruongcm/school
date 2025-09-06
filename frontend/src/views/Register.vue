<template>
    <div class="register">
        <div>Đăng ký làm thành viên của trường chúng tôi</div>
        <form @submit.prevent="handleSubmit">
            <label>Username</label> <br>
            <input type="text" v-model="username" required> <br>
            <label>Password</label> <br>
            <input type="password" v-model="password" required> <br>
            <label>Re-type password</label> <br>
            <input type="password" v-model="rePassword" required> <br>
            <label>Name</label> <br>
            <input type="text" v-model="name" required> <br>
            <label>Email</label> <br>
            <input type="email" v-model="email" required> <br>
            <button type="submit">Đăng ký</button>
            <button type="reset">Nhập lại từ đầu</button>
        </form>
        <div>{{ message }}</div>
    </div>

</template>
<script setup>
import { ref } from 'vue'
import axios from 'axios'
import router from '../router'

const username = ref('')
const password = ref('')
const rePassword = ref('')
const name = ref('')
const email = ref('')
let message = ref('')

const handleSubmit = async () => {
    const payload = {
        username: username.value,
        password: password.value,
        repassword: rePassword.value,
        name: name.value,
        email: email.value
    }

    try {
        await axios.post("/api/auth/register", payload, {
        headers: {"Content-Type": "application/json"}
        })
        router.push('/')
    } catch (error) {
        if (error.response && error.response.data) {
            message.value = error.response.data.msg
        } else {
            message.value = 'có lỗi xảy ra!!'
        }        
    }
}


</script>
<style scoped>
.register {
    position: relative;
    justify-items: center;
    top: 200px;
}
</style>