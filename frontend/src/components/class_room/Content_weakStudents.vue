<template>
    <div>
        <h4>Danh sách học sinh cần chú ý</h4>
        <div style="display: flex; gap: 2em;">
            <label>
                Lớp 
                <select v-model="selectedClass">
                    <option value="">--Chọn lớp--</option>
                    <option v-for="cl in classList" :key="cl.class_room_id" :value="cl.class_room_id">{{ cl.class_room }}</option>
                </select>
            </label>
            <label>
                Học kỳ
                <select v-model="selectedSemester" @change="fetchweakStudentList">
                    <option value="">--Chọn học kỳ--</option>
                    <option v-for="sm in semesterList" :value="sm.semester_id" :key="sm.semester_id">{{ sm.semester }}</option>
                </select>
            </label>
        </div>
        <div>
            <span>Danh sách học sinh cần chú ý trong kỳ</span>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th style="width: 3em;">STT</th>
                        <th style="width: 9em;">Tên</th>
                        <th style="width: 5em;" v-for="lssc in Object.values(weakStudents?.[0]?.scores || {})" :key="lssc">
                            <span v-for="ls in Object.keys(lssc)" :key="ls">
                                {{ ls }}
                            </span>
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(st, idx) in weakStudents" :key="st">
                        <td>{{ idx + 1 }}</td>
                        <td>{{ st.name }}</td>
                        <td v-for="lssc in st?.scores" :key="lssc">
                            <span v-for="sc in Object.values(Object.values(lssc))" :key="sc">
                                {{ sc }}
                            </span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div v-if="selectedSemester === 2 && weakStudentsFirstSemester.length > 0">
                <span>Danh sách học sinh cần chú ý học kỳ I</span>
                <table border="1" style="border-collapse: collapse; text-align: center;">
                    <thead>
                        <tr>
                            <th style="width: 3em;">STT</th>
                            <th style="width: 9em;">Tên</th>
                            <th style="width: 5em;" v-for="lssc in Object.values(weakStudentsFirstSemester?.[0]?.scores || {})" :key="lssc">
                                <span v-for="ls in Object.keys(lssc)" :key="ls">
                                    {{ ls }}
                                </span>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(st, idx) in weakStudentsFirstSemester" :key="st">
                            <td>{{ idx + 1 }}</td>
                            <td>{{ st.name }}</td>
                            <td v-for="(lssc, lsId) in st.scores" :key="lsId">
                                <span v-for="(sc, ls) in lssc" :key="ls">
                                    {{ sc }}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
        </div>
    </div>
</template>
<script setup>
import axios from 'axios';
import { ref, onMounted, watch } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore } from '../../stores/semesterStore';
import { useUserStore } from '../../stores/user';

const userStore = useUserStore()
const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const selectedClass = ref('')
const classList = ref('')
const selectedSemester = ref('')
const semesterList = ref('')
selectedSemester.value = semesterStore.semester.semester_id
const homeroom_id = userStore.userInfo.homeroom_id
const weakStudents = ref('')
const fetchClassList = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: '',
        }
    })
    classList.value = res.data.data
    selectedClass.value = homeroom_id || classList.value[0].class_room_id
}

const fetchSemesterList = async () => {
    const res = await axios.get(`api/academic/semesters`, {
    withCredentials: true,
    params: {
        is_active: ''
    }
    })
    semesterList.value = res.data.data
}

const fetchweakStudentList = async () => {
    const res = await axios.get('api/scores/students/weak', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: selectedSemester.value,
            class_room_id: selectedClass.value
        }
    })
    weakStudents.value = res.data.data
}

const weakStudentsFirstSemester = ref('')
const fetchFirstSemesterWeakStudentsList = async () => {
    const res = await axios.get('api/scores/students/weak', {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            semester_id: 1,
            class_room_id: selectedClass.value
        }
    })
    weakStudentsFirstSemester.value = res.data.data
}

watch([selectedClass, selectedSemester], async ([newClass, newSem]) => {
    if (newClass || newSem) await fetchweakStudentList()
    if (newClass && newSem === 2) await fetchFirstSemesterWeakStudentsList()
})

onMounted(async () => {
    await fetchClassList()
    await fetchSemesterList()
    await fetchweakStudentList()
    if (selectedSemester.value === 2) await fetchFirstSemesterWeakStudentsList()
})
</script>