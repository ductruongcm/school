<template>
    <nav class="sidebar">
        <div @click="$emit('change', 'ContentClass')">Danh sách lớp học</div>
        <div @click="$emit('change', 'ContentTeacher')">Danh sách giáo viên</div>
        <div @click="$emit('change', 'ContentStudent')">Tra cứu học sinh</div>
        <div @click="$emit('change', 'ContentReport')">Thống kê</div>
        <div @click="$emit('change', 'ContentToolTeacher')">Quản lý giáo viên</div>
        <div @click="$emit('change', 'ContentToolClass')">Quản lý lớp học</div>
        <div @click="$emit('change', 'ContentToolStudent')">Quản lý học sinh</div>
        <div @click="$emit('change', 'ContentToolInfo')">Quản lý thông tin cá nhân</div>
    </nav>
</template>
<script setup>


</script>
<style scoped>
.sidebar {
    cursor: pointer;
}
</style>