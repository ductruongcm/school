<script setup>
import { onMounted, ref, inject } from 'vue';
import axios from 'axios';

const year = inject('year')
const classList = ref([])
onMounted(async () => {
    const payload = { year: year.value}
    const res = await axios.put('api/class_room/show_class_room', payload, { 
        withCredentials: true, 
        headers: {'Content-Type': 'application/json'}
    })
    classList.value = res.data.data
})

</script>


<template>
    <div>Danh sách lớp học</div>
    <div>
        <table>
            <thead>
                <tr>
                    <th>STT</th>
                    <th>Lớp</th>
                    <th>Sỉ số</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(item, index) in classList" :key="item">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.class_room }}</td>
                    <td>{{ item.qty }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>