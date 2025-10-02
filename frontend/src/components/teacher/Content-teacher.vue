<template>
    <div>Danh sách giáo viên</div>
    <div class="main">
        <div>
            <form @submit.prevent="fetchdata">
                <label>Tìm theo môn học: </label>
                <input type="text" v-model="selectedLesson">
                <label> Tìm theo lớp: </label>
                <input type="text" v-model="selectedClass">
                <label> Tìm theo tên: </label>
                <input v-model="filterName" placeholder="Nhập tên giáo viên">
                <button>Tìm kiếm</button>
                <button type="button" @click="onReset">Nhập lại</button>
            </form>
        </div>
        <div> {{ teacherSearchMsg }}</div>
        <div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th style="width: 12em;">Họ và tên</th>
                        <th style="width: 7em;">Chuyên môn</th>
                        <th style="width: 7em;">Chủ nhiệm</th>
                        <th style="width: 12em;">Phụ trách</th>
                        <th style="width: 7em;">Số điện thoại</th>
                        <th style="width: 15em;">Địa chỉ</th>
                        <th style="width: 10em;">Email</th>
                        <th style="width: 10em;"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in teacherList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>
                            <span v-if="!item.editing">{{ item.name }}</span>
                            <input v-else v-model="item.name" @keyup.enter="saveEdit(item)" type="text" style="width: 11em">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.lesson }}</span>
                            <input v-else v-model="item.lesson" @keyup.enter="saveEdit(item)" type="text" style="width: 5em">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.class_room }}</span>
                            <input v-else v-model="item.class_room" @keyup.enter="saveEdit(item)" type="text" style="width: 5em">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.teach_room }}</span>
                            <input v-else v-model="item.teach_room" @keyup.enter="saveEdit(item)" type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.tel }}</span>
                            <input v-else v-model="item.tel" @keyup.enter="saveEdit(item)" type="text" style="width: 7em">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.add }}</span>
                            <input v-else v-model="item.add" @keyup.enter="saveEdit(item)" type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.email }}</span>
                            <input v-else v-model="item.email" @keyup.enter="saveEdit(item)" type="email" style="width: 11em">
                        </td>
                        <td v-if="userStore.userInfo.role === 'admin'">
                            <button v-if="!item.editing" @click="editRow(item)">Chỉnh sửa</button>
                            <button v-else @click="saveEdit(item)">Lưu</button>
                            <button v-if="item.editing" @click="cancelEdit(item)">Hủy</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, inject } from 'vue';
import axios from 'axios';
import useUserStore from '../../stores/user';
import { message } from '../../stores/usePopup';

const teacherList = ref([])
const teacherSearchMsg = ref('')
const lessonList = ref([])
const selectedLesson = ref('')
const selectedClass = ref('')
const classRoomList = ref('')
const year = inject('year')
const filterName = ref('')
const userStore = useUserStore()

onMounted( () => {
    fetchdata()
})

async function fetchdata() {
    try {
        const res = await axios.get('/api/teacher/show_teacher', {
        params: {
            lesson: selectedLesson.value, 
            class_room: selectedClass.value, 
            name: filterName.value}}, {
        withCredentials: true
    })
        console.log(res.data)
        teacherList.value = res.data
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            teacherSearchMsg.value = e.response.data.msg
        } else {
            teacherSearchMsg.value = 'Có vấn đề gì rồi!!'
        }
    }
}

function onReset() {
  selectedLesson.value = ""
  selectedClass.value = ""
  filterName.value = ""
  teacherSearchMsg.value = "" 
  fetchdata()
}

function editRow(item) {
    item.original = {...item}
    item.editing = true
}

function cancelEdit(item) {
    Object.assign(item, item.original) //Revert lại
    item.editing = false
}

async function saveEdit(item) {
    try {
        const payload = {
            id: item.id,
            name: item.name,
            lesson: item.lesson,
            class_room: item.class_room,
            teach_room: item.teach_room,
            tel: item.tel,
            add: item.add,
            email: item.email,
            year: year.value
        }
        await axios.put('api/teacher/update_info', payload, { 
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}})
        item.editing = false
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            teacherSearchMsg.value = e.response.data.msg
        } else {
            teacherSearchMsg.value = 'Có vấn đề gì rồi!!'
        }

    }
}




</script>
