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
                    <input type="radio" name="action" @change="forAssignment">
                    Danh sách đã xét duyệt
                </label>
            </div>
            <div>
                <label>
                    Năm học
                    <select v-model="selectedYear">
                        <option value="">--Chọn năm học--</option>
                        <option v-for="y in yearList" :key="y.id" :value="y.id">{{ y.year }}</option>
                    </select>
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
                        <option value="" disabled>--Kết quả--</option>
                        <option value="Lên lớp">Lên lớp</option>
                        <option value="Lưu ban">Lưu ban</option>
                    </select>
                </label>
            </div>
            <div>
                <button @click.prevent="fetchData">Lấy danh sách</button>
                <button v-if="!selectedReviewStatus || edit && selectedReviewStatus" @click.prevent="confirm">Xác nhận</button>
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
                        <th style="width: 6em;">Chuyên cần</th>
                        <th style="width: 5em;">Lớp học</th>
                        <th style="width: 18em;">Ghi chú</th>
                        <th style="width: 7em;">Kết quả</th>
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
                        <td>{{ item.absent_day }}</td>
                        <td>{{ item.class_room_id ? item.class_room_id : 'N/A'}}</td>
                        <td>{{ item.note }}</td>
                        <td>
                            <span v-if="selectedReviewStatus && !edit">{{ item.status }}</span>
                            <select v-if="!selectedReviewStatus || selectedReviewStatus && edit" v-model="item.status">
                                <option :value="null">--Xét duyệt--</option>
                                <option value="Lên lớp">Lên lớp</option>
                                <option value="Lưu ban">Lưu ban</option>
                                <option value="Bảo lưu">Bảo lưu</option>
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

const resultMSG = ref('')
const yearStore = userYearStore()
const edit = ref(false)

onMounted(() => {
    fetchGradeData()
    fetchYearData()
})

const selectedYear = ref('')
selectedYear.value = yearStore.year.id
const yearList = ref([])
const fetchYearData = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {year: ''}
    })
    yearList.value = res.data.data
}

const selectedStatus = ref('')

const forApproval = () => {
    selectedStatus.value = ''
    selectedReviewStatus.value = false
}

const forAssignment = () => {
    selectedReviewStatus.value = true
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
    } 

    try {
        const res = await axios.get(`api/years/${selectedYear.value}/students/review`, {
            withCredentials: true,
            params: {
                grade: selectedGrade.value,
                review_status: selectedReviewStatus.value,
                status: selectedStatus.value,
            }
        })
        studentList.value = []
        studentList.value = res.data.data
        original.value = JSON.parse(JSON.stringify(studentList.value))
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMSG.value = e.response.data.msg
        }  
    }
}

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
    const res = await axios.put(`api/years/${selectedYear.value}/students/review`, changeRows, {
        withCredentials: true
    })
    fetchStudentData()
    resultMSG.value = res.data.msg
    edit.value = false
}
</script>
