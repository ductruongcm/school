<template>
    <div>
        <label> Môn học: </label>
        <select v-model="selectedLesson">
            <option value="" disabled>--Chọn môn học--</option>
            <option v-for="ls in lessonList" :key="ls.lesson_id" :value="ls.lesson_id">{{ ls.lesson }}</option>
        </select>
        <label> Danh sách lớp học:  </label>
        <select v-model="selectedClass">
            <option value="" disabled>-- Chọn lớp --</option>    
            <option v-for="item in classList" :key="item.class_room_id" :value="item.class_room_id">{{ item.class_room }}</option>
        </select>
        <label> Học kỳ: </label>
        <select v-model="selectedSemester">
            <option value="" disabled>-- Chọn học kỳ --</option>
            <option v-for="semester in semesterList" :key="semester.semester_id" :value="semester.semester_id">{{ semester.semester }}</option>
        </select>
        <button @click.prevent="fetchStudentData">Lấy danh sách</button>
        <button v-if="!editing" @click.prevent="addScore">Cho điểm</button>
        <button v-else @click.prevent="confirm">Xác nhận</button>
        <button v-if="editing" @click.prevent="cancel">Hủy</button>
        <button @click.prevent="summary">Tổng kết</button>
    </div>
    <div>{{ resultMsg }}</div>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th rowspan="2" style="width: 3em;">STT</th>
                    <th rowspan="2" style="width: 10em;">Tên</th>
                    <th colspan="4">Thường xuyên</th>
                    <th rowspan="2" style="width: 5em;">Giữa kỳ</th>
                    <th rowspan="2" style="width: 5em;">Cuối kỳ</th>
                    <th rowspan="2" style="width: 5em;">Tổng kết</th>
                    <th rowspan="2" style="width: 6em;">Xếp loại</th>
                    <th rowspan="2" style="width: 20em;">Ghi chú</th>
                </tr>
                <tr>
                    <th style="width: 5em;">Miệng</th>
                    <th style="width: 5em;">KT 15P</th>
                    <th style="width: 5em;">Miệng</th>
                    <th style="width: 5em;">KT 15P</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="(s, i) in studentList" :key="s.student_id">
                    <td>{{ i + 1 }}</td>
                    <td>{{ s.name }}</td>
                    <template v-for="scoreType in Object.keys(s.scores).sort()" :key="scoreType">
                        <td v-for="attempt in Object.keys(s.scores[scoreType]).sort()" :key="attempt">
                                <input v-if="editing" v-model="s.scores[scoreType][attempt]" style="width: 6em;"/>
                                <span v-else>{{ s.scores[scoreType][attempt] }}</span>
                        </td>
                    </template>
                    <td>{{ s.total ? s.total : '-' }}</td>
                    <td>{{ s.status === true ? 'Đạt' 
                                             : s.status === false ? 'Không đạt' : '-'}}</td>
                    <td>
                        <input v-if="editing" type="text" v-model="s.note" style="width: 23em;" />
                        <span v-else>{{ s.note }}</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>

</template>

<script setup>
import { onMounted, ref, watch } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const yearStore = userYearStore()
const classList = ref([])
const studentList = ref([])
const selectedClass = ref('')
const resultMsg = ref('')

onMounted(async () => {
    await Promise.all([
        fetchSemesterData(),
        fetchClassData(),
        fetchLessonData()
    ])
})

watch(selectedClass, (newVal) => {
    if (newVal) {
        fetchStudentData()
    }
})

const selectedGrade = ref('')
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
        }
    })
    classList.value = res.data.data
}

const semesterList = ref([])
const selectedSemester = ref('')
const semesterSearch = ref('')
const fetchSemesterData = async () =>{
    const res = await axios.get('api/academic/semesters', {
        withCredentials: true,
        params: {
            semester: semesterSearch.value
        }
    })
    semesterList.value = res.data.data
    const active = semesterList.value?.find(i => i.semester_status === true)
    selectedSemester.value = active.semester_id
}

const selectedLesson = ref('')
const lessonList = ref([])
const fetchLessonData = async () => {
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

const fetchStudentData = async () => {
    if (selectedLesson.value === '' || selectedClass.value === '' || selectedSemester.value === '') {
        alert('Chưa chọn môn học/danh sách lớp học/học kỳ!')
        return
    }

    const res = await axios.get(`api/academic/entity/lessons/${selectedLesson.value}/scores`, {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: selectedSemester.value,
            class_room_id: selectedClass.value
        },
        withCredentials: true
    })
    studentList.value = res.data.data
}

const editing = ref(false)
const originalStudentList = ref({})
const addScore = () => {
    originalStudentList.value = JSON.parse(JSON.stringify(studentList.value))
    editing.value = true
}

const cancel = () => {
    studentList.value = originalStudentList.value
    editing.value = false
}

const confirm = async () => {
    const changedRows = studentList.value.map(s => {
        const origin = originalStudentList.value.find(o => o.student_id === s.student_id)
        
        if (!origin) return null;

        const noteChanged = s.note !== origin.note;
        
        const changedScoreEntries = Object.entries(s.scores).map(([typeId, scoreGroup]) => {
            const originGroup = origin.scores[typeId] || {};
            const diffs = Object.fromEntries(Object.entries(scoreGroup)
                .filter(([attempt, newVal]) => Number(newVal) !== Number(originGroup[attempt])))

            return Object.keys(diffs).length > 0 ? [typeId, diffs] : null;
        })
        .filter(Boolean);
        
        const changedScore = Object.fromEntries(changedScoreEntries)

        if (noteChanged || Object.keys(changedScore).length > 0) {
            return {
                student_id: s.student_id,
                ...(noteChanged ? { note: s.note } : {}),
                ...(Object.keys(changedScore).length > 0 ? { scores: changedScore } : {})
            };
        }

        return null;
    })
    .filter(Boolean);

    if (changedRows.length > 0) {

        const payload = {
            students: changedRows, 
            year_id: yearStore.year.id,
            lesson_id: selectedLesson.value,
            semester_id: selectedSemester.value
        }

        try {
            const res = await axios.post(`api/academic/entity/scores`, payload, {

                withCredentials: true,
                headers: {'Content-Type': 'application/json'}

            })

            resultMsg.value = res.data.msg
            editing.value = false
            fetchStudentData()

        } catch (e) { 
            if (e.response && [400,404,409,422,500].includes(e.response.status)) {
                resultMsg.value = e.response.data.msg
            }
        }
    }
    
    return
}

const summary = async () => {
    const payload = {
        class_room_id: selectedClass.value,
        year_id: yearStore.year.id,
        semester_id: selectedSemester.value,
        lesson_id: selectedLesson.value
    }
    try{
        const res = await axios.put('api/academic/entity/scores/lessons/summary', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        fetchStudentData()
        resultMsg.value = res.data.msg

    } catch (e) {
        
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}

</script>
