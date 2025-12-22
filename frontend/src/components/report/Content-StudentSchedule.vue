<template>
    <div>Lịch học</div>
    <div style="display: flex; gap: 2em;">
        <div>Học sinh: {{ info.name }}</div>
        <div>MS: {{ info.student_code }}</div>
        <div>Lớp: {{ info.class_room }}</div>
    </div> 
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
                        <span>{{ subject.lesson }}</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import { userYearStore } from '../../stores/yearStore'
import { useSemesterStore } from '../../stores/semesterStore'
import { ref, onMounted } from 'vue';
import axios from 'axios';

const yearStore = userYearStore()
const semesterStore = useSemesterStore()

onMounted( () => {
    fetchUserInfo()
})


const info = ref([])
const scheduleData = ref([])
const fetchUserInfo = async () => {
    const res = await axios.get(`api/users/years/${yearStore.year.id}/me`, {
        withCredentials: true
    })
        info.value = res.data.data[0]

    const scheduleRes = await axios.get('api/academic/entity/schedules/me', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: semesterStore.semester.semester_id,
            class_room_id: info.value.class_room_id
        }
    })
    scheduleData.value = scheduleRes.data.data
}

</script>