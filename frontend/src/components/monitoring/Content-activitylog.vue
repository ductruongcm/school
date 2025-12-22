<template>
<div>Lịch sử hoạt động</div>
<div style="display: flex; gap: 0.8em">
    <div v-if="role === 'admin'">
        <label>
            Username: 
            <input style="width: 10em;" type="text" v-model="usernameSearch">
        </label>
        <label>
            Module:
            <input style="width: 10em;"  type="text" v-model="moduleSearch">
        </label>
        <label>
            Action:
            <input style="width: 10em;"  type="text" v-model="actionSearch">
        </label>
    </div>
    <div>
        <label>
            Start date:
            <input type="date" v-model="startDateSearch">
        </label>
        <label>
            End date:
            <input type="date" v-model="endDateSearch">
        </label>
    </div>
    <button @click.prevent="fetchLogData(page)">Tìm kiếm</button>
    <button @click.prevent="resetSearch">Nhập lại</button>
</div>
<div>
    <table border="1" style="border-collapse: collapse; text-align: center;">
        <thead>
            <tr>
                <th style="width: 3em;">STT</th>
                <th style="width: 10em;">Username</th>
                <th v-if="role === 'admin'" style="width: 9em;" >Module</th>
                <th style="width: 6em;">Thao tác</th>
                <th v-if="role === 'admin'" style="width: 9em;" >Target Id</th>
                <th style="width: 32em;">Chi tiết</th>
                <th style="width: 12em;">Thời gian</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(log, idx) in logList" :key="idx">
                <td>{{ idx + 1 }}</td>
                <td>{{ log.username }}</td>
                <td v-if="role === 'admin'">{{ log.module }}</td>
                <td>{{ log.action }}</td>
                <td v-if="role === 'admin'">{{ log.target_id }}</td>
                <td>{{ log.detail }}</td>
                <td>{{ dayjs(log.created_at).format('YYYY/MM/DD HH:mm:ss') }}</td>
            </tr>
        </tbody>
    </table>
</div>
<div class="pagination">
    <button @click="goToPage(1)" :disabled="currentPage === 1"><< Đầu tiên</button>
    <button @click="goToPage(currentPage - 1)" :disabled="currentPage === 1">< Trước</button>
    <span>Page {{ currentPage }} of {{ totalPages }}</span>
    <button @click="goToPage(currentPage + 1)" :disabled="currentPage === totalPages">Sau ></button>
    <button @click="goToPage(totalPages)" :disabled="currentPage === totalPages">Cuối >></button>
</div>
</template>
<script setup>
import axios from 'axios';
import dayjs from 'dayjs';
import { ref, onMounted } from 'vue';
import { useUserStore } from '../../stores/user';

const userStore = useUserStore()
const role = userStore.userInfo.role

const logList = ref([])
const usernameSearch = ref('')
const moduleSearch = ref('')
const actionSearch = ref('')
const startDateSearch = ref('')
const endDateSearch = ref('')
const totalPages = ref('')
const currentPage = ref('')
const fetchLogData = async (page = 1) => {
    const res = await axios.get(`api/activity-log`, {
        withCredentials: true,
        params: {
            username: usernameSearch.value,
            module: moduleSearch.value,
            action: actionSearch.value,
            start_date: startDateSearch.value,
            end_date: endDateSearch.value,
            page: page
        }
    })

    logList.value = res.data.data.data
    currentPage.value = res.data.data.page
    totalPages.value = res.data.data.total_pages
}

const goToPage = (page) => {
    if (page < 1 || page > totalPages.value) return
    fetchLogData(page)
}

onMounted( () => {
    fetchLogData(1)
})

const resetSearch = () => {
    usernameSearch.value = ''
    moduleSearch.value = ''
    actionSearch.value = ''
    startDateSearch.value = ''
    endDateSearch.value = ''
    fetchLogData(1)
}
</script>