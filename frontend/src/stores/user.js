// lưu user_info
import {defineStore} from 'pinia'
import axios from 'axios'


// Tạo 1 store tên là user để chứa user_info
export const useUserStore = defineStore('user', {
    // state để định nghĩa trước 
    state: () => ({
        info: null
    }),
    // action chứa hành động lấy user_info và lưu về định nghĩa ở state
    actions: {
        async fetchUser() {
            // có user_info rồi thì trả user_info và ko làm gì nữa
            if (this.info) return this.info
            try {
                const tokenInfo = await axios.get("api/auth/user_info", { withCredentials:true })
                this.info = tokenInfo.data
                return this.info
            } catch {
                try {
                    const refreshInfo = await axios.get("api/auth/refresh_token", { withCredentials: true})
                    this.info = refreshInfo.data
                    return this.info
                } catch (errs) {
                    this.info = null
                }
            }
        }      
    }
})