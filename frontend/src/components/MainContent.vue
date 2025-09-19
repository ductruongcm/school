<template>
    <main class="main">
        <component :is="activeComponent" />
    </main>
</template>

<script setup>
import ContentReport from '../components/Content-report.vue';
import ContentClass from '../components/Content-class.vue';
import ContentStudent from '../components/Content-student.vue';
import ContentTeacher from '../components/Content-teacher.vue';
import ContentToolClass from '../components/Content-toolClass.vue';
import ContentToolInfo from '../components/Content-toolInfo.vue';
import ContentToolStudent from '../components/Content-toolStudent.vue';
import ContentToolTeacher from '../components/Content-toolTeacher.vue';
import ContentDownload from './Content-download.vue';
import ContentUpload from './Content-upload.vue';
import ContentUser from './Content-user.vue';

const props = defineProps({
    activeComponent: {
        type: Object,
        default: () => ContentReport
    }
})

</script>
