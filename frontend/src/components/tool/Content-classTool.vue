<template>
    <div>Công cụ: Lớp học</div>
    <form>
        <label>Thêm Khối lớp: </label> 
        <input v-model="gradeInput" type="text">
        <label>
            Khối lớp thực
            <input v-model="gradeStatus" type="checkbox" :value="true">
        </label>
        <button @click.prevent="addGrade">Thêm</button>
    </form>
    <form>
        <label>Thêm Lớp học: </label> 
        <input v-model="classInput" type="text">
        <button @click.prevent="addClass">Thêm</button>
    </form>
    <div>{{ resultMsg }}</div>
    <div>
        <button @click.prevent="createLessonClass ">Tạo liên kết môn học - lớp</button> <br>
        <span>***Lưu ý quan trọng: Sau khi tạo lớp học cho năm mới, phải tạo liên kết môn học - lớp để có thể xếp lớp cho giáo viên!!</span>
    </div>
    <div style="display: flex;">
        <div>Danh sách khối lớp</div>
        <div>
            <button v-if="!gradeEditing" @click.prevent="editGrade">Chỉnh sửa khối lớp</button>
            <button v-else @click.prevent="saveEditGrade">Lưu</button>
            <button v-if="gradeEditing" @click.prevent="cancelEditGrade">Hủy</button>
        </div>
    </div>
    <table border="1" style="border-collapse: collapse; text-align: center;">
        <thead>
            <tr>
                <th style="width: 3em;">STT</th>
                <th style="width: 7em;">Khối lớp</th>
                <th style="width: 7em;">Khối lớp thực</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(g, index) in gradeList" :key="g.id" :value="g.id">
                <td>{{ index + 1 }}</td>
                <td>
                    <span v-if="!gradeEditing">Khối {{ g.grade }}</span>
                    <input v-else type="text" v-model="g.grade" style="width: 7em;">
                </td>
                <td>
                    <span v-if="!gradeEditing">{{ g.grade_status ? 'Y' : 'N' }}</span>
                    <input v-else type="checkbox" v-model="g.grade_status" style="width: 7em;">
                </td>
            </tr>
        </tbody>
    </table>
    <div>Danh sách lớp học</div>
    <form>
        <label>Niên khóa: </label>
        <select v-model="selectedYear">
            <option :value="yearStore.year.id">{{ yearStore.year.year }}</option>
            <option value="" disabled>-- Chọn niên khóa --</option>
            <option v-for="year in yearList" :key="year.id" :value="year.id">{{ year.year }}</option>
        </select>
        <label> Khối lớp: </label>
        <select v-model="selectedGrade">
            <option value="" selected disabled>-- Chọn khối lớp --</option>
            <option value="">Toàn bộ</option>
            <option v-for="item in gradeList" :key="item.id" :value="item.grade"> Khối {{ item.grade }}</option>
        </select>
        <button  @click.prevent="fetchClassData">Tìm kiếm</button>
        <button v-if="!classEditing" @click.prevent="classEdit">Chỉnh sửa lớp học</button>
        <button @click.prevent="editSave" v-else>Lưu</button>
        <button @click.prevent="editCancel" v-if="classEditing">Hủy</button>
    </form>
    <div>
        <table border="1" style="border-collapse: collapse; text-align: center;">
            <thead>
                <tr>
                    <th style="width: 3em;">STT</th>
                    <th style="width: 5em;">Lớp học</th>
                    <th style="width: 10em;">Danh sách username/password</th>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(classRoom, index) in classList" :key="classRoom">
                    <td>{{index + 1}}</td>
                    <td>
                        <span v-if="!classEditing">{{ classRoom.class_room }}</span>
                        <input v-else v-model="classRoom.class_room" type="text" style="width: 5em;">
                    </td>
                    <td>
                        <button @click.prevent="exportXML(classRoom.class_room_id)">In danh sách</button>
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
const classEditing = ref(false)
const gradeEditing = ref(false)
const gradeStatus = ref(false)
selectedYear.value = yearStore.year?.id || ''

onMounted( () => {
    fetchClassData()
    fetchGradeData()
    fetchYearData()
})

const addGrade = async () => {
    const payload = {
        grade: gradeInput.value,
        grade_status: gradeStatus.value
    }
    try {
        const res = await axios.post('api/academic/grades', payload, {
            withCredentials: true,
            headers: {'Content-Type': 'application/json'}
        })
        resultMsg.value = res.data.msg
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

const gradeOriginal = ref([])
const editGrade = () => {
    gradeEditing.value = true
    gradeOriginal.value = JSON.parse(JSON.stringify(gradeList.value))
}

const cancelEditGrade = () => {
    gradeEditing.value = false
    gradeList.value = gradeOriginal.value
}

const saveEditGrade = async () => {
    const payload = gradeList.value.map(item => {
        const origin = gradeOriginal.value.find(o => o.id === item.id);
        if (!origin) return null;

        const changedEntries = Object.entries(item).filter(([k, v]) => v !== origin[k]);
        if (changedEntries.length === 0) return null;
        
        const changedObject = Object.fromEntries(changedEntries);
        changedObject.grade_id = item.id;

        return changedObject
    })
    .filter(Boolean)

    if (payload.length > 0) {

        try {
            const res = await axios.put('api/academic/grades', payload, {
                withCredentials: true,
                headers: {'Content-Type': 'application/json'}
            })
            resultMsg.value = res.data.msg
            gradeEditing.value = false
            fetchGradeData()

        } catch (e) {
            if (e.response && [400,404,409,422,500].includes(e.response.status)) {
                resultMsg.value = e.response.data.msg
            }
        }

    } else {
        gradeEditing.value = false
    }
}

const addClass = async () => {
    const payload = {
        year_id: yearStore.year.id,
        class_room: classInput.value
    }

    try {
        const res = await axios.post('api/academic/class-rooms', payload, 
            { 
            withCredentials: true, 
            headers: {'Content-Type': 'application/json'}
            })
        resultMsg.value = res.data.msg 
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            resultMsg.value = e.response.data.msg
        } else {
            resultMsg.value = 'Có vấn đề rồi!!'
        }
    }
}

const fetchClassData = async () => {
    const res = await axios.get(`api/academic/years/${selectedYear.value}/me/class-rooms`, {
        params: {
            grade: selectedGrade.value
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

const createLessonClass = async () => {
    const payload = {
        year_id: yearStore.year.id
    }
    const res = await axios.post('api/academic/relation/lessons-class', payload, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
}

let originalClassList = []
const classEdit = () => {
    classEditing.value = true
    originalClassList = JSON.parse(JSON.stringify(classList.value))
}

const editCancel = () => {
    classEditing.value = false
    classList.value = originalClassList
}

const editSave = async () => {
    const changedRows = classList.value.filter(item => {
        const origin = originalClassList.find(o => o.class_room_id === item.class_room_id);
        if(!origin) return null;

        const changedEntries = Object.entries(item).filter(([k, v]) => v !== origin[k]);
        if (changedEntries.length === 0) return null;

        const changedObject = Object.fromEntries(changedEntries)
        changedObject.class_room_id = item.class_room_id
        return changedObject
    }).filter(Boolean)
    
    if (changedRows.length > 0) {

        try {
            const res = await axios.put('api/academic/class-rooms', changedRows, {
                withCredentials: true
            })

            resultMsg.value = res.data.msg
            classEditing.value = false
            fetchClassData()

        } catch (e) {
            if (e.response && [400,404,409,422,500].includes(e.response.status)) {
                resultMsg.value = e.response.data.msg
            }
        }
    } else {    
        classEditing.value = false
    }
}

const exportXML = (item) => {
    const url = `api/export/class-rooms/${item}?year_id=${selectedYear.value}`
    window.open(url, '_blank') 
}
</script>