<template>
    <nav class="sidebar">
        <div @click="$emit('change', 'ContentReport')">Thống kê</div>
        <div @click="classControlStatus = true">Quản lý lớp học</div>
        <div v-if="classControlStatus" class="classControl">
            <div @click="$emit('change', 'ContentClass')">Cho điểm học sinh</div>
            <div v-if="role === 'admin'" @click="$emit('change', 'ContentToolClass')">Thêm lớp học</div>
            <div>Cloud lưu trữ</div>
            <div class="cloudControl">
                <div @click="$emit('change', 'ContentUpload')">Upload</div>
                <div @click="$emit('change', 'ContentDownload')">Download</div>
            </div>
            <div @click="classControlStatus = false">Đóng</div>
        </div>
        <div @click="studentControlStatus = true">Quản lý học sinh</div>
        <div v-if="studentControlStatus" class="studentControl">
            <div @click="$emit('change', 'ContentStudent')">Danh sách học sinh</div>
            <div @click="$emit('change', 'ContentToolStudent')">Thêm học sinh</div>
            <div @click="studentControlStatus = false">Đóng</div>
        </div>
        <div @click="teacherControlStatus = true">Quản lý giáo viên</div>
        <div v-if="teacherControlStatus"  class="teacherControl">
            <div @click="$emit('change', 'ContentTeacher')">Danh sách giáo viên</div>
            <div v-if="role === 'admin'" @click="$emit('change', 'ContentToolTeacher')">Thêm giáo viên</div>
            <div @click="teacherControlStatus = false">Đóng</div>
        </div>
        <div v-if="role === 'admin'" @click="$emit('change', 'ContentUser')">Quản lý User</div>
        <div v-if="role === 'admin'" @click="$emit('change', 'ContentMonitoring')">Quản lý log</div>
        <div @click="$emit('change', 'ContentToolInfo')">Quản lý thông tin cá nhân</div>
    </nav>
</template>
<script setup>
import { ref } from 'vue';
import useUserStore from '../stores/user';

const studentControlStatus = ref(false)
const teacherControlStatus = ref(false)
const classControlStatus = ref(false)
const userStore = useUserStore() 

const role = userStore.userInfo.role

</script>
<style scoped>
.studentControl, .classControl, .teacherControl {
    position: relative;
    left: 20px;
}

.cloudControl {
    position: relative;
    left: 30px;
}
</style>
