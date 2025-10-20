<template>
    <div>Công cụ: Lớp học</div>
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
    <div>Danh sách lớp học</div>
    <form>
        <label>Niên khóa: </label>
        <select v-model="selectedYear" @change="fetchClassData">
            <option :value="yearStore.year.id">{{ yearStore.year.year }}</option>
            <option value="" disabled>-- Chọn niên khóa --</option>
            <option v-for="year in yearList" :key="year.id" :value="year.id">{{ year.year }}</option>
        </select>
        <label> Khối lớp: </label>
        <select v-model="selectedGrade" @change="fetchClassData">
            <option value="" selected disabled>-- Chọn khối lớp --</option>
            <option value="">Toàn bộ</option>
            <option v-for="item in gradeList" :key="item.id" :value="item.id"> Khối {{ item.grade }}</option>
        </select>
        <button v-if="!editing" @click.prevent="classEdit">Cập nhật</button>
        <button @click.prevent="editSave" v-else>Lưu</button>
        <button @click.prevent="editCancel" v-if="editing">Hủy</button>
    </form>
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
                    <td>
                        <span v-if="!editing">{{ classRoom.class_room }}</span>
                        <input v-else v-model="classRoom.class_room" type="text">
                    </td>
                    <td>
                        <button @click.prevent="exportXML(classRoom.class_room_id)">In list username/password</button>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import axios from 'axios';
import { ref, onMounted } from 'vue';
import { userYearStore } from '../../stores/yearStore';

const classInput = ref('')
const gradeInput = ref('')
const resultMsg = ref('')
const classRoomInput = ref('')
const classList = ref([])
const gradeList = ref([])
const selectedGrade = ref('')
const selectedYear = ref('')
const yearStore = userYearStore()
const editing = ref(false)
selectedYear.value = yearStore.year?.id || ''

onMounted( () => {
    fetchClassData()
    fetchGradeData()
    fetchYearData()
})

const addGrade = async () => {
    const payload = {
        grade: gradeInput.value,
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
        year_id: yearStore.year.id,
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
            grade_id: selectedGrade.value,
            year_id: selectedYear.value
        },
        withCredentials: true
    })
    classList.value = res.data.data
}

const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        params: {grade: gradeInput.value},
        withCredentials: true
    })
    gradeList.value = res.data.data
}

const yearList = ref([])
const yearSearch = ref('')
const fetchYearData = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {year: yearSearch.value}
    })
    yearList.value = res.data.data
}

let originalClassList = []
const classEdit = () => {
    editing.value = true
    originalClassList = JSON.parse(JSON.stringify(classList.value))
}

const editCancel = () => {
    editing.value = false
    classList.value = originalClassList
}

const editSave = async () => {
    const changedRows = classList.value.filter(cls => {
        cls['year_id'] = yearStore.year.id
        const original = originalClassList.find(o => o.class_room_id === cls.class_room_id)
        return original.class_room !== cls.class_room
    })
    const payload = changedRows
    try {
        const res = await axios.put('api/academic/class_rooms', payload, {
        withCredentials: true
        })
        resultMsg.value = res.data.msg
        editing.value = false
        fetchClassData()
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        }
    }
}

const exportXML = (item) => {
    const url = `api/export/class_rooms/${item}?year_id=${selectedYear.value}`
    window.open(url, '_blank') 
}
</script>