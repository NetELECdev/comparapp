export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  routeRules: {
    '/': { redirect: '/intro' }
  },
  app: {
    head: {
      title: 'ComparApp - Compara y Ahorra',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' }
      ],
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' }
      ]
    }
  },
  css: [
    '~/assets/css/glass.css',
    '~/assets/css/tokens.css',
    '~/assets/css/components.css',
    '~/assets/css/animations.css'
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api/v1'
    }
  },
  nitro: {
    preset: 'static',
    devProxy: {
      '/api/': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
        prependPath: true
      }
    }
  },
  devtools: { enabled: true }
})