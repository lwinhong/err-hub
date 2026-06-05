import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://10.1.32.245:8888/',
        changeOrigin: true,
      }
    }
  }
})
