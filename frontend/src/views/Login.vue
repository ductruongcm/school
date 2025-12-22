<template>
    <div class="login">
        <div>
            <form @submit.prevent="login">
                <div>Đăng nhập</div>
                <legend>  
                    <label>Username</label> <br>
                    <input type="text" v-model="username"> <br>
                    <label>Password</label> <br>
                    <input type="password" v-model="password"> <br>
                    <button type="submit">Đăng nhập</button>
                </legend>
                <div class="forgetPassword">Quên mật khẩu</div>
                <div>{{ loginMsg }}</div>
            </form>
        </div>
        <div style="position: relative; top: 10em;">
            <span>Tài khoản được cấp bởi nhà trường/quản trị viên</span> <br>
            <span>Liên hệ admin nếu bạn chưa có tài khoản</span>
        </div>
    </div>
    
</template>
<script setup>
import axios from 'axios';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
import { message } from '../stores/usePopup';
import { useUserStore } from '../stores/user';
import { userYearStore } from '../stores/yearStore';

const username = ref('')
const password = ref('')
const loginMsg = ref('')

const router = useRouter()
const userStore = useUserStore()
const yearStore = userYearStore()
const login = async () => {
    const payload = {
        username: username.value,
        password: password.value,
        year_id: yearStore.year.id
    }
    try {
        const res = await axios.post('api/auth/login', payload, {
            headers: {'Content-Type': 'application/json'}
        })
        userStore.setUserInfo(res.data)

        userStore.userInfo.active === true ? router.push('/dashboard') : router.push('/changepassword')

    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            loginMsg.value = e.response.data.msg
        } else {
            loginMsg.value = 'Có rắc rối rồi!'
        }
    }
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