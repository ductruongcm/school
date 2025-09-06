<template>
    <component :is="activeComponent" />
</template>

<script setup>
import ContentClass from '../components/Content-class.vue';
import ContentReport from '../components/Content-report.vue';
import ContentStudent from '../components/Content-student.vue';
import ContentTeacher from '../components/Content-teacher.vue';
import ContentToolClass from '../components/Content-toolClass.vue';
import ContentToolInfo from '../components/Content-toolInfo.vue';
import ContentToolStudent from '../components/Content-toolStudent.vue';
import ContentToolTeacher from '../components/Content-toolTeacher.vue';


const props = defineProps({
    activeComponent: {
        type: Object,
        default: () => ContentClass
    }
})

</script>