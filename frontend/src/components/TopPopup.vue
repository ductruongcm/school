<template>
  <transition name="slide-down">
    <div
      v-if="visible"
      class="fixed top-0 left-0 w-full bg-red-500 text-white text-center p-3 z-50 shadow-md"
    >
      <span>{{ message }}</span>
      <button class="ml-4 underline" @click="visible = false">Đóng</button>
    </div>
  </transition>
</template>

<script setup>
import { visible, message } from '../stores/usePopup'
</script>
