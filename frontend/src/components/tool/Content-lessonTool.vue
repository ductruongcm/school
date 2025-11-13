<template>
    <div>Công cụ: Môn học</div>

    <form>
        <label>Thêm Môn học: </label> 
        <input v-model="lessonInput" type="text">
        <label> Khối lớp: </label>
        <select v-model="selectedGrade">
            <option value="" selected disabled>-- Click chọn khối --</option>
            <option v-for="item in gradeList" :key="item.id" :value="item.grade">Khối {{ item.grade }}</option> 
        </select> <br>
        <label>
            <input v-model="is_folder" type="checkbox"> 
            Đăng ký vào danh sách thư mục
        </label><br>
        <label>
            <input v-model="is_schedule" type="checkbox">
             Đăng ký vào danh sách lịch học </label> <br>
        <label>
            <input v-model="is_visible" type="checkbox">
            Đăng ký vào danh sách giáo viên 
        </label> <br>
        <button @click.prevent="addLesson">Thêm Môn học</button>    
        <button @click.prevent="createLessonClass">Tạo bảng Môn học và Lớp</button>
        <button v-if="!editing" @click.prevent="edit">Cài đặt môn học</button>
        <button v-else @click.prevent="saveEdit">Xác nhận</button>
        <button v-if="editing" @click.prevent="editing = false">Hủy</button>
    </form>
    <div>{{ resultMsg }}</div>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 7em;">Môn học</th>
                    <th style="width: 5em;">Khối lớp</th>
                    <th style="width: 5em;">Thư mục</th>
                    <th style="width: 5em;">Giáo viên</th>
                    <th style="width: 5em;">Lịch học</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(lesson, index) in lessonList" :key="lesson.id">
                    <td>
                        <span>{{ index + 1 }}</span>
                    </td>
                    <td>
                        <span v-if="!editing">{{ lesson.lesson }}</span>
                        <input style="width: 7em;" v-model="lesson.lesson" v-else></input>
                    </td>

                    <td>
                        <span v-if="!editing">Khối {{ lesson.grade }}</span>
                        <select style="width: 5em;" v-else v-model="lesson.grade">
                            <option value="" disabled>-- Click chọn khối --</option>
                            <option v-for="g in gradeList" :key="g.id" :value="g.grade">Khối {{ g.grade }}</option>
                        </select>       
                    </td>
                    <td>
                        <span v-if="!editing">{{ lesson.is_folder ? 'Y' : 'N' }}</span>
                        <input v-else v-model="lesson.is_folder" :value="true" type="checkbox">
                    </td>
                    <td>
                        <span v-if="!editing">{{ lesson.is_visible ? 'Y' : 'N' }}</span>
                        <input v-else v-model="lesson.is_visible" type="checkbox">
                    </td>
                    <td>
                        <span v-if="!editing">{{ lesson.is_schedule ? 'Y' : 'N' }}</span>
                        <input v-else v-model="lesson.is_schedule" type="checkbox">
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
const is_visible = ref('')
const is_folder = ref('')
const is_schedule = ref('')
const addLesson = async () => {
    const payload = {
        lesson: lessonInput.value,
        grade: selectedGrade.value,
        is_visible: is_visible.value,
        is_schedule: is_schedule.value,
        is_folder: is_folder.value
    }
    try {
        const res = await axios.post('api/academic/lessons', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}

const createLessonClass = async () => {
    const payload = {year_id: yearStore.year.id}
    const res = await axios.post('api/academic/relation/lessons-class', payload, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
}

const lessonList = ref([])
const selectedGrade = ref('')
const fetchLessonData = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        params: {
            grade: selectedGrade.value,
            is_folder: '',
            is_visible: '',
            is_schedule: ''
        },
        withCredentials: true
    })
    lessonList.value = res.data.data
}

const gradeList = ref([])
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade_status: ''
        }
    })
    gradeList.value = res.data.data
}

onMounted(() => {
    fetchLessonData()
    fetchGradeData()
})

const editing = ref(false)
const original = ref([])

const edit = () => {
    editing.value = true
    original.value = JSON.parse(JSON.stringify(lessonList.value))
}

const saveEdit = async () => {
    const changedRows = lessonList.value.map(item => {
        const origin = original.value.find(o => o.lesson_id === item.lesson_id)
        if (!origin) return null;

        const changedEntries = Object.entries(item).filter(([k, v]) => v !== origin[k]);
        if (changedEntries.length === 0) return null;

        const changedObject = {
            ...Object.fromEntries(changedEntries),
            lesson_id: item.lesson_id,
            year_id: yearStore.year.id
        }
        
        return changedObject
    }).filter(Boolean)

    if (changedRows.length > 0) {
        try {
            const res = await axios.put('api/academic/lessons', changedRows, {
                withCredentials: true,
                headers: {'Content-Type': 'application/json'}
            })

            resultMsg.value = res.data.msg
            editing.value = false
            fetchLessonData()
        } catch (e) {
            if (e.response && [400,404,409,422,500].includes(e.response.status)) {
                resultMsg.value = e.response.data.msg
            }
        }
    } else {
        editing.value = false
    }
}




</script>