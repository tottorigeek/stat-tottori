import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  server: {
    port: 3000,
    open: true,
    host: true, // すべてのネットワークインターフェースでリッスン
    hmr: {
      port: 3000, // HMRポートを明示的に設定
      overlay: false // エラーオーバーレイを無効化
    }
  },
  build: {
    outDir: 'dist',
    assetsDir: 'assets'
  }
})
