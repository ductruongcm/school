<template>
    <h3>Điểm danh</h3>
    <div style="display: flex; gap: 2em;">
        <label>
            Ngày
            <input type="date" v-model="selectedDate">
        </label>
        <label>
            Lớp: 
            <select v-model="selectedClass">
                <option value="">--Chọn lớp--</option>
                <option v-for="cl in classList" :key="cl.class_room_id" :value="cl.class_room_id">{{ cl.class_room }}</option>
            </select>
        </label>
        <div>
            <button @click.prevent="fetchLessonTimeData">Lấy danh sách</button>
            <button v-if="!editing" @click.prevent="attend">Điểm danh</button>
            <button v-else @click.prevent="confirm">Xác nhận</button>
            <button v-if="editing" @click.prevent="cancel">Hủy</button>
        </div>
    </div>
    <div>{{ resultMsg }}</div>
    <div v-if="!resultMsg">
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 15em;">Họ tên</th>
                    <th v-for="(atnt, day) in attendence[0]?.dates" :key="day" style="width: 8em;">
                        <span>{{ day }}</span> <br>
                    </th>
                    <th style="width: 18em;">Ghi chú</th>
                </tr>
            </thead>

            <tbody>
                <tr v-for="(student, idx) in attendence" :key="attendence.student_id">
                    <td style="width: 3em;">{{ idx + 1 }}</td>
                    <td style="width: 15em;">{{ student.name }}</td>
                    <td v-for="(att, day) in student.dates" :key="day">
                        <select style="width: 7em;" v-if="editing && day === selectedDate" v-model="student.dates[day]">
                            <option value="P">Có</option>
                            <option value="E">Vắng (P)</option>
                            <option value="A">Vắng (KP)</option>
                        </select>
                        <span v-else>{{ att === 'P' ? 'Có' : att === 'A' ? 'Kh phép' : att === 'E' ? 'Có phép' : '-' }}</span>
                    </td>
                    <td>
                        <span v-if="editing"><input type="text" style="width: 19em;" v-model="student.note"></span>
                        <span v-else>{{ student.note }}</span>
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
import { useSemesterStore } from '../../stores/semesterStore';

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const resultMsg = ref('')

onMounted(async () => {
    await fetchScheduleData()
})

const classList = ref('')
const fetchScheduleData = async () => {
    const res = await axios.get('api/academic/entity/attendence/schedules', {
        withCredentials: true, 
        params: {
            year_id: yearStore.year.id,
            semester_id: semesterStore.semester.semester_id,
            day: selectedDate.value
        }
    })
    classList.value = res.data.data
    if (classList.value) {
        resultMsg.value = ''
        selectedClass.value = classList.value?.[0].class_room_id
        fetchLessonTimeData()
    } else {
        resultMsg.value = 'Không có tiết dạy!'
    } 
}

const selectedClass = ref('')
const attendence = ref('')
const fetchLessonTimeData = async () => {
    if (!classList.value) return null

    const res = await axios.get(`api/academic/entity/class-rooms/${selectedClass.value}/attendence`, {
        withCredentials: true, 
        params: {
            year_id: yearStore.year.id,
            semester_id: semesterStore.semester.semester_id,
            day: selectedDate.value
        }
    })
    attendence.value = res.data.data
    if (!attendence.value) {
        resultMsg.value = 'Không có tiết dạy!'
    }
}

const editing = ref(false)
const originalAttendence = ref('')
const attend = () => {
    originalAttendence.value = JSON.parse(JSON.stringify(attendence.value))
    editing.value = true
    attendence.value.forEach(item => item.dates[selectedDate.value] = 'P')
}

const cancel = () => {
    attendence.value = originalAttendence.value
    editing.value = false
}
const today = () => {
    const d = new Date()
    return d.toISOString().split('T')[0]
}

const selectedDate = ref(today())
const confirm = async () => {
    const changeRows = attendence.value.filter(item => {
        const origin = originalAttendence.value.find(o =>
            o.student_id === item.student_id
        )
        if (!origin) return false;

        return origin.dates[selectedDate.value] !== item.dates[selectedDate.value] || origin.note !== item.note
    })
    .map(item => ({
        student_id: item.student_id,
        status: item.dates[selectedDate.value],
        note: item.note
    }))

    if (changeRows.length === 0) return;

    const payload = {
        day: selectedDate.value,
        semester_id: semesterStore.semester.semester_id,
        year_id: yearStore.year.id,
        students: changeRows
    }
    
    try {
        const res = await axios.post('api/academic/entity/attendence', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
        })

        resultMsg.value = res.data.msg
        fetchLessonTimeData()
        editing.value = false
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}

watch(selectedDate, (newVal) => {
    if (newVal) {
        fetchScheduleData()
    }
})

</script>
