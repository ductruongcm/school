<template>
    <div>Quản lý giáo viên</div>
    <div> Thêm giáo viên </div>
    <form @submit.prevent="addTeacher">
        <label>Họ và tên</label> <br>
        <input type="text" v-model="name" required> <br>
        <label>Chuyên môn</label> <br>
        <select v-model="selectedLesson">
            <option value="" selected disabled>--Chọn môn học--</option>
            <option v-for="lesson in lessonList" :key="lesson">{{ lesson }}</option>
        </select> <br>
        <label>Chủ nhiệm lớp</label> <br>
        <select v-model="selectedClassRoom">
            <option value="" selected disabled>--Chọn lớp học--</option>
            <option v-for="classRoom in classList" :key="classRoom.class_room_id" :value="classRoom.class_room_id">{{ classRoom.class_room }}</option>
        </select> <br>
        <label>Phụ trách lớp</label> <br>
        <div style="display: flex; gap: 20px">
            <!-- Bảng trái -->
            <div>
                <div>Chọn lớp học</div>
                <ul>
                    <li v-for="teachRoom in teachClassList" :key="teachRoom.class_room_id" :value="teachRoom.class_room_id">
                        <input type="checkbox" :value="teachRoom" v-model="selectedLeft" /> {{ teachRoom.class_room }}
                    </li>
                </ul>
            </div>

            <!-- Nút chuyển -->
            <div style="display: flex; flex-direction: column; justify-content: center; gap: 10px">
                <button @click.prevent="addToRight">→</button>
                <button @click.prevent="removeFromRight">←</button>
            </div>

            <!-- Bảng phải -->
            <div>
                <div>Lớp đã chọn</div>
                <ul>
                    <li v-for="item in rightList" :key="item">
                        <input type="checkbox" :value="item" v-model="selectedRight" /> {{ item }}
                    </li>
                </ul>
            </div>
        </div> <br>
        <label>Số điện thoại</label> <br>
        <input type="text" v-model="tel" required> <br>
        <label>Địa chỉ</label> <br>
        <input type="text" v-model="add" required> <br>
        <label>Username</label> <br>
        <input type="text" v-model="username" required> <br>
        <label>Email</label> <br>
        <input type="text" v-model="email" required> <br>
        <label>Role</label> <br>
        <input type="text" v-model="role" placeholder="teacher" default="teacher"> <br>
        <button>Đăng ký</button>
    </form>
    <div>{{ teacherMsg }}</div>
</template>
<script setup>
import { ref, inject, onMounted } from 'vue';
import axios from 'axios';

const name = ref('')
const lessonList = ref([])
const selectedLesson = ref('')

const selectedClassRoom = ref('')
const tel = ref('')
const add = ref('')
const username = ref('')
const email = ref('')
const role = ref('')
const teacherMsg = ref('')
const year = inject('year')
const teachClassList = ref([])


onMounted( () => {
    fetchLesson()
    fetchClass()
})

const fetchLesson = async () => {
    const res = await axios.get('api/academic/lessons', {
        withCredentials: true,
        params: {lesson: ''}
    })
    lessonList.value = res.data.data
}

const fetchClass = async () => {
    const res = await axios.get('api/academic/class_rooms', {
        withCredentials: true,
        params: {year: year.value}
    })
    classList.value = res.data.data
    teachClassList.value = res.data.data
}

const classList = ref([])
const selectedLeft = ref([])
const selectedRight = ref([])
const rightList = ref([])

const addToRight = () => {
  rightList.value.push(...selectedLeft.value)
  selectedRight.value.push(...selectedLeft.value)
  teachClassList.value = teachClassList.value.filter(item => !selectedLeft.value.includes(item))
  selectedLeft.value = []
}

const removeFromRight = () => {
  teachClassList.value.push(...selectedRight.value)
  rightList.value = rightList.value.filter(item => !selectedRight.value.includes(item))
  selectedRight.value = []
}


const addTeacher = async () => {
    const payload = {
        name: name.value,
        lesson: selectedLesson.value,
        class_room: selectedClassRoom.value,
        teach_room: selectedRight.value,
        tel: tel.value,
        add: add.value,
        email: email.value,
        username: username.value,
        role: role.value,
        year: year.value
    }
    try {
        const res = await axios.post('api/teacher/teachers', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        teacherMsg.value = 'Thêm giáo viên thành công!'
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            teacherMsg.value = e.response.data.msg
        } else {
        teacherMsg.value = 'Có vấn đề gì rồi!!!'
        }
    }
}


</script>