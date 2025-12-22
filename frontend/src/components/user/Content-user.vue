<template>
    <div>Danh sách User</div>
    <div>{{ editMSG }}</div>
    <div>
        <form @submit.prevent="fetchData(page)" style="display: flex; gap: 1em">
            <label>Username: <input v-model="username" type="text"></label>

            <label>Role: <input v-model="role" type="text"></label>
            <button type="submit">Tìm</button>
            <button @click="onReset">Bỏ tìm kiếm</button>
        </form>
    </div>
    <div>
        <table border="1"  style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 10em;">Username</th>
                    <th style="width: 7em;">role</th>
                    <th style="width: 14em;">Tên</th>
   
                </tr>
            </thead>
            <tbody >
                <tr v-for="(item, index) in userList" :key="item.id" class="row-wrapper">
                    <td>{{ index + 1 }}</td>
                    <td @click.prevent="edit(item)" style="cursor: pointer;">{{ item.username }}</td>
                    <td>
                        <span v-if="editingId !== item.id">{{ item.role }}</span>
                        <select v-if="editingId === item.id" v-model="item.role">
                            <option disabled value="">--Chọn role--</option>
                            <option value="admin">Admin</option>
                            <option value="Teacher">Teacher</option>
                            <option value="Student">Student</option>
                        </select>
                    </td>
                    <td>{{ item.name }}</td>
                    <div
                            v-if="editingId === item.id"
                            class="floating-td"
                        >
                            <button @click="confirmEdit(item)">✔</button>
                            <button @click="cancelEdit(item)">✖</button>
                    </div>
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

const userList = ref([])
const username = ref('')
const role = ref('')
const editMSG = ref('')
const currentPage = ref('')
const totalPages = ref('')

onMounted(() => {
    fetchData(1)
})

const fetchData = async (page = 1) => {
    try {
        const res = await axios.get('api/users', {
            params: {
                username: username.value,
                role: role.value,
                page
            }, 
            withCredentials: true
            })
        userList.value = res.data.data.data
        currentPage.value = res.data.data.page
        totalPages.value = res.data.data.total_pages
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            editMSG.value = e.response.data.msg
        } else {
            editMSG.value = 'Có rắc rối khác!'
        }
    }
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
const editingId = ref('')
const original = ref('')
const edit = (item) => {
    editingId.value = item.id
    original.value = item.role
}

const cancelEdit = (item) => {
    editingId.value = ''
    item.role = original.value
}

const confirmEdit = async (item) => {
    if (item.role === original.value) return null

    const payload = {
        role: item.role
    }

    const res = await axios.put(`api/users/${item.id}/role`, payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })

    editMSG.value = res.data.msg
    editingId.value = ''
    fetchData()
}

</script>
<style scoped>
.row-wrapper {
  position: relative;
}

.floating-td {
  position: absolute;
  top: 50%;
  right: -90px;        /* đẩy ra ngoài bảng */
  transform: translateY(-50%);
  display: flex;
  gap: 6px;
}
</style>