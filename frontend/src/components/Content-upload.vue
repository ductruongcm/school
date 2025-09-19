<template>
    <div>Upload</div>
    <div>
        <form @submit.prevent="upload">
            <label>Lớp: </label>
            <select v-model="classRoom">
                <option value="" disabled>-- Chọn lớp --</option>
                <option v-for="item in classList" :key="item" :value="item"> {{ item }} </option>
            </select> <br>
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

const classList = ref([])
const classRoom = ref('')
const year = inject('year')

onMounted(async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, { 
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
})

const selectedFile = ref(null)
const uploadMSG = ref('')
const filename = ref('')

function handleFileChange(event) {
    selectedFile.value = event.target.files[0]
}

async function upload() {
    if (!selectedFile.value) {
        uploadMSG.value = 'Bạn chưa chọn file để upload!!'
        
    } else {
        const file = selectedFile.value
        console.log(file)
        const formData = new FormData()

        formData.append('file', file)
        formData.append('fileName', filename.value)
        formData.append('fileExtension', file.name)
        formData.append('fileSize', file.size)
        formData.append('fileType', file.type)
        formData.append('classRoom', classRoom.value)
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

watch(classList, (newList) => {
    if (newList.length === 1) {
        classRoom.value = newList[0]
    }
})
</script>