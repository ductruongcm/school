<template>
    <div class="setPassword">
        <form @submit.prevent="handleSubmit">
            <div>Xin chào! Hãy thiết lập mật khẩu cá nhân để đăng nhập</div>
            <label>Password</label> <br>
            <input type="password" v-model="password" required> <br>
            <label>Re-type password</label> <br>
            <input type="password" v-model="rePassword" required> <br>
        
            <button @click="setPassword">Xác nhận</button>
            <button type="reset">Nhập lại từ đầu</button>
                    <div>{{ message }}</div>
        </form>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const password = ref('')
const rePassword = ref('')
const message = ref('')
const router = useRouter()
const setPassword = async () => {
    const payload = {
        password: password.value,
        repassword: rePassword.value
    }

    try {
        await axios.put('api/users/me/password', payload, {
            withCredentials: true,
            headers: {"Content-Type": "application/json"}
        })
        
        router.push('/')
        
    } catch (err) {

        if (err.response && [400,404,409,422,500].includes(err.response.status)) {
            message.value = err.response.data.msg
            
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