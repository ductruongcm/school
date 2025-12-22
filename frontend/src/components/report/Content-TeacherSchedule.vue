<template>
    <div>Lịch dạy</div>
    <input type="date" v-model="selectedDate">
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr style="height: 2em;">
                    <th style="width: 8em;" class="border px-2 py-1">Tiết</th>
                    <th style="width: 8em;" v-for="day in Object.keys(Object.values(scheduleData)[0] || {})" :key="day">
                        <span>Thứ {{ Number(day) + 1 }}</span>
                    </th>
                </tr>
            </thead>
            <tbody>
                <tr style="height: 2em;" v-for="(dayCls, period) in scheduleData" :key="period">
                    <td>Tiết {{ period }}</td>
                    <td v-for="cls in dayCls" :key = cls>
                        <span>{{ cls.class_room ? cls.class_room : '-' }}</span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore } from '../../stores/semesterStore';

onMounted(async () => {
    await fetchScheduleData()
})

const today = () => {
    const d = new Date()
    return d.toISOString().split('T')[0]
}

const selectedDate = ref(today())

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const scheduleData = ref([])
const fetchScheduleData = async () => {
    const res = await axios.get('api/academic/entity/schedules/me', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: semesterStore.semester.semester_id,
            day: selectedDate.value
        }
    })
    scheduleData.value = res.data.data
}

</script>