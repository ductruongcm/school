<template>
    <div>Công cụ: Niên khóa</div>
    <div>
        <form>
            <div> Thêm niên khóa mới </div>
            <label>Ngày dự kiến khai giảng 
                <input v-model="start_date" type="date">
            </label> <br>
            <label> Ngày dự kiến bế giảng
                <input v-model="end_date" type="date">
            </label>
            
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
const start_date = ref('')
const end_date = ref('')
const resultMsg = ref('')
const yearList = ref([])
const selectedYear = ref(null)
const yearStore = userYearStore()

onMounted(() => {
    fetchYear()
})

const addYear = async () => {
    const payload = {
                     start_date: start_date.value,
                     end_date: end_date.value
                    }
    try {
        const res = await axios.post('/api/academic/years', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })

        resultMsg.value = res.data.msg

    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
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
    if (!selectedYear.value) {
        alert('Chưa chọn niên khóa để thiết lập!')
        return
    }
    const res = await axios.put(`api/academic/years/${selectedYear.value}/status`, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
    yearStore.setYear(res.data.data)
}

</script>