<template>
    <div>Danh sách học sinh chờ xếp lớp</div>
    <div class="main">
        <form>
            <label>Khối lớp </label>
            <select v-model="selectedGrade" @change="fetchData">
                <option value="" disabled>--Chọn khối lớp--</option>
                <option value="">Toàn bộ</option>
                <option v-for="grade in gradeList" :key="grade.id" :value="grade.id">Khối lớp {{ grade.grade }}</option>
            </select>
            <label> Chọn lớp  </label>
            <select v-model="selectedClass">
                <option value="" selected disabled>-- Chọn lớp --</option>
                <option v-for="item in classList" :key="item.class_room_id" :value="item"> {{ item.class_room }}</option>
            </select>
            <button @click.prevent="setClass">Xác nhận</button>
            <button @click.prevent="cancelTick">Bỏ chọn</button>
        </form>
        <div>{{ resultMSG }}</div>
        <div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 2em;">STT</th>
                        <th style="width: 15em;">Họ và tên</th>
                        <th style="width: 10em;">Số điện thoại</th>
                        <th style="width: 15em;">Địa chỉ</th>
                        <th>Chọn xếp lớp</th>
                        <th style="width: 10em;"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in studentList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>
                            <span v-if="!item.editing">{{ item.name }}</span>
                            <input v-else v-model="item.name" @keyup.enter="saveEdit(item)" style="width: 10em;" type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.tel }}</span>
                            <input v-else v-model="item.tel" @keyup.enter="saveEdit(item)" style="width: 7em;"  type="text">
                        </td>
                        <td>
                            <span v-if="!item.editing">{{ item.add }}</span>
                            <input v-else v-model="item.add" @keyup.enter="saveEdit(item)" type="text">
                        </td>
                        <td>
                            <input type="checkbox"  v-model="selectedStudent" :value="item.student_id"/>
                        </td>
                        <td>
                            <button v-if="!item.editing" @click="editRow(item)">Sửa thông tin</button>
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
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
const resultMSG = ref('')
const yearStore = userYearStore()

onMounted(async () => {
    fetchGradeData()
})
const selectedStudent = ref([])
const setClass = async () => {
    const payload = {
        student_ids: selectedStudent.value, 
        class_room: selectedClass.value.class_room,
        year_id: yearStore.year.id
    }
    const res = await axios.put(`api/academic/class_rooms/${selectedClass.value.class_room_id}/students`, payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
    })
    resultMSG.value = res.data.msg
}

const cancelTick = () => {
    selectedStudent.value = []
}

const gradeSearch = ref('')
const gradeList = ref(null)
const selectedGrade = ref('')
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value
        }
    })
    gradeList.value = res.data.data
}

const fetchData = () => {
    fetchStudentData()
    fetchClassData()
}

const studentList = ref([])
const fetchStudentData = async () => {
    try {
        const res = await axios.get(`api/students`, {
            withCredentials: true,
            params: {
                grade_id: selectedGrade.value
            }
        })
        studentList.value = res.data.data
    } catch (e) {
        if (e.response && e.response.status === 400 || 404 || 422 || 500) {
            resultMSG.value = e.response.data.msg
        }   else {
            resultMSG.value = 'Có vấn đề gì rồi'
        }
    }
}

const selectedClass = ref('')
const classList = ref([])
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/class_rooms`, {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            class_room: "",
            grade_id: selectedGrade.value 
        }
    })
    classList.value = res.data.data
}

const editRow = (item) => {
    item.original = {...item}
    item.editing = true
}

const cancelEdit = (item) => {
    Object.assign(item, item.original)
    item.editing = false
}

const saveEdit = async (item) => {
    try {
        const payload = {
            id: item.id,
            name: item.name,
            tel: item.tel,
            add: item.add            
        }
        const res = await axios.put('/api/student/update_info', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMSG.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400) {
            resultMSG.value = e.response.data.msg
        } else {
            resultMSG.value = 'Có rắc rối rồi!!'
        }
    }
}


</script>
