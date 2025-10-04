<template>
    <div>Download</div>
    <div>
        <div>
            <form>
                <label>Lớp: </label>
                <select v-model="classFolder" @change="fetchFolder">
                    <option value="" disabled>-- Chọn lớp --</option>
                    <option v-for="classRoom in classList" :key="classRoom.class_room_id" :value="classRoom.class_room_id">{{ classRoom.class_room }}</option>
                </select>
                <label>Thư mục: </label>
                <select v-model="fileFolder" @change="showFile">
                    <option value="" disabled>-- Chọn môn --</option>
                    <option v-for="item in folder" :key="item" :value="item"> {{ item }}</option>
                </select>
            </form>
        </div>
        <table>
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 15em;">File name</th>
                    <th style="width: 7em;">File type</th>
                    <th style="width: 4em;">File size</th>
                    <th style="width: 15em;">Upload lúc</th>
                    <th style="width: 8em;">Người upload</th>
                    <th style="width: 8em;">Trạng thái</th>
                    <th style="width: 12em;"></th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in file" :key="item.upload_at" >
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.file_name }}</td>
                    <td>{{ item.file_type }}</td>
                    <td>{{ (item.file_size/1024/1024).toFixed(2) }} MB</td>
                    <td>{{ dayjs(item.upload_at).format('MM/DD/YYYY HH:mm:ss') }}</td>
                    <td>{{ item.upload_by }}</td>
                    <td>{{ item.status ? 'Hiện' : 'Ẩn'}}</td>
                    <td>
                        <button @click="download(item)">Download</button>
                        <button v-if="!item.status" @click="unhideFile(item)">Hiện</button>
                        <button v-else @click="hideFile(item)">Ẩn</button>
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
import { ref, onMounted, inject, watch } from 'vue';

const classList = ref([])
const classFolder = ref('')
const folder = ref([])
const fileFolder = ref('')
const file = ref([])
const year = inject('year')

onMounted( () => {
    fetchTeachRoom()
})

const fetchTeachRoom = async () => {
    const res = await axios.get('api/academic/teach_rooms', {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'},
        params: {year: year.value}
    })
    classList.value = res.data.data
}

const fetchFolder = async () => {
    const res = await axios.get('api/cloud/folders', {
        params: {class_room_id: classFolder.value},
        withCredentials: true
    })
    folder.value = res.data.data
}

watch([classFolder, fileFolder], async ([newClass, newFolder]) => {
    if (newClass && newFolder) {
        await showFile()
    }
})

const showFile = async () => {
    const res = await axios.get('api/cloud/files', {
        withCredentials: true,
        params: { 
            class_room_id: classFolder.value,
            folder: fileFolder.value
        }
    })
    file.value = res.data.data
}

async function hideFile(item) {
    await axios.put(`/api/cloud/files/${item.id}/hide`, { 
        withCredentials: true, 
    })
    console.log(res.data.msg)
}

async function unhideFile(item) {
    const payload = {file_name: item.file_name}
    await axios.put(`/api/cloud/files/${item.id}/unhide`, {
        withCredentials: true,
    })
    console.log(res.data.msg)
}

async function download(item) {
    const res = await axios.get(`api/cloud/files/${item.id}/download`, {
        withCredentials: true,
    })
    window.open(res.data) 
}

async function del(item) {
    const res = await axios.delete(`api/cloud/files/${item.id}`, {
        withCredentials: true,
    })
    console.log(res.data.msg)
}

</script>