<template>
    <div>Danh sách Log</div>

    <form @submit.prevent="fetchData(page)">
        <label>IP: </label>
        <input v-model="ip" type="text">
        <label>Username: </label>
        <input v-model="username" type="text">
        <label>Action: </label>
        <input v-model="action" type="text"> 
        <label>Status: </label>
        <select v-model="status">
            <option value="">--choose--</option>
            <option>Success</option>
            <option>Fail</option>
        </select>
        <br>
        <label>Start Date: </label>
        <input v-model="startDate" type="date">
        <label>End Date: </label>
        <input v-model="endDate" type="date">
        <button>Search</button>
        <button @click="onReset()" type="reset">Reset</button>
    </form>
    <table>
        <thead>
            <tr>
                <th style="width: 2em;">STT</th>
                <th style="width: 5em;">IP</th>
                <th style="width: 7em;">Username</th>
                <th style="width: 10em;">Thao tác</th>
                <th style="width: 10em;">Ngày</th>
                <th style="width: 7em;">Trạng thái</th>
                <th style="width: 30em;">Chi tiết</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(item, index) in data" :key="item">
                <td>{{ index + 1 }}</td>
                <td>{{ item.client_ip }}</td>
                <td>{{ item.username }}</td>
                <td>{{ item.action }}</td>
                <td>{{ dayjs(item.datetime).format('YYYY/MM/DD HH:mm:ss') }}</td>
                <td>{{ item.status }}</td>
                <td>{{ item.info }}</td>
            </tr>
        </tbody>
    </table>
    <div class="pagination">
        <button @click="goToPage(1)" :disabled="currentPage === 1"><< Đầu tiên</button>
        <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">< Trước</button>
        <span>Page {{ currentPage }} of {{ totalPages }}</span>
        <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Sau ></button>
        <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Cuối >></button>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import dayjs from 'dayjs';

const data = ref([])
const ip = ref('')
const username = ref('')
const action = ref('')
const startDate = ref('')
const endDate = ref('')
const status = ref('')
const currentPage = ref('')
const totalPages = ref('')

const fetchData = async (page = 1) => {
    try {
        const res = await axios.get('api/monitoring/show_monitoring', {
            params: {ip: ip.value,
                username: username.value,
                action: action.value,
                start_date: startDate.value,
                end_date: endDate.value,
                status: status.value,
                page: page
            },
            withCredentials: true
        })
        data.value = res.data.data
        currentPage.value = res.data.page
        totalPages.value = res.data.total_pages
    } catch (e) {
        if (e.response.status === 400 || 422 || 500) {
            console.log(e.response.data.msg)
        } else {
            console.log('Có rắc rối với frontend!')
        }
    }
} 

const goToPage = (page) => {
    if (page < 1 || page > totalPages.value) return
    fetchData(page)
}

onMounted( () => {
    fetchData(1)
})

function onReset() {
    ip.value = ''
    username.value = ''
    action.value = ''
    status.value = ''
    startDate.value = ''
    endDate.value = ''
    fetchData(1)
}

</script>