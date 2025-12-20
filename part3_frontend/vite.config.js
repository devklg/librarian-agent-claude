import react from '@vitejs/plugin-react'

export default {
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 3000,
    strictPort: true,
    proxy: {
      '/api': 'http://localhost:9600',
      '/ws': {
        target: 'ws://localhost:9600',
        ws: true
      }
    }
  }
}
