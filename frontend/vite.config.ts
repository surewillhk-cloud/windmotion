import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiBase = env.VITE_API_BASE || 'http://localhost:8000'

  return {
    plugins: [vue()],
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: apiBase,
          changeOrigin: true,
        },
        '/ws': {
          target: apiBase.replace('http', 'ws'),
          ws: true,
        },
      },
    },
    build: {
      outDir: 'dist',
      sourcemap: false,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor-vue': ['vue', 'vue-router', 'pinia', 'vue-i18n'],
            'vendor-d3': ['d3'],
            'vendor-echarts': ['echarts'],
          },
        },
      },
    },
  }
})
