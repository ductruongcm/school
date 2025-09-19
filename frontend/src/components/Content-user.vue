<template>
    <div>Danh sách User</div>
    <div>{{ editMSG }}</div>
    <div>
        <form @submit.prevent="userSearch()">
            <label>Username: </label>
            <input v-model="username" type="text">
            <label>Role: </label>
            <input v-model="role" type="text">
            <button type="submit">Tìm</button>
        </form>
    </div>
    <div>
        <table>
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Username</th>
                    <th>role</th>
                </tr>
            </thead>
            <tbody  v-for="(item,index) in data" :key="item">
                <tr>
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.username }}</td>
                    <td>
                        <span v-if="!item.editing">{{ item.role }}</span>
                        <input v-else v-model="item.role" type="text">
                    </td>
                    <td>
                        <div>
                            <button v-if="!item.editing" @click="edit(item)">Edit</button>
                            <button v-else @click.prevent="save(item)">Save</button>
                            <button v-if="item.editing" @click.prevent="cancel(item)">Cancel</button>
                            <button @click.prevent="item.setPasswordStatus = true">Set password</button>
                        </div>
                    </td>  
                </tr>      
                <tr v-if="item.setPasswordStatus">
                    <td colspan="6">
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

onMounted(async () => {
    const res = await axios.get('api/user/show_users', {
        withCredentials: true
    })
    data.value = res.data.data
})

async function userSearch() {
    const res = await axios.get(`api/user/show_users?username=${username.value}&role=${role.value}&email=${email.value}`, {
        withCredentials: true
    })
    data.value = res.data.data
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

async function savePassword(item) {
    const payload = {
        username: item.username,
        password: password.value,
        rePassword: rePassword.value
    }
    try {
        const res = await axios.post('api/user/set_password', payload, {
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