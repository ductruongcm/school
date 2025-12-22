<template>
    <div>Upload</div>
    <div>
        <form @submit.prevent="upload">
            <label>Lớp: </label>
            <select @change="fetchFolderData" v-model="teachRoom">
                <option :value="null" disabled>-- Chọn lớp --</option>
                <option v-for="item in teachRoomList" :key="item.class_room_id" :value="item"> {{ item.class_room }} </option>
            </select> 
            <label>Thư mục: </label>
            <select v-model="folder">
                <option :value="null" disabled>-- Chọn môn --</option>
                <option v-for="lesson in lessonList" :key="lesson.lesson_id" :value="lesson">{{ lesson.lesson }}</option>
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
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const teachRoomList = ref(null)
const lessonList = ref([])
const yearStore = userYearStore()
const folder = ref(null)

onMounted(() => {
    fetchTeachClass()
})

const selectedFile = ref(null)
const uploadMSG = ref('')
const filename = ref('')
const gradeSearch = ref('')

const fetchTeachClass = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: gradeSearch.value,
        }
    })
    teachRoomList.value = res.data.data
}

const teachRoom = ref(null)
const fetchFolderData = async () => {
    const res = await axios.get('api/cloud/me/folders', {
        withCredentials: true,
        params: {
            grade: teachRoom.value.grade,
            year_id: yearStore.year.id,
            class_room_id: teachRoom.value.class_room_id
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
            lesson_id: folder.value.lesson_id,
            folder: folder.value.lesson,
            filename: filename.value,
            file_ext: file.name,
            filetype: file.type,
            filesize: file.size,
            year_id: yearStore.year.id
        }
        try {
            const res = await axios.post('api/cloud/files', payload, { 
                withCredentials: true,
            })
            const uploadURL = res.data.data
            
            await axios.put(uploadURL, file, {
                headers: {'Content-Type': file.type}
            })
            uploadMSG.value = res.data.msg
            
        } catch (e) {
            if (e.response && e.response.status == 400 || 404 || 422 || 500) {
                uploadMSG.value = e.response.data.msg
            } else {
                uploadMSG.value = 'Có rắc rối rồi đó!!'
            }
        }
    }
}

</script>