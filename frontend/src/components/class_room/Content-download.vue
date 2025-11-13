<template>
    <div>Download</div>

    <div>
        <div>
            <form>
                <label>Lớp: </label>
                <select v-model="classFolder" @change="fetchFolder">
                    <option :value="null" disabled>-- Chọn lớp --</option>
                    <option v-for="item in classList" :key="item.class_room_id" :value="item">{{item.class_room }}</option>
                </select>
                <label> Thư mục: </label>
                <select v-model="fileFolder">
                    <option :value="null" disabled>-- Chọn môn --</option>
                    <option v-for="item in folder" :key="item" :value="item"> {{ item.lesson }}</option>
                </select>
                <label>{{ downloadMsg }}</label>
            </form>
        </div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 15em;">File name</th>
                    <th style="width: 7em;">File type</th>
                    <th style="width: 4em;">File size</th>
                    <th style="width: 10em;">Upload lúc</th>
                    <th style="width: 8em;">Người upload</th>
                    <th style="width: 7em;">Trạng thái</th>
                    <th style="width: 14em;"></th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in fileList" :key="item.id" :value="item.id">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.file_name }}</td>
                    <td>{{ item.file_type }}</td>
                    <td>{{ (item.file_size/1024/1024).toFixed(2) }} MB</td>
                    <td>{{ dayjs(item.upload_at).format('MM/DD/YYYY HH:mm:ss') }}</td>
                    <td>{{ item.upload_by }}</td>
                    <td>{{ item.status ? 'Hiện' : 'Ẩn'}}</td>
                    <td>
                        <button @click="download(item)">Download</button>
                        <button @click="hideFile(item)">Ẩn/Hiện</button>
                        <button @click="del(item)">Xóa</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import axios from 'axios';
import dayjs from 'dayjs'
import { ref, onMounted, watch } from 'vue';
import { userYearStore } from '../../stores/yearStore';

const classList = ref([])
const classFolder = ref(null)
const folder = ref([])
const fileFolder = ref(null)
const yearStore = userYearStore()
const downloadMsg = ref(null)

onMounted( () => {
    fetchTeachRoom()
})

const classSearch = ref('')
const gradeSearch = ref('')
const fetchTeachRoom = async () => {
    const res = await axios.get('api/academic/me/class-rooms', {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'},
        params: {
            year_id: yearStore.year.id,
            class_room: classSearch.value,
            grade_id: gradeSearch.value
        }
    })
    classList.value = res.data.data
}

const fetchFolder = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        params: {
            grade_id: gradeSearch.value,
            year_id: yearStore.year.id,
            is_visible: false,
            is_folder: true,
            is_schedule: false
        },
        withCredentials: true
    })
    folder.value = res.data.data
}

const fileList = ref(null)
const fetchFile = async () => {
    try{
        const res = await axios.get('api/cloud/files', {
            withCredentials: true,
            params: {
                class_room_id: classFolder.value.class_room_id,
                lesson_id: fileFolder.value.lesson_id,
                year_id: yearStore.year.id
            }   
        })
        fileList.value = res.data.data

    } catch (e) {
        if (e.response && e.response.status === 400 || 404 || 422 || 500) {
            downloadMsg.value = e.response.data.msg
        }
    }
}

watch([fileFolder, classFolder], async([newLessonId, newClassId]) => {
    if (newLessonId && newClassId) {
        await fetchFile()
    }
})

async function hideFile(item) {
    const res = await axios.put(`/api/cloud/files/${item.id}/hide`, { 
        withCredentials: true, 
    })
    downloadMsg.value = res.data.msg
    fetchFile()
}

async function download(item) {
    const res = await axios.get(`api/cloud/files/${item.id}`, {
        withCredentials: true,
    })
    window.open(res.data.data) 
}

async function del(item) {
    const res = await axios.delete(`api/cloud/files/${item.id}`, {
        withCredentials: true,
    })
    fetchFile()
    downloadMsg.value = res.data.msg
}

</script>