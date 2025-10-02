<template>
    <div>
        <form class="login" @submit.prevent="login">
            <div>Đăng nhập</div>
            <legend>  
                <label>Username</label> <br>
                <input type="text" v-model="username"> <br>
                <label>Password</label> <br>
                <input type="password" v-model="password"> <br>
                <button type="submit">Đăng nhập</button>
            </legend>
            <div @click="loginGG" class="loginGG">Đăng nhập bằng Google</div>
            <div class="forgetPassword">Quên mật khẩu</div>
            <div @click="register" class="register">Đăng ký</div>
            <div>{{ loginMsg }}</div>
        </form>
    </div>
    
</template>
<script setup>
import axios from 'axios';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { message } from '../stores/usePopup';
import useUserStore from '../stores/user';

const username = ref('')
const password = ref('')
let loginMsg = ref('')

const router = useRouter()
const userStore = useUserStore()

async function login() {
    const payload = {
        username: username.value,
        password: password.value
    }
    try {
        const res = await axios.post('/api/user/login', payload, {
            headers: {"Content-Type": "application/json"}
        })
        userStore.setUserInfo(res.data)
        
        router.push('/dashboard')
        
  
    } catch (error) {
        if (error.response && error.response.status === 400) {
            loginMsg.value = error.response.data.msg
        } else {
            loginMsg.value = 'Có lỗi xảy ra!'
        }
    }
}

async function loginGG() {
    const res = await axios.get("/api/oauth2/login_gg");
    const url = res.data;
    window.location.href = url;
}

async function register() {
    router.push('/register')
}

</script>
<style scoped>
.login {
    position: relative;
    justify-items: center;
    top: 8em;
}

.register, .forgetPassword, .loginGG {
    cursor: pointer;
}
</style>