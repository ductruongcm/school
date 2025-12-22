<template>
    <div>Quản lý giáo viên</div>
    <div> Thêm giáo viên </div>
    <form @submit.prevent="addTeacher">
        <label >Họ và tên: </label> 
        <input type="text" v-model="name" required> 
        <label> Số điện thoại: </label> 
        <input type="text" v-model="tel" required style="width: 8em;"> 
        <label> Địa chỉ: </label>
        <input style="width: 20em;" type="text" v-model="add" required> <br>
        <label> Username: </label> 
        <input type="text" v-model="username" required> 
        <label> Email: </label> 
        <input type="text" v-model="email" required style="width: 15em;"> <br>
        <label>Chủ nhiệm lớp: </label> 
        <select v-model="selectedClassRoom">
            <option value="null" selected disabled>--Chọn lớp học--</option>
            <option value="null"> Bỏ chọn </option>
            <option v-for="classRoom in classList" :key="classRoom.class_room_id" :value="classRoom">Lớp {{ classRoom.class_room }}</option>
        </select> 
         <label> Chuyên môn: </label> 
        <select v-model="selectedLesson">
            <option value="null" selected disabled>--Chọn môn học--</option>
            <option v-for="lesson in lessonList" :key="lesson.lesson_id" :value="lesson">{{ lesson.lesson }}</option>
        </select> <br>
        <label>Phụ trách lớp</label> <br>
        <div style="display: flex; gap: 20px">
            <!-- Bảng trái -->
            <div>
                <div>Chọn lớp học</div>
                <ul>
                    <li v-for="teachRoom in teachClassList" :key="teachRoom.id" :value="teachRoom.id">
                        <input type="checkbox" :value="teachRoom" v-model="selectedLeft" />Lớp {{ teachRoom.class_room }}
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
                    <li v-for="item in rightList" :key="item.id">
                        <input type="checkbox" :value="item" v-model="selectedRight" /> {{ item.class_room }}
                    </li>
                </ul>
            </div>
        </div> 
        <button>Đăng ký</button>
    </form>

    <div>{{ teacherMsg }}</div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';

const name = ref('')
const lessonList = ref([])
const selectedLesson = ref(null)

const selectedClassRoom = ref(null)
const tel = ref('')
const add = ref('')
const username = ref('')
const email = ref('')
const teacherMsg = ref('')
const teachClassList = ref([])
const yearStore = userYearStore()

onMounted( () => {
    fetchClassData()
    fetchLessonData()
})

const selectedGrade = ref('')
const fetchLessonData = async () => {
    const res = await axios.get('api/academic/me/lessons', {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
            is_schedule: false,
            is_visible: true,
            is_folder: false
        }
    })
    lessonList.value = res.data.data
}

const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: selectedGrade.value
        }
    })
    classList.value = res.data.data
    teachClassList.value = JSON.parse(JSON.stringify(classList.value))
}

const classList = ref([])
const selectedLeft = ref([])
const selectedRight = ref([])
const rightList = ref([])
const newIds = ref([])
const addToRight = () => {
  rightList.value.push(...selectedLeft.value)
  newIds.value.push(...selectedLeft.value.map(i => i.class_room_id))
  teachClassList.value = teachClassList.value.filter(item => !selectedLeft.value.includes(item))
  selectedLeft.value = []
}

const removeFromRight = () => {
  teachClassList.value.push(...selectedRight.value)
  const idsToRemove = selectedRight.value.map(i => i.class_room_id)
  newIds.value = newIds.value.filter(id => !idsToRemove.includes(id))
  rightList.value = rightList.value.filter(item => !selectedRight.value.includes(item))
  selectedRight.value = []
}

const addTeacher = async () => {
    const payload = {
        name: name.value,
        lesson_id: selectedLesson.value?.lesson_id || null,
        lesson: selectedLesson.value?.lesson || null,
        class_room_id: selectedClassRoom.value?.class_room_id || null,
        class_room: selectedClassRoom.value?.class_room || null,
        teaching_class_ids: newIds.value,
        tel: tel.value,
        add: add.value,
        email: email.value,
        username: username.value,
        year_id: yearStore.year.id
    }

    try {
        const res = await axios.post('api/teachers', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        teacherMsg.value = res.data.msg

    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            teacherMsg.value = e.response.data.msg
        } else {
        teacherMsg.value = 'Có vấn đề gì rồi!!!'
        }
    }
}


</script>