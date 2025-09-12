<template>
    <nav class="sidebar">
        <div @click="$emit('change', 'ContentReport')">Thống kê</div>
        <div @click="teacherControl">Quản lý giáo viên</div>
        <div v-if="teacherControlStatus"  class="teacherControl">
            <div @click="$emit('change', 'ContentTeacher')">Danh sách giáo viên</div>
            <div @click="$emit('change', 'ContentToolTeacher')">Thêm giáo viên</div>
            <div @click="closeTeacherControl">Đóng</div>
        </div>
        <div @click="classControl">Quản lý lớp học</div>
        <div v-if="classControlStatus" class="classControl">
            <div @click="$emit('change', 'ContentClass')">Danh sách lớp học</div>
            <div @click="$emit('change', 'ContentToolClass')">Thêm lớp học</div>
            <div @click="closeClassControl">Đóng</div>
        </div>
        <div @click="studentControl">Quản lý học sinh</div>
        <div v-if="studentControlStatus" class="studentControl">
            <div @click="$emit('change', 'ContentStudent')">Danh sách học sinh</div>
            <div @click="$emit('change', 'ContentToolStudent')">Thêm học sinh</div>
            <div @click="closestudentControl">Đóng</div>
        </div>
        <div @click="$emit('change', 'ContentToolInfo')">Quản lý thông tin cá nhân</div>
    </nav>
</template>
<script setup>
import { ref } from 'vue';

const teacherControlStatus = ref(false)
function teacherControl() {
    teacherControlStatus.value = true
}

function closeTeacherControl() {
    teacherControlStatus.value = false
}

const classControlStatus = ref(false)
function classControl() {
    classControlStatus.value = true
}

function closeClassControl() {
    classControlStatus.value = false
}

const studentControlStatus = ref(false)
function studentControl() {
    studentControlStatus.value = true
}

function closestudentControl() {
    studentControlStatus.value = false
}

</script>
<style scoped>
.studentControl, .classControl, .teacherControl {
    position: relative;
    left: 20px;
}
</style>
