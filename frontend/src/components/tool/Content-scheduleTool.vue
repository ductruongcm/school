<template>
    <div>Công cụ: Thời khóa biểu</div>
    <label>Niên khóa: </label>
    <select v-model="selectedYear">
        <option :value="yearStore.year.id">{{ yearStore.year.year }}</option>
        <option value="" disabled>--Chọn niên khóa--</option>
        <option v-for="year in yearList" :key="year.id" :value="year.id">{{ year.year }}</option>
    </select>
    <label> Khối lớp: </label>
    <select v-model="selectedGrade" @change="fetchClassData">
        <option value="" disabled>- Chọn khối lớp -</option>
        <option value="">Toàn bộ</option>
        <option v-for="grade in gradeList" :key="grade.id" :value="grade.id">Khối lớp {{ grade.grade }}</option>
    </select>
    <label> Lớp học: </label>
    <select v-model="selectedClass">
        <option value="" disabled>- Chọn lớp -</option>
        <option v-for="cls in classList" :key="cls.class_room_id" :value="cls.class_room_id">{{ cls.class_room }}</option>
    </select>
    <label> Học kỳ: </label>
    <select v-model="selectedSemester">
        <option value="" disabled>- Chọn học kỳ -</option>
        <option v-for="semester in semesterList" :key="semester.id" :value="semester.id">{{ semester.semester}}</option>
    </select>
    <button @click.prevent="scheduleCreate">Tạo mới</button>
    <button @click.prevent="scheduleEdit">Điều chỉnh</button>
    <button @click.prevent="saveEdit">Lưu</button>
    <button @click.prevent="cancelEdit">Hủy</button>
    <div>{{ resultMsg }}</div>

</template>
<script setup>
import { ref, onMounted } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import axios from 'axios';

onMounted(() => {
    fetchYearData()
    fetchClassData()
    fetchGradeData()
    fetchSemesterData()
})
const yearStore = userYearStore()
const yearSearch = ref('')
const yearList = ref([])
const resultMsg = ref('')

const fetchYearData = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {
            year: yearSearch.value
        }
    })
    yearList.value = res.data.data
}

const gradeList = ref([])
const gradeSearch = ref('')
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value
        }
    })
    gradeList.value = res.data.data
}

const classList = ref([])
const classSearch = ref('')
const selectedYear = ref('')
selectedYear.value = yearStore.year.id
const selectedGrade = ref('')

const fetchClassData = async () => {
    const res = await axios.get('api/academic/class_rooms', {
        withCredentials: true,
        params: {
            class_room: classSearch.value,
            grade_id: selectedGrade.value,
            year_id: selectedYear.value
        }
    })
    classList.value = res.data.data
}

const semesterSearch = ref('')
const semesterList = ref([])
const fetchSemesterData = async () => {
    const res = await axios.get('api/academic/semester', {
        withCredentials: true,
        params: {
            semester: semesterSearch.value
        }
    })
    semesterList = res.data.data
}

const selectedSemester = ref('')
const selectedClass = ref('')
const scheduleCreate = async () => {
    const payload = {
        year_id: selectedYear.value,
        semester_id: selectedSemester.value,
        class_room_id: selectedClass.value
    }
    try {
        const res = await axios.post('api/academic/schedules', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    resultMsg.value = res.data.msg
    } catch (err) {
        if (err.response && err.response.status === 400 || 422 || 500) {
            resultMsg.value = err.response.data.msg
        }
    }
}

</script>