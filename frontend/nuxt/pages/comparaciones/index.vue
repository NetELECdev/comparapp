<template>
  <div class="comparaciones-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-top">
          <button class="back-btn" @click="volver()">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div class="header-text">
            <h1 class="page-title">Comparación</h1>
            <p class="page-subtitle">{{ productos.length }} productos seleccionados</p>
          </div>
        </div>
      </header>

      <!-- RESUMEN -->
      <div v-if="productos.length > 0" class="resumen-card animate-fade-in-up stagger-1">
        <div class="resumen-row">
          <div class="resumen-item">
            <span class="resumen-label">Productos</span>
            <span class="resumen-value">{{ totalItems }}</span>
          </div>
          <div class="resumen-divider" />
          <div class="resumen-item">
            <span class="resumen-label">Total estimado</span>
            <span class="resumen-value resumen-total">${{ formatPrice(totalPrecio) }}</span>
          </div>
          <div class="resumen-divider" />
          <div class="resumen-item">
            <span class="resumen-label">Comercios</span>
            <span class="resumen-value">{{ comerciosUnicos }}</span>
          </div>
        </div>
      </div>

      <!-- SORT BAR -->
      <div v-if="productos.length > 0" class="sort-bar animate-fade-in-up stagger-1">
        <div class="sort-label">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 16 4 4 4-4"/><path d="M7 20V4"/><path d="M11 4h10"/><path d="M11 8h7"/><path d="M11 12h4"/>
          </svg>
          Ordenar
        </div>
        <div class="sort-chips">
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            class="sort-chip"
            :class="{ active: sortBy === opt.value }"
            @click="sortBy = opt.value"
          >{{ opt.label }}</button>
        </div>
      </div>

      <!-- LISTA DE PRODUCTOS A COMPARAR -->
      <div v-if="productos.length > 0" class="comparacion-lista">

        <!-- Vista agrupada por comercio -->
        <template v-if="sortBy === 'comercio'">
          <div
            v-for="(grupo, comercio) in productosAgrupadosPorComercio"
            :key="comercio"
            class="comercio-grupo animate-fade-in-up"
          >
            <div class="comercio-header">
              <div class="comercio-badge">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9 22 9 12 15 12 15 22"/>
                </svg>
                {{ comercio }}
              </div>
              <span class="comercio-subtotal">${{ formatPrice(grupo.reduce((s, p) => s + Number(p.precio_prod) * p.cantidad, 0)) }}</span>
            </div>
            <div class="comercio-items">
              <div
                v-for="prod in grupo"
                :key="prod.id_prod"
                class="comparacion-item"
              >
                <div class="item-img">
                  <img :src="prod.imagen_prod || '/images/avatar_default.png'" :alt="prod.nombre_prod" />
                </div>
                <div class="item-info">
                  <h4 class="item-name">{{ prod.nombre_prod }}</h4>
                  <p class="item-brand">{{ prod.marca_prod }}</p>
                  <div class="item-qty">Cantidad: {{ prod.cantidad }}</div>
                </div>
                <div class="item-price-col">
                  <span class="item-unit">${{ formatPrice(Number(prod.precio_prod)) }}</span>
                  <span class="item-total">${{ formatPrice(Number(prod.precio_prod) * prod.cantidad) }}</span>
                  <span v-if="formatPrecioNorm(prod)" class="item-precio-norm">
                    {{ formatPrecioNorm(prod) }}
                  </span>
                </div>
                <button class="item-remove" @click="removerProducto(prod.id_prod)" aria-label="Quitar">
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                  </svg>
                </button>
              </div>
            </div>
          </div>
        </template>

        <!-- Vista lista ordenada (precio o nombre) -->
        <template v-else>
          <div
            v-for="(prod, index) in productosOrdenados"
            :key="prod.id_prod"
            class="comparacion-item animate-fade-in-up"
            :class="`stagger-${Math.min(index + 2, 8)}`"
          >
            <div class="item-img">
              <img :src="prod.imagen_prod || '/images/avatar_default.png'" :alt="prod.nombre_prod" />
            </div>
            <div class="item-info">
              <h4 class="item-name">{{ prod.nombre_prod }}</h4>
              <p class="item-brand">{{ prod.marca_prod }}</p>
              <p class="item-venue">{{ prod.comercio_prod }}</p>
              <div class="item-qty">Cantidad: {{ prod.cantidad }}</div>
              <div class="item-fecha-distancia">
                <div v-if="prod.fecha_prod" class="item-fecha">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></svg>
                  {{ formatFecha(prod.fecha_prod) }}
                </div>
                <div v-if="distanciasPorComercio[prod.comercio_prod]" class="item-distancia">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7Z"/><circle cx="12" cy="9" r="2.5"/></svg>
                  {{ distanciasPorComercio[prod.comercio_prod] }}
                </div>
              </div>
            </div>
            <div class="item-price-col">
              <span class="item-unit">${{ formatPrice(Number(prod.precio_prod)) }}</span>
              <span class="item-total">${{ formatPrice(Number(prod.precio_prod) * prod.cantidad) }}</span>
              <span v-if="formatPrecioNorm(prod)" class="item-precio-norm">
                {{ formatPrecioNorm(prod) }}
              </span>
            </div>
            <button class="item-remove" @click="removerProducto(prod.id_prod)" aria-label="Quitar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>
        </template>
      </div>

      <!-- ACCIONES -->
      <div v-if="productos.length > 0" class="acciones animate-fade-in-up stagger-5">
        <button class="btn-guardar" @click="guardarComparacion">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
            <polyline points="17 21 17 13 7 13 7 21"/>
            <polyline points="7 3 7 8 15 8"/>
          </svg>
          Guardar comparación
        </button>
        <button class="btn-limpiar" @click="limpiarTodo">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 6h18"/>
            <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
            <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
          </svg>
          Limpiar todo
        </button>
      </div>

      <!-- EMPTY STATE -->
      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 6h18"/>
            <path d="M7 12h10"/>
            <path d="M10 18h4"/>
          </svg>
        </div>
        <h3>No hay productos para comparar</h3>
        <p>Agregá productos desde la lista para empezar</p>
        <button class="empty-btn" @click="volver()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="m12 5 7 7-7 7"/>
          </svg>
          Ir a productos
        </button>
      </div>

      <!-- HISTORIAL RÁPIDO -->
      <div v-if="historial.length > 0" class="historial-section animate-fade-in-up stagger-6">
        <h3 class="section-title">Comparaciones recientes</h3>
        <div class="historial-list">
          <div
            v-for="h in historial.slice(0, 3)"
            :key="h.id"
            class="historial-item"
            @click="recargarHistorial(h)"
          >
            <div class="historial-info">
              <span class="historial-fecha">{{ formatFecha(h.fecha) }}</span>
              <span class="historial-count">{{ h.totalProductos }} productos</span>
            </div>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m9 18 6-6-6-6"/>
            </svg>
          </div>
        </div>
        <NuxtLink to="/comparaciones/historial" class="ver-historial">
          Ver historial completo
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="m12 5 7 7-7 7"/>
          </svg>
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo, useRouter } from '#app'

const { volver } = useVolver('/dashboard')

interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  cate_prod: string
  imagen_prod: string | null
  comercio_prod: string
  cantidad: number
  fecha_prod?: string
  cantidad_prod?: number
  unidad_prod?: string
}

interface HistorialItem {
  id: string
  fecha: string
  productos: Producto[]
  totalProductos: number
}

const productos = ref<Producto[]>([])
const historial = ref<HistorialItem[]>([])
const sortBy = ref('default')

// Ubicación del usuario y distancias a comercios
const userLat = ref<number | null>(null)
const userLng = ref<number | null>(null)
const distanciasPorComercio = ref<Record<string, string>>({})

function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2)**2 + Math.cos(lat1 * Math.PI/180) * Math.cos(lat2 * Math.PI/180) * Math.sin(dLng/2)**2
  return R * 2 * Math.asin(Math.sqrt(a))
}

function formatDistancia(km: number): string {
  return km < 1 ? `${(km * 1000).toFixed(0)} m` : `${km.toFixed(1)} km`
}

async function cargarDistancias() {
  if (!navigator.geolocation) return
  navigator.geolocation.getCurrentPosition(async (pos) => {
    userLat.value = pos.coords.latitude
    userLng.value = pos.coords.longitude
    try {
      const config = useRuntimeConfig()
      const res = await $fetch<{ results: any[] }>(`${config.public.apiBase}/comercios`)
      const map: Record<string, string> = {}
      for (const prov of (res.results || [])) {
        if (prov.lat && prov.lng && userLat.value && userLng.value) {
          const km = haversine(userLat.value, userLng.value, prov.lat, prov.lng)
          map[prov.nombre_comer] = formatDistancia(km)
        }
      }
      distanciasPorComercio.value = map
    } catch {}
  }, () => {}, { timeout: 5000 })
}

const sortOptions = [
  { label: 'Precio/Unidad', value: 'precio_unidad' },
  { label: 'Precio ↑', value: 'precio_asc' },
  { label: 'Precio ↓', value: 'precio_desc' },
  { label: 'Comercio', value: 'comercio' },
  { label: 'Fecha', value: 'fecha' },
]

const productosOrdenados = computed(() => {
  const arr = [...productos.value]
  switch (sortBy.value) {
    case 'precio_unidad':
      return arr.sort((a, b) => {
        const normA = precioNormalizado(a)
        const normB = precioNormalizado(b)
        // Productos sin precio normalizado van al final
        if (!normA && !normB) return 0
        if (!normA) return 1
        if (!normB) return -1
        // Solo comparar si son del mismo grupo de unidad
        if (normA.unidad !== normB.unidad) return normA.unidad.localeCompare(normB.unidad)
        return normA.precio - normB.precio
      })
    case 'precio_asc':
      return arr.sort((a, b) => Number(a.precio_prod) - Number(b.precio_prod))
    case 'precio_desc':
      return arr.sort((a, b) => Number(b.precio_prod) - Number(a.precio_prod))
    case 'fecha':
      return arr.sort((a, b) => {
        const dateA = a.fecha_prod ? new Date(a.fecha_prod).getTime() : 0
        const dateB = b.fecha_prod ? new Date(b.fecha_prod).getTime() : 0
        return dateB - dateA  // más reciente primero
      })
    default:
      return arr
  }
})

const productosAgrupadosPorComercio = computed(() => {
  const grupos: Record<string, Producto[]> = {}
  for (const p of productos.value) {
    const key = p.comercio_prod || 'Sin comercio'
    if (!grupos[key]) grupos[key] = []
    grupos[key].push(p)
  }
  // Ordenar grupos por nombre de comercio
  return Object.fromEntries(
    Object.entries(grupos).sort(([a], [b]) => a.localeCompare(b, 'es'))
  )
})

const totalItems = computed(() => productos.value.reduce((sum, p) => sum + p.cantidad, 0))

const totalPrecio = computed(() => {
  return productos.value.reduce((sum, p) => sum + (Number(p.precio_prod) * p.cantidad), 0)
})

const comerciosUnicos = computed(() => {
  return new Set(productos.value.map(p => p.comercio_prod)).size
})

onMounted(() => {
  cargarDistancias()
  const stored = localStorage.getItem('comparapp_comparacion')
  if (stored) {
    try { productos.value = JSON.parse(stored) } catch {}
  }

  const storedHist = localStorage.getItem('comparapp_historial')
  if (storedHist) {
    try { historial.value = JSON.parse(storedHist) } catch {}
  }
})

// ── Precio por unidad normalizada ──────────────────────────────
const GRUPOS_UNIDAD: Record<string, { base: string; factor: number }> = {
  'Kilogramo': { base: 'kg', factor: 1 },
  'Gramo':     { base: 'kg', factor: 0.001 },
  'Litro':     { base: 'L',  factor: 1 },
  'Mililitro': { base: 'L',  factor: 0.001 },
  'CC':        { base: 'L',  factor: 0.001 },
  'Metro':     { base: 'm',  factor: 1 },
  'Centímetro':{ base: 'm',  factor: 0.01 },
}

function precioNormalizado(prod: Producto): { precio: number; unidad: string } | null {
  const unidad = prod.unidad_prod || ''
  const cantidad = Number(prod.cantidad_prod) || 0
  const precio = Number(prod.precio_prod) || 0
  if (!unidad || cantidad <= 0 || precio <= 0) return null
  const grupo = GRUPOS_UNIDAD[unidad]
  if (!grupo) return null
  const cantidadBase = cantidad * grupo.factor
  if (cantidadBase <= 0) return null
  return { precio: precio / cantidadBase, unidad: grupo.base }
}

function formatPrecioNorm(prod: Producto): string | null {
  const norm = precioNormalizado(prod)
  if (!norm) return null
  return `precio x ${norm.unidad}: $${norm.precio.toFixed(1)}`
}

// Mostrar comparación de precio por unidad si hay productos del mismo grupo
const mostrarPrecioNorm = computed(() => {
  const unidades = new Set(
    productos.value
      .map(p => GRUPOS_UNIDAD[p.unidad_prod || '']?.base)
      .filter(Boolean)
  )
  return unidades.size > 0
})

const formatPrice = (price: number): string => {
  return price.toLocaleString('es-AR')
}

const formatFecha = (fecha: string): string => {
  const d = new Date(fecha)
  return d.toLocaleDateString('es-AR', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const removerProducto = (id: string) => {
  productos.value = productos.value.filter(p => p.id_prod !== id)
  localStorage.setItem('comparapp_comparacion', JSON.stringify(productos.value))
}

const limpiarTodo = () => {
  productos.value = []
  localStorage.removeItem('comparapp_comparacion')
}

const guardarComparacion = () => {
  const nueva: HistorialItem = {
    id: Date.now().toString(),
    fecha: new Date().toISOString(),
    productos: productos.value,
    totalProductos: totalItems.value
  }
  historial.value.unshift(nueva)
  if (historial.value.length > 20) historial.value.pop()
  localStorage.setItem('comparapp_historial', JSON.stringify(historial.value))
  alert('Comparación guardada en el historial')
}

const recargarHistorial = (h: HistorialItem) => {
  productos.value = h.productos
  localStorage.setItem('comparapp_comparacion', JSON.stringify(h.productos))
}
</script>

<style scoped>
.comparaciones-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-card-hover: rgba(255, 255, 255, 0.06);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-glow: rgba(232, 196, 160, 0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245, 240, 235, 0.6);
  --text-muted: rgba(245, 240, 235, 0.35);
  --accent-gold: #e8c4a0;
  --accent-violet: #a78bfa;
  --accent-green: #4ade80;
  --accent-rose: #fb7185;
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  --radius-xl: 24px;
  --shadow-glow: 0 0 20px rgba(232, 196, 160, 0.12);
  --shadow-card: 0 4px 24px rgba(0, 0, 0, 0.2);

  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.bg-gradient {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232, 196, 160, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167, 139, 250, 0.05), transparent),
    linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 40%, #0a0a0f 100%);
  z-index: 0;
}

.bg-noise {
  position: fixed;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  z-index: 1;
  pointer-events: none;
}

.page-content {
  position: relative;
  z-index: 2;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 2.5rem;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }
.stagger-4 { animation-delay: 0.2s; }
.stagger-5 { animation-delay: 0.25s; }
.stagger-6 { animation-delay: 0.3s; }

/* ─── HEADER ─── */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.header-top {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-glow);
  color: var(--text-primary);
  transform: scale(1.05);
}

.header-text {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0;
}

/* ─── RESUMEN ─── */
.resumen-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-card);
}

.resumen-row {
  display: flex;
  align-items: center;
  justify-content: space-around;
  gap: 0.5rem;
}

.resumen-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  text-align: center;
}

.resumen-label {
  color: var(--text-muted);
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.resumen-value {
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 700;
}

.resumen-total {
  color: var(--accent-green);
}

.resumen-divider {
  width: 1px;
  height: 32px;
  background: var(--border-subtle);
}

/* ─── SORT BAR ─── */
.sort-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.sort-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  flex-shrink: 0;
}

.sort-chips {
  display: flex;
  gap: 0.4rem;
  flex-wrap: wrap;
}

.sort-chip {
  padding: 0.35rem 0.75rem;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-secondary);
  font-size: 0.78rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.sort-chip:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: var(--border-glow);
  color: var(--text-primary);
}

.sort-chip.active {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.15), rgba(232, 196, 160, 0.08));
  border-color: rgba(232, 196, 160, 0.3);
  color: var(--accent-gold);
  box-shadow: 0 0 12px rgba(232, 196, 160, 0.1);
}

/* ─── GRUPOS DE PROVEEDOR ─── */
.comercio-grupo {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(167, 139, 250, 0.2);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.comercio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.12), rgba(167, 139, 250, 0.04));
  border-bottom: 1px solid rgba(167, 139, 250, 0.12);
}

.comercio-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  color: #c4b5fd;
  font-size: 0.8rem;
  font-weight: 600;
}

.comercio-badge svg {
  color: rgba(167, 139, 250, 0.6);
  flex-shrink: 0;
}

.comercio-subtotal {
  color: var(--accent-green);
  font-size: 0.82rem;
  font-weight: 700;
}

.comercio-items {
  display: flex;
  flex-direction: column;
}

.comercio-items .comparacion-item {
  border-radius: 0;
  border: none;
  border-bottom: 1px solid var(--border-subtle);
}

.comercio-items .comparacion-item:last-child {
  border-bottom: none;
}

/* ─── LISTA ─── */
.comparacion-lista {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.comparacion-item {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.25s ease;
}

.comparacion-item:hover {
  background: var(--bg-card-hover);
  border-color: rgba(167, 139, 250, 0.15);
}

.item-img {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.item-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.item-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.item-name {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-brand {
  color: var(--text-secondary);
  font-size: 0.78rem;
  margin: 0;
}

.item-venue {
  color: var(--text-muted);
  font-size: 0.72rem;
  margin: 0;
}

.item-qty {
  color: var(--accent-violet);
  font-size: 0.75rem;
  font-weight: 500;
  margin-top: 0.1rem;
}

.item-price-col {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
  flex-shrink: 0;
}

.item-precio-norm {
  font-size: 0.68rem;
  color: var(--accent-emerald);
  font-weight: 500;
  margin-top: 2px;
  white-space: nowrap;
}

.item-unit {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.item-total {
  color: var(--accent-green);
  font-size: 1rem;
  font-weight: 700;
}

.item-remove {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.item-remove:hover {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
}

/* ─── ACCIONES ─── */
.acciones {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-guardar {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(167, 139, 250, 0.1));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: var(--radius-md);
  color: #c4b5fd;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-guardar:hover {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(167, 139, 250, 0.15));
  border-color: rgba(167, 139, 250, 0.5);
  color: #ddd6fe;
  transform: translateY(-2px);
}

.btn-limpiar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.875rem 1.25rem;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.btn-limpiar:hover {
  background: rgba(251, 113, 133, 0.08);
  border-color: rgba(251, 113, 133, 0.2);
  color: #fb7185;
}

/* ─── EMPTY ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  padding: 4rem 1rem;
  text-align: center;
}

.empty-icon-wrap {
  width: 72px;
  height: 72px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.empty-state h3 {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0;
}

.empty-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.15), rgba(232, 196, 160, 0.08));
  border: 1px solid rgba(232, 196, 160, 0.25);
  border-radius: var(--radius-md);
  color: var(--accent-gold);
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  margin-top: 0.5rem;
}

.empty-btn:hover {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.25), rgba(232, 196, 160, 0.12));
  border-color: rgba(232, 196, 160, 0.4);
  transform: translateY(-2px);
}

/* ─── HISTORIAL SECTION ─── */
.historial-section {
  margin-top: 1rem;
}

.section-title {
  color: var(--text-muted);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  font-weight: 600;
  margin: 0 0 0.75rem;
}

.historial-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.historial-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.25s ease;
}

.historial-item:hover {
  background: rgba(255, 255, 255, 0.04);
  border-color: rgba(167, 139, 250, 0.15);
}

.historial-info {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.item-fecha-distancia {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 2px;
}
.item-distancia {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: var(--accent-gold);
}
.item-fecha {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-top: 2px;
}

.historial-fecha {
  color: var(--text-secondary);
  font-size: 0.82rem;
}

.historial-count {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.historial-item svg {
  color: var(--text-muted);
  transition: all 0.25s ease;
}

.historial-item:hover svg {
  color: var(--accent-violet);
  transform: translateX(2px);
}

.ver-historial {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  margin-top: 0.75rem;
  padding: 0.625rem;
  color: var(--accent-violet);
  font-size: 0.85rem;
  font-weight: 500;
  text-decoration: none;
  transition: gap 0.25s ease;
}

.ver-historial:hover {
  gap: 0.5rem;
}

@media (max-width: 480px) {
  .page-content { padding: 1rem; }
  .page-title { font-size: 1.25rem; }
  .resumen-row { gap: 0.25rem; }
  .resumen-value { font-size: 1.1rem; }
  .acciones { flex-direction: column; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>