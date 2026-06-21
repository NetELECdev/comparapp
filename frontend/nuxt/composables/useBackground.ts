/**
 * composables/useBackground.ts
 * Fondo ciclico con transicion suave (fade) cada 5 minutos.
 * Respeta el tema actual (claro/oscuro) via overlay dinamico.
 */

import { useTema } from './useTema'

export interface FondoConfig {
  id: string
  tipo: 'imagen'
  valor: string
  descripcion?: string
}

// ── CONFIGURACION ────────────────────────────────────────────
const INTERVALO_MINUTOS = 5

const FONDOS_DARK: FondoConfig[] = [
  { id: 'fondo-01', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp01.jpg', descripcion: 'Fondo 1' },
  { id: 'fondo-02', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp02.jpg', descripcion: 'Fondo 2' },
  { id: 'fondo-03', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp03.jpg', descripcion: 'Fondo 3' },
  { id: 'fondo-04', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp04.jpg', descripcion: 'Fondo 4' },
  { id: 'fondo-05', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp05.jpg', descripcion: 'Fondo 5' },
  { id: 'fondo-06', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp06.jpg', descripcion: 'Fondo 6' },
  { id: 'fondo-07', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparapp07.jpg', descripcion: 'Fondo 7' },
]

const FONDOS_LIGHT: FondoConfig[] = [
  { id: 'fondo-claro-01', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/fondoClaro1.jpg', descripcion: 'Fondo Claro 1' },
  { id: 'fondo-claro-02', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/fondoClaro2.jpg', descripcion: 'Fondo Claro 2' },
  { id: 'fondo-claro-03', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/fondoClaro3.jpg', descripcion: 'Fondo Claro 3' },
  { id: 'fondo-claro-04', tipo: 'imagen', valor: 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/fondoClaro4.jpg', descripcion: 'Fondo Claro 4' },
]

// ── ESTADO GLOBAL ────────────────────────────────────────────
const indiceFondo = ref(0)
const fondoActual = ref<FondoConfig>(FONDOS_DARK[0])
const isVisible = ref(true)
let intervaloId: ReturnType<typeof setInterval> | null = null
let instancias = 0

export function useBackground() {
  const { esDark } = useTema()

  // Lista activa según tema
  const fondosActivos = computed(() => esDark.value ? FONDOS_DARK : FONDOS_LIGHT)

  // Cuando cambia el tema, reiniciar al primer fondo del nuevo set
  watch(esDark, (isDark) => {
    indiceFondo.value = 0
    fondoActual.value = isDark ? FONDOS_DARK[0] : FONDOS_LIGHT[0]
  })

  const overlayClass = computed(() =>
    esDark.value ? 'bg-black/40' : 'bg-white/25'
  )

  function iniciarCiclo() {
    if (intervaloId) return
    const ms = INTERVALO_MINUTOS * 60 * 1000
    intervaloId = setInterval(siguienteFondo, ms)
  }

  function detenerCiclo() {
    if (intervaloId) {
      clearInterval(intervaloId)
      intervaloId = null
    }
  }

  function siguienteFondo() {
    isVisible.value = false
    setTimeout(() => {
      const lista = fondosActivos.value
      indiceFondo.value = (indiceFondo.value + 1) % lista.length
      fondoActual.value = lista[indiceFondo.value]
      isVisible.value = true
    }, 700)
  }

  function irAFondo(indice: number) {
    const lista = fondosActivos.value
    if (indice < 0 || indice >= lista.length) return
    isVisible.value = false
    setTimeout(() => {
      indiceFondo.value = indice
      fondoActual.value = lista[indice]
      isVisible.value = true
    }, 700)
  }

  onMounted(() => {
    instancias++
    if (instancias === 1) iniciarCiclo()
  })

  onUnmounted(() => {
    instancias--
    if (instancias === 0) detenerCiclo()
  })

  return {
    fondos: readonly(fondosActivos),
    fondoActual: readonly(fondoActual),
    indiceFondo: readonly(indiceFondo),
    isVisible,
    overlayClass,
    siguienteFondo,
    irAFondo,
  }
}