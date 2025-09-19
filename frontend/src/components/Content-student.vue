<template>
    <div>Danh sách học sinh</div>
    <div class="main">
        <form>
            <label>Chọn lớp  </label>
            <select v-model="selectedClass">
                <option value="" selected disabled>-- Chọn lớp --</option>
                <option v-for="item in classList" :key="item"> {{ item }}</option>
            </select>
        </form>

        <div>
            <table>
                <thead>
                    <tr>
                        <th style="width: 2em;">STT</th>
                        <th style="width: 15em;">Họ và tên</th>
                        <th style="width: 10em;">Số điện thoại</th>
                        <th style="width: 20em;">Địa chỉ</th>
                        <th style="width: 10em;"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in student" :key="item">
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
                            <button v-if="!item.editing" @click="editRow(item)">Sửa thông tin</button>
                            <button v-else @click="saveEdit(item)">Lưu</button>
                            <button v-if="item.editing" @click="cancelEdit(item)">Hủy</button>
                        </td>
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

watch(classList, (newVal) => {
    if (newVal.length === 1) {
        selectedClass.value = newVal[0]
    }
})

function editRow(item) {
    item.original = {...item}
    item.editing = true
}

function cancelEdit(item) {
    Object.assign(item, item.original)
    item.editing = false
}

async function saveEdit(item) {
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
        msg.value = 'Updated!'
    } catch (e) {
        if (e.response && e.response.status === 400) {
            msg.value = e.response.data.msg
        } else {
            msg.value = 'Có rắc rối rồi!!'
        }
    }
}


</script>
