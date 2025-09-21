<template>
    <div>
        <label>Danh sách lớp học:  </label>
        <select @change="fetchStudentList" v-model="classRoom">
            <option value="">-- Chọn lớp --</option>
            <option v-for="item in classList" :key="item">{{ item }}</option>
        </select>
    </div>
    <div>
        <table>
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Họ và tên</th>
                    <th>Sỉ số</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(student, index) in studentList" :key="student">
                    <td>{{ index + 1 }}</td>
                    <td>{{ student.name }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import { onMounted, ref, inject } from 'vue';
import axios from 'axios';

const year = inject('year')
const classList = ref([])
const studentList = ref([])
const classRoom = ref('')
onMounted(async () => {
    fetchClassList()
})

const fetchClassList = async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_teach_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
}

const fetchStudentList = async () => {
    const res = await axios.get('api/student/show_student', {
        params: {class_room: classRoom.value},
        withCredentials: true
    })
    studentList.value = res.data.data 
}

</script>
