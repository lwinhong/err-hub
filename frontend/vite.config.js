import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  base: "./",
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    chunkSizeWarningLimit: 4096,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules')) {
            const parts = id.toString().split('node_modules/');
            const packageName = parts[parts.length - 1].split('/')[0];
            return packageName;
          }
        },
      }
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://10.1.32.245:8888/',
        changeOrigin: true,
      }
    }
  }
})
