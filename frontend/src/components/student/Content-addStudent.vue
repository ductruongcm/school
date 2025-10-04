<template>
    <div>Quản lý học sinh</div>
    <form @submit.prevent="addStudent">
        <div> Thêm học sinh </div>
        <label>Họ và tên</label> <br>
        <input type="text" v-model="name" required> <br>
        <label >Lớp học</label> <br>
        <!-- <input type="text" v-model="class_room" required> <br> -->
        <select v-model="classRoom">
            <option value="" selected disabled>-- Chọn lớp --</option>
            <option v-for="item in classList" :key="item">{{ item }}</option>
        </select>   <br>
        <label>Số điện thoại liên lạc</label> <br>
        <input type="text" v-model="tel" required> <br>
        <label>Địa chỉ</label> <br>
        <input type="text" v-model="add" required> <br>
        <label>Role</label> <br>
        <input type="text" v-model="role" default="guest" placeholder="guest"> <br>
        <button type="submit">Đăng ký</button>
    </form>
    <div>{{ msg }}</div>
</template>

<script setup>
import { inject, ref, onMounted, watch } from 'vue';
import axios from 'axios';

const year = inject('year')
const name = ref('')
const classList = ref([])
const tel = ref('')
const add = ref('')
const role = ref('')
const msg = ref('')
const classRoom = ref('')

const addStudent = async () => {
    const payload = {
        name: name.value,
        class_room: classRoom.value,
        year: year.value,
        tel: tel.value,
        add: add.value,
        role: role.value,    
    }
    try {const res = await axios.post('/api/student/add_student', payload, { 
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        
        msg.value = res.data.msg
    } catch (err) {
        if (err.response && err.response.status === 403) {
            msg.value = 'Forbidden: Access denied!'
        } else if (err.response && err.response.status === 400) {
            msg.value = err.response.data.msg
        } else {
            msg.value = 'Có vấn đề gì rồi!!'
        }
    }
}

onMounted(async () => {
    fetchClassList()
})

const fetchClassList = async () => {
    const payload = {
        year: year.value
    }
    const res = await axios.put('api/academic/show_class_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
}

watch(classList, (newval) => {
    if (newval.length === 1) {
        classRoom.value = newval[0]
    }
})
</script>