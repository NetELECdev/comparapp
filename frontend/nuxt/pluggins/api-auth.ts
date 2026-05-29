// plugins/api-auth.ts
export default defineNuxtPlugin(() => {
  const supabase = useSupabaseClient()
  const config = useRuntimeConfig()

  // Interceptar TODAS las peticiones $fetch del lado del cliente
  const originalFetch = $fetch.create({})

  globalThis.$fetch = $fetch.create({
    async onRequest({ options }) {
      const apiUrl = config.public.apiBaseUrl

      // Solo interceptar peticiones a tu backend FastAPI
      const targetUrl = options.baseURL || ''
      const isApiCall = targetUrl.includes('localhost:8000') ||
                        targetUrl.includes('/api/') ||
                        targetUrl === ''  // URLs relativas como /api/v1/products

      if (isApiCall) {
        const { data: { session } } = await supabase.auth.getSession()

        if (session?.access_token) {
          options.headers = {
            ...options.headers,
            'Authorization': `Bearer ${session.access_token}`
          }
        }
      }
    }
  })
})