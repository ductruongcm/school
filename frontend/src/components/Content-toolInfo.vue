<template>
    <div>Thông tin cá nhân</div>
    <div>
        <div>
            <label>name: </label>
            <span v-if="!editing">{{ name }} </span>
            <input v-else v-model="changeName" type="text">
        </div>
        <div>
            <label>role: </label>
            <span v-if="!editing">{{ role }}</span>
            <input v-else v-model="changeRole" type="text">
        </div>
        <div>
            <label>username: </label>
            <span v-if="!editing">{{ username }}</span>
            <input v-else v-model="changeUsername" type="text">
        </div>
        <div>
            <label>email: </label>
            <span v-if="!editing">{{ email }}</span>
            <input v-else v-model="changeEmail" type="email">
        </div>
        <div>
            <label>tel: </label>
            <span v-if="!editing">{{ tel }}</span>
            <input v-else v-model="changeTel" type="text">
        </div>
        <div>
            <label>add: </label>
            <span v-if="!editing">{{ add }}</span>
            <input v-else v-model="changeAdd" type="text">
        </div>
        <button v-if="!editing" @click="changeInfo">Sửa thông tin</button>
        <div v-else>        
            <button @click="cancelEdit">Hủy</button>
            <button @click="saveEdit">Xác nhận</button>
        </div> <br>
        <button @click="setPassword">Đặt mật khẩu</button>
        <div class="setPassword">
            <form @submit.prevent="updatePassword">
                <label>Password</label> <br>
                <input type="password" v-model="password"> <br>
                <label>Re-type password</label> <br>
                <input type="password" v-model="re_password"> <br>
                <button>Xác nhận</button>
            </form>
        </div>
        <div>{{ updatePasswordMsg }}</div>
    </div>
</template>
<script setup>
import { ref } from 'vue';
import  useUserStore  from '../stores/user';
import axios from 'axios';


const userStore = useUserStore() 
const name = ref(userStore.userInfo.name)
const username = ref(userStore.userInfo.username)
const role = ref(userStore.userInfo.role)
const email = ref(userStore.userInfo.email)
const tel = ref(userStore.userInfo.tel)
const add = ref(userStore.userInfo.add)
const editing = ref(userStore.userInfo.editing)
const changeUsername = ref('')
const changeName = ref('')
const changeRole = ref('')
const changeEmail = ref('')
const changeTel = ref('')
const changeAdd = ref('')
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

function changeInfo() {
    changeUsername.value = username.value
    changeName.value = name.value
    changeRole.value = role.value
    changeEmail.value = email.value
    changeTel.value = tel.value
    changeAdd.value = add.value
    editing.value = true
}

function cancelEdit() {
    editing.value = false
}

async function saveEdit() {
    const payload = {
        id: userStore.userInfo.id,
        name: changeName.value,
        role: changeRole.value,
        username: changeUsername.value,
        email: changeEmail.value,
        tel: changeTel.value,
        add: changeAdd.value
    }
    try {
        const res = await axios.put('/api/user/update_info', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        updatePasswordMsg.value = res.data.msg
        window.location.reload()
    } catch (e) {
        if (e.response && e.response.status === 400) {
            updatePasswordMsg.value = e.response.data.msg
        } else {
            updatePasswordMsg.value = 'Có vấn đề gì rồi!!'
        }
    }
}
</script>

<style scoped>
.setPassword {
    display: none;
} 
</style>