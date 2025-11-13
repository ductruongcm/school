<template>
    <div>Công cụ: Điểm số</div>
    <form>
        <label>
            Loại điểm số:
            <input v-model="scoreType" type="text" required>
        </label>   
        <label>
            Hệ số:
            <input v-model="scoreWeight" type="number" required>
        </label>
        <button @click.prevent="createScore">Thêm</button>
        <button v-if="!editing" @click.prevent="edit">Chỉnh sửa</button>
        <button v-else @click.prevent="saveEdit">Xác nhận</button>
        <button v-if="editing" @click.prevent="cancelEdit">Hủy</button>
    </form>
    <div>{{ resultMsg }}</div>
    <div>Danh sách điểm số</div>
    <table border="1" style="border-collapse: collapse; text-align: center;">
        <thead>
            <tr>
                <th style="width: 3em;">STT</th>
                <th style="width: 10em;">Loại điểm số</th>
                <th style="width: 5em;">Hệ số</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(scoreType, index) in scoreTypesList" :key="scoreType.score_type_id">
                <td>
                    <span>{{ index + 1 }}</span>
                </td>
                <td>
                    <span v-if="!editing">{{ scoreType.score_type }}</span>
                    <input v-else type="text" style="width: 10em;" v-model="scoreType.score_type">
                </td>
                <td>
                    <span v-if="!editing">{{ scoreType.weight }}</span>
                    <input v-else type="number" style="width: 5em;" v-model="scoreType.weight">
                </td>
            </tr>
        </tbody>
    </table>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';


onMounted(() => {
    fetchScoreTypesData()
})

const scoreType = ref('')
const scoreWeight = ref('')
const resultMsg = ref('')
const createScore = async () => {
    const payload = {
        score_type: scoreType.value,
        weight: scoreWeight.value
    }

    try {
        const res = await axios.post('api/academic/score-types', payload, {
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

const scoreTypesList = ref([])
const fetchScoreTypesData = async () => {
    const res = await axios.get('api/academic/score-types', {
        withCredentials: true
    })

    scoreTypesList.value = res.data.data
}

const original = ref([])
const editing = ref(false)
const edit = () => {
    editing.value = true
    original.value = JSON.parse(JSON.stringify(scoreTypesList.value))
}

const cancelEdit = () => {
    scoreTypesList.value = original.value
    editing.value = false
}

const saveEdit = async () => {
    const changedRows = scoreTypesList.value.map(item => {
        const origin = original.value.find(o => o.score_type_id === item.score_type_id)
        if (!origin) return null;

        const changedEntries = Object.entries(item).filter(([k, v]) => v !== origin[k])

        const changedObject = Object.fromEntries(changedEntries)
        if (Object.keys(changedObject).length === 0) return null;
        
        changedObject.score_type_id = item.score_type_id
        return changedObject

    }).filter(Boolean)
    
    try {
        const res = await axios.put('api/academic/score-types', changedRows, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })

        resultMsg.value = res.data.msg
        editing.value = false
        fetchScoreTypesData()
        
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {

            resultMsg.value = e.response.data.msg
        }
    }
}
</script>