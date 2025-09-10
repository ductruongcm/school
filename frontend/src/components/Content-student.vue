<template>
    <div>Danh sách học sinh</div>
    <div>
        <form>
            <label>Chọn lớp  </label>
            <select v-model="selectedClass">
                <option disabled selected>-- Chọn lớp --</option>
                <option v-for="item in classList" :key="item.class_room"> {{ item.class_room }}</option>
            </select>
        </form>

        <div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th>Họ và tên</th>
                        <th>Số điện thoại</th>
                        <th>Địa chỉ</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in student" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>{{ item.name }}</td>
                        <td>{{ item.tel }}</td>
                        <td>{{ item.add }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div>{{ msg }}</div>
</template>
<script setup>
import { ref, onMounted, inject, watch } from 'vue';
import axios from 'axios';

const year = inject('year')
const classList = ref([])
const selectedClass = ref('')
const student = ref([])
const msg = ref('')

onMounted(async () => {
    const payload = { year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, { 
        withCredentials: true, 
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
})

watch(selectedClass, async (newVal) => {
    try{
        const res = await axios.get(`api/student/show_student?class_room=${newVal}`, { 
            withCredentials: true, 
        })
        student.value = res.data.data
    } catch (err) {
        if (err.response && err.response.status === 403) {
            msg.value = 'Forbidden: Access denied'
        } else {
            msg.value = 'Có vấn đề gì rồi'
        }
    }
})
</script>