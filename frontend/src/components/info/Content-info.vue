<template>
    <div>Thông tin cá nhân</div>
    <div>
        <div>
            <label>name: </label>
            <span>{{ info.name }} </span>
        </div>
        <div>
            <label>role: </label>
            <span>{{ userStore.userInfo.role }}</span>
        </div>
        <div>
            <label>username: </label>
            <span>{{ userStore.userInfo.username }}</span>
        </div>
        <div>
            <label>email: </label>
            <span v-if="!editing">{{ info.email }}</span>
            <input v-else v-model="info.email" type="email">
        </div>
        <div>
            <label>tel: </label>
            <span v-if="!editing">{{ info.tel }}</span>
            <input v-else v-model="info.tel" type="text">
        </div>
        <div>
            <label>add: </label>
            <span v-if="!editing">{{ info.add }}</span>
            <input v-else v-model="info.add" type="text">
        </div>
        <button v-if="!editing" @click="editInfo">Sửa thông tin</button>
        <div v-else>        
            <button @click.prevent="saveEdit">Xác nhận</button>
            <button @click="cancelEdit">Hủy</button>
        </div> <br>
        <button @click="setPassword = true">Đặt mật khẩu</button>
        <div v-if="setPassword" class="setPassword">
            <form>
                <label>Password</label> <br>
                <input type="password" v-model="password" required> <br>
                <label>Re-type password</label> <br>
                <input type="password" v-model="re_password" required> <br>

                <button @click.prevent="updatePassword">Xác nhận</button>
                <button @click="cancelSetPassword">Hủy</button>
            </form>
        </div>
        <div>{{ resultMsg }}</div>

    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import useUserStore from '../../stores/user';
import axios from 'axios';

const userStore = useUserStore() 
const info = ref({})
const password = ref('')
const re_password = ref('')
const resultMsg = ref('')
const setPassword = ref(false)
const editing = ref(false)

onMounted(() => {
    fetchUserInfo()
})

const fetchUserInfo = async () => {
    try {const res = await axios.get(`api/users/me`, {
            withCredentials: true,
    })
        info.value = res.data.data
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề gì rồi!!'
        }
    }
}

async function updatePassword() {
    const payload = {
        password: password.value,
        repassword: re_password.value
    }

    try {
        const res = await axios.put('api/users/me/password', payload, {
            withCredentials: true, 
            headers: {"Content-Type": "application/json"}
        })
            resultMsg.value = res.data.msg
            setPassword.value = false
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        } else {        
            resultMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

const cancelSetPassword = () => {
    setPassword.value = false
    password.value = ''
    re_password.value = '' 
}

const cancelEdit = () => {
    editing.value = false
    info.value = original.value
}

const original = ref({})
const editInfo = () => {
    editing.value = true
    original.value = JSON.parse(JSON.stringify(info.value))
}

const saveEdit = async () => {
    const payload = Object.entries(info.value)
    .filter(([k, v]) => v !== original.value[k])
    .reduce((acc, [k, v]) => {
      acc[k] = v
      return acc
    }, {})
    try {
        const res = await axios.put('/api/users/me', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
        editing.value = false
        fetchUserInfo()
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề gì rồi!!'
        }
    }
}
</script>

<style scoped>

</style>