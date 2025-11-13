<template>
  <transition name="fade">
    <div v-if="visible" class="backdrop" @click.self="close">
      <div class="popup">
        <h3>Điều chỉnh thông tin giáo viên</h3>
        <label>Họ và tên: </label>
        <input style="width: 10em;" v-model="data.name" type="text"/>
 
        <label> Email: </label>
        <input style="width: 20.7em;" v-model="data.email" type="text"> <br>
        <label> Số điện thoại: </label>
        <input style="width: 8em;" v-model="data.tel" type="text">
        <label> Địa chỉ: </label>
        <input style="width: 20em;" v-model="data.add" type="text"> <br>
        <label> Chuyên môn: </label>
        <select v-model="data.lesson_id" @change="fetchTeachClassData">
            <option disabled>--Chọn môn học--</option>
            <option v-for="lesson in lessonList" :key="lesson.lesson_id" :value="lesson.lesson_id">{{ lesson.lesson }}</option>
        </select>
        <label> Chủ nhiệm lớp: </label>
        <select v-model="data.class_room_id">
            <option :value='null' disabled>--Chọn lớp--</option>
            <option :value="null">Bỏ chọn</option>
            <option v-for="cls in homeClassList" :key="cls.class_room_id" :value="cls.class_room_id">{{ cls.class_room }}</option>
        </select> <br>
        <label>Phụ trách lớp </label> <br>
        <div style="display: flex; gap: 20px">
            <!-- Bảng trái -->
            <div>
                <div>Chọn lớp học</div>
                <ul>
                    <li v-for="teachRoom in leftList" :key="teachRoom.id" :value="teachRoom.id">
                        <input type="checkbox" :value="teachRoom" v-model="selectedLeft" /> {{ teachRoom.class_room }}
                    </li>
                </ul>
            </div>

            <!-- Nút chuyển -->
            <div style="display: flex; flex-direction: column; justify-content: center; gap: 10px">
                <button @click.prevent="addToRight">→</button>
                <button @click.prevent="removeFromRight">←</button>
            </div>

            <!-- Bảng phải -->
            <div>
                <div>Lớp đã chọn</div>
                <ul>
                    <li v-for="item in rightList" :key="item.id">
                        <input type="checkbox" :value="item" v-model="selectedRight" /> {{ item.class_room }}
                    </li>
                </ul>
            </div>
        </div> 
        <div>{{ resultMsg }}</div>
        <div class="actions">
          <button @click="status">Hiện/Ẩn</button>
          <button @click="save">Lưu</button>
          <button @click="close">Đóng</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, toRaw } from 'vue'
import axios from 'axios'
import { userYearStore } from '../../stores/yearStore'

const yearStore = userYearStore()

const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  visible: Boolean // nhận prop từ cha
})
const emit = defineEmits(['update:visible', 'save'])

function close() {
  emit('update:visible', false)
}

onMounted(() => {
  fetchLessonData()
  fetchClassList()
  fetchTeachClassData()
})

const original = JSON.parse(JSON.stringify(props.data))

const lessonSearch = ref('')
const selectedGrade = ref('')
const lessonList = ref(null)
const fetchLessonData = async () => {
  const res = await axios.get('api/academic/me/lessons', {
        params: {
            lesson: lessonSearch.value,
            grade: selectedGrade.value,
            is_visible: true,
            is_schedule: false,
            is_folder: false
        },
        withCredentials: true
    })
    lessonList.value = res.data.data
}

const homeClassList = ref(null)
const class_roomSearch = ref('')
const fetchClassList = async () => {
  const res = await axios.get(`api/academic/years/${yearStore.year.id}/class-rooms`, {
    withCredentials: true,
    params: {
      grade: selectedGrade.value,
      class_room: class_roomSearch.value
    }
  })
  homeClassList.value = res.data.data
}

const selectedLeft = ref([])
const selectedRight = ref([])
const rightList = ref([])
const leftList = ref([])
const newIds = ref([])
const addToRight = () => {
  rightList.value.push(...selectedLeft.value)
  rightList.value.sort((a, b) => a.class_room.localeCompare(b.class_room))
  newIds.value.push(...selectedLeft.value.map(i => i.class_room_id))
  leftList.value = leftList.value.filter(item => !selectedLeft.value.includes(item))
  selectedLeft.value = []
}

const removeFromRight = () => {
  leftList.value.push(...selectedRight.value)
  leftList.value.sort((a, b) => a.class_room.localeCompare(b.class_room))
  const idsToRemove = selectedRight.value.map(i => i.class_room_id)
  newIds.value = newIds.value.filter(id => !idsToRemove.includes(id))
  rightList.value = rightList.value.filter(item => !selectedRight.value.includes(item))
  selectedRight.value = []
}

const teachClassList = ref([])
const fetchTeachClassData = async () => {
  const res = await axios.get(`api/academic/lessons/${props.data.lesson_id}/class-rooms`, {
    withCredentials: true,
    params: {
      year_id: yearStore.year.id,
      teacher_id: props.data.id
    }
  })
  teachClassList.value = res.data.data
  leftList.value = teachClassList.value.filter(item => item.teacher_id === null)
  if (props.data.lesson_id === original.lesson_id) {
    rightList.value = teachClassList.value.filter(item => props.data.teach_room_ids.includes(item.class_room_id))
  } else {
    rightList.value = []
  }
  newIds.value = rightList.value.map(i => i.class_room_id)
}

const status = async () => {
    const res = await axios.put(`api/teachers/${props.data.id}/status`, {
        withCredentials: true
    })
    resultMsg.value = res.data.msg
    emit('save', resultMsg.value)
    close()
}

const resultMsg = ref('')

const data = toRaw(props.data)
const save = async () => {
  const changedEntries = Object.entries(data)
    .filter(([k, v]) => v !== original[k]).filter(Boolean) // chỉ lấy field bị thay đổi

  if (changedEntries.length === 0) return null;

  const payload = {
    ...Object.fromEntries(changedEntries), 
    year_id: yearStore.year.id,
    lesson_id: data.lesson_id,
    teach_class: newIds.value
    }

  if (Object.keys(payload).length > 0) {
    try {
      const res = await axios.put(`api/teachers/${props.data.id}`, payload, {
        withCredentials: true
      })
      resultMsg.value = res.data.msg
      emit('save', resultMsg.value)
      close()

    } catch (err) {
      if (err.response && [400, 404, 409, 422, 500].includes(err.response.status)) {
          resultMsg.value = err.response.data.msg
      } else {
        resultMsg.value = 'Có vấn đề khác!'
      }    
    }
  } else {
    close()
  }
}









</script>

<style scoped>
.backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: grid;
  place-items: center;
  z-index: 999;
}
.popup {
  background: rgb(0, 0, 0);
  padding: 1rem;
  border-radius: 8px;
  width: 700px;
}
.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
