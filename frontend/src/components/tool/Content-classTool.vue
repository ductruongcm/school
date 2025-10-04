<template>
    <div>Công cụ</div>
    <form>
        <label>Thêm Khối lớp: </label> 
        <input v-model="gradeInput" type="text">
        <button @click.prevent="addGrade">Thêm</button>
    </form>
    <form>
        <label>Thêm Lớp học: </label> 
        <input v-model="classInput" type="text">
        <button @click.prevent="addClass">Thêm</button>
    </form>
    <div>{{ resultMsg }}</div>

    <div>
        <table>
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Lớp học</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(classRoom, index) in classList" :key="classRoom">
                    <td>{{index + 1}}</td>
                    <td>{{ classRoom }}</td>
                </tr>
            </tbody>
        </table>
    </div>

    <div>
        <table>
            <thead>
                <tr v-for="(grade, index) in gradeList" :key="grade">
                    <th>STT</th>
                    <th>Khối lớp</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{index + 1}}</td>
                    <td>{{ grade }}</td>
                </tr>
            </tbody>
        </table>
    </div> 
</template>
<script setup>
import axios from 'axios';
import { ref, inject, onMounted } from 'vue';

const classInput = ref('')
const gradeInput = ref('')
const resultMsg = ref('')
const year = inject('year')
const classRoomInput = ref('')
const classList = ref([])
const gradeList = ref([])

onMounted( () => {
    fetchClassData()
    fetchGradeData()
})

const addGrade = async () => {
    const payload = {
        grade: gradeInput.value
    }
    try {
        const res = await axios.post('api/academic/grades', payload, {
        withCredentials: true,
        headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

const addClass = async () => {
    const payload = {
        year: year.value,
        class_room: classInput.value
    }
    try {
        const res = await axios.post('api/academic/class_rooms', payload, 
            { 
            withCredentials: true, 
            headers: {'Content-Type': 'application/json'}
            })
        resultMsg.value = res.data.msg 
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

const fetchClassData = async () => {
    const res = await axios.get('api/academic/class_rooms', {
        params: {
            class_room: classRoomInput.value,
            year: year.value
        },
        withCredentials: true
    })
    console.log(res.data)
    classList.value = res.data.data
}

const fetchGradeData = async () => {
    const res = axios.get('api/academic/grades', {
        params: {grade: gradeInput.value},
        withCredentials: true
    })
    gradeList.value = res.data
}

</script>