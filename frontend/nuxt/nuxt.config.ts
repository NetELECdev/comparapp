export default defineNuxtConfig({
  compatibilityDate: '2024-04-03',
  modules: ['@vite-pwa/nuxt'],
  routeRules: {
    '/': { redirect: '/intro' }
  },
  app: {
    head: {
      title: 'ComparApp - Compara y Ahorra',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        // OG por defecto (las páginas de comercio lo pisan con su propio contenido)
        { property: 'og:site_name', content: 'ComparApp' },
        { property: 'og:type', content: 'website' },
        { property: 'og:title', content: 'ComparApp - Compara y Ahorra' },
        { property: 'og:description', content: 'Compará precios de tus comercios y ahorrá en cada compra.' },
        { name: 'twitter:card', content: 'summary' }
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
    '~/assets/css/components.css'
  ],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api/v1'
    }
  },
  nitro: {
    preset: 'static',
    prerender: {
      crawlLinks: false,
      routes: ['/'],
      ignore: ['/terms', '/components']
    },
    devProxy: {
      '/api/': {
        target: 'http://localhost:8000/api/v1',
        changeOrigin: true,
        prependPath: true
      }
    }
  },
  // En el build de producción, trae la lista de comercios y agrega una ruta
  // /c/{id_comer} por cada uno, para que cada página de comercio se prerenderice
  // con su propio OG (tarjeta linda al compartir en WhatsApp/Facebook).
  // Requiere que NUXT_PUBLIC_API_BASE apunte al backend de Render en Netlify.
  hooks: {
    async 'nitro:config'(nitroConfig) {
      if (nitroConfig.dev) return
      try {
        const apiBase = process.env.NUXT_PUBLIC_API_BASE ?? 'http://localhost:8000/api/v1'
        const res = await fetch(`${apiBase}/comercios`)
        const data = await res.json()
        const rutas = (data.results || [])
          .filter((c) => c && c.id_comer)
          .map((c) => `/c/${c.id_comer}`)
        nitroConfig.prerender = nitroConfig.prerender || {}
        nitroConfig.prerender.routes = [...(nitroConfig.prerender.routes || []), ...rutas]
        console.log(`[prerender] ${rutas.length} páginas de comercio agregadas`)
      } catch (e) {
        console.warn('[prerender] no se pudieron traer los comercios:', e?.message || e)
      }
    }
  },
  pwa: {
    registerType: 'autoUpdate',
    manifest: {
      name: 'ComparApp - Compara y Ahorra',
      short_name: 'ComparApp',
      description: 'Compará precios de tus comercios locales y ahorrá en cada compra.',
      lang: 'es-AR',
      theme_color: '#182E1B',
      background_color: '#182E1B',
      display: 'standalone',
      orientation: 'portrait',
      start_url: '/dashboard',
      icons: [
        { src: '/pwa-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'any' },
        { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any' },
        { src: '/pwa-maskable-192x192.png', sizes: '192x192', type: 'image/png', purpose: 'maskable' },
        { src: '/pwa-maskable-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'maskable' },
        { src: '/pwa-512x512.png', sizes: '512x512', type: 'image/png', purpose: 'any maskable' }
      ]
    },
    workbox: {
      navigateFallback: undefined,
      globPatterns: ['**/*.{js,css,html,png,svg,ico,woff2}']
    },
    client: {
      installPrompt: true
    },
    devOptions: {
      enabled: true,
      type: 'module'
    }
  },
  devtools: { enabled: true }
})
