<template>
    <div>Download</div>
    <div>
        <div>
            <form  @change="selectedFolder">
                <label>Lớp: </label>
                <select v-model="classFolder">
                    <option value="" disabled>-- Chọn lớp --</option>
                    <option v-for="classRoom in classList" :key="classRoom" :value="classRoom">{{ classRoom }}</option>
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
                <tr v-for="(item,index) in data" :key="item">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.file_name }}</td>
                    <td>{{ item.file_type }}</td>
                    <td>{{ (item.file_size/1024/1024).toFixed(2) }} MB</td>
                    <td>{{ dayjs(item.upload_at).format('MM/DD/YYYY HH:MM:ss') }}</td>
                    <td>{{ item.upload_by }}</td>
                    <td>{{ item.status }}</td>
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
const year = inject('year')
onMounted(async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
})

const classFolder = ref('')
const data = ref('')
async function selectedFolder() {
    const res = await axios.get(`api/cloud/show_folder?class_room=${classFolder.value}`, { withCredentials: true})
    data.value = res.data.data
}

watch(classList, (newList) => {
    if(newList.length === 1) {
        classFolder.value = newList[0]
        selectedFolder()
    }
})

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