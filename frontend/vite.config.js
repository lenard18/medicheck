import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  // sockjs-client usa `global` de Node — lo mapeamos a globalThis para el browser
  define: {
    global: 'globalThis',
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  preview: {
    port: parseInt(process.env.PORT) || 4173,
    host: true,
    allowedHosts: true,
  },
  server: {
    port: parseInt(process.env.PORT) || 5173,
    host: true,
    allowedHosts: true,
    // ── HMR en puerto propio para no colisionar con los proxies WS ──────────
    hmr: {
      protocol: 'ws',
      host: 'localhost',
      port: 5173,
      path: '/__vite_hmr'        // ruta distinta a /ws y /ws-stomp
    },
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true
      },
      '/ws': {
        target: 'ws://localhost:8080',
        ws: true,
        changeOrigin: true
      },
      '/ws-stomp': {
        target: 'http://localhost:8080',
        ws: true,
        changeOrigin: true
      }
    }
  }
})