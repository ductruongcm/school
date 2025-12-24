<template>
    <div>Công cụ: Học kỳ</div>
        <form>
            <label> Thêm học kỳ </label>
            <input v-model="semesterInput" type="text"></input>
            <label> Hệ số điểm </label>
            <input v-model="weightInput" type="text">
            <button @click.prevent="addSemester">Thêm</button>
        </form>
        <label> Thiết lập học kỳ </label>
        <select v-model="selectedSemester">
            <option value="" disabled>-- Chọn học kỳ --</option>
            <option v-for="item in semesterList" :key="item.semester_id" :value="item.semester_id">{{ item.semester }}</option>
        </select> 
        <button @click.prevent="setSemester">Xác nhận</button>
        <br>
        <button v-if="!editing" @click.prevent="edit">Điều chỉnh</button>
        <button v-else @click.prevent="saveEdit">Lưu</button>
        <button v-if="editing" @click.prevent="cancelEdit">Hủy</button>
        <button v-if="!deleting" @click.prevent="del">Xóa</button>
        <button v-else @click.prevent="agreeDel">XÁC NHẬN XÓA</button>
        <button v-if="deleting" @click.prevent="cancelDel">Hủy</button>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th v-if="deleting" style="width: 3em;">Chọn</th>
                    <th style="width: 4em;">STT</th>
                    <th style="width: 6em;">Học kỳ</th>
                    <th style="width: 6em;">Hệ số điểm</th>
                    <th style="width: 6em;">Trạng thái</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in semesterList" :key="item.semester_id">
                    <td v-if="deleting">
                    <input
                        type="checkbox"
                        :value="item.semester_id"
                        v-model="selectedIds"
                    />
                    </td>
                    <td>{{ index + 1 }}</td>
                    <td>
                        <span v-if="!editing">{{ item.semester }}</span>
                        <input style="width: 6em;" v-model="item.semester" v-else type="text">
                    </td>
                    <td>
                        <span v-if="!editing">{{ item.weight }}</span>
                        <input style="width: 6em;" v-model="item.weight" v-else type="number">
                    </td>
                    <td>
                        {{ item.is_active === true ? 'Active' : '-' }}
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
    <div v-if="deleting">
            <div>****Cực kỳ lưu ý: Nếu học kỳ đã được sử dụng cho các tác vụ</div>
            <div>khi xóa đi sẽ làm sai lệch hoặc có thể mất tất cả dữ liệu.</div>
            <div>Hãy liên hệ với quản trị viên trước khi thao tác!!</div>
    </div>
    <div>{{ resultMsg }}</div>
</template>
<script setup>
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore } from '../../stores/semesterStore';

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const semesterInput = ref('')
const weightInput = ref('')
const resultMsg = ref('')
const editing = ref(false)

const addSemester = async () => {
    const payload = {
        semester: semesterInput.value,
        weight: weightInput.value,
        year_id: yearStore.year.id
    }
    try {
        const res = await axios.post('api/academic/semesters', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
        fetchSemesterData()
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!'
        }
    }
}

const semesterList = ref([])
const semesterSearch = ref('')
const fetchSemesterData = async () => {
    const res = await axios.get('api/academic/semesters', {
        withCredentials: true,
        params: {
            semester: semesterSearch.value,
            year_id: yearStore.year.id
        }
    })
    semesterList.value = res.data.data
    
}

onMounted(() => {
    fetchSemesterData()
})

const originalSemester= ref([])
const edit = () => {
    editing.value = true
    originalSemester.value = JSON.parse(JSON.stringify(semesterList.value))
}

const cancelEdit = () => {
    semesterList.value = originalSemester.value
    editing.value = false
}

const saveEdit = async () => {
    const changedRows = semesterList.value.map(semester => {
        const original = originalSemester.value.find(o => o.semester_id === semester.semester_id)
        if (!original) return null

        const changes = Object.keys(semester).reduce((acc, key) => {
      if (semester[key] !== original[key]) {
            acc[key] = semester[key]
        }
        return acc
        }, {})

        if (Object.keys(changes).length === 0) return null

        return {
        semester_id: semester.semester_id,
        changes
        }
    })
    .filter(Boolean)
    
    if (changedRows.length > 0) {
        try {
            const res = await axios.put('api/academic/semesters', changedRows, {
                withCredentials: true
            })
            resultMsg.value = res.data.msg
            editing.value = false
            fetchSemesterData()

        } catch (e) {
            if (e.response && [400,404,409,422,500].includes(e.response.status)) {
                resultMsg.value = e.response.data.msg
            }
        }
    } else {
        editing.value = false
    }
}

const selectedSemester = ref('')
const setSemester = async () => {
    if (!selectedSemester.value) {
        alert('Chưa chọn học kỳ để thiết lập!')
        return
    }
    const res = await axios.put(`api/academic/semesters/${selectedSemester.value}/status`, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
    semesterStore.setSemester(res.data.data)
}

const selectedIds = ref([])

const deleting = ref(false)
const del = () => {
    deleting.value = true
}

const cancelDel = () => {
    selectedIds.value = []
    deleting.value = false
}

const agreeDel = async () => {
    const payload = {
        semester_ids: selectedIds.value
    }
    try {
        const res = await axios.delete('api/academic/semesters', {
            data: payload,
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        }
    }
}
</script>