<template>
    <div>Quản lý thư mục Cloud</div>
    <form>
        <label>Lớp học: </label>
        <select v-model="selectedClass_room" @change.prevent="fetchFolderData">
            <option value="" selected disabled>-- Chọn lớp --</option>
            <option v-for="item in classList" :key="item.id" :value="item">{{ item.class_room }}</option>
        </select>
        <label>Thư mục: </label>
        <select v-model="selectedFolder">
            <option value="" selected disabled>-- Chọn thư mục --</option>
            <option value="Tổng hợp">Tổng hợp</option>
            <option v-for="item in folderList" :key="item.id" :value="item.lesson">{{ item.lesson }}</option>
        </select>
        <button @click.prevent="createFolder">Tạo thư mục</button>
    </form>
    <div>{{ resultMsg }}</div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const yearStore = userYearStore()
const classList = ref([])
const class_roomSearch = ref('')
const lessonSearch = ref('')
const selectedClass_room = ref('')
const selectedFolder = ref('')
const resultMsg = ref('')

onMounted(() => {
    fetchClassData()
})

const gradeSearch = ref('')
const fetchClassData = async () => {
    const res = await axios.get('api/academic/class_rooms', {
        withCredentials: true,
        params: {
            class_room: class_roomSearch.value,
            year_id: yearStore.year.id,
            grade_id: gradeSearch.value
        }
    })
    classList.value = res.data.data
}

const folderList = ref(null)
const fetchFolderData = async () => {
    console.log(selectedClass_room)
    const res = await axios.get('api/cloud/folders', {
        withCredentials: true,
        params: {
            grade_id: selectedClass_room.grade_id,
        }
    })
    console.log(res.data.data)
    folderList.value = res.data.data
}

// const fetchLessonData = async () => {
//     const res = await axios.get('api/academic/lessons', {
//         withCredentials: true,
//         params: {
//             lesson: lessonSearch.value,
//             grade_id: gradeSearch.value
//         }
//     })
//     lessonList.value = res.data.data
// }

const createFolder = async () => {
    const payload = {
        class_room_id: selectedClass_room.value,
        year_id: yearStore.year.id,
        folder: selectedFolder.value
    }
    try {    const res = await axios.post('api/cloud/folders', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        }
    }
}
</script>