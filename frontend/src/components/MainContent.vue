<template>
    <main class="main">
        <component :is="activeComponent" />
    </main>
</template>

<script setup>
import ContentDownload from './class_room/Content-download.vue';
import ContentUpload from './class_room/Content-upload.vue';
import ContentInfo from './info/Content-info.vue';
import ContentMonitoring from './monitoring/Content-monitoring.vue';
import ContentReport from './report/Content-report.vue';
import ContentAddStudent from './student/Content-addStudent.vue';
import ContentStudent from './student/Content-addStudent.vue';
import ContentAddTeacher from './teacher/Content-addTeacher.vue';
import ContentTeacher from './teacher/Content-teacher.vue';
import ContentClassTool from './tool/Content-classTool.vue';
import ContentLessonTool from './tool/Content-lessonTool.vue';
import ContentYearTool from './tool/Content-yearTool.vue';
import ContentFolder from './class_room/Content-folder.vue';
import ContentUser from './user/Content-user.vue';
import ContentScheduleTool from './tool/Content-scheduleTool.vue';

const props = defineProps({
    activeComponent: {
        type: Object,
        default: () => ContentReport
    }
})

</script>
