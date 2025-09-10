<template>
    <div>Danh sách giáo viên</div>
    <div class="main">
        <div>
            <form>
                <label>Tìm theo môn học: </label>
                <select v-model="selectedLesson">
                    <option selected value="">-- Theo môn học --</option>
                    <option v-for="lesson in lessonList" :key="lesson">{{ lesson.lesson }}</option>
                </select>
                <label> Tìm theo lớp: </label>
                <select v-model="selectedClass">
                    <option selected value="">-- Theo lớp --</option>
                    <option v-for="classRoom in classRoomList" :key="classRoom">{{ classRoom.class_room }}</option>
                </select>
                <label> Tìm theo tên: </label>
                <input v-model="filterName" placeholder="Nhập tên giáo viên">
                <button type="button" @click="onReset">Nhập lại</button>
                
            </form>
        </div>
        <div> {{ teacherSearchMsg }}</div>
        <div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ và tên</th>
                        <th>Chuyên môn</th>
                        <th>Phụ trách lớp</th>
                        <th>Số điện thoại</th>
                        <th>Địa chỉ</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in teacherList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>{{ item.name }}</td>
                        <td>{{ item.lesson }}</td>
                        <td>{{ item.class_room }}</td>
                        <td>{{ item.tel }}</td>
                        <td>{{ item.add }}</td>
                        <td>{{ item.email }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, watch, inject } from 'vue';
import axios from 'axios';
import { message } from '../stores/usePopup';

const teacherList = ref([])
const teacherSearchMsg = ref('')
const lessonList = ref([])
const selectedLesson = ref('')
const selectedClass = ref('')
const classRoomList = ref('')
const year = inject('year')
const page = ref(1)
const limit = 20
const filterName = ref('')

onMounted(async () => {
    const res = await axios.get('api/teacher/show_lesson', { withCredentials: true})
    lessonList.value = res.data.data
})

onMounted(async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, { 
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classRoomList.value = res.data.data
})

async function fetchdata(lessonVal, classVal, nameVal) {
    const res = await axios.get('/api/teacher/show_teacher', {
        params: {page: page.value, limit, lesson: lessonVal, class_room: classVal, name: nameVal}}, {
        withCredentials: true})
    teacherList.value = res.data.data
}

onMounted(() => {
    fetchdata(selectedLesson.value, selectedClass.value, filterName.value)

    watch([selectedLesson, selectedClass, filterName], async([lessonVal, classVal, nameVal]) => {
        fetchdata(lessonVal, classVal, nameVal)
    })
})

function onReset() {
  selectedLesson.value = ""
  selectedClass.value = ""
  filterName.value = ""

  // gọi API lại để load bảng mặc định
  fetchTeachers("", "", "")
}
// 

// async function changePage(newPage) {
//     page.value = newPage
//     await fetchdata()
// }







</script>
<style scoped>
.main {
    position: relative;
    right: 20em;
    margin-top: 2em;
}
</style>