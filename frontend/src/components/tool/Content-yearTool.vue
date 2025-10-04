<template>
    <div>Công cụ</div>

    <div @click.prevent="yearTool = true" style="cursor: pointer;">Thêm niên khóa</div>
    <div v-if="yearTool">
        <form>
            <input v-model="yearInput" type="text">
            <button @click.prevent="addYear">Thêm</button>
            <button @click.prevent="yearTool = false">Đóng</button>
        </form>
    </div>

    <div @click.prevent="semesterTool = true" style="cursor: pointer;">Thêm học kỳ</div>
    <div v-if="semesterTool">
        <form>
            <input v-model="semesterInput" type="text">
            <button @click.prevent="addSemester">Thêm</button>
            <button @click.prevent="semesterTool = false">Đóng</button>
        </form>
    </div>

    <div>{{ resultMsg }}</div>

</template>
<script setup>
import { ref, inject } from 'vue';
import axios from 'axios';

const yearTool = ref(false)
const semesterTool = ref(false)
const yearInput = ref('')
const semesterInput = ref('')
const resultMsg = ref('')
const year = inject('year')

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

const addSemester = async () => {
    const payload = {
        year: year.value,
        semester: semesterInput.value
    }
    try {
        const res = await axios.post('api/academic/semesters', payload, {
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

</script>