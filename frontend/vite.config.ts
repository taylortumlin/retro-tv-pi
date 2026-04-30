import { defineConfig } from 'vite'
import { svelte } from '@sveltejs/vite-plugin-svelte'

export default defineConfig({
  plugins: [svelte()],
  base: '/static/dist/',
  build: {
    outDir: '../static/dist',
    emptyOutDir: true,
    target: 'es2020',
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes('mpegts.js')) return 'mpegts';
        }
      }
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': 'http://localhost:5001',
      '/admin/api': 'http://localhost:5001',
      '/stream': 'http://localhost:5001',
      '/static/Media': 'http://localhost:5001',
      '/static/logos': 'http://localhost:5001',
    }
  }
})
