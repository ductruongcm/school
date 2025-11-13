import { defineStore } from "pinia";
import { ref } from "vue";

export const useSemesterStore = defineStore('semester', () => {
    const semester = ref([])
    const setSemester = (newSemester) => {
        semester.value = newSemester
    }
    return {semester, setSemester}
}, {
    persist: true 
})