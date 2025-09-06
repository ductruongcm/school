// usePopup.js
import { ref } from 'vue'

const visible = ref(false)
const message = ref('')

function showPopup(msg, duration = 5000) {
  message.value = msg
  visible.value = true
  if (duration > 0) {
    setTimeout(() => (visible.value = false), duration)
  }
}

export { visible, message, showPopup }
