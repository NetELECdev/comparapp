// composables/useAuth.ts
//
// VERSIÓN DEL SCHEMA DE comparapp_user EN localStorage
// ─────────────────────────────────────────────────────
// Cada vez que cambiamos las claves o el formato del objeto guardado en
// localStorage (es_comercio_user, avatar_url, plan, etc.), incrementamos
// este número. Si el objeto guardado tiene una versión distinta a la actual,
// se considera "viejo" y se borra — el usuario tiene que volver a loguearse,
// lo que regenera el objeto con el formato correcto.
// Esto evita bugs silenciosos donde un usuario con sesión vieja ve la app
// rota en partes específicas (ej. el ícono de comercio que no aparece,
// o el avatar que no carga) porque las claves cambiaron entre versiones.
//
// CUÁNDO INCREMENTAR: cualquier vez que se agregue, cambie o elimine una
// clave del objeto guardado en login.vue o callback.vue.
// Versiones anteriores:
//   1 — formato original
//   2 — agregado es_comercio_user, comercio_verificado_user (ya no era solo 'rol')
//   3 — unificado formato entre login/email y callback/Google (mapBackendUser)
//   4 — agregado avatar_url_user, plan info
export const COMPARAPP_USER_VERSION = 4

export function clearUserSession() {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('comparapp_user')
  }
}

export function useAuth() {
  const user = computed(() => {
    if (typeof window === 'undefined') return null
    try {
      const stored = localStorage.getItem('comparapp_user')
      if (!stored) return null
      const parsed = JSON.parse(stored)
      // Si el objeto no tiene versión, o tiene una versión vieja,
      // lo descartamos — es de un formato anterior incompatible.
      if (!parsed._v || parsed._v < COMPARAPP_USER_VERSION) {
        localStorage.removeItem('comparapp_user')
        return null
      }
      return parsed
    } catch {
      return null
    }
  })

  const isAdmin = computed(() => user.value?.rol === 'admin')
  const isLoggedIn = computed(() => !!user.value)

  return { user, isAdmin, isLoggedIn }
}