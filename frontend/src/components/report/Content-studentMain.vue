<template>
    <div style="display: flex; gap: 1em;">
        <span>Kết quả học tập</span>
        <div>
            <select v-model="yearSelected">
                <option value=""> --Chọn năm học-- </option>
                <option v-for="y in yearList" :key="y.id" :value="y.id">{{ y.year }}</option>
            </select>
        </div>

        <div>
            <select v-model="semesterSelected">
                <option value="">-- Chọn học kỳ --</option>
                <option v-for="s in semesterList" :key="s.semester_id" :value="s.semester_id">{{ s.semester }}</option>
            </select>
        </div>

        <button @click.prevent="getData">Lấy kết quả</button>
    </div>
    <div style="display: flex; gap: 2em;">
        <div>Học sinh: {{ info.name }}</div>
        <div>MS: {{ info.student_code }}</div>
        <div>{{ info.class_room ? `Lớp ${info.class_room}` : info.transfer_info }}</div>
    </div> 
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th rowspan="2" style="width: 7em;">Môn học</th>
                    <th colspan="4">Thường xuyên</th>
                    <th rowspan="2" style="width: 5em;">Giữa kỳ</th>
                    <th rowspan="2" style="width: 5em;">Cuối kỳ</th>
                    <th rowspan="2" style="width: 5em;">Tổng kết</th>
                    <th rowspan="2" style="width: 6em;">Xếp loại</th>
                    <th rowspan="2" style="width: 25em;">Nhận xét</th>
                </tr>
                <tr>
                    <th style="width: 5em;">Miệng</th>
                    <th style="width: 5em;">KT 15P</th>
                    <th style="width: 5em;">Miệng</th>
                    <th style="width: 5em;">KT 15P</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="(s, i) in results" :key="s.student_id">
                    <td>{{ s.lesson}}</td>
                    <template v-for="scoreType in Object.keys(s.scores).sort()" :key="scoreType">
                        <td v-for="attempt in Object.keys(s.scores[scoreType]).sort()" :key="attempt">
                                <span>{{ s.scores[scoreType][attempt] ? s.scores[scoreType][attempt] : '-' }}</span>
                        </td>
                    </template>
                    <td>{{ s.total ? s.total : '-' }}</td>
                    <td>{{ s.status === true ? 'Đạt' : s.status === false ? 'Chưa đạt' : '-' }}</td>
                    <td>{{ s.note }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-if="summary.status" style="display:flex; gap: 2em">
        <span>Kết quả năm học</span>
        <span>Điểm trung bình: {{ summary.score }}</span>
        <span>Chuyên cần: Vắng {{ summary.absent_day }}</span>
        <span>Hạnh kiểm: {{ summary.conduct === 'true' ? 'Đạt' : summary.conduct === 'false' ? 'Chưa đạt' : '-' }}</span>
        <span>Kết quả: {{ summary.status }}</span>
        <span>Xếp loại: {{ summary.learning_status }}</span>
    </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore} from '../../stores/semesterStore'

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const yearSelected = ref('')
const semesterSelected = ref('')
yearSelected.value = yearStore.year.id
semesterSelected.value = semesterStore.semester.semester_id
onMounted(() => {
    Promise.all([
        fetchSemester(),
        fetchYear(),
        fetchUserInfo(),
        getAcademicData()
    ])
})
const info = ref([])
const fetchUserInfo = async () => {
    const res = await axios.get(`api/users/years/${yearSelected.value}/me`, {
        withCredentials: true
    })
    info.value = res.data.data[0]
}

const yearSearch = ref('')
const yearList = ref([])
const fetchYear = async () => {
  const res = await axios.get('api/academic/me/years', {
    params: {
      year: yearSearch.value
    }
  })
  yearList.value = res.data.data
}

const semesterSearch = ref('')
const semesterList = ref([])
const fetchSemester = async () => {
  const res = await axios.get('api/academic/semesters', {
    withCredentials: true, 
    params: {
      semester: semesterSearch.value,
      is_active: ''
    }
  })
  semesterList.value = res.data.data
}

const results = ref([])
const getAcademicData = async () => {
    const res = await axios.get(`api/academic/entity/scores/me`, {
        withCredentials: true,
        params: {
            year_id: yearSelected.value,
            semester_id: semesterSelected.value
        }
    })
    results.value = res.data.data
}
const summary = ref('')
const yearSummary = async () => {
    const res = await axios.get(`api/academic/summary/years/${yearSelected.value}/me`, {
        withCredentials: true
    })
    summary.value = res.data.data
}

const getData = async () => {
    await fetchUserInfo()
    await getAcademicData()
    await yearSummary()
}
</script>