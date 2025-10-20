<template>
    <div>Công cụ: Học kỳ</div>
        <form>
            <label> Thêm học kỳ </label>
            <input v-model="semesterInput" type="text"></input>
            <button @click.prevent="addSemester">Thêm</button>
        </form>
        <button v-if="!editing" @click.prevent="edit">Điều chỉnh</button>
        <button v-else @click.prevent="saveEdit">Lưu</button>
        <button v-if="editing" @click.prevent="cancelEdit">Hủy</button>
    <div>
        <table>
            <thead>
                <tr>
                    <td>STT</td>
                    <td>Học kỳ</td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in semesterList" :key="item.semester_id">
                    <td>{{ index + 1 }}</td>
                    <td>
                        <span v-if="!editing">{{ item.semester }}</span>
                        <input v-model="item.semester" v-else type="text">
                    </td>
                    <td>
                        <button @click.prevent="setScoreBoard(item)">Tạo bảng điểm</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div>{{ resultMsg }}</div>

</template>
<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const yearStore = userYearStore()
const semesterInput = ref('')
const resultMsg = ref('')
const editing = ref(false)

const addSemester = async () => {
    const payload = {
        semester: semesterInput.value,
        year_id: yearStore.year.id
    }
    try {
        const res = await axios.post('api/academic/semesters', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!'
        }
    }
}

const semesterList = ref([])
const semesterSearch = ref('')
const fetchSemesterData = async () => {
    const res = await axios.get('api/academic/semesters', {
        withCredentials: true,
        params: {
            semester: semesterSearch.value,
            year_id: yearStore.year.id
        }
    })
    semesterList.value = res.data.data
    
}

onMounted(() => {
    fetchSemesterData()
})

const originalSemester= ref([])
const edit = () => {
    editing.value = true
    originalSemester.value = JSON.parse(JSON.stringify(semesterList.value))
}

const cancelEdit = () => {
    semesterList.value = originalSemester.value
    editing.value = false
}

const saveEdit = async () => {
    const changedRows = semesterList.value.filter(semester => {
        semester['year_id'] = yearStore.year.id
        const original = originalSemester.value.find(o => o.semester_id === semester.semester_id)
        return original.semester !== semester.semester
    })
    try {
        const res = await axios.put('api/academic/semester', changedRows, {
            withCredentials: true
        })
        resultMsg.value = res.data.msg
        editing.value = false
        fetchSemesterData()
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 404 || 500) {
            resultMsg.value = e.response.data.msg
        }
    }
}

const setScoreBoard = async(item) => {
    const payload = {
        semester_id: item.semester_id,
        semester: item.semester,
        year_id: yearStore.year.id
    }
    try {
        const res = await axios.post('api/academic/scores', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status) {
            resultMsg.value = e.response.data.msg
        }
    }
}

</script>