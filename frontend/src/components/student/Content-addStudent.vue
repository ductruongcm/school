<template>
    <div>Quản lý học sinh</div>
    <form @submit.prevent="addStudent">
        <div> Thêm học sinh </div>
        <label>Khối lớp: </label>
        <select v-model="selectedGrade" @change="fetchClassData()">
            <option value="null" disabled>-- Chọn khối --</option>
            <option v-for="grade in gradeList" :key="grade.id" :value="grade.id">Khối {{ grade.grade }}</option>
        </select> 
        <label > Lớp học: </label> 
        <select v-model="classRoom">
            <option value="">-- Xếp lớp sau --</option>
            <option v-for="class_room in classList" :key="class_room.clas_room_id" :value="class_room">
                {{ class_room.class_room }}
            </option>
        </select>   <br>
        <label>Họ và tên: </label> 
        <input type="text" v-model="name" required> <br>
        <label>Giới tính: </label>
        <select v-model="selectedGender">
            <option value="">--Chọn giới tính --</option>
            <option value="Nam">Nam</option>
            <option value="Nữ">Nữ</option>
        </select> <br>
        <label>Sinh ngày: </label> 
        <input type="date" v-model="selectedBOD"> <br>
        <label>Số điện thoại gia đình: </label> 
        <input type="text" v-model="tel"> <br>
        <label>Địa chỉ: </label> 
        <input type="text" v-model="add"> <br>
        <button type="submit">Đăng ký</button>
    </form>
    <div>{{ msg }}</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import axios from 'axios';

const yearStore = userYearStore()
const name = ref('')
const tel = ref('')
const add = ref('')
const msg = ref('')
const classRoom = ref('')
const selectedGender = ref('')
const selectedBOD = ref('')
const addStudent = async () => {
    const payload = {
        name: name.value,
        class_room_id: classRoom.value?.class_room_id || null,
        class_room: classRoom.value?.class_room || null,
        year_id: yearStore.year.id,
        year: yearStore.year.year,                                  // quan trọng: để làm student code
        tel: tel.value,
        add: add.value,
        gender: selectedGender.value,
        bod: selectedBOD.value,
        grade_id: selectedGrade?.value || null
    }
    try {const res = await axios.post('/api/students', payload, { 
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })

        msg.value = res.data.msg
    } catch (err) {
        if (err.response && err.response.status === 403) {
            msg.value = 'Forbidden: Access denied!'
        } else if (err.response && err.response.status === 400 || 404 || 422) {
            msg.value = err.response.data.msg
        } else {
            msg.value = 'Có vấn đề gì rồi!!'
        }
    }
}

onMounted( () => {
    fetchGradeData()
})

const gradeSearch = ref('')
const gradeList = ref(null)
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value
        }
    })
    gradeList.value = res.data.data
}

const selectedGrade = ref('null')
const classList = ref(null)
const fetchClassData = async () => {
    const res = await axios.get('api/academic/class_rooms', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            grade_id: selectedGrade.value
        }
    })
    classList.value = res.data.data
}
</script>
