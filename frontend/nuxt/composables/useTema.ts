/**
 * composables/useTema.ts
 * Manejo de tema claro/oscuro con persistencia en localStorage.
 * Uso: const { tema, esDark, toggleTema } = useTema()
 */

type Tema = 'dark' | 'light'

const STORAGE_KEY = 'comparapp_tema'

// Estado global compartido entre todas las páginas
const tema = ref<Tema>('dark')
const iniciado = ref(false)

export function useTema() {
  function aplicarTema(t: Tema) {
    tema.value = t
    if (import.meta.client) {
      document.documentElement.setAttribute('data-tema', t)
      localStorage.setItem(STORAGE_KEY, t)
    }
  }

  function inicializar() {
    if (iniciado.value || !import.meta.client) return
    iniciado.value = true

    // Preferencia guardada → preferencia del sistema → dark por defecto
    const guardado = localStorage.getItem(STORAGE_KEY) as Tema | null
    if (guardado === 'light' || guardado === 'dark') {
      aplicarTema(guardado)
    } else if (window.matchMedia('(prefers-color-scheme: light)').matches) {
      aplicarTema('light')
    } else {
      aplicarTema('dark')
    }
  }

  function toggleTema() {
    aplicarTema(tema.value === 'dark' ? 'light' : 'dark')
  }

  function setTema(t: Tema) {
    aplicarTema(t)
  }

  const esDark = computed(() => tema.value === 'dark')

  // Inicializar al montar si no se hizo antes
  onMounted(() => inicializar())

  return { tema, esDark, toggleTema, setTema, inicializar }
}