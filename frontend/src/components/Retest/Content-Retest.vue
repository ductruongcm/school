<template>
    <h4>Danh sách học sinh thi lại</h4>
    <div style="display: flex; gap: 2em;">
        <label>
            Khối
            <select v-model="selectedGrade">
                <option value="" disabled>--Chọn khối--</option>
                <option v-for="grade in gradeList" :value="grade.grade" :key="grade.grade">{{ grade.grade }}</option>
            </select>
        </label>
        <label>
            Lớp
            <select v-model="selectedClass">
                <option value="">Tất cả</option>
                <option v-for="cl in classList" :value="cl.class_room_id" :key="cl.class_room_id">{{ cl.class_room }}</option>
            </select>
        </label>
        <label>
            Môn 
            <select v-model="selectedLesson">
                <option value="">Tất cả</option>
                <option v-for="ls in lessonList" :value="ls.lesson_id">{{ ls.lesson }}</option>
            </select>
        </label>
        <button @click.prevent="fetchStudentList">Lấy danh sách</button>
        <button v-if="!editing" @click.prevent="edit">Cho điểm</button>
        <button v-else @click.prevent="save">Lưu</button>
        <button v-if="editing" @click.prevent="cancel">Hủy</button>
        <button @click.prevent="summary">Tổng kết</button>
    </div>
    <div>{{ resultMsg }}</div>
    <div>{{ searchMsg }}</div>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;" v-if="studentList !== ''">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 8em;">Tên</th>
                    <th style="width: 4em;">Lớp</th>
                    <th style="width: 5em;" v-for="(lssc, lsId) in studentList?.[0]?.lesson_score || []" :key="lsId">
                        <span v-for="ls in Object.keys(lssc)">{{ ls }}</span>
                    </th>
                    <th style="width: 20em;">Ghi chú</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(student, idx) in studentList" :key="student">
                    <td>{{ idx + 1 }}</td>
                    <td>{{ student.name }}</td>
                    <td>{{ student.class_room }}</td>
                    <td v-for="(lssc, lsId) in student?.lesson_score || []" :key="lsId">
                        <span v-for="(sc, ls) in lssc">
                            <input style="width: 5em;" type="number" 
                                v-if="editing && 
                                ls === lessonList[0].lesson &&
                                student.note.includes(ls) &&
                                teachingClass.includes(student.class_room)" v-model="student.lesson_score[lsId][ls]">
                            <span v-else>{{ sc ? sc : '-' }}</span>
                        </span>
                    </td>
                    <td>{{ student.note }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const yearStore = userYearStore()
const classList = ref('')
const selectedClass = ref('')
const gradeList = ref('')
const selectedGrade = ref('')
const selectedLesson = ref('')
const resultMsg = ref('')
const searchMsg = ref('')
const fetchGradeList = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade_status: true
        }
    })
    gradeList.value = res.data.data
}
const teachingClass = ref([])
const fetchClassList = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
        }
    })
    classList.value = res.data.data
    classList.value.forEach(item => teachingClass.value.push(item.class_room))
}

const lessonList = ref([])
const fetchLessonList = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
            is_visible: true,
            is_folder: false,
            is_schedule: false
        }
    })
    lessonList.value = res.data.data
    if (lessonList.value.length === 1) {
        selectedLesson.value = lessonList.value[0].lesson_id
    }
}

const studentList = ref('')
const fetchStudentList = async () => {
    if (selectedGrade.value === '') {
        alert('Vui lòng chọn khối lớp để lấy danh sách!')
        return
    }

    const res = await axios.get(`api/years/${yearStore.year.id}/students/retest`, {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
            class_room_id: selectedClass.value,
            lesson_id: selectedLesson.value
        }
    })
    studentList.value = res.data.data || ''
    searchMsg.value = res.data.msg
}

const editing = ref(false)
const original = ref('')
const edit = () => {
    editing.value = true
    original.value = JSON.parse(JSON.stringify(studentList.value))
}

const cancel = () => {
    studentList.value = original.value
    editing.value = false
}

const save = async () => {
    const payload = studentList.value.map(item => {
        const origin = original.value.find(o => o.student_id === item.student_id)
        if (!original) return null

        const diff = getLessonScoreDiff(item.lesson_score, origin.lesson_score)
        if (!diff || Object.keys(diff).length === 0) return null

        return {student_id: item.student_id,
                lessons: diff
        }
    }).filter(Boolean)
    try {
        const res = await axios.put(`api/years/${yearStore.year.id}/students/retest`, payload, {
            withCredentials: true, 
            headers: {'Content-Type': 'application/json'}
        })
        
        fetchStudentList()
        editing.value = false
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}

const getLessonScoreDiff = (current, original) => {
    const diff = {}
    for (const lsId in current) {
        const curLessonScore = current[lsId]
        const orgLessonScore = original[lsId] || {}

        for (const lesson in curLessonScore) {
            const curScore = curLessonScore[lesson]
            const orgScore = orgLessonScore[lesson]

            if (curScore !== orgScore) {
                diff[lsId] = {'score': curScore}
            }
        }
    }
    return diff
}

const summary = async () => {
    try {
        const res = await axios.put(`api/years/${yearStore.year.id}/summary/retest`, {
            withCredentials: true
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}

onMounted(async() => {
    await fetchGradeList()
    await fetchLessonList()
    await fetchClassList()
})
</script>