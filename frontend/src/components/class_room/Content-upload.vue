<template>
    <div>Upload</div>
    <div>
        <form @submit.prevent="upload">
            <label>Lớp: </label>
            <select @change="fetchLesson" v-model="teachRoom">
                <option value="" disabled>-- Chọn lớp --</option>
                <option v-for="item in teachRoomList" :key="item.class_room_id" :value="item"> {{ item.class_room }} </option>
            </select> 
            <label>Thư mục: </label>
            <select v-model="folder">
                <option value="" disabled>-- Chọn môn --</option>
                <option>Tổng hợp</option>
                <option v-for="lesson in lessonList" :key="lesson.lesson_id" :value="lesson.lesson">{{ lesson.lesson }}</option>
            </select>         
            <br>
            <label>Nhập tên file: </label>
            <input type="text" v-model="filename" required> <br>
            <input type="file" @change="handleFileChange">
            <button type="submit">Upload</button>
        </form>
    </div>
    <div>{{ uploadMSG }}</div>
</template>
<script setup>
import { ref, onMounted, inject, watch } from 'vue';
import axios from 'axios';
import useUserStore from '../../stores/user';

const teachRoomList = ref([])
const lessonList = ref([])
const teachRoom = ref('')
const year = inject('year')
const folder = ref('')
const userStore = useUserStore()
onMounted(() => {
    fetchTeachClass()
})

const selectedFile = ref(null)
const uploadMSG = ref('')
const filename = ref('')

const fetchTeachClass = async () => {
    const res = await axios.get('api/academic/teach_rooms', {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'},
        params: {year: year.value}
    })
    teachRoomList.value = res.data.data
}

const fetchLesson = async () => {
    const res = await axios.get('api/academic/lessons', {
        withCredentials: true,
        params: {
            class_room_id: teachRoom.class_room_id,
            id: userStore.userInfo.id,
            year: year.value
        }
    })
    lessonList.value = res.data.data
}

function handleFileChange(event) {
    selectedFile.value = event.target.files[0]
}

const upload = async () => {
    if (!selectedFile.value) {
        uploadMSG.value = 'Bạn chưa chọn file để upload!!'
        
    } else {
        const file = selectedFile.value
        const payload = {
            class_room_id: teachRoom.value.class_room_id,
            class_room: teachRoom.value.class_room,
            folder: folder.value,
            file_name: filename.value,
            file_ext: file.name,
            file_type: file.type,
            file_size: file.size,
            user_id: userStore.userInfo.id,
            year: year.value
        }
        try {
            const res = await axios.post('api/cloud/files', payload, { 
                withCredentials: true,
            })
            const uploadURL = res.data.url
            
            await axios.put(uploadURL, file, {
                headers: {'Content-Type': file.type}
            })
            uploadMSG.value = 'Uploaded thành công!!'
        } catch (e) {
            if (e.response && e.response.status == 400 || 422 || 500) {
                uploadMSG.value = e.response.data.msg
            } else {
                uploadMSG.value = 'Có rắc rối rồi đó!!'
            }
        }
    }
}

// watch(classList, (newList) => {
//     if (newList.length === 1) {
//         classRoom.value = newList[0]
//     }
// })
</script>