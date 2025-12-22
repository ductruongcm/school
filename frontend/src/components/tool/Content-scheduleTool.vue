<template>
    <div>Công cụ: Thời khóa biểu</div>
    <label> Khối lớp: </label>
    <select v-model="selectedGrade" @change="fetchClassData">
        <option value="" disabled>- Chọn khối lớp -</option>
        <option value="">Toàn bộ</option>
        <option v-for="grade in gradeList" :key="grade.grade" :value="grade.grade">Khối lớp {{ grade.grade }}</option>
    </select>
    <label> Học kỳ: </label>
    <select v-model="selectedSemester">
        <option value="" disabled>- Chọn học kỳ -</option>
        <option v-for="semester in semesterList" :key="semester.semester_id" :value="semester.semester_id">{{ semester.semester }}</option>
    </select>
    <label> Lớp học: </label>
    <select v-model="selectedClass">
        <option value="" disabled>- Chọn lớp -</option>
        <option v-for="cls in classList" :key="cls.class_room_id" :value="cls.class_room_id">{{ cls.class_room }}</option>
    </select>
    <button v-if="!editing" @click.prevent="fetchScheduleData" :disabled="selectedClass === ''">Tìm</button>
    <button v-if="!editing" @click.prevent="editSchedule">Tạo/Điều chỉnh</button>
    <button v-if="editing" @click.prevent="save">Lưu</button>
    <button v-if="editing" @click.prevent="cancelEdit">Hủy</button>
    <div>{{ resultMsg }}</div>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr style="height: 2em;">
                    <th style="width: 8em;" class="border px-2 py-1">Tiết</th>
                    <th style="width: 8em;" v-for="day in Object.keys(Object.values(scheduleData)[0] || {})">Thứ {{ Number(day) + 1 }} </th>
                </tr>
            </thead>
            <tbody>
                <tr style="height: 2em;" v-for="(dayObj, period) in scheduleData" :key="period">
                    <td>Tiết {{ period }}</td>
                    <td v-for="(subject, day) in dayObj" :key = day>
                        <span v-if="!editing">{{ subject.lesson}}</span>
                        <select style="width: 8em;" v-else v-model="subject.lesson_id">
                            <option :value="null" disabled>Chọn môn</option>
                            <option :value="null">Bỏ chọn</option>
                            <option v-for="ls in lessonList" :key="ls.lesson_id" :value="ls.lesson_id">{{ ls.lesson }}</option>
                        </select>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import axios from 'axios';
import { useSemesterStore } from '../../stores/semesterStore';

onMounted(async () => {
    await Promise.all[
        fetchClassData(), 
        fetchGradeData(),
        fetchSemesterData(),
        fetchScheduleData()
    ]
})

const scheduleData = ref("")
const fetchScheduleData = async () => {
    const res = await axios.get('api/academic/entity/schedules', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: selectedSemester.value,
            class_room_id: selectedClass.value
        }
    })
    scheduleData.value = res.data.data
}


const yearStore = userYearStore()
const resultMsg = ref('')

const gradeList = ref([])

const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade_status: true
        }
    })
    gradeList.value = res.data.data
}

const classList = ref([])
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

const semesterSearch = ref('')
const semesterList = ref([])
const fetchSemesterData = async () => {
    const res = await axios.get('api/academic/semesters', {
        withCredentials: true,
        params: {
            semester: semesterSearch.value
        }
    })
    semesterList.value = res.data.data
}

const semesterStore = useSemesterStore()
const selectedSemester = ref('')
selectedSemester.value = semesterStore.semester.semester_id
const selectedClass = ref('')
const editing = ref(false)
const lessonList = ref([])
const fetchLessondata = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            grade: selectedGrade.value,
            is_visible: false,
            is_folder: false,
            is_schedule: true
        }
    })
    lessonList.value = res.data.data
}

const original = ref({})
const editSchedule = async () => {
    if (selectedClass.value === '') {
        alert('Vui lòng chọn lớp học để tạo thời khóa biểu!') 
        return
    }
    original.value = JSON.parse(JSON.stringify(scheduleData.value))
    await fetchLessondata()
    editing.value = true
}

function deepEqual(obj1, obj2) {
  if (obj1 === obj2) return true; // cùng reference hoặc cùng giá trị nguyên thủy

  if (typeof obj1 !== 'object' || obj1 === null ||
      typeof obj2 !== 'object' || obj2 === null) {
    return false;
  }

  const keys1 = Object.keys(obj1);
  const keys2 = Object.keys(obj2);

  if (keys1.length !== keys2.length) return false;

  for (let key of keys1) {
    if (!keys2.includes(key)) return false;
    if (!deepEqual(obj1[key], obj2[key])) return false;
  }

  return true;
}

const save = async () => {
    Object.values(scheduleData.value).forEach(row => 
        Object.values(row).forEach(cell => 
            delete cell.lesson
        )
    )

    Object.values(original.value).forEach(row => 
        Object.values(row).forEach(cell => 
            delete cell.lesson
        )
    )

    if (deepEqual(original.value, scheduleData.value)) return null;

    const payload = {
        year_id: yearStore.year.id, 
        semester_id: selectedSemester.value,
        class_room_id: selectedClass.value,
        schedules: scheduleData.value
    }
    try {        
        const res = await axios.post(`api/academic/entity/schedules`, payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        editing.value = false
        resultMsg.value = res.data.msg
        fetchScheduleData()

    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}


const cancelEdit = () => {
    editing.value = false
}
</script>
