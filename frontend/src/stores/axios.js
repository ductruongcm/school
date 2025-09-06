import { showPopup } from '../stores/usePopup'
import axios from 'axios'

axios.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 429) {
      const retryAfter = err.response.headers['retry-after'] || 60
      showPopup(`Bạn thao tác quá nhanh. Thử lại sau ${retryAfter} giây.`)
    }
    return Promise.reject(err)
  }
)

export default {showPopup}