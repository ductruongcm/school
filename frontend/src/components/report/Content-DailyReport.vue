<template>
    <div>
        <h4>Thống kê ngày</h4>
        <div style="display: flex; gap: 1em;">
            <label>
                Ngày
                <input type="date" v-model="selectedDate">
            </label>
            <label>
                Học kỳ
                <select v-model="selectedSemester">
                    <option>--Chọn học kỳ--</option>
                    <option v-for="se in semesterList" :value="se.semester_id">{{ se.semester }}</option>
                </select>
            </label>
        </div>
    </div>
    <div style="display: flex; gap: 2em;">
        <div style="border-collapse: collapse; text-align: center;">
            <span>Danh sách lớp học</span>
            <table border="1">
                <thead>
                    <tr>
                        <th rowspan="2" style="width: 3em;">STT</th>
                        <th rowspan="2" style="width: 5em;">Lớp học</th>
                        <th rowspan="2" style="width: 4em;">Sỉ số</th>
                        <th colspan="2" style="width: 4em;">Vắng</th>
                        <th rowspan="2" style="width: 9em;">GV chủ nhiệm</th>
                        <th colspan="4">Kết quả học tập</th>
                    </tr>
                    <tr>
                        <th style="width: 5em;">Có phép</th>
                        <th style="width: 5em;">Không phép</th>
                        <th style="width: 5em;">Chưa đạt</th>
                        <th style="width: 5em;">Đạt</th>
                        <th style="width: 5em;">Khá</th>
                        <th style="width: 5em;">Giỏi</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(cl, idx) in classInfoList" :key="cl.class_room">
                        <td>{{ idx + 1 }}</td>
                        <td>{{ cl.class_room }}</td>
                        <td>{{ cl.qty ? cl.qty : 0 }}</td>
                        <td>{{ cl.absence_e ? cl.absence_e: 0 }}</td>
                        <td>{{ cl.absence_a ? cl.absence_a : 0 }}</td>
                        <td>{{ cl.teacher }}</td>
                        <td>{{ cl.bad ? cl.bad : 0 }}</td>
                        <td>{{ cl.avg ? cl.avg : 0 }}</td>
                        <td>{{ cl.fair ? cl.fair : 0 }}</td>
                        <td>{{ cl.good ? cl.good : 0 }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
   <div>
        <div>Danh sách học sinh cần lưu ý trong kỳ</div>
        <div style="display:flex; gap:1em;">
            <label>Khối
                <select v-model="selectedGrade">
                    <option disabled value="">--Chọn khối--</option>
                    <option value="">Tất cả</option>
                    <option v-for="gr in gradeList" :value="gr.grade">{{ gr.grade }}</option>
                </select>
            </label>
            <label>Lớp
                <select v-model="selectedClass">
                    <option disabled value="">--Chọn lớp--</option>
                    <option value="">Tất cả</option>
                    <option v-for="cl in classList" :value="cl.class_room_id">{{ cl.class_room }}</option>
                </select>
            </label>
            <button @click.prevent="fetchWeakStudents">Lấy danh sách</button>
        </div>
        <table style="border-collapse: collapse; text-align: center; gap: 2em;" border="1">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 9em;">Tên</th>
                    <th style="width: 4em;">Lớp</th>
                    <th v-for="lssc in (weakStudents?.[0]?.scores || {})" :key="lssc" style="width: 5em;">
                        <span v-for="ls in Object.keys(lssc)" :key="ls">{{ ls }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(st, ind) in weakStudents" :key="st">
                    <td>{{ ind + 1 }}</td>
                    <td>{{ st.name }}</td>
                    <td>{{ st.class_room }}</td>
                    <td v-for="lssc in st?.scores" :key="lssc">
                        <span v-for="sc in Object.values(lssc)" :key="sc">{{ sc ? sc.toFixed(2) : '-' }}</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-if="selectedSemester === 2 && weakStudentsFirstSemester.length > 0">
        <span>Danh sách học sinh cần chú ý học kỳ I</span>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 9em;">Tên</th>
                    <th style="width: 4em;">Lớp</th>
                    <th style="width: 5em;" v-for="lssc in Object.values(weakStudentsFirstSemester?.[0]?.scores || {})" :key="lssc">
                        <span v-for="ls in Object.keys(lssc)" :key="ls">
                            {{ ls }}
                        </span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(st, idx) in weakStudentsFirstSemester" :key="st">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ st.name }}</td>
                    <td>{{ st.class_room }}</td>
                    <td v-for="(lssc, lsId) in st.scores" :key="lsId">
                        <span v-for="(sc, ls) in lssc" :key="ls">
                            {{ sc }}
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>


</template>
<script setup>
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore } from '../../stores/semesterStore';
import { ref, onMounted, watch } from 'vue';

onMounted(async () => {
    await fetchSemesterList()
    await fetchClassInfo()
    await fetchWeakStudents()
    await fetchGradeList()
    await fetchClassList()
    if (selectedSemester.value === 2) await fetchFirstSemesterWeakStudentsList()
})

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const semesterList = ref('')
const selectedSemester = ref(semesterStore.semester.semester_id)
const selectedGrade = ref('')
const selectedClass = ref('')
const gradeList = ref('')
const classList = ref('')
const fetchSemesterList = async () => {
    const res = await axios.get(`api/academic/semesters`, {
    withCredentials: true,
    params: {
        is_active: ''
    }
    })
    semesterList.value = res.data.data
}

const fetchGradeList = async () => {
    const res = await axios.get('api/academic/grades', {
        params: {
            grade: '',
            grade_status: true
        },
        withCredentials: true
    })
    gradeList.value = res.data.data
}

const fetchClassList = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        params: {
            grade: selectedGrade.value
        },
        withCredentials: true
    })
    classList.value = res.data.data
}

const today = () => {
    const d = new Date()
    return d.toISOString().split('T')[0]
}

const selectedDate = ref(today())

const classInfoList = ref([])
const fetchClassInfo = async () => {
    const res = await axios.get(`api/report/daily/class-rooms`, {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: selectedSemester.value,
            day: selectedDate.value
        }
    })
    classInfoList.value = res.data.data
}


watch([selectedDate, selectedSemester], ([newDate, newSe]) => {
    if (newDate || newSe) {
        fetchClassInfo()
        fetchWeakStudents()
    }
})


const weakStudents = ref([])
const fetchWeakStudents = async () => {
    const res = await axios.get('api/scores/students/weak', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: selectedSemester.value,
            grade: selectedGrade.value,
            class_room_id: selectedClass.value,
            
        }
    })
    weakStudents.value = res.data.data
    if (selectedSemester.value === 2) {
        fetchFirstSemesterWeakStudentsList()
    }
}

const weakStudentsFirstSemester = ref('')
const fetchFirstSemesterWeakStudentsList = async () => {
    const res = await axios.get('api/scores/students/weak', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: 1,
            grade: selectedGrade.value,
            class_room_id: selectedClass.value
        }
    })
    weakStudentsFirstSemester.value = res.data.data
}

</script>