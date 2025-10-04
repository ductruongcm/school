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
const loginMsg = ref('')

const router = useRouter()
const userStore = useUserStore()

const login = async () => {
    const payload = {
        username: username.value,
        password: password.value
    }
    try {
        const res = await axios.post('api/user/login', payload, {
            headers: {'Content-Type': 'application/json'}
        })
        userStore.setUserInfo(res.data)
        router.push('/dashboard')
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            loginMsg.value = e.response.data.msg
        } else {
            loginMsg.value = 'Có rắc rối rồi!'
        }
    }
}

const loginGG = async () => {
    const res = await axios.get('api/oauth2/login_gg')
    const url = res.data
    window.location.href = url
}

function register() {
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