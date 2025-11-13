<template>
    <div>Danh sách học sinh chờ xét duyệt</div>
    <div class="main">
        <div style="display: flex; gap: 1rem; align-items: center;">
            <div >
                <label>
                    <input type="radio" name="action" @change="forApproval">
                    Danh sách chờ xét duyệt 
                </label>

                <label> 
                    <input type="radio" name="action" @change="forAssigment" v-model="selectedReviewStatus" :value=true>
                    Danh sách chờ xếp lớp 
                </label>
                <label>
                    Khối lớp
                    <select v-model="selectedGrade">
                    <option value="" disabled>--Chọn khối lớp--</option>
                    <option v-for="grade in gradeList" :key="grade.id" :value="grade.grade">Khối lớp {{ grade.grade }}</option>
                    </select>
                </label>
            </div>
            <div v-if="!edit && selectedReviewStatus" >
                <label>
                    Kết quả
                    <select v-model="selectedStatus">
                    <option value="" disabled>--Chọn trạng thái--</option>
                    <option value="Lên lớp">Lên lớp</option>
                    <option value="Lưu ban">Lưu ban</option>
                    </select>
                </label>
            </div>
            <div>
                <button @click.prevent="fetchData">Lấy danh sách</button>
                <button v-if="!selectedReviewStatus || edit && selectedReviewStatus" @click.prevent="confirm">Xác nhận</button>
                <button v-if="!edit && selectedReviewStatus" @click.prevent="assignStudent">Xác nhận xếp lớp</button>
                <button v-if="!edit && selectedReviewStatus" @click.prevent="edit = true">Điều chỉnh</button>
                <button v-if="edit" @click.prevent="edit = false">Hủy</button>
            </div>
        </div>
        <div>{{ resultMSG }}</div>
        <div>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th style="width: 2em;">STT</th>
                        <th style="width: 10em;">Họ và tên</th>
                        <th style="width: 6em;">Mã số</th>
                        <th style="width: 5em;">Điểm TB</th>
                        <th style="width: 6em;">Xếp loại</th>
                        <th style="width: 6em;">Hạnh kiểm</th>
                        <th style="width: 6em;">Khối lớp</th>
                        <th style="width: 5em;">Lớp học</th>
                        <th style="width: 18em;">Ghi chú</th>
                        <th style="width: 7em;">Kết quả</th>
                        <th style="width: 5em;">Thao tác</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in studentList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>
                            <span>{{ item.name }}</span>
                        </td>
                        <td>{{ item.student_code }}</td>
                        <td>
                            <span>{{ item.score?.toFixed(2) }}</span>
                        </td>
                        <td>
                            <span>{{ item.learning_status }}</span>
                        </td>
                        <td>{{ item.conduct ? 'Đạt' : 'Không đạt' }}</td>
                        <td>
                           Khối {{ item.grade }}
                        </td>
                        <td>{{ item.class_room_id ? item.class_room_id : 'N/A'}}</td>
                        <td>{{ item.note }}</td>
                        <td>
                            <span v-if="!edit">{{ item.status }}</span>
                            <select v-model="item.status" v-else>
                                <option value="Chờ xét duyệt">--Xét duyệt--</option>
                                <option value="Lên lớp">Lên lớp</option>
                                <option value="Lưu ban">Lưu ban</option>
                                <option value="Bảo lưu">Bảo lưu</option>
                            </select>
                            
                        </td>
                        <td>
                            <select v-model="item.status" v-if="!item.review_status">
                                <option :value="null">--Xét duyệt--</option>
                                <option value="Lên lớp">Lên lớp</option>
                                <option value="Lưu ban">Lưu ban</option>
                                <option value="Bảo lưu">Bảo lưu</option>
                            </select>
                            <span v-else-if="item.status === 'Bảo lưu'"></span>
                            <select v-if="item.review_status" v-model="item.assign_class_id">
                                <option :value="null" disabled>--Xếp lớp--</option>
                                <option v-for="cls in classList" :key="cls.class_room_id" :value="cls.class_room_id">{{ cls.class_room }}</option>
                            </select>
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
import { useSemesterStore } from '../../stores/semesterStore'
const resultMSG = ref('')
const yearStore = userYearStore()
const semesterStore = useSemesterStore()

onMounted(() => {
    fetchGradeData()
})

const selectedStatus = ref('')
const selectedStudent = ref([])
const assignStudent = async () => {
    const changedRows = studentList.value.filter(item => {
        const origin = original.value.find(o => o.student_id === item.student_id)
        return item.assign_class_id !== origin.assign_class_id
    })
    .map(item => ({
        class_room_id: item.assign_class_id, 
        student_id: item.student_id,
       })) 
    
    const payload = {
        year_id: yearStore.year.id,
        student_assign_list: changedRows
    }

    try {
        const res = await axios.post(`api/students/assignment`, payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMSG.value = res.data.msg
        fetchStudentData()
        selectedStudent.value = []
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMSG.value = e.response.data.msg
        }
    }
}
const forApproval = () => {
    selectedStatus.value = ''
    selectedReviewStatus.value = false
}

const gradeSearch = ref('')
const gradeList = ref('')
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
}
const selectedReviewStatus = ref('')
const studentList = ref([])
const fetchStudentData = async () => {
    if (selectedReviewStatus.value === '') {
        alert("Vui lòng chọn danh sách tìm kiếm trước khi lấy danh sách học sinh!")
        return

    } else if (selectedReviewStatus.value === true) {

        if (selectedGrade.value === '' || selectedStatus.value === '') {
            alert("Vui lòng chọn khối lớp và kết quả!")
            return
        }
    } 

    try {
        const res = await axios.get(`api/years/${yearStore.year.id}/students`, {
            withCredentials: true,
            params: {
                grade: selectedGrade.value,
                review_status: selectedReviewStatus.value,
                status: selectedStatus.value,
            }
        })
        studentList.value = []
        studentList.value = res.data.data.map(item => ({...item, assign_class_id: null}))
        original.value = JSON.parse(JSON.stringify(studentList.value))

        if(selectedStatus.value !== '') {
            fetchClassData()
        }

    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMSG.value = e.response.data.msg
        }  
    }
}

const classList = ref([])
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/class-rooms/assignable`, {
        withCredentials: true,
        params: {
            grade: selectedGrade.value,
            status: selectedStatus.value
        }
    })
    classList.value = res.data.data
}
const edit = ref(false)
const original = ref([])
const confirm = async () => {
    const changeRows = studentList.value.filter(item => {
        const origin = original.value.find(o => o.student_id === item.student_id)
        return item.status !== origin.status
    })
    .map(item => ({
        student_id: item.student_id,
        status: item.status
    }))
    const res = await axios.put(`api/years/${yearStore.year.id}/students/review`, changeRows, {
        withCredentials: true
    })
    fetchStudentData()
    resultMSG.value = res.data.msg
    edit.value = false
}



</script>
