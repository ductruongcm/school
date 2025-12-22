<template>
    <div>
        <h4>Kết quả cuối năm</h4>
        <div style="display: flex; gap: 2em;">
            <label>
                Lớp
                <select v-model="selectedClass">
                    <option value="" disabled>--Chọn lớp--</option>
                    <option v-for="cl in classList" :value="cl.class_room_id" :key="cl.class_room_id">{{ cl.class_room }}</option>
                </select>
            </label>
            <label>
                Kết quả
                <select v-model="status">
                    <option value="">Tất cả</option>
                    <option value="Lên lớp">Lên lớp</option>
                    <option value="Thi lại">Thi lại</option>
                </select>
            </label>
            <label>
                Xếp loại
                <select v-model="learning_status">
                    <option value="">Tất cả</option>
                    <option value="Tốt">Tốt</option>
                    <option value="Khá">Khá</option>
                    <option value="Đạt">Đạt</option>
                    <option value="Chưa đạt">Chưa đạt</option>
                </select>
            </label>
            <button @click.prevent="fetchStudentList">Lấy danh sách</button>
            <div style="display: flex; gap: 2em;">
                <span>Tốt: {{ studentList?.summary?.good }}</span>
                <span>Khá: {{ studentList?.summary?.fair }}</span>
                <span>Đạt: {{ studentList?.summary?.avg }}</span>
                <span>Chưa đạt: {{ studentList?.summary?.bad }}</span>
            </div>
        </div>
        <div>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th style="width: 3em;">STT</th>
                        <th style="width: 9em;">Tên</th>
                        <th style="width: 6em;">Mã HS</th>
                        <th style="width: 6em;">Điểm TB</th>
                        <th style="width: 8em;">Xếp loại</th>
                        <th style="width: 8em;">Hạnh kiểm</th>
                        <th style="width: 8em;">Kết quả</th>
                        <th style="width: 15em;">Ghi chú</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(student, idx) in studentList.students">
                        <td>{{ idx + 1 }}</td>
                        <td>{{ student.name }}</td>
                        <td>{{ student.student_code }}</td>
                        <td>{{ student.score }}</td>
                        <td>{{ student.learning_status }}</td>
                        <td>{{ student.conduct ? 'Đạt' : 'Không đạt'  }}</td>
                        <td>{{ student.status }}</td>
                        <td>{{ student.note }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
<script setup>
import { ref, onMounted, watch } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useUserStore } from '../../stores/user';

const yearStore = userYearStore()
const userStore = useUserStore()
const homeRoomId = userStore.userInfo.homeroom_id
const selectedClass = ref('')
const classList = ref('')
const learning_status = ref('')
const status = ref('')
const fetchClassList = async () => {
     const res = await axios.get(`api/academic/years/${yearStore.year.id}/me/class-rooms`, {
        withCredentials: true,
        params: {
            grade: '',
        }
    })
    classList.value = res.data.data
    selectedClass.value = homeRoomId || classList.value[0].class_room_id
}

const studentList = ref('')
const fetchStudentList = async () => {
    const res = await axios.get(`api/years/${yearStore.year.id}/students/summary/result`, {
        withCredentials: true,
        params: {
            class_room_id: selectedClass.value,
            learning_status: learning_status.value,
            status: status.value
        }
    })
    studentList.value = res.data.data
}

watch(selectedClass, async (newVal) => {
    if (newVal) await fetchStudentList()
})

onMounted(async () => {
    await fetchClassList()
    await fetchStudentList()
})
</script>