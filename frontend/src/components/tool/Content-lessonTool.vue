<template>
    <div>Công cụ: Môn học</div>

    <form>
        <label>Thêm Môn học: </label> 
        <input v-model="lessonInput" type="text">
        <select v-model="selectedGrade">
            <option value="" selected disabled>-- Click chọn khối --</option>
            <option v-for="item in gradeList" :key="item.id" :value="item.id">Khối {{ item.grade }}</option>
        </select>
        <button @click.prevent="addLesson">Thêm</button>
    </form>
    <div>{{ resultMsg }}</div>
    <div>
        <button v-if="!editing" @click.prevent="edit">Cài đặt môn học</button>
        <button v-else @click.prevent="saveEdit">Xác nhận</button>
        <button v-if="editing" @click.prevent="editing = false">Hủy</button>
    </div>
    <div>
        <table>
            <thead>
                <tr>
                    <td>STT</td>
                    <td>Môn học</td>
                    <td>Khối lớp</td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(lesson, index) in lessonList" :key="lesson.id">
                    <td>
                        <span>{{ index + 1 }}</span>
                    </td>
                    <td>
                        <span v-if="!editing">{{ lesson.lesson }}</span>
                        <input v-model="lesson.lesson" v-else></input>
                    </td>

                    <td>
                        <span v-if="!editing">Khối {{ lesson.grade }}</span>
                        <select v-else v-model="lesson.grade_id">
                            <option value="" disabled>-- Click chọn khối --</option>
                            <option v-for="g in gradeList" :key="g.id" :value="g.id">Khối {{ g.grade }}</option>
                        </select>       
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

</template>
<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
const yearStore = userYearStore()
const resultMsg = ref('')
const lessonInput = ref('')

const addLesson = async () => {
    const payload = {
        lesson: lessonInput.value,
        grade_id: selectedGrade.value,
        year_id: yearStore.year.id
    }
    try {
        const res = await axios.post('api/academic/lessons', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        }
    }
}

const lessonList = ref([])
const lessonSearch = ref('')
const selectedGrade = ref('')
const fetchLessonData = async () => {
    const res = await axios.get('api/academic/lessons', {
        params: {
            lesson: lessonSearch.value,
            grade_id: selectedGrade.value,
            year_id: yearStore.year.id
        },
        withCredentials: true
    })
    lessonList.value = res.data.data
}

const gradeSearch = ref('')
const gradeList = ref([])
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value
        }
    })
    gradeList.value = res.data.data
}

onMounted(() => {
    fetchLessonData()
    fetchGradeData()
})

const editing = ref(false)
let originalLessonList = []

const edit = () => {
    editing.value = true
    originalLessonList = JSON.parse(JSON.stringify(lessonList.value))
}


const saveEdit = async () => {
    const changedRows = lessonList.value.filter(lesson => {
        lesson['year_id'] = yearStore.year.id
        const original = originalLessonList.find(o => o.lesson_id === lesson.lesson_id)
        return lesson.lesson !== original.lesson || lesson.grade_id !== original.grade_id
    })  
    const payload = changedRows

    const res = await axios.put('api/academic/lessons', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    resultMsg.value = res.data.msg
    editing.value = false
    fetchLessonData()
}




</script>