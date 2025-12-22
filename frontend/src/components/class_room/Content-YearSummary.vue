<template>
    <div>
        <div>Tổng kết Năm học</div>
        <div style="display: flex; gap: 1em">
            <div>
                <label>
                    Lớp học:
                    <select v-model="selectedClass" @change="fetchStudentData">
                        <option value="">--Chọn lớp--</option>
                        <option v-for="cl in classList" :key="cl.class_room_id" :value="cl.class_room_id">{{ cl.class_room }}</option>
                    </select>
                </label>
            </div>
            <div v-if="role === 'admin' || role === 'Teacher' && isHomeroomTeacher && homeRoomId === selectedClass">
                <button v-if="!editing" @click.prevent="edit">Tổng kết</button>
                <button v-else @click.prevent="confirmEdit">Xác nhận</button>
                <button v-if="editing" @click.prevent = cancelEdit>Hủy</button>
            </div>
        </div>
        <div>{{ resultMsg }}</div>
        <div>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th style="width: 3em;">STT</th>
                        <th style="width: 10em;">Tên</th>
                        <template v-for="subjectScore in Object.values(studentList[0]?.lessons || {})" :key="subjectScore">  
                            <th style="width: 4.5em;" v-for="subject in Object.keys(subjectScore)">{{ subject }}</th>
                        </template>
                        <th style="width: 6em;">Tổng kết</th>
                        <th style="width: 4.5em;">Xếp loại</th>
                        <th style="width: 6em;">Hạnh kiểm</th>
                        <th style="width: 6em;">Chuyên cần</th>
                        <th style="width: 10em;">Ghi chú</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="studentList.length > 1" v-for="(student, ind) in studentList" :key="ind">
                        <td>{{ ind + 1 }}</td>
                        <td>{{ student.name }}</td>
                      
                        <template v-for="subjectScore in Object.values(student.lessons || {})" :key="subjectScore">  
                            <td style="width: 4.5em;" v-for="score in Object.values(subjectScore)">{{ score }}</td>
                        </template>
                        <td>{{ student.score }}</td>
                        <td>{{ student.status }}</td>
                        <td>
                            <span v-if="!editing">{{ student.conduct ? 'Đạt' : '-' }}</span>
                            <select v-else v-model="student.conduct">
                                <option disabled :value="null">Đánh giá</option>
                                <option :value="true">Đạt</option>
                                <option :value="false">Không đạt</option>
                            </select>
                        </td>
                        <td>
                            <span>{{ student.absent_day ? student.absent_day : '-' }}</span>
                        </td>
                        <td>
                            <span v-if="!editing">{{ student.note }}</span>
                            <input v-else type="text" v-model="student.note">
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useUserStore } from '../../stores/user';

const userStore = useUserStore()
const isHomeroomTeacher = userStore.userInfo.is_homeroom_teacher
const homeRoomId = userStore.userInfo.homeroom_id
const role = userStore.userInfo.role

onMounted(async () => {
        await fetchClassData()
        await fetchStudentData()
})

const yearStore = userYearStore()
const classList = ref('')
const gradeSearch = ref('')
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: gradeSearch.value,
        }
    })
    classList.value = res.data.data
    selectedClass.value = homeRoomId || classList.value?.[0].class_room_id
}

const selectedClass = ref('')
const studentList = ref([])
const fetchStudentData = async () => {
    studentList.value = []

    const selected = classList.value.find(c => c.class_room_id === selectedClass.value)

    const res = await axios.get(`api/years/${yearStore.year.id}/students/summary`, {
        withCredentials: true,
        params: {
            class_room_id: selected.class_room_id
        }
    })
    
    studentList.value = res.data.data

}

const resultMsg = ref('')

const editing = ref(false)
const original = ref('')
const edit = () => {
    if (selectedClass.value === '') {
        alert('Bạn chưa chọn lớp học')
        return
    }
    
    editing.value = true
    original.value = JSON.parse(JSON.stringify(studentList.value))
}

const cancelEdit = () => {
    editing.value = false
    studentList.value = JSON.parse(JSON.stringify(original.value))
}

const confirmEdit = async () => {
    if (selectedClass.value === '') {
        alert('Bạn chưa chọn lớp học')
        return
    }

    studentList.value.forEach(item => 
        delete item.scores
    )
    
    const payload = {
        students : studentList.value,
        class_room_id: selectedClass.value
    }

    try {
        const res = await axios.put(`api/academic/entity/years/${yearStore.year.id}/summary`, payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
            resultMsg.value = res.data.msg
            fetchStudentData()
            editing.value = false

    } catch (e) {

        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg

        }
    }
}
</script>