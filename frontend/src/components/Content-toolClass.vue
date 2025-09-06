<template>
    <div>Quản lý lớp học</div>
    <form @submit.prevent="addClass">
        <label>Thêm lớp học: </label>
        <input type="text" v-model="classRoom"> 
        <button>Thêm</button> <br>
        <label>Xóa lớp học</label> <br>
    </form>
    <div>{{ classRoomMsg }}</div>
</template>
<script setup>
import axios from 'axios';
import { ref } from 'vue';

const classRoomMsg = ref('')
const classRoom = ref('')

async function addClass() {
    const payload = {
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
        if (err.response && err.response.status === 401) {
            classRoomMsg.value = err.response.data.msg
        } else {
            classRoomMsg.value = 'Có vấn đề rồi!!'
        }
    }
    

}

</script>