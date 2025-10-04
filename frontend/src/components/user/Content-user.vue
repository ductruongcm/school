<template>
    <div>Danh sách User</div>
    <div>{{ editMSG }}</div>
    <div>
        <form @submit.prevent="fetchData(page)">
            <label>Username: </label>
            <input v-model="username" type="text">
            <label>Role: </label>
            <input v-model="role" type="text">
            <button type="submit">Tìm</button>
            <button @click="onReset">Bỏ tìm kiếm</button>
        </form>
    </div>
    <div>
        <table>
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 7em;">Username</th>
                    <th style="width: 4em;">role</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in data" :key="item.username">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.username }}</td>
                    <td>
                        <span v-if="!item.editing">{{ item.role }}</span>
                        <input style="width: 4em;" v-else v-model="item.role" type="text">
                    </td>
                    <td>
                        <div>
                            <button v-if="!item.editing" @click="edit(item)">Edit</button>
                            <button v-else @click.prevent="save(item)">Save</button>
                            <button v-if="item.editing" @click.prevent="cancel(item)">Cancel</button>
                            <button @click.prevent="item.setPasswordStatus = true">Set password</button>
                        </div>
                    </td>  
                    <td v-if="item.setPasswordStatus" colspan="6">
                        <form @submit.prevent="savePassword(item)">
                            <label>Set password: </label>
                            <input v-model="password" type="password">
                            <label>Re-type password : </label>
                            <input v-model="rePassword" type="password">
                            <button type="submit">Confirm</button>
                            <button @click.prevent="item.setPasswordStatus = false">Cancel</button>
                        </form>
                    </td>
                </tr>      
            </tbody>
        </table>
    </div>
    <div>
        <button @click="goToPage(1)" :disabled="currentPage === 1"><< Đầu</button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">< Trước</button>
        <span>{{ currentPage }} of {{ totalPages }}</span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Sau ></button>
        <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Cuối >></button>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';

const data = ref([])
const username = ref('')
const role = ref('')
const email = ref('')
const editMSG = ref('')
const password = ref('')
const rePassword = ref('')
const currentPage = ref('')
const totalPages = ref('')

onMounted(() => {
    fetchData(1)
})

const fetchData = async (page = 1) => {
    const res = await axios.get('api/user/users', {
        params: {
            username: username.value,
            role: role.value,
            email: email.value,
            page
        }, 
        withCredentials: true
    })
    data.value = res.data.data
    currentPage.value = res.data.page
    totalPages.value = res.data.total_pages
}

const goToPage = (page) => {
    if (page < 0 || page > totalPages.value) return
    fetchData(page)
}

const onReset = () => {
    username.value = ''
    role.value = ''
    fetchData(1)
}

function edit(item) {
    item.original = {...item}
    item.editing = true
}

function cancel(item) {
    Object.assign(item, item.original)
    item.editing = false
}

async function save(item) {
    const payload = {
        username: item.username,
        role: item.role
    }
    const res = await axios.put('api/user/update_role', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    editMSG.value = res.data.msg
}

const savePassword = async (item) => {
    const payload = {
        username: item.username,
        password: password.value,
        rePassword: rePassword.value
    }
    console.log(payload)
    try {
        const res = await axios.put('api/user/password', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })              
        editMSG.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400) {
            alert(e.response.data.msg)
        } else {
            editMSG.value = 'Có rắc rối rồi đó!!'
        }
    }
}
</script>