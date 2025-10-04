<template>
    <div>Công cụ</div>

    <form>
        <label>Thêm Môn học: </label> 
        <input v-model="lessonInput" type="text">
        <button @click.prevent="addLesson">Thêm</button>
    </form>
    <div>{{ resultMsg }}</div>
</template>
<script setup>
import { ref } from 'vue';
import axios from 'axios';
const resultMsg = ref('')
const lessonInput = ref('')

const addLesson = async () => {
    const payload = {
        lesson: lessonInput.value
    }
    try {
        const res = await axios.post('api/academic/lessons', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        }
    }
}

</script>