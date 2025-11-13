<template>
    <div>Quản lý học sinh</div>
    <form @submit.prevent="addStudent">
        <div> Thêm học sinh </div>
        <label>Họ và tên: </label> 
        <input style="width: 13em;"  type="text" v-model="name" required> 
        <label> Giới tính: </label>
        <select v-model="selectedGender">
            <option value="">--Chọn giới tính --</option>
            <option value="Nam">Nam</option>
            <option value="Nữ">Nữ</option>
        </select> 
        <label> Sinh ngày: </label> 
        <input type="date" v-model="selectedBOD"> <br>
        <label>Số điện thoại gia đình: </label> 
        <input style="width: 8em;" type="text" v-model="tel"> 
        <label> Địa chỉ: </label> 
        <input style="width: 23em;" type="text" v-model="add"> <br>
        <button type="submit">Đăng ký</button> <br>
        <div>Lịch sử học tập năm trước: 
            <select v-model="prev_year">
                <option value="">Chọn niên khóa</option>
                <option v-for="y in yearCode" :key="y.id" :value="y.id">{{ y.year_code }}</option>
            </select>
        </div> 
        <label>Khối lớp: </label>
        <select v-model="selectedGrade" @change="onGradeChange">
            <option value="" disabled>-- Chọn khối --</option>
            <option v-for="grade in gradeList" :key="grade.id" :value="grade.grade">Khối {{ grade.grade }}</option>
        </select> 
        <label> Hạnh kiểm: </label>
        <select v-model="conduct">
            <option value="" disabled>-- Chọn --</option>
            <option :value="true">Đạt</option>
            <option :value="false">Không đạt</option>
        </select>
        <label> Chuyên cần: </label>
        <input style="width: 5em;" v-model="absent_day" type="number" required min="0">
        <label> Ghi chú: </label>
        <input v-model="note" style="width: 30em;" type="text">
        <table>
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 7em;">Môn</th>
                    <th style="width: 5em;">Học kỳ I</th>
                    <th style="width: 5em;">Học kỳ II</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(ls, index) in lessonList" :key="ls.lesson_id">
                    <td style="width: 3em;">{{ index + 1 }}</td>
                    <td>{{ls.lesson}}</td>
                    <td><input v-model="ls.score_1" style="width: 5em;" type="number" required min="0" max="10" step="0.1"></td>
                    <td><input v-model="ls.score_2" style="width: 5em;" type="number" required min="0" max="10" step="0.1"></td>
                </tr>
            </tbody>
        </table>
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
const selectedGender = ref('')
const selectedBOD = ref('')
const selectedGrade = ref('')
const conduct = ref('')
const absent_day = ref('')
const note = ref('')
const prev_year = ref('')
const addStudent = async () => {
    const payload = {
        name: name.value,
        year_id: prev_year.value,
        year: yearStore.year.year,                                  // quan trọng: để làm student code
        tel: tel.value,
        add: add.value,
        gender: selectedGender.value,
        bod: selectedBOD.value,
        grade: selectedGrade.value,
        conduct: conduct.value,
        absent_day: absent_day.value,
        lesson: lessonList.value,
        note: note.value
    }
    console.log(payload)
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
    fetchYearCode()
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

const lessonList = ref([])
const fetchLessonData = async () => {
    const res = await axios.get(`api/academic/grades/${selectedGrade.value}/lessons`, {
        withCredentials: true, 
        params: {year_id: yearStore.year.id-1}
    })
    lessonList.value = res.data.data
}
const yearCode = ref([])
const fetchYearCode = async () => {
    const res = await axios.get('api/academic/prev-year-code', {
        withCredentials: true
    })
    yearCode.value = res.data.data
}

const onGradeChange = async () => {
    await fetchLessonData()
}

</script>
