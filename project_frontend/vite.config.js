import { fileURLToPath, URL } from 'node:url'
import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  
  return {
    plugins: [
      vue(),
      vueDevTools(),
      {
        name: 'html-transform',
        transformIndexHtml(html) {
          return html.replace(
            /<%= VITE_KAKAO_MAP_API_KEY %>/g,
            env.VITE_KAKAO_MAP_API_KEY || ''
          )
        }
      }
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      },
    },
    define: {
      'process.env.VITE_KAKAO_MAP_API_KEY': JSON.stringify(env.VITE_KAKAO_MAP_API_KEY)
    }
  }
})
