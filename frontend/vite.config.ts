import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/VoxPrivacyRecord.github.io/', // GitHub Pages base path
  server: {
    port: 5173,
  },
})

