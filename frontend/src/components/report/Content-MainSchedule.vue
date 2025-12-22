<template>
    <div style="display: flex; gap: 2em;">
        <div style="border-collapse: collapse; text-align: center;">
            <span>Lịch học</span> <br>
            <input type="date" v-model="selectedDate" @change="fetchTodayScheduleData">
            <table border="1">
                <thead>
                    <tr>
                        <th style="width: 4em;">Tiết</th>
                        <th style="width: 8em;" v-for="(ls, cl) in (Object.values(todayScheduleList)[0] || {})" :key="cl">
                            {{ cl }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(col, row) in todayScheduleList" :key="row">
                        <td>{{ row }}</td>
                        <template v-for="(ls, cl) in Object.values(col)" :key="cl">
                            <td>
                                <span>{{ ls.lesson }}</span> <br>
                                <span>{{ ls.teacher ? ls.teacher : '' }}</span>
                            </td>
                        </template>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
import axios from 'axios'
import { userYearStore } from '../../stores/yearStore'
import { useSemesterStore } from '../../stores/semesterStore'
import { ref, onMounted } from 'vue'

const yearStore = userYearStore()
const semesterStore = useSemesterStore()

onMounted(() => {
    fetchTodayScheduleData()
})

const today = () => {
    const d = new Date()
    return d.toISOString().split('T')[0]
}

const selectedDate = ref(today())

const todayScheduleList = ref([])
const fetchTodayScheduleData = async () => {
    const res = await axios.get('api/academic/entity/schedules/today', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: semesterStore.semester.semester_id,
            day: selectedDate.value
        }
    })
    todayScheduleList.value = res.data.data
}

</script>