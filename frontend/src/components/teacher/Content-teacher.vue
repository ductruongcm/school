<template>
    <div style="display: flex; gap: 1em;">
        <div>Danh sách Giáo viên</div>
        <div v-if="userStore.userInfo.role === 'admin'">
            Niên Khóa 
            <select v-model="selectedYear">
                <!-- <option value="">Toàn bộ</option> -->
                <option v-for="year in yearList" :key="year.id" :value="year.id">{{ year.year }}</option>
            </select>
        </div>
        <div v-else>
            Niên Khóa {{ yearStore.year.year }}
        </div>
    </div>

    <div class="main">
        <div>
            <form @submit.prevent="fetchdata" style="display: flex; gap: 1em;">
                <label> 
                    Tìm theo tên: <input style="width: 9em;" v-model="filterName" placeholder="Nhập tên giáo viên"> 
                </label>
                
                <label> 
                    Tìm theo môn học: <input style="width: 7em;"  type="text" v-model="lessonSearch" placeholder="Nhập môn học">
                </label>
                
                <label> 
                    Tìm theo lớp: <input style="width: 6em;"  type="text" v-model="classSearch" placeholder="Nhập lớp học">
                </label>
                
                <label> 
                    Khối lớp: 
                    <select v-model="selectedGrade">
                        <option value="" disabled>--Chọn khối--</option>
                        <option value="">Toàn bộ</option>
                        <option v-for="grade in gradeList" :key="grade.grade" :value="grade.grade">Khối lớp {{ grade.grade }}</option>
                    </select>
                </label>
                <label v-if="userStore.userInfo.role === 'admin'">
                    Trạng thái:
                    <select v-model="selectedStatus">
                        <option value="" disabled>--Chọn--</option>
                        <option value="">Toàn bộ</option>
                        <option :value="true">Hiện</option>
                        <option :value="false">Ẩn</option>
                    </select>
                </label>

                <button>Tìm kiếm</button>
                <button type="button" @click="onReset">Nhập lại</button>
            </form>
        </div>
        <div> {{ teacherSearchMsg }}</div>
        <div>
            <table border="1" style="border-collapse: collapse; text-align: center;">
                <thead>
                    <tr>
                        <th>STT</th>
                        <th style="width: 10em;">Họ và tên</th>
                        <th style="width: 8em;">Chuyên môn</th>
                        <th style="width: 7em;">Chủ nhiệm</th>
                        <th style="width: 14em;">Phụ trách</th>
                        <th style="width: 8em;">Số điện thoại</th>
                        <th style="width: 15em;">Địa chỉ</th>
                        <th style="width: 13em;">Email</th>
                        <th style="width: 8em;" v-if="userStore.userInfo.role === 'admin'">Trạng thái</th>
                        <th style="width: 8em;" v-if="userStore.userInfo.role === 'admin'">Thao tác</th>
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
                        <td v-if="userStore.userInfo.role === 'admin'">{{ item.status ? 'Hiện' : 'Ẩn' }} </td>
                        <td v-if="userStore.userInfo.role === 'admin'">
                            <button @click="openPopup(item)">Chỉnh sửa</button>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <ContentEditTeacher 
    v-if="editPopup && selectedItem"
    :data="selectedItem"
    @save="updateTeacher"
    @close="editPopup = false"
    />
</template>
<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useUserStore } from '../../stores/user';
import { message } from '../../stores/usePopup';
import { userYearStore } from '../../stores/yearStore';

const teacherList = ref([])
const teacherSearchMsg = ref('')
const lessonSearch = ref('')
const classSearch = ref('')
const filterName = ref('')
const userStore = useUserStore()
const yearStore = userYearStore()
onMounted(() => {
    fetchdata()
    fetchGradeData()
    fetchYearData()
})

const selectedStatus = ref(true)
const fetchdata = async () => {
    try {
        const res = await axios.get('api/teachers', {
            params: {
                year_id: selectedYear.value,
                grade: selectedGrade.value,
                lesson: lessonSearch.value,
                class_room: classSearch.value,
                name: filterName.value,
                status: selectedStatus.value
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
selectedYear.value = yearStore.year.id
const fetchYearData = async () => {
    const res = await axios.get('api/academic/years', {
        withCredentials: true,
        params: {
            year: yearSearch.value
        }
    })
    yearList.value = res.data.data
}

const selectedGrade = ref('')
const gradeList = ref(null)
const gradeSearch = ref('')
const fetchGradeData = async () => {
    const res = await axios.get('api/academic/grades', {
        withCredentials: true,
        params: {
            grade: gradeSearch.value,
            grade_status: true
        }
    })
    gradeList.value = res.data.data
}

const editPopup = ref(false)
const selectedItem = ref(null)
import ContentEditTeacher from './Content-editTeacher.vue';
import { toRaw } from 'vue';
const openPopup = (item) => {
    selectedItem.value = structuredClone(toRaw(item))
    editPopup.value = true
}

const updateTeacher = async (msg) => {
    editPopup.value = false
    await fetchdata()
    teacherSearchMsg.value = msg
}

const onReset = () => {
    classSearch.value =''
    filterName.value =''
    selectedGrade.value = ''
    lessonSearch.value = ''
    fetchdata()
}
</script>
