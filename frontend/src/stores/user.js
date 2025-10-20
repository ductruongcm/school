// lưu user_info
import {defineStore} from 'pinia'

// Tạo 1 store tên là user để chứa user_info
const useUserStore = defineStore('user', {
    // state để định nghĩa trước 
    state: () => ({
        userInfo: null,
        isAuthentincated: false
    }),
    // action chứa hành động lấy user_info và lưu về định nghĩa ở state
    actions: {
        setUserInfo(info) {
            this.userInfo = info
            this.isAuthentincated = true
        },

        clearUser() {
            this.userInfo = null,
            this.isAuthentincated = false
        }
    },
    persist: true
})
export default useUserStore

