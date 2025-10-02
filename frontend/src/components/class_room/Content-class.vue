<template>
    <div>
        <label>Danh sách lớp học:  </label>
        <select @change="fetchStudentList" v-model="classRoom">
            <option value="">-- Chọn lớp --</option>
            <option v-for="item in classList" :key="item">{{ item }}</option>
        </select>
        <label>Học kỳ: </label>
        <select v-model="semester">
            <option value="1">HK I</option>
            <option value="2">HK II</option>
        </select>
    </div>
    <div>
        <table>
            <thead>
                <tr>
                    <th style="width: 2em;">STT</th>
                    <th style="width: 10em;">Họ và tên</th>
                    <th style="width: 6em;">Điểm miệng</th>
                    <th style="width: 6em;">Điểm 15p</th>
                    <th style="width: 6em;">Điểm 45p</th>
                    <th style="width: 6em;">Điểm HK I</th>
                    <th style="width: 6em;">Tổng kết</th>
                    <th style="width: 20em;">Ghi chú</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="semester === 1" v-for="(student, index) in studentList" :key="student">
                    <td>{{ index + 1 }}</td>
                    <td>{{ student.name }}</td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
                    <td></td>
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
const semester = ref('')
onMounted(async () => {
    fetchClassList()
})

const fetchClassList = async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/academic/show_teach_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
}

const fetchStudentList = async () => {
    const res = await axios.get('api/student/show_score', {
        params: {
            class_room: classRoom.value,
            lesson: 'Toán'
        },
        withCredentials: true
    })
    studentList.value = res.data.data 
    console.log(studentList.value)
}

</script>
