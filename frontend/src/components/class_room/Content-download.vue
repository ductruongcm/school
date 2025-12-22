<template>
    <div>Download</div>

    <div>
        <div>
            <form>
                <label>Lớp: </label>
                <select v-model="classFolder" @change="fetchFolder">
                    <option :value="null" disabled>-- Chọn lớp --</option>
                    <option v-for="item in classList" :key="item.class_room_id" :value="item">{{ item.class_room }}</option>
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
                    <th style="width: 20em;">File name</th>
                    <th style="width: 7em;">File type</th>
                    <th style="width: 6em;">File size</th>
                    <th style="width: 11em;">Upload lúc</th>
                    <th style="width: 9em;">Người upload</th>
                    <th style="width: 7em;">Trạng thái</th>
                    <th style="width: 7em;">Thao tác</th>
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
                        <button v-if="userStore.userInfo.role === 'admmin' || userStore.userInfo.role === 'Teacher'" @click="hideFile(item)">Ẩn/Hiện</button>
                        <button v-if="userStore.userInfo.role === 'admmin' || userStore.userInfo.role === 'Teacher'" @click="del(item)">Xóa</button>
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
import { useSemesterStore } from '../../stores/semesterStore';
import { useUserStore } from '../../stores/user';

const classList = ref([])
const classFolder = ref(null)
const folder = ref([])
const fileFolder = ref(null)
const yearStore = userYearStore()
const downloadMsg = ref(null)
const semesterStore = useSemesterStore()
const userStore = useUserStore()

onMounted( async () => {
    Promise.all[
        fetchTeachRoom()
    ]
})

const gradeSearch = ref('')
const fetchTeachRoom = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            semester_id: semesterStore.semester.semester_id,
            grade: gradeSearch.value
        }
    })
    classList.value = res.data.data

    if (classList.value.length === 1) {
        classFolder.value = classList.value[0]
        fetchFolder()
    }
}

const fetchFolder = async () => {
    const res = await axios.get('api/cloud/me/folders', {
        params: {
            grade: classFolder.value.grade,
            year_id: yearStore.year.id,
            class_room_id: classFolder.value.class_room_id
        },
        withCredentials: true
    })
    folder.value = res.data.data
}

watch([fileFolder, classFolder], async([newLessonId, newClassId]) => {
    if (newLessonId && newClassId) {
        await fetchFile()
    }
})

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
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            downloadMsg.value = e.response.data.msg
        }
    }
}

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