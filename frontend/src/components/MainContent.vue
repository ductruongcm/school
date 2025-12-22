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
import ContentAssignStudent from './student/Content-assignStudent.vue';
import ContentAddTeacher from './teacher/Content-addTeacher.vue';
import ContentTeacher from './teacher/Content-teacher.vue';
import ContentClassTool from './tool/Content-classTool.vue';
import ContentLessonTool from './tool/Content-lessonTool.vue';
import ContentYearTool from './tool/Content-yearTool.vue';
import ContentUser from './user/Content-user.vue';
import ContentStudent from './class_room/Content-student.vue';
import ContentScheduleTool from './tool/Content-scheduleTool.vue';
import ContentScoreTool from './tool/Content-scoreTool.vue';
import ContentPeriodSummary from './class_room/Content-PeriodSummary.vue';
import ContentYearSummary from './class_room/Content-YearSummary.vue';
import ContentActivitylog from './monitoring/Content-activitylog.vue';
import ContentApproveStudent from './student/Content-approveStudent.vue';
import ContentStudentMain from './report/Content-studentMain.vue';
import ContentStudentSchedule from './report/Content-StudentSchedule.vue';
import ContentTeacherSchedule from './report/Content-TeacherSchedule.vue';
import ContentClass from './class_room/Content-class.vue';
import ContentMainSchedule from './report/Content-MainSchedule.vue';
import ContentAttendence from './class_room/Content-attendence.vue';
import Content_weakStudents from './class_room/Content_weakStudents.vue';
import ContentSummaryResult from './class_room/Content-SummaryResult.vue';
import ContentRetest from './Retest/Content-Retest.vue';
import ContentDailyReport from './report/Content-DailyReport.vue';

defineProps({
  activeComponent: {
    type: Object,
    required: true
  }
})

</script>
