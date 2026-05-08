// nuxt.config.ts
export default defineNuxtConfig({
  compatibilityDate: '2026-05-03',

  routeRules: {
    '/': { redirect: '/intro' }
  },

  // Fuentes: Inter (principal) + fallback del sistema
  app: {
    head: {
      link: [
        {
          rel: 'preconnect',
          href: 'https://fonts.googleapis.com'
        },
        {
          rel: 'preconnect',
          href: 'https://fonts.gstatic.com',
          crossorigin: ''
        },
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
        }
      ]
    }
  },

  // CSS global: glass original + nuevo design system
  css: [
    '~/assets/css/glass.css',
    '~/assets/css/tokens.css',
    '~/assets/css/components.css',
    '~/assets/css/animations.css'
  ],

  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  },

  nitro: {
    devProxy: {
      '/api/': {
        target: 'http://localhost:8000/',
        changeOrigin: true,
      },
    },
  },
})