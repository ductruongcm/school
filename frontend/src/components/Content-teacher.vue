<template>
    <div>Danh sách giáo viên</div>
    <div class="main">
        <div>
            <form>
                <label>Tìm theo môn học: </label>
                <select v-model="selectedLesson">
                    <option selected value="">-- Theo môn học --</option>
                    <option v-for="lesson in lessonList" :key="lesson">{{ lesson.lesson }}</option>
                </select>
                <label> Tìm theo lớp: </label>
                <select v-model="selectedClass">
                    <option selected value="">-- Theo lớp --</option>
                    <option v-for="classRoom in classRoomList" :key="classRoom">{{ classRoom.class_room }}</option>
                </select>
                <label> Tìm theo tên: </label>
                <input v-model="filterName" placeholder="Nhập tên giáo viên">
                <button type="button" @click="onReset">Nhập lại</button>
                
            </form>
        </div>
        <div> {{ teacherSearchMsg }}</div>
        <div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ và tên</th>
                        <th>Chuyên môn</th>
                        <th>Chủ nhiệm</th>
                        <th>Phụ trách</th>
                        <th>Số điện thoại</th>
                        <th>Địa chỉ</th>
                        <th>Email</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in teacherList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td style="width: 9em;">
                            <span v-if="!item.editing">{{ item.name }}</span>
                            <input v-else v-model="item.name" @keyup.enter="saveEdit(item)" type="text" style="width: 11em">
                        </td>
                        <td style="width: 7em;">
                            <span v-if="!item.editing">{{ item.lesson }}</span>
                            <input v-else v-model="item.lesson" @keyup.enter="saveEdit(item)" type="text" style="width: 5em">
                        </td>
                        <td style="width: 7em;">
                            <span v-if="!item.editing">{{ item.class_room }}</span>
                            <input v-else v-model="item.class_room" @keyup.enter="saveEdit(item)" type="text" style="width: 5em">
                        </td>
                        <td style="width: 7em;">
                            <span v-if="!item.editing">{{ item.teach_room }}</span>
                            <input v-else v-model="item.teach_room" @keyup.enter="saveEdit(item)" type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.tel }}</span>
                            <input v-else v-model="item.tel" @keyup.enter="saveEdit(item)" type="text" style="width: 7em">
                        </td>
                        <td style="width: 15em;">
                            <span v-if="!item.editing">{{ item.add }}</span>
                            <input v-else v-model="item.add" @keyup.enter="saveEdit(item)" type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.email }}</span>
                            <input v-else v-model="item.email" @keyup.enter="saveEdit(item)" type="email" style="width: 11em">
                        </td>
                        <td>
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
import { ref, onMounted, watch, inject } from 'vue';
import axios from 'axios';
import { message } from '../stores/usePopup';

const teacherList = ref([])
const teacherSearchMsg = ref('')
const lessonList = ref([])
const selectedLesson = ref('')
const selectedClass = ref('')
const classRoomList = ref('')
const year = inject('year')
const filterName = ref('')

onMounted(async () => {
    const res = await axios.get('api/teacher/show_lesson', { withCredentials: true})
    lessonList.value = res.data.data
})

onMounted(async () => {
    const payload = {year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, { 
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    classRoomList.value = res.data.data
})

async function fetchdata(lessonVal, classVal, nameVal) {
    try {
        const res = await axios.get('/api/teacher/show_teacher', {
        params: {lesson: lessonVal, class_room: classVal, name: nameVal}}, {
        withCredentials: true})
        teacherList.value = res.data.data.map(s => ({ ...s, editing: false}))
  
    } catch (e) {
        if (e.response && e.response.status === 400) {
            teacherSearchMsg.value = e.response.data.msg
        } else {
            teacherSearchMsg.value = 'Có vấn đề gì rồi!!'
        }
    }
}

onMounted(() => {
    fetchdata(selectedLesson.value, selectedClass.value, filterName.value)

    watch([selectedLesson, selectedClass, filterName], async([lessonVal, classVal, nameVal]) => {
        fetchdata(lessonVal, classVal, nameVal)
    })
})

function onReset() {
  selectedLesson.value = ""
  selectedClass.value = ""
  filterName.value = ""
  teacherSearchMsg.value = ""

  // gọi API lại để load bảng mặc định
  fetchTeachers("", "", "")
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
        const res = await axios.put('api/teacher/update_info', payload, { 
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}})
        item.editing = false
    } catch (e) {
        if (e.response && e.response.status === 400) {
            teacherSearchMsg.value = e.response.data.msg
        } else {
            teacherSearchMsg.value = 'Có vấn đề gì rồi!!'
        }

    }
}




</script>
