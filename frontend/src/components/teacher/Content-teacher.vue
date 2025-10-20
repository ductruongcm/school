<template>
    <div>
        <label>Danh sách Giáo viên</label>
        <label> - Niên Khóa </label>
        <select v-model="selectedYear">
            <option :value="yearList[0]?.id">{{ yearList[0]?.year }}</option>
            <option value="">Toàn bộ</option>
            <option v-for="year in yearList" :key="year.id" :value="year.id">{{ year.year }}</option>
        </select>
    </div>

    <div class="main">
        <div>
            <form @submit.prevent="fetchdata">
                <label>Tìm theo môn học: </label>
                <input type="text" v-model="lessonSearch" placeholder="Nhập môn học">
                <label> Tìm theo lớp: </label>
                <input type="text" v-model="classSearch" placeholder="Nhập tên lớp">
                <label> Tìm theo tên: </label>
                <input v-model="filterName" placeholder="Nhập tên giáo viên">
                <label> Khối lớp: </label>
                <select v-model="selectedGrade">
                    <option value="" disabled>--Chọn khối--</option>
                    <option value="">Toàn bộ</option>
                    <option v-for="grade in gradeList" :key="grade.id" :value="grade.id">Khối lớp {{ grade.grade }}</option>
                </select>
                <button>Tìm kiếm</button>
                <button type="button" @click="onReset">Nhập lại</button>
            </form>
        </div>
        <div> {{ teacherSearchMsg }}</div>
        <div>
            <table>
                <thead>
                    <tr>
                        <th>STT</th>
                        <th style="width: 11em;">Họ và tên</th>
                        <th style="width: 7em;">Chuyên môn</th>
                        <th style="width: 7em;">Chủ nhiệm</th>
                        <th style="width: 10em;">Phụ trách</th>
                        <th style="width: 7em;">Số điện thoại</th>
                        <th style="width: 10em;">Địa chỉ</th>
                        <th style="width: 13em;">Email</th>
                        <th style="width: 6em;">Trạng thái</th>
                        <th style="width: 15em;"></th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(item, index) in teacherList" :key="item">
                        <td>{{ index + 1 }}</td>
                        <td>{{ item.name }}</td>
                        <td>{{ item.lesson }}</td>
                        <td>{{ item.class_room }}</td>
                        <td>{{ item.teach_room }}</td>
                        <td>{{ item.tel }}</td>
                        <td>{{ item.add }}</td>
                        <td>{{ item.email }}</td>
                        <td>{{ item.status ? 'Hiện' : 'Ẩn' }} </td>
                        <td v-if="userStore.userInfo.role === 'admin'">
                            <button @click="openPopup(item)">Chỉnh sửa</button>
                            <button @click.prevent="status(item)">Hiện/Ẩn</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <ContentEditTeacher 
    v-if="editPopup"
    :data="selectedItem"
    @save="updateTeacher"
    @close="editPopup=false"
    v-model:visible="editPopup"
  
    />
</template>
<script setup>
import { ref, onMounted} from 'vue';
import axios from 'axios';
import useUserStore from '../../stores/user';
import { message } from '../../stores/usePopup';
import { userYearStore } from '../../stores/yearStore';

const teacherList = ref([])
const teacherSearchMsg = ref('')
const lessonSearch = ref('')
const classSearch = ref('')
const filterName = ref('')
const userStore = useUserStore()

onMounted(() => {
    fetchdata()
    fetchGradeData()
    fetchYearData()
})

const fetchdata = async () => {
    try {
        const res = await axios.get('api/teachers', {
            params: {
                year_id: selectedYear.value,
                grade_id: selectedGrade.value,
                lesson: lessonSearch.value,
                class_room: classSearch.value,
                name: filterName.value
            },
            withCredentials: true
        })     
        teacherList.value = res.data.data
        teacherSearchMsg.value = res.data.msg
        
    } catch (e) {
        if (e.response && e.response.status === 400 || 422 || 500) {
            teacherSearchMsg.value = e.response.data.msg
        } else {
            teacherSearchMsg.value = 'Có rắc rồi rồi!'
        }
    }
}

const selectedYear = ref('')
const yearSearch = ref('')
const yearList = ref([])

const fetchYearData = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {
            year: yearSearch.value
        }
    })
    yearList.value = res.data.data
    selectedYear.value = yearList.value[0]?.id
}

const selectedGrade = ref('')
const gradeList = ref(null)
const gradeSearch = ref('')
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value,
            is_active: ''
        }
    })
    gradeList.value = res.data.data
}

const status = async (item) => {
    const res = await axios.put(`api/teachers/${item.id}/status`, {
        withCredentials: true
    })
    item.status = !item.status
    teacherSearchMsg.value = res.data.msg
}

const editPopup = ref(false)
const selectedItem = ref(null)
import ContentEditTeacher from './Content-editTeacher.vue';
const openPopup = (item) => {
    selectedItem.value = JSON.parse(JSON.stringify(item))
     editPopup.value = true
}

const updateTeacher = () => {
    editPopup.value = false
    fetchdata()
}

const onReset = () => {
    classSearch.value =''
    filterName.value =''
    selectedGrade.value = ''
    lessonSearch.value = ''
    selectedYear.value = yearList.value[0]?.id
    fetchdata()
}
</script>
