<template>
    <div>
        <div>Tổng kết Học Kỳ</div>
        <div>
            <label for="">
                Lớp học:
                <select v-model="selectedClass" @change="fetchStudentData">
                    <option value="">--Chọn lớp--</option>
                    <option v-for="cl in classList" :key="cl.class_room_id" :value="cl.class_room_id">{{ cl.class_room }}</option>
                </select>
            </label>
            <label for="">
                Học kỳ:
                <select v-model="selectedSemester" @change="fetchStudentData">
                    <option value="">--Chọn học kỳ--</option>
                    <option v-for="sem in semesterList" :key="sem.semester_id" :value="sem.semester_id">{{ sem.semester }}</option>
                </select>
            </label>
            <!-- <button @click.prevent="fetchStudentData">Lấy danh sách</button> -->
            <!-- <button @click.prevent="summaryPeriod">Tổng kết</button> -->
            <button v-if="!editing" @click.prevent="edit">Tổng kết</button>
            <button v-else @click.prevent="confirmEdit">Xác nhận</button>
            <button v-if="editing" @click.prevent = cancelEdit>Hủy</button>
            <!-- <button @click.prevent="yearSummary">Tổng kết cả năm</button> -->
        </div>
        <div>{{ resultMsg }}</div>
        <div>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th style="width: 3em;">STT</th>
                        <th style="width: 10em;">Tên</th>
                        <th style="width: 4.5em;" v-for="subject in Object.keys(studentList[0]?.scores || {})" :key="subject">{{ subject }}</th>
                        <th style="width: 4.5em;">Tổng kết</th>
                        <th style="width: 4.5em;">Xếp loại</th>
                        <th style="width: 6em;">Hạnh kiểm</th>
                        <th style="width: 6em;">Chuyên cần</th>
                        <th style="width: 10em;">Ghi chú</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(student, ind) in studentList" :key="ind">
                        <td>{{ ind + 1 }}</td>
                        <td>{{ student.name }}</td>
                        <td v-for="score in Object.values(student?.scores || {})" :key="score">{{ score }}</td>
                        <td>{{ student.total }}</td>
                        <td>{{ student.status }}</td>
                        <td>
                            <span v-if="!editing">{{ student.conduct }}</span>
                            <select v-else v-model="student.conduct">
                                <option disabled :value="null">Đánh giá</option>
                                <option :value="true">Đạt</option>
                                <option :value="false">Không đạt</option>
                            </select>
                        </td>
                        <td>
                            <span v-if="!editing">{{ student.absent_day }}</span>
                            <input v-else style="width: 6em;" type="number"  v-model="student.absent_day" required>
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
import { useSemesterStore } from '../../stores/semesterStore';

onMounted(async () => {
    await Promise.all([
        fetchClassData(),
        fetchSemesterData()
    ])
})
const yearStore = userYearStore()
const semesterStore = useSemesterStore()

const classList = ref('')
const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
    })
    classList.value = res.data.data
}

const selectedSemester = ref(semesterStore.semester.semester_id)
const semesterList = ref('')
const fetchSemesterData = async () => {
    const res = await axios.get(`api/academic/semesters`, {
        withCredentials: true,
        params: {
            is_active: ''
        }
    })
    semesterList.value = res.data.data
}

const selectedClass = ref('')
const studentList = ref([])
const fetchStudentData = async () => {
    if (selectedClass.value === '') {
        alert('Bạn chưa chọn lớp học')
        return
    }

    studentList.value = []

    const res = await axios.get(`api/semesters/${selectedSemester.value}/students/summary`, {
        withCredentials: true,
        params: {
            year_id: yearStore.year.id,
            class_room_id: selectedClass.value
        }
    })
    
    studentList.value = res.data.data

}

const resultMsg = ref('')

const editing = ref(false)
const original = ref('')
const edit = () => {
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
        year_id: yearStore.year.id,
        class_room_id: selectedClass.value,
    }

    try {
        const res = await axios.put(`api/academic/entity/semesters/${selectedSemester.value}/summary`, payload, {
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