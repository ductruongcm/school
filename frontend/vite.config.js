import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig(({ mode }) => {
  // Load các biến môi trường dựa trên 'mode' (development, production, v.v.)
  // tham số thứ hai là đường dẫn đến thư mục chứa file .env (thường là root: process.cwd())
  const env = loadEnv(mode, process.cwd())

  return {
    plugins: [vue()],
    server: {
      host: true,
      port: 5173,
      proxy: {
        '/api': {
          // Sử dụng env.VITE_... thay vì import.meta.env
          target: env.VITE_API_PROXY || 'http://localhost:5000',
          changeOrigin: true
        }
      }
    }
  }
})