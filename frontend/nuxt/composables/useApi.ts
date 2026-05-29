// composables/useApi.ts
export const useApi = () => {
  const config = useRuntimeConfig()
  const apiUrl = config.public.apiBase || 'http://localhost:8000/api/v1'

  const api = async <T = any>(
    endpoint: string,
    options: any = {}
  ): Promise<T> => {
    // Leer token del localStorage (guardado por login.vue)
    let token = ''
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem('comparapp_user')
        if (stored) {
          const userData = JSON.parse(stored)
          token = userData.access_token || ''
        }
      } catch {}
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...options.headers
    }

    if (token) {
      headers['Authorization'] = `Bearer ${token}`
    }

    const path = endpoint.startsWith('/') ? endpoint : '/' + endpoint
    const url = `${apiUrl}${path}`

    return $fetch<T>(url, {
      ...options,
      headers
    })
  }

  return { api, apiUrl }
}