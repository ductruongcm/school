// lưu user_info
import {defineStore} from 'pinia'
import { ref } from 'vue'


export const useUserStore = defineStore('user', () => {
    const userInfo = ref([])
    const setUserInfo = (info) => {
        userInfo.value = info
    }
    
    const clearUser = () => {
        userInfo.value = null
    }

    return {userInfo, setUserInfo, clearUser}
},{
    persist: true
})