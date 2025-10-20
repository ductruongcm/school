<template>
    <div>Công cụ: Niên khóa</div>
    <div>
        <form>
            <label> Thêm niên khóa </label>
            <input v-model="yearInput" type="text">
            <button @click.prevent="addYear">Thêm</button>
        </form>
    </div>
    <div>{{ resultMsg }}</div>
    <div>Thiết lập niên khóa</div>
    <form>
        <select v-model="selectedYear">
            <option selected disabled :value="null">-- Chọn niên khóa --</option>
            <option v-for="item in yearList" :key="item.id" :value="item.id">{{ item.year }}</option>
        </select>
        <button @click.prevent="setYear">Xác nhận</button>
    </form>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
const yearInput = ref('')
const resultMsg = ref('')
const yearList = ref([])
const selectedYear = ref(null)
const yearStore = userYearStore()

onMounted(() => {
    fetchYear()
})

const addYear = async () => {
    const payload = {year: yearInput.value}
    try {
        const res = await axios.post('/api/academic/years', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!'
        }
    }
}

const yearSearch = ref('')
const fetchYear = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {year: yearSearch.value}
    })
    yearList.value = res.data.data
}


const setYear = async () => {
    const res = await axios.put(`api/academic/years/${selectedYear.value}`, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
    yearStore.setYear(res.data.data)
}

</script>