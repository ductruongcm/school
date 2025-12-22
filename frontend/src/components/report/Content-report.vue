<template>
    <div>
        <h3>Thống kê</h3>
        <div style="display: flex; gap: 1em;">
            <label>
                Niên khóa
                <select v-model="selectedYear">
                    <option value="" disabled>--Chọn niên khóa--</option>
                    <option v-for="y in yearList" :key="y.id" :value="y.id">{{ y.year }}</option>
                </select>
            </label>
            <label>
                Học Kỳ
                <select v-model="selectedSemester">
                    <option value="" disabled>--Chọn học kỳ--</option>
                    <option v-for="s in semesterList" :value="s.semester_id" :key="s.semester_id">{{ s.semester }}</option>
                </select>
            </label>
        </div>
    </div>
    <div style="display: flex; gap: 2em;">
        <div style="border-collapse: collapse; text-align: center;">
            <span>Danh sách lớp học</span>
            <table border="1">
                <thead>
                    <tr>
                        <th rowspan="2" style="width: 3em;">STT</th>
                        <th rowspan="2" style="width: 5em;">Lớp học</th>
                        <th rowspan="2" style="width: 4em;">Sỉ số</th>
                        <th rowspan="2" style="width: 9em;">GV chủ nhiệm</th>
                        <th colspan="4">Kết quả học tập</th>
                    </tr>
                    <tr>
                        <th style="width: 5em;">Chưa đạt</th>
                        <th style="width: 5em;">Đạt</th>
                        <th style="width: 5em;">Khá</th>
                        <th style="width: 5em;">Giỏi</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(cl, idx) in classInfoList" :key="cl.class_room">
                        <td>{{ idx + 1 }}</td>
                        <td>{{ cl.class_room }}</td>
                        <td>{{ cl.qty ? cl.qty : 0 }}</td>
                        <td>{{ cl.teacher }}</td>
                        <td>{{ cl.bad ? cl.bad : 0 }}</td>
                        <td>{{ cl.avg ? cl.avg : 0 }}</td>
                        <td>{{ cl.fair ? cl.fair : 0 }}</td>
                        <td>{{ cl.good ? cl.good : 0 }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div style="border-collapse: collapse; text-align: center;">
            <span>Thống kê chung</span>
            <table table border="1">
                <thead>
                    <tr>
                        <th style="width: 10em;">Thông tin</th>
                        <th style="width: 7em;">Số lượng</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Số lớp</td>
                        <td>{{ sum.count_class }}</td>
                    </tr>
                    <tr>
                        <td>Giáo viên</td>
                        <td>{{ sum.count_teacher }}</td>
                    </tr>
                    <tr>
                        <td>Học sinh Khối 10</td>
                        <td>{{ sum.count_student10 }}</td>
                    </tr>
                    <tr>
                        <td>Học sinh Khối 11</td>
                        <td>{{ sum.count_student11 }}</td>
                    </tr>
                    <tr>
                        <td>Học sinh Khối 12</td>
                        <td>{{ sum.count_student12 }}</td>
                    </tr>
                    <tr>
                        <td>Tổng số học sinh</td>
                        <td>{{ sum.count_students }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    <div style="border-collapse: collapse; text-align: center;">
        <span>Thống kê chung</span>
        <table border="1">
            <thead>
                <tr>
                    <th style="width: 8em;" rowspan="2">Tổng học sinh</th>
                    <th style="width: 6em;" rowspan="2">Tốt nghiệp</th>
                    <th style="width: 15em;" rowspan="1" colspan="4">Lên lớp</th>
                    <th style="width: 6em;" rowspan="2">thi lại</th>
                    <th style="width: 6em;" rowspan="2">Lưu ban</th>
                    <th style="width: 7em;" rowspan="2">học sinh mới</th>
                    <th style="width: 8em;" rowspan="2">Chuyển trường</th>
                </tr>
                <tr>
                    <th style="width: 5em;">Tốt</th>
                    <th style="width: 5em;">Khá</th>
                    <th style="width: 6em;">Trung bình</th>
                    <th style="width: 5em;">dưới TB</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ resultSummaryReport.total }}</td>
                    <td>{{ resultSummaryReport.graduation }}</td>
                    <td>{{ resultSummaryReport.good }}</td>
                    <td>{{ resultSummaryReport.fair }}</td>
                    <td>{{ resultSummaryReport.avg }}</td>
                    <td>{{ resultSummaryReport.retest - resultSummaryReport.failure }} </td>
                    <td>{{ resultSummaryReport.retest }}</td>
                    <td>{{ resultSummaryReport.failure }}</td>
                    <td>{{ resultSummaryReport.new }}</td>
                    <td>{{ resultSummaryReport.transfer }}</td>
                </tr>
            </tbody>
        </table>
    </div>
</template>
<script setup>
import axios from 'axios';
import { userYearStore } from '../../stores/yearStore';
import { useSemesterStore } from '../../stores/semesterStore';
import { ref, onMounted, watch } from 'vue';

onMounted(async () => {
    await fetchYearData()
    await fetchSemesterData()
    await fetchClassInfo()
    await fetchSummary()
    await fetchResultSummary()
})

const yearStore = userYearStore()
const semesterStore = useSemesterStore()
const selectedYear = ref('')
const selectedSemester = ref('')
selectedSemester.value = semesterStore.semester.semester_id

const yearList = ref([])
const fetchYearData = async () => {
    try {
        const res = await axios.get('api/academic/years', {
            withCredentials: true,
            params: {
                is_active: ''
            }
        })
        yearList.value = res.data.data
        selectedYear.value = yearStore.year.id
    } catch (e) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            console.log(e.response.data.msg)
        }
    }
}

const semesterList = ref([])
const fetchSemesterData = async () => {
    try {
        const res = await axios.get('api/academic/semesters', {
            withCredentials: true, 
            params: {
                is_active: ''
            }
        })
        semesterList.value = res.data.data

    } catch (error) {
        if (e.response && [400,404,409,422,500].includes(e.response.status)) {
            console.log(e.response.data.msg)
        }
    }
}

const classInfoList = ref([])
const fetchClassInfo = async () => {
    const res = await axios.get(`api/report/daily/class-rooms`, {
        withCredentials: true,
        params: {
            year_id: selectedYear.value,
            semester_id: selectedSemester.value
        }
    })
    classInfoList.value = res.data.data
}

const sum = ref({})
const fetchSummary = async () => {
    const res = await axios.get(`api/report/years/${selectedYear.value}/info`, {
        withCredentials: true,
        params: {
            semester_id: selectedSemester.value
        }
    })
    sum.value = res.data.data
}

const resultSummaryReport = ref('')
const fetchResultSummary = async () => {
    const res = await axios.get(`api/report/years/${selectedYear.value}/summary/report`, {
        withCredentials: true
    })
    resultSummaryReport.value = res.data.data
}

watch([selectedSemester, selectedYear], ([newSem, newYea]) => {
    if (newSem || newYea) {
        fetchClassInfo()
        fetchResultSummary()
    }
})
</script>