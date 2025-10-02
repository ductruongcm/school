<template>
    <div>Upload</div>
    <div>
        <form @submit.prevent="upload">
            <label>Lớp: </label>
            <select v-model="teachRoom">
                <option value="" disabled>-- Chọn lớp --</option>
                <option v-for="item in teachRoomList" :key="item" :value="item"> {{ item }} </option>
            </select> 
            <label>Thư mục: </label>
            <select v-model="folder">
                <option>-- Chọn môn --</option>
                <option> {{ lesson }}</option>
                <option v-if="teachRoom === classRoom">Chung</option>
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

const teachRoomList = ref([])
const teachRoom = ref('')
const year = inject('year')
const folder = ref('')
onMounted( () => {
    fetchTeachClass()
    fetchLesson()
    fetchClass()
})

const selectedFile = ref(null)
const uploadMSG = ref('')
const filename = ref('')

const fetchTeachClass = async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/academic/show_teach_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    teachRoomList.value = res.data.data
}

const lesson = ref('')
const fetchLesson = async () => {
    const res = await axios.get('api/teacher/show_lesson', {
        withCredentials: true
    })
    lesson.value = res.data.data
}

const classRoom = ref(null)
const fetchClass = async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/academic/show_class_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classRoom.value = res.data.data[0]
}

function handleFileChange(event) {
    selectedFile.value = event.target.files[0]
}

async function upload() {
    if (!selectedFile.value) {
        uploadMSG.value = 'Bạn chưa chọn file để upload!!'
        
    } else {
        const file = selectedFile.value
        
        const formData = new FormData()

        formData.append('file', file)
        formData.append('fileName', filename.value)
        formData.append('fileExtension', file.name)
        formData.append('fileSize', file.size)
        formData.append('fileType', file.type)
        formData.append('classRoom', teachRoom.value)
        formData.append('folder', folder.value)
        try {
            const res = await axios.post('api/cloud/upload', formData, { 
                withCredentials: true,
            })
            const uploadURL = res.data.url
            
            await axios.put(uploadURL, file, {
                headers: {'Content-Type': file.type}
            })

            uploadMSG.value = 'Uploaded thành công!!'
        } catch (e) {
            if (e.response && e.response.status == 400) {
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