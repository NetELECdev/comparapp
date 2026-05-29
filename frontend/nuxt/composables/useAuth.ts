// composables/useAuth.ts
export function useAuth() {
  const user = computed(() => {
    if (typeof window === 'undefined') return null
    try {
      const stored = localStorage.getItem('comparapp_user')
      return stored ? JSON.parse(stored) : null
    } catch {
      return null
    }
  })

  const isAdmin = computed(() => user.value?.rol === 'admin')
  const isLoggedIn = computed(() => !!user.value)

  return { user, isAdmin, isLoggedIn }
}