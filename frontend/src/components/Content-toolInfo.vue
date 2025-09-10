<template>
    <div>Thông tin cá nhân</div>
    <div>
        <div>
            {{ name }} 
            <button>Edit</button>
        </div>
        <div>
            {{ role }}
            <button>Edit</button>
        </div>
        <div>
            {{ classRoom }}
            <button>Edit</button>
        </div>
        <div>
            {{ username }}
            <button>Edit</button>
        </div>
        <div>
            {{ email }}
            <button>Edit</button>
        </div>
        <div>
            {{ tel }}
            <button>Edit</button>
        </div>
        <div>
            {{ add }}
            <button>Edit</button>
        </div>
        <div @click="setPassword" style="cursor: pointer;">Đặt mật khẩu</div>
        <div class="setPassword">
            <form @submit.prevent="updatePassword">
                <label>Password</label> <br>
                <input type="password" v-model="password"> <br>
                <label>Re-type password</label> <br>
                <input type="password" v-model="re_password"> <br>
                <button>Xác nhận</button>
            </form>
            <div>{{ updatePasswordMsg }}</div>
        </div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import  useUserStore  from '../stores/user';
import axios from 'axios';


const userStore = useUserStore() 
const name = ref(`name: ${userStore.userInfo.name}`)
const username = ref(`username: ${userStore.userInfo.username}`)
const role = ref(`role: ${userStore.userInfo.role}`)
const email = ref(`email: ${userStore.userInfo.email}`)
const classRoom = ref(`Lớp: ${userStore.userInfo.class_room}`)
const tel = ref(`Số điện thoại: ${userStore.userInfo.tel}`)
const add = ref(`Địa chỉ: ${userStore.userInfo.add}`)

const password = ref('')
const re_password = ref('')
let updatePasswordMsg = ref('')

function setPassword() {
    const el = document.querySelector(".setPassword");
    el.style.display = (el.style.display === "block") ? "none" : "block";
}

async function updatePassword() {
    try { const payload = {
        password: password.value,
        re_password: re_password.value
    }
    const res = await axios.put('api/user/reset_password', payload, { withCredentials: true, headers: {"Content-Type": "application/json"}})
    updatePasswordMsg.value = res.data.msg
    } catch (err) {
        if (err.response && err.response.status === 400) {
            updatePasswordMsg.value = err.response.data.msg
        } else {        
            updatePasswordMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

</script>

<style scoped>
.setPassword {
    display: none;
} 
</style>