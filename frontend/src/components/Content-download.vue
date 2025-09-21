<template>
    <div>Download</div>
    <div>
        <div>
            <form>
                <label>Lớp: </label>
                <select v-model="classFolder" @change="showFolder()">
                    <option value="" disabled>-- Chọn lớp --</option>
                    <option v-for="classRoom in classList" :key="classRoom">{{ classRoom }}</option>
                </select>
                <label>Thư mục: </label>
                <select v-model="fileFolder" @change="showFile">
                    <option value="" disabled>-- Chọn môn --</option>
                    <option v-for="item in folder" :key="item"> {{ item }}</option>
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
    showTeachRoom()
})

const showTeachRoom = async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_teach_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
}

const showFolder = async () => {
    const res = await axios.get('api/cloud/show_folder', {
        params: {class_room: classFolder.value},
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
    const res = await axios.get('api/cloud/show_file', {
        withCredentials: true,
        params: { 
            class_room: classFolder.value,
            folder: fileFolder.value
        }
    })
    file.value = res.data.data
}

async function hideFile(item) {
    const payload = {file_name: item.file_name}
    await axios.put(`/api/cloud/hide_file?class_room=${classFolder.value}`, payload, { 
        withCredentials: true, 
        headers: {'Content-Type': 'application/json'}
    })
}

async function unhideFile(item) {
    const payload = {file_name: item.file_name}
    await axios.put(`/api/cloud/unhide_file?class_room=${classFolder.value}`, payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
}

async function download(item) {
    const payload = {
        class_room: classFolder.value,
        file_name: item.file_name
    }
    const res = await axios.put('api/cloud/download', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    window.open(res.data.url) 
}

async function del(item) {
    const res = await axios.delete(`api/cloud/delete?class_room=${classFolder.value}&file_name=${item.file_name}`, {
        withCredentials: true,
    })
    await axios.delete(res.data.url)
}

</script>