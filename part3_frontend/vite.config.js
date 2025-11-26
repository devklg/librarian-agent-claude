import react from '@vitejs/plugin-react'

export default {
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': 'http://localhost:9600',
      '/ws': {
        target: 'ws://localhost:9600',
        ws: true
      }
    }
  }
}
