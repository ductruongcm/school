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
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import useUserStore from '../../stores/user';
import { userYearStore } from '../../stores/yearStore';

const teachRoomList = ref(null)
const lessonList = ref([])
const class_roomSearch = ref('')
const yearStore = userYearStore()
const folder = ref(null)
const userStore = useUserStore()

onMounted(() => {
    fetchTeachClass()
})

const selectedFile = ref(null)
const uploadMSG = ref('')
const filename = ref('')
const gradeSearch = ref('')

const fetchTeachClass = async () => {
    const res = await axios.get('api/academic/me/class-rooms', {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'},
        params: {
            year_id: yearStore.year.id,
            class_room: class_roomSearch.value,
            grade_id: gradeSearch.value,
        }
    })
    teachRoomList.value = res.data.data
}

const lessonSearch = ref('')
const teachRoom = ref(null)
const selectedGrade = ref('')
const fetchFolderData = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        withCredentials: true,
        params: {
            grade_id: selectedGrade.value,
            year_id: yearStore.year.id,
            is_visible: false,
            is_folder: true,
            is_schedule: false
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