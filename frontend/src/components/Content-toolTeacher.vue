<template>
    <div>Quản lý giáo viên</div>
    <div> Thêm giáo viên </div>
    <form @submit.prevent="addTeacher">
        <label>Họ và tên</label> <br>
        <input type="text" v-model="name" required> <br>
        <label>Chuyên môn</label> <br>
        <input type="text" v-model="lesson" required> <br>
        <label>Chủ nhiệm lớp</label> <br>
        <input type="text" v-model="classRoom"> <br>
        <label>Phụ trách lớp</label> <br>
        <input type="text" v-model="teachRoom" required> <br>
        <label>Số điện thoại</label> <br>
        <input type="text" v-model="tel" required> <br>
        <label>Địa chỉ</label> <br>
        <input type="text" v-model="add" required> <br>
        <label>Username</label> <br>
        <input type="text" v-model="username" required> <br>
        <label>Email</label> <br>
        <input type="text" v-model="email" required> <br>
        <label>Role</label> <br>
        <input type="text" v-model="role" placeholder="teacher" default="teacher"> <br>
        <button>Đăng ký</button>
    </form>
    <div>{{ teacherMsg }}</div>
</template>
<script setup>
import { ref, inject } from 'vue';
import axios from 'axios';

const name = ref('')
const lesson = ref('')
const classRoom = ref('')
const teachRoom = ref('')
const tel = ref('')
const add = ref('')
const username = ref('')
const email = ref('')
const role = ref('')
const teacherMsg = ref('')
const year = inject('year')

async function addTeacher() {
    const payload = {
        name: name.value,
        lesson: lesson.value,
        class_room: classRoom.value,
        teach_room: teachRoom.value,
        tel: tel.value,
        add: add.value,
        email: email.value,
        username: username.value,
        role: role.value,
        year: year.value
    }
    try {
        const res = await axios.post('api/teacher/add_teacher', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        teacherMsg.value = 'Thêm giáo viên thành công!'
    } catch (e) {
        if (e.response && e.response.status === 400) {
            teacherMsg.value = e.response.data.msg
        } else {
        teacherMsg.value = 'Có vấn đề gì rồi!!!'
        }
    }
}


</script>