<template>
    <div>Quản lý lớp học</div>
    <form @submit.prevent="addClass">
        <label>Thêm lớp học: </label>
        <input type="text" v-model="classRoom"> 
        <button>Thêm</button> <br>
        <label>Xóa lớp học</label> <br>
    </form>
    <div>{{ classRoomMsg }}</div>
    <form @submit.prevent="addLesson">
        <label>Thêm môn học: </label>
        <input type="text" v-model="lesson">
        <button>Thêm môn học</button>
    </form>
    <div>{{ lessonMsg }}</div>
</template>
<script setup>
import axios from 'axios';
import { ref, inject } from 'vue';

const classRoomMsg = ref('')
const classRoom = ref('')
const lesson = ref('')
const lessonMsg = ref('')
const year = inject('year')

async function addClass() {
    const payload = {
        year: year.value,
        class_room: classRoom.value
    }
    try {
        const res = await axios.post('api/class_room/add_class', payload, 
            { 
            withCredentials: true, 
            headers: {'Content-Type': 'application/json'}
            })
        classRoomMsg.value = res.data.msg 
    } catch (err) {
        if (err.response && err.response.status === 400) {
            classRoomMsg.value = err.response.data.msg
        } else {
            classRoomMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

async function addLesson() {
    const payload = {lesson: lesson.value}
    try {
        const res = await axios.post('api/teacher/add_lesson', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
        })
        lessonMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400) {
            lessonMsg.value = 'Nhập sai thông tin!'
        } else if (e.response && e.response.status === 403) {
            lessonMsg.value = 'Forbidden: Access denied!'
        } else {
            lessonMsg.value = 'Có vấn đề gì rồi!'
        }
    }
}
</script>