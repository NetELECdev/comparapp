// composables/useFavoritos.ts
// Favoritos sincronizados con Supabase.
// Si el usuario NO está logueado, usa localStorage como fallback.

const FAVORITOS_KEY = 'comparapp_favoritos'
let _favoritos = null

export const useFavoritos = () => {
  if (!_favoritos) {
    _favoritos = ref([])
    // Cargar desde localStorage siempre al inicio (offline/fallback)
    try {
      const stored = localStorage.getItem(FAVORITOS_KEY)
      if (stored) _favoritos.value = JSON.parse(stored)
    } catch {}
  }

  const favoritos = _favoritos
  const { $fetch } = useNuxtApp()
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase || 'http://localhost:8000/api/v1'

  const getToken = () => {
    try {
      const stored = localStorage.getItem('comparapp_user')
      return stored ? JSON.parse(stored).access_token || '' : ''
    } catch { return '' }
  }

  const isLoggedIn = () => !!getToken()

  // ── Persistencia local (siempre como caché) ──────────────────────
  const saveLocal = () => {
    try { localStorage.setItem(FAVORITOS_KEY, JSON.stringify(favoritos.value)) } catch {}
  }

  // ── Cargar desde Supabase (si hay sesión) ─────────────────────────
  const cargarDesdeBackend = async () => {
    if (!isLoggedIn()) return
    try {
      const res = await fetch(`${apiBase}/favoritos`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      if (!res.ok) return
      const data = await res.json()
      favoritos.value = data.results || []
      saveLocal()
    } catch (e) {
      console.warn('useFavoritos: error cargando desde backend', e)
    }
  }

  // ── Helpers ───────────────────────────────────────────────────────
  const esFavorito = (id_prod) => {
    if (!id_prod) return false
    return favoritos.value.some(f => f.id_prod === id_prod)
  }

  // ── Toggle ────────────────────────────────────────────────────────
  const toggleFavorito = async (producto) => {
    if (!producto?.id_prod) return

    const yaEsta = esFavorito(producto.id_prod)

    // 1. Actualizar estado local inmediatamente (optimistic UI)
    if (yaEsta) {
      favoritos.value = favoritos.value.filter(f => f.id_prod !== producto.id_prod)
    } else {
      favoritos.value.push({
        id_prod: producto.id_prod,
        nombre_prod: producto.nombre_prod,
        marca_prod: producto.marca_prod,
        precio_prod: producto.precio_prod,
        cate_prod: producto.cate_prod,
        imagen_prod: producto.imagen_prod,
        provee_prod: producto.provee_prod,
      })
    }
    saveLocal()

    // 2. Sincronizar con backend si está logueado
    if (!isLoggedIn()) return

    try {
      if (yaEsta) {
        await fetch(`${apiBase}/favoritos/${producto.id_prod}`, {
          method: 'DELETE',
          headers: { Authorization: `Bearer ${getToken()}` }
        })
      } else {
        await fetch(`${apiBase}/favoritos`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${getToken()}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({ id_prod: producto.id_prod })
        })
      }
    } catch (e) {
      console.warn('useFavoritos: error sincronizando con backend', e)
      // No revertir — el local ya quedó guardado
    }
  }

  const eliminarFavorito = (id_prod) => {
    const producto = favoritos.value.find(f => f.id_prod === id_prod)
    if (producto) toggleFavorito(producto)
  }

  // Orden por nombre
  const favoritosOrdenados = computed(() =>
    [...favoritos.value].sort((a, b) =>
      (a.nombre_prod || '').localeCompare(b.nombre_prod || '', 'es')
    )
  )

  return {
    favoritos,
    favoritosOrdenados,
    esFavorito,
    toggleFavorito,
    eliminarFavorito,
    cargarDesdeBackend,
  }
}
