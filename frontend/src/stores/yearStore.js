import { defineStore } from "pinia";
import { ref } from 'vue'

export const userYearStore = defineStore('year', () => {
    const year = ref([])
    const setYear = (newYear) => {
        year.value = newYear
    }

    return {year, setYear}
}, {
    persist: true 
})