<template>
  <div class="productos-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Productos</h1>
            <p class="page-subtitle">Explorá y compará precios</p>
          </div>
        </div>
      </header>

      <!-- BARRA DE BÚSQUEDA -->
      <div class="search-wrapper animate-fade-in-up stagger-1">
        <div class="search-bar" :class="{ 'search-focused': searchFocused, 'search-has-value': searchQuery.length > 0 }">
          <svg class="search-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          <input
            ref="searchInputRef"
            v-model="searchQuery"
            type="text"
            placeholder="Buscar producto..."
            class="search-input"
            @focus="onSearchFocus"
            @blur="onSearchBlur"
            @keydown.enter.prevent="applySearch"
            @keydown.esc="closeSuggestions"
            autocomplete="off"
          />
          <button v-if="searchQuery" class="search-clear" @click="clearSearch" aria-label="Limpiar búsqueda">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18"/>
              <path d="m6 6 12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- RESULTADOS -->
      <div class="results-header animate-fade-in-up stagger-2">
        <div class="results-count">
          <span v-if="searchQuery.length >= minChars">
            {{ productos.length }} resultado{{ productos.length !== 1 ? 's' : '' }} para "{{ searchQuery }}"
          </span>
          <span v-else-if="searchQuery.length > 0">
            Escribí al menos {{ minChars }} caracteres...
          </span>
          <span v-else>
            {{ productos.length }} productos disponibles
          </span>
        </div>
        <div v-if="gruposConCompetencia > 0" class="competencia-badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
          </svg>
          {{ gruposConCompetencia }} con comparación
        </div>
      </div>

      <!-- BARRA DE ORDENAMIENTO -->
      <div class="sort-bar animate-fade-in-up stagger-2">
        <div class="sort-label">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m3 16 4 4 4-4"/>
            <path d="M7 20V4"/>
            <path d="M11 4h10"/>
            <path d="M11 8h7"/>
            <path d="M11 12h4"/>
          </svg>
          Ordenar por
        </div>
        <div class="sort-chips">
          <button
            v-for="opt in sortOptions"
            :key="opt.value"
            class="sort-chip"
            :class="{ active: sortBy === opt.value }"
            @click="sortBy = opt.value"
          >
            {{ opt.label }}
          </button>
        </div>
      </div>

      <!-- LISTA DE PRODUCTOS -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando productos...</p>
      </div>

      <!-- GRUPOS POR NOMBRE (búsqueda activa) -->
      <template v-else-if="searchQuery.length >= minChars && productosAgrupadosPorNombre && Object.keys(productosAgrupadosPorNombre).length > 0">
        <div
          v-for="(grupo, nombre) in productosAgrupadosPorNombre"
          :key="nombre"
          class="nombre-grupo animate-fade-in-up"
          :class="{ 'tiene-competencia': grupo.length > 1 }"
        >
          <div v-if="grupo.length > 1" class="grupo-header">
            <span class="grupo-nombre">{{ nombre }}</span>
            <div class="grupo-stats">
              <span class="grupo-stat stat-min">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
                Mín: ${{ formatPrice(grupoStats[nombre]?.min) }}
              </span>
              <span class="grupo-stat stat-max">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                Máx: ${{ formatPrice(grupoStats[nombre]?.max) }}
              </span>
              <span class="grupo-stat stat-diff" v-if="grupoStats[nombre]?.diff > 0">
                Dif: {{ grupoStats[nombre]?.diffPct }}%
              </span>
            </div>
          </div>

          <div class="grupo-items">
            <ProductRow
              v-for="producto in grupo"
              :key="producto.id_prod"
              :product="producto"
              :comparacion="grupo.length > 1 ? {
                esMasBarato: producto.es_mas_barato,
                esMasCaro: producto.es_mas_caro,
                pctVsMin: producto.pct_vs_min,
                totalCompetidores: producto.total_competidores
              } : undefined"
              @compare="agregarAComparacion"
              @click="irADetalle(producto.id_prod)"
            />
          </div>
        </div>
      </template>

      <!-- Lista normal (sin búsqueda o sin resultados agrupados) -->
      <div v-else-if="productosOrdenados.length > 0" class="productos-lista animate-fade-in-up stagger-3">
        <ProductRow
          v-for="(producto, index) in productosOrdenados"
          :key="producto.id_prod"
          :product="producto"
          :class="'stagger-' + Math.min(index + 4, 8)"
          @compare="agregarAComparacion"
          @click="irADetalle(producto.id_prod)"
        />
      </div>

      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <h3>No se encontraron productos</h3>
        <p v-if="searchQuery.length >= minChars">Intentá con otro término de búsqueda</p>
        <p v-else>No hay productos disponibles</p>
        <button v-if="searchQuery.length >= minChars" class="back-btn-text" @click="clearSearch">Ver todos los productos</button>
      </div>
    </main>

    <!-- BARRA DE COMPARACIÓN FLOTANTE -->
    <Transition name="slide-up">
      <div v-if="comparacion.length > 0" class="compare-float">
        <div class="compare-info">
          <span class="compare-count">{{ comparacion.length }} para comparar</span>
        </div>
        <div class="compare-actions">
          <button class="compare-clear" @click="limpiarComparacion" aria-label="Quitar selección">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18"/>
              <path d="m6 6 12 12"/>
            </svg>
          </button>
          <button class="compare-btn-float" @click="irAComparar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"/>
              <path d="M7 12h10"/>
              <path d="M10 18h4"/>
            </svg>
            Comparar
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'
import ProductRow from '~/components/ProductRow.vue'

// ─── Interfaces ───
interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: number | string
  cate_prod: string
  imagen_prod: string | null
  provee_prod: string
  fecha_prod?: string
  activo_prod: boolean
  describe_prod?: string
  pct_vs_min?: number
  es_mas_barato?: boolean
  es_mas_caro?: boolean
  total_competidores?: number
  precio_min_grupo?: number
  precio_max_grupo?: number
  cantidad_prod?: number
  unidad_prod?: string
}

interface ComparacionItem extends Producto {
  cantidad: number
}

// ─── Config ───
const config = useRuntimeConfig()

// ─── Estado ───
const loading = ref(true)
const productos = ref<Producto[]>([])
const comparacion = ref<ComparacionItem[]>([])
const sortBy = ref('nombre')
const searchQuery = ref('')
const searchFocused = ref(false)
const searchInputRef = ref<HTMLInputElement>()

// ─── Constantes ───
const DEBOUNCE_MS = 300
const minChars = 3

// ─── Opciones de ordenamiento ───
const sortOptions = [
  { label: 'Nombre', value: 'nombre' },
  { label: 'Precio ↓', value: 'precio_asc' },
  { label: 'Precio ↑', value: 'precio_desc' },
  { label: 'Fecha', value: 'fecha' },
  { label: 'Proveedor', value: 'proveedor' },
  { label: 'Categoría', value: 'categoria' },
  { label: 'Marca', value: 'marca' },
]

// ─── API helper con prefix correcto ───
async function api<T>(endpoint: string, opts?: any): Promise<T> {
  const base = config.public.apiBase || ''
  const url = endpoint.startsWith('/api/v1/') ? endpoint : `/api/v1${endpoint}`
  const fullUrl = `${base}${url}`
  const res = await $fetch<T>(fullUrl, opts)
  return res
}

// ─── Computed ───
const productosAgrupadosPorNombre = computed(() => {
  if (searchQuery.value.length < minChars || productos.value.length === 0) return null

  const grupos: Record<string, Producto[]> = {}
  for (const p of productos.value) {
    const key = p.nombre_prod
    if (!grupos[key]) grupos[key] = []
    grupos[key].push(p)
  }

  for (const key in grupos) {
    grupos[key].sort((a, b) => Number(a.precio_prod) - Number(b.precio_prod))
  }

  return grupos
})

const grupoStats = computed(() => {
  const stats: Record<string, { min: number; max: number; diff: number; diffPct: number }> = {}
  if (!productosAgrupadosPorNombre.value) return stats

  for (const [nombre, grupo] of Object.entries(productosAgrupadosPorNombre.value)) {
    if (grupo.length > 1) {
      const precios = grupo.map(p => Number(p.precio_prod))
      const min = Math.min(...precios)
      const max = Math.max(...precios)
      stats[nombre] = {
        min,
        max,
        diff: max - min,
        diffPct: min > 0 ? Math.round(((max - min) / min) * 100) : 0
      }
    }
  }
  return stats
})

const gruposConCompetencia = computed(() => {
  let count = 0
  for (const grupo of Object.values(grupoStats.value)) {
    if (grupo.diff > 0) count++
  }
  return count
})

const productosOrdenados = computed(() => {
  const list = [...productos.value]
  switch (sortBy.value) {
    case 'nombre':
      return list.sort((a, b) => a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'precio_asc':
      return list.sort((a, b) => Number(a.precio_prod) - Number(b.precio_prod))
    case 'precio_desc':
      return list.sort((a, b) => Number(b.precio_prod) - Number(a.precio_prod))
    case 'fecha':
      return list.sort((a, b) => {
        const dateA = a.fecha_prod ? new Date(a.fecha_prod).getTime() : 0
        const dateB = b.fecha_prod ? new Date(b.fecha_prod).getTime() : 0
        return dateB - dateA
      })
    case 'proveedor':
      return list.sort((a, b) => a.provee_prod.localeCompare(b.provee_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'categoria':
      return list.sort((a, b) => a.cate_prod.localeCompare(b.cate_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'marca':
      return list.sort((a, b) => a.marca_prod.localeCompare(b.marca_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'fecha':
      return list.sort((a, b) => {
        const dA = a.fecha_prod ? new Date(a.fecha_prod).getTime() : 0
        const dB = b.fecha_prod ? new Date(b.fecha_prod).getTime() : 0
        return dB - dA  // más reciente primero
      })
    default:
      return list
  }
})

// ─── Debounce para búsqueda ───
let debounceTimer: ReturnType<typeof setTimeout>

watch(searchQuery, (newVal) => {
  if (newVal.length >= minChars) {
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      fetchSearchResults(newVal)
    }, DEBOUNCE_MS)
  } else if (newVal.length === 0) {
    cargarTodosLosProductos()
  }
})

// ─── Métodos ───
async function fetchSearchResults(query: string) {
  loading.value = true
  try {
    const res = await api<{ count: number; query: string; results: Producto[] }>(
      `/products/search?q=${encodeURIComponent(query)}&limit=50`
    )
    console.log('Resultados búsqueda:', res)
    productos.value = res.results || []
  } catch (err) {
    console.error('Error buscando:', err)
    productos.value = []
  } finally {
    loading.value = false
  }
}

async function cargarTodosLosProductos() {
  loading.value = true
  try {
    const res = await api<{ count: number; results: Producto[] }>('/products?limit=100')
    productos.value = res.results || []
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loading.value = false
  }
}

function applySearch() {
  if (searchQuery.value.length >= minChars) {
    fetchSearchResults(searchQuery.value)
  }
  searchFocused.value = false
  searchInputRef.value?.blur()
}

function onSearchFocus() {
  searchFocused.value = true
}

function onSearchBlur() {
  setTimeout(() => {
    searchFocused.value = false
  }, 200)
}

function closeSuggestions() {
  searchFocused.value = false
  searchInputRef.value?.blur()
}

function clearSearch() {
  searchQuery.value = ''
  productos.value = []
  cargarTodosLosProductos()
}

function formatPrice(price: string | number | null | undefined): string {
  if (price === null || price === undefined) return '0'
  return Number(price).toLocaleString('es-AR')
}

async function irADetalle(id: string) {
  console.log('Navegando a detalle:', id)
  await navigateTo(`/productos/${id}`)
}

// ─── Comparación ───
const agregarAComparacion = (producto: ComparacionItem) => {
  const existente = comparacion.value.find(p => p.id_prod === producto.id_prod)
  if (existente) {
    existente.cantidad = producto.cantidad
  } else {
    comparacion.value.push(producto)
  }
  localStorage.setItem('comparapp_comparacion', JSON.stringify(comparacion.value))
}

const limpiarComparacion = () => {
  comparacion.value = []
  localStorage.removeItem('comparapp_comparacion')
}

const irAComparar = () => {
  const historial = JSON.parse(localStorage.getItem('comparapp_historial') || '[]')
  const nuevaComparacion = {
    id: Date.now().toString(),
    fecha: new Date().toISOString(),
    productos: comparacion.value,
    totalProductos: comparacion.value.reduce((sum, p) => sum + p.cantidad, 0)
  }
  historial.unshift(nuevaComparacion)
  if (historial.length > 20) historial.pop()
  localStorage.setItem('comparapp_historial', JSON.stringify(historial))
  navigateTo('/comparaciones')
}

// ─── Lifecycle ───
onMounted(async () => {
  const storedComp = localStorage.getItem('comparapp_comparacion')
  if (storedComp) {
    try { comparacion.value = JSON.parse(storedComp) } catch {}
  }
  await cargarTodosLosProductos()
})
</script>

<style scoped>
.productos-page {
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
  padding-bottom: 6rem;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
.stagger-7 { animation-delay: 0.35s; }
.stagger-8 { animation-delay: 0.4s; }

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.header-left {
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
  margin: 0.15rem 0 0;
}

.search-wrapper {
  position: relative;
  z-index: 50;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}

.search-bar.search-focused {
  border-color: var(--border-glow);
  box-shadow: 0 0 0 3px rgba(232, 196, 160, 0.08), var(--shadow-glow);
  background: rgba(255, 255, 255, 0.05);
}

.search-bar.search-has-value {
  background: rgba(255, 255, 255, 0.04);
}

.search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: color 0.25s ease;
}

.search-bar.search-focused .search-icon {
  color: var(--accent-gold);
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 0.95rem;
  font-family: inherit;
  padding: 0;
  min-width: 0;
}

.search-input::placeholder {
  color: var(--text-muted);
}

.search-clear {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid var(--border-subtle);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.search-clear:hover {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
}

.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.results-count {
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 500;
}

.competencia-badge {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: var(--accent-gold);
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(232, 196, 160, 0.1);
  padding: 0.25rem 0.75rem;
  border-radius: 999px;
  border: 1px solid rgba(232, 196, 160, 0.2);
}

.sort-bar {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
  padding: 0.875rem 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.sort-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-muted);
  font-size: 0.78rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.sort-chips {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.sort-chip {
  padding: 0.4rem 0.875rem;
  border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: rgba(255, 255, 255, 0.02);
  color: var(--text-secondary);
  font-size: 0.8rem;
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
  box-shadow: 0 0 15px rgba(232, 196, 160, 0.1);
}

.nombre-grupo {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 0.75rem;
  transition: all 0.3s ease;
}

.nombre-grupo.tiene-competencia {
  border-color: rgba(232, 196, 160, 0.2);
  box-shadow: 0 0 20px rgba(232, 196, 160, 0.05);
}

.grupo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.08), rgba(232, 196, 160, 0.02));
  border-bottom: 1px solid rgba(232, 196, 160, 0.1);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.grupo-nombre {
  color: var(--accent-gold);
  font-size: 0.9rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.grupo-stats {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.grupo-stat {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.stat-min { color: #34d399; }
.stat-max { color: #fb7185; }
.stat-diff { 
  color: var(--accent-gold); 
  background: rgba(232, 196, 160, 0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.grupo-items {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  padding: 4rem 1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.productos-lista {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 4rem 1rem;
  text-align: center;
}

.empty-icon-wrap {
  width: 64px;
  height: 64px;
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

.back-btn-text {
  margin-top: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.back-btn-text:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-glow);
  color: var(--text-primary);
}

.compare-float {
  position: fixed;
  bottom: 1.25rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.875rem 1.125rem;
  width: calc(100% - 3rem);
  max-width: 560px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.18), rgba(167, 139, 250, 0.08));
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid rgba(167, 139, 250, 0.25);
  border-radius: var(--radius-xl);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4), 0 0 24px rgba(167, 139, 250, 0.1);
}

.compare-info {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.compare-count {
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
}

.compare-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.compare-clear {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
}

.compare-clear:hover {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
}

.compare-btn-float {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(167, 139, 250, 0.1));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: var(--radius-md);
  color: #c4b5fd;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
}

.compare-btn-float:hover {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(167, 139, 250, 0.15));
  border-color: rgba(167, 139, 250, 0.5);
  color: #ddd6fe;
  transform: translateY(-1px);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

@media (max-width: 480px) {
  .page-content { padding: 1rem; gap: 1rem; }
  .page-title { font-size: 1.25rem; }
  .sort-chips { gap: 0.375rem; }
  .sort-chip { padding: 0.35rem 0.625rem; font-size: 0.75rem; }
  .results-count { font-size: 0.75rem; }
  .grupo-header { padding: 0.6rem 0.75rem; }
  .grupo-nombre { font-size: 0.82rem; }
  .grupo-stats { gap: 0.5rem; }
  .grupo-stat { font-size: 0.7rem; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>
