export default defineNuxtConfig({
  ssr: true,
  css: ['~/assets/styles/main.styl'],
  runtimeConfig: {
    public: {
      apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000'
    }
  },
  vite: {
    css: {
      preprocessorOptions: {
        styl: {}
      }
    }
  }
})
