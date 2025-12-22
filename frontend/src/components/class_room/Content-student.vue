<template>
    <div style="display: flex; gap: 1em;">Danh sách học sinh Lớp
        <div>
            <select v-model="selectedClass">
                <option value="" disabled>--Chọn lớp--</option>
                <option v-for="class_room in classList" :key="class_room.class_room_id" :value="class_room.class_room_id">{{ class_room.class_room }}</option>
            </select>
        </div>
        <div v-if="role ==='admin' || role === 'Teacher' && isHomeroomTeacher && selectedClass === homeroomId">
            <button v-if="!editing" @click.prevent="updateInfo">Cập nhật thông tin</button>
            <button v-else @click.prevent="saveUpdate">Lưu</button>
            <button v-if="editing" @click.prevent="cancelUpdate">Hủy</button>
        </div>
    </div>
    <div>{{ resultMsg }}</div>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 2em;">STT</th>
                    <th style="width: 10em;">Họ và tên</th>
                    <th style="width: 5em;">Giới tính</th>
                    <th style="width: 7em;">Ngày sinh</th>
                    <th style="width: 7em;">Số điện thoại</th>
                    <th style="width: 14em;">Địa chỉ</th>
                    <th style="width: 16em;">Ghi chú</th>
                    <th style="width: 6em;">Chuyển lớp</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in studentList" :key="item.student_id" :value="item.student_id">
                    <td>
                        {{ index + 1 }}
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.name }}</span>
                        <input style="width: 12em;" v-else v-model="item.name" type="text">
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.gender }}</span>
                        <select v-else style="width: 5em;" v-model="item.gender">
                            <option value="" disabled>--Chọn--</option>
                            <option value="Nam">Nam</option>
                            <option value="Nữ">Nữ</option>
                        </select>
                    </td>
                    <td>
                        <span v-if="!editing">{{ dayjs(item.BOD).isValid() ? dayjs(item.BOD).format('DD/MM/YYYY') : 'Cập nhật sau' }}</span>
                        <input style="width:8em;" v-else v-model="item.BOD" type="date">
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.tel }}</span>
                        <input style="width: 8em;" v-else v-model="item.tel" type="text">
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.add }}</span>
                        <input style="width: 17em;" v-else v-model="item.add" type="text">
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.note }}</span>
                        <input style="width: 19em;" v-else v-model="item.note" type="text">
                    </td>
                    <td>
                        <select v-model="item.class_room_id" v-if="editing">
                            <option disabled>-Chọn lớp-</option>
                            <option v-for="classChange in classChangeList" :key="classChange.class_room_id" :value="classChange.class_room_id">{{ classChange.class_room }}</option>
                        </select>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>    
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import { userYearStore } from '../../stores/yearStore';
import { useUserStore } from '../../stores/user';
import axios from 'axios';
import dayjs from 'dayjs';

const yearStore = userYearStore()
const userStore = useUserStore()
const isHomeroomTeacher = userStore.userInfo.is_homeroom_teacher
const homeroomId = userStore.userInfo.homeroom_id
const role = userStore.userInfo.role

onMounted( async () => {
    await fetchClassData()
})

const classList = ref([])
const gradeSearch = ref('')
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true, 
        params: {
            grade: gradeSearch.value
        }
    })
    classList.value = res.data.data
    selectedClass.value = homeroomId || classList.value[0].class_room_id
}

const selectedClass = ref('')
const studentList = ref([])
const fetchStudentData = async () => {
    if (!selectedClass.value) return
    const res = await axios.get(`api/students`, {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            grade: gradeSearch.value,
            class_room_id: selectedClass.value
        }
    })
    studentList.value = res.data.data
    studentList.value = studentList.value.map(s => ({
        ...s, BOD: dayjs(s.BOD).format("YYYY-MM-DD")
    }))
    selectedGrade.value = studentList.value[0].grade
}

watch(selectedClass, (newVal) => {
    if (newVal) {
        fetchStudentData()
    }
})

const editing = ref(false)
const original = ref([])
const updateInfo = () => {
    editing.value = true
    original.value = JSON.parse(JSON.stringify(studentList.value))
    fetchClassChange()
}
const selectedGrade = ref('')
const classChangeList = ref([])
const fetchClassChange = async () => {
    const res = await axios.get(`/api/academic/years/${yearStore.year.id}/class-rooms/assignable`, {
        withCredentials: true,
        params: {
            status: '',
            grade: selectedGrade.value
        }
    })
    classChangeList.value = res.data.data.filter(item => item.class_room_id !== selectedClass.value)
}

const cancelUpdate = () => {
    studentList.value = original.value
    editing.value = false
}

const resultMsg = ref('')
const saveUpdate = async () => {
    const changedRows = studentList.value.map(item => {
        const origin = original.value.find(o => o.student_id === item.student_id)
        if (!origin) return null

        const changedEntries = Object.entries(item).filter(([k, v]) => v !== origin[k]);
        if (changedEntries.length === 0) return null;

        const changedObject = {
            ...Object.fromEntries(changedEntries),
            student_id: item.student_id,
            year_id: yearStore.year.id
        }
        return changedObject
    })
    .filter(Boolean)

    try {
        const res = await axios.put(`api/students`, changedRows, {
            withCredentials: true
        })
        resultMsg.value = res.data.msg
        editing.value = false
        fetchStudentData()
    } catch (e) {
        if (e.response && [400, 404, 409, 422, 500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}


</script>