<template>
    <div>Thông tin cá nhân</div>
    <div>
        <div>
            <label>name: </label>
            <span v-if="!editing">{{ info.name }} </span>
            <input v-else v-model="changeName" type="text">
        </div>
        <div>
            <label>role: </label>
            <span>{{ role }}</span>
        </div>
        <div>
            <label>username: </label>
            <span v-if="!editing">{{ username }}</span>
            <input v-else v-model="changeUsername" type="text">
        </div>
        <div>
            <label>email: </label>
            <span v-if="!editing">{{ info.email }}</span>
            <input v-else v-model="changeEmail" type="email">
        </div>
        <div>
            <label>tel: </label>
            <span v-if="!editing">{{ info.tel }}</span>
            <input v-else v-model="changeTel" type="text">
        </div>
        <div>
            <label>add: </label>
            <span v-if="!editing">{{ info.add }}</span>
            <input v-else v-model="changeAdd" type="text">
        </div>
        <button v-if="!editing" @click="changeInfo(info)">Sửa thông tin</button>
        <div v-else>        
            <button @click="saveEdit">Xác nhận</button>
            <button @click="editing = false">Hủy</button>
        </div> <br>
        <button @click="setPassword = true">Đặt mật khẩu</button>
        <div v-if="setPassword" class="setPassword">
            <form @submit.prevent="updatePassword">
                <label>Password</label> <br>
                <input type="password" v-model="password"> <br>
                <label>Re-type password</label> <br>
                <input type="password" v-model="re_password"> <br>
                <div>
                    <button>Xác nhận</button>
                    <button @click="setPassword = false">Hủy</button>
                </div>
            </form>
        </div>
        <div>{{ updatePasswordMsg }}</div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import  useUserStore  from '../stores/user';
import axios from 'axios';


const userStore = useUserStore() 
const info = ref([])
const username = ref(userStore.userInfo.username)
const role = ref(userStore.userInfo.role)
const editing = ref(userStore.userInfo.editing)
const changeUsername = ref('')
const changeName = ref('')
const changeEmail = ref('')
const changeTel = ref('')
const changeAdd = ref('')
const password = ref('')
const re_password = ref('')
let updatePasswordMsg = ref('')
const setPassword = ref(false)

onMounted(async () => {
    const res = await axios.get(`api/user/user_info?id=${userStore.userInfo.id}`, {
        withCredentials: true
    })
    info.value = res.data.data
})

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

function changeInfo(info) {
    changeUsername.value = username.value
    changeName.value = info.name
    changeEmail.value = info.email
    changeTel.value = info.tel
    changeAdd.value = info.add
    editing.value = true
}

async function saveEdit() {
    const payload = {
        id: userStore.userInfo.id,
        name: changeName.value,
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

</style>