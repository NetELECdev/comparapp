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

      <!-- 🔍 BARRA DE BÚSQUEDA CON SUGERENCIAS -->
      <div class="search-wrapper animate-fade-in-up stagger-1" ref="searchWrapperRef">
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
            @keydown.down.prevent="navigateSuggestions(1)"
            @keydown.up.prevent="navigateSuggestions(-1)"
            @keydown.enter.prevent="applySearch"
            @keydown.esc="closeSuggestions"
            autocomplete="off"
          />
          <button
            v-if="searchQuery"
            class="search-clear"
            @click="clearSearch"
            aria-label="Limpiar búsqueda"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18"/>
              <path d="m6 6 12 12"/>
            </svg>
          </button>
        </div>

        <!-- Dropdown de sugerencias -->
        <Transition name="suggestions">
          <div v-if="showSuggestions" class="suggestions-dropdown">
            <!-- Estado de carga -->
            <div v-if="searchLoading" class="suggestions-loading">
              <div class="loading-spinner loading-spinner--sm" />
              <span>Buscando...</span>
            </div>

            <!-- Sin resultados -->
            <div v-else-if="suggestions.length === 0 && searchQuery.length >= minChars" class="suggestions-empty">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="11" cy="11" r="8"/>
                <path d="m21 21-4.3-4.3"/>
              </svg>
              <span>No se encontraron productos</span>
            </div>

            <!-- Lista de sugerencias -->
            <ul v-else-if="suggestions.length > 0" class="suggestions-list">
              <li
                v-for="(item, index) in suggestions"
                :key="item.id_prod"
                class="suggestion-item"
                :class="{ highlighted: highlightedIndex === index }"
                @mousedown.prevent="selectSuggestion(item)"
                @mouseenter="highlightedIndex = index"
              >
                <div class="suggestion-img">
                  <img :src="item.imagen_prod || '/images/avatar_default.png'" />
                </div>
                <div class="suggestion-info">
                  <span class="suggestion-name" v-html="highlightMatch(item.nombre_prod)"></span>
                  <span class="suggestion-meta">{{ item.marca_prod }} · ${{ formatPrice(item.precio_prod) }}</span>
                </div>
                <svg class="suggestion-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m9 18 6-6-6-6"/>
                </svg>
              </li>
            </ul>

            <!-- Historial de búsquedas recientes -->
            <div v-if="recentSearches.length > 0 && !searchQuery" class="suggestions-section">
              <div class="suggestions-section-title">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 3v5h5"/>
                  <path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/>
                </svg>
                Búsquedas recientes
              </div>
              <ul class="suggestions-list">
                <li
                  v-for="(term, index) in recentSearches"
                  :key="term"
                  class="suggestion-item suggestion-history"
                  :class="{ highlighted: highlightedIndex === index }"
                  @mousedown.prevent="searchFromHistory(term)"
                  @mouseenter="highlightedIndex = index"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="11" cy="11" r="8"/>
                    <path d="m21 21-4.3-4.3"/>
                  </svg>
                  <span class="suggestion-name">{{ term }}</span>
                  <button
                    class="history-remove"
                    @mousedown.stop.prevent="removeFromHistory(term)"
                    aria-label="Eliminar del historial"
                  >
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M18 6 6 18"/>
                      <path d="m6 6 12 12"/>
                    </svg>
                  </button>
                </li>
              </ul>
            </div>
          </div>
        </Transition>
      </div>

      <!-- RESULTADOS DE BÚSQUEDA / LISTA PRINCIPAL -->
      <div class="results-header animate-fade-in-up stagger-2">
        <div class="results-count">
          <span v-if="searchQuery.length >= minChars">
            {{ productosFiltrados.length }} resultado{{ productosFiltrados.length !== 1 ? 's' : '' }} para "{{ searchQuery }}"
          </span>
          <span v-else>
            {{ productos.length }} productos disponibles
          </span>
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

      <div v-else-if="productosOrdenados.length > 0" class="productos-lista animate-fade-in-up stagger-3">
        <ProductRow
          v-for="(producto, index) in productosOrdenados"
          :key="producto.id_prod"
          :product="producto"
          :class="'stagger-' + Math.min(index + 4, 8)"
          @compare="agregarAComparacion"
        />
      </div>

      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <h3>No se encontraron productos</h3>
        <p v-if="searchQuery.length >= minChars">
          Intentá con otro término de búsqueda
        </p>
        <p v-else>
          No hay productos disponibles
        </p>
        <button v-if="searchQuery.length >= minChars" class="back-btn-text" @click="clearSearch">
          Ver todos los productos
        </button>
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
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'
import ProductRow from '~/components/ProductRow.vue'

// ─── Interfaces ───
interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  cate_prod: string
  imagen_prod: string | null
  provee_prod: string
  fecha_prod?: string
  activo_prod: boolean
  describe_prod?: string
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

// 🔍 Estado de búsqueda
const searchQuery = ref('')
const searchFocused = ref(false)
const searchLoading = ref(false)
const suggestions = ref<Producto[]>([])
const highlightedIndex = ref(-1)
const searchInputRef = ref<HTMLInputElement>()
const searchWrapperRef = ref<HTMLElement>()
const recentSearches = ref<string[]>([])

// ─── Constantes ───
const RECENT_SEARCHES_KEY = 'comparapp_recent_searches'
const MAX_RECENT = 8
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

// ─── Computed ───
const showSuggestions = computed(() => {
  return searchFocused.value && (
    searchQuery.value.length >= minChars ||
    (!searchQuery.value && recentSearches.value.length > 0)
  )
})

// Productos filtrados por búsqueda
const productosFiltrados = computed(() => {
  if (searchQuery.value.length < minChars) {
    return productos.value
  }
  
  const q = searchQuery.value.toLowerCase().trim()
  return productos.value.filter(p =>
    p.nombre_prod.toLowerCase().includes(q) ||
    p.marca_prod.toLowerCase().includes(q) ||
    (p.describe_prod && p.describe_prod.toLowerCase().includes(q)) ||
    p.provee_prod.toLowerCase().includes(q) ||
    p.cate_prod.toLowerCase().includes(q)
  )
})

// Productos ordenados (sobre los filtrados)
const productosOrdenados = computed(() => {
  const list = [...productosFiltrados.value]

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
        return dateB - dateA // Más reciente primero
      })
    case 'proveedor':
      return list.sort((a, b) => a.provee_prod.localeCompare(b.provee_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'categoria':
      return list.sort((a, b) => a.cate_prod.localeCompare(b.cate_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'marca':
      return list.sort((a, b) => a.marca_prod.localeCompare(b.marca_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    default:
      return list
  }
})

// ─── Debounce para sugerencias ───
let debounceTimer: ReturnType<typeof setTimeout>

watch(searchQuery, (newVal) => {
  highlightedIndex.value = -1
  
  if (newVal.length >= minChars) {
    searchLoading.value = true
    clearTimeout(debounceTimer)
    debounceTimer = setTimeout(() => {
      fetchSuggestions(newVal)
    }, DEBOUNCE_MS)
  } else {
    suggestions.value = []
    searchLoading.value = false
  }
})

// ─── Métodos de búsqueda ───
async function fetchSuggestions(query: string) {
  try {
    const res = await $fetch<{ count: number; results: Producto[] }>(
      `${config.public.apiBase}/products?q=${encodeURIComponent(query)}&limit=8`
    )

    if (res.results && res.results.length > 0) {
      suggestions.value = res.results.slice(0, 8)
    } else {
      // Fallback local
      const q = query.toLowerCase()
      suggestions.value = productos.value
        .filter(p =>
          p.nombre_prod.toLowerCase().includes(q) ||
          p.marca_prod.toLowerCase().includes(q)
        )
        .slice(0, 8)
    }
  } catch (err) {
    console.error('Error buscando sugerencias:', err)
    // Fallback local
    const q = query.toLowerCase()
    suggestions.value = productos.value
      .filter(p =>
        p.nombre_prod.toLowerCase().includes(q) ||
        p.marca_prod.toLowerCase().includes(q)
      )
      .slice(0, 8)
  } finally {
    searchLoading.value = false
  }
}

// Al tocar Enter o una sugerencia → aplica el filtro a la lista
function applySearch() {
  if (highlightedIndex.value >= 0 && suggestions.value[highlightedIndex.value]) {
    // Si hay una sugerencia resaltada, usa ese producto
    searchQuery.value = suggestions.value[highlightedIndex.value].nombre_prod
  }
  saveToHistory(searchQuery.value)
  closeSuggestions()
  searchInputRef.value?.blur()
}

// Al hacer click en una sugerencia
function selectSuggestion(item: Producto) {
  searchQuery.value = item.nombre_prod
  saveToHistory(item.nombre_prod)
  closeSuggestions()
}

function onSearchFocus() {
  searchFocused.value = true
  loadRecentSearches()
}

function onSearchBlur() {
  setTimeout(() => {
    searchFocused.value = false
    highlightedIndex.value = -1
  }, 200)
}

function closeSuggestions() {
  searchFocused.value = false
  highlightedIndex.value = -1
  searchInputRef.value?.blur()
}

function clearSearch() {
  searchQuery.value = ''
  suggestions.value = []
  highlightedIndex.value = -1
  searchInputRef.value?.focus()
}

function navigateSuggestions(direction: number) {
  const max = searchQuery.value
    ? suggestions.value.length
    : recentSearches.value.length

  if (max === 0) return

  highlightedIndex.value += direction

  if (highlightedIndex.value < 0) highlightedIndex.value = max - 1
  if (highlightedIndex.value >= max) highlightedIndex.value = 0
}

function formatPrice(price: string | number): string {
  return Number(price)?.toLocaleString('es-AR') || '0'
}

// ─── Historial ───
function loadRecentSearches() {
  try {
    const stored = localStorage.getItem(RECENT_SEARCHES_KEY)
    if (stored) {
      recentSearches.value = JSON.parse(stored)
    }
  } catch {}
}

function saveToHistory(term: string) {
  if (!term || term.length < minChars) return
  const normalized = term.trim().toLowerCase()
  recentSearches.value = [
    normalized,
    ...recentSearches.value.filter(t => t !== normalized)
  ].slice(0, MAX_RECENT)
  localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(recentSearches.value))
}

function searchFromHistory(term: string) {
  searchQuery.value = term
  saveToHistory(term)
  nextTick(() => searchInputRef.value?.focus())
}

function removeFromHistory(term: string) {
  recentSearches.value = recentSearches.value.filter(t => t !== term)
  localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(recentSearches.value))
}

// ─── Highlight de texto coincidente ───
function highlightMatch(text: string): string {
  if (!searchQuery.value) return text
  const regex = new RegExp(`(${escapeRegex(searchQuery.value)})`, 'gi')
  return text.replace(regex, '<mark>$1</mark>')
}

function escapeRegex(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
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
  // Cargar comparación previa
  const storedComp = localStorage.getItem('comparapp_comparacion')
  if (storedComp) {
    try { comparacion.value = JSON.parse(storedComp) } catch {}
  }

  // Cargar productos
  try {
    const res = await $fetch<{ count: number; results: Producto[] }>(
      `${config.public.apiBase}/products`
    )
    productos.value = res.results || []
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loading.value = false
  }

  // Cargar historial
  loadRecentSearches()
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

/* ─── HEADER ─── */
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

/* ─── 🔍 SEARCH BAR ─── */
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

/* ─── SUGGESTIONS DROPDOWN ─── */
.suggestions-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  right: 0;
  background: rgba(15, 15, 20, 0.95);
  backdrop-filter: blur(24px) saturate(180%);
  -webkit-backdrop-filter: blur(24px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), 0 0 24px rgba(232, 196, 160, 0.05);
  overflow: hidden;
  max-height: 420px;
  overflow-y: auto;
}

.suggestions-enter-active,
.suggestions-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.suggestions-enter-from,
.suggestions-leave-to {
  opacity: 0;
  transform: translateY(-8px) scale(0.98);
}

.suggestions-loading,
.suggestions-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.625rem;
  padding: 1.25rem;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.suggestions-section {
  border-top: 1px solid var(--border-subtle);
}

.suggestions-section:first-child {
  border-top: none;
}

.suggestions-section-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem 0.5rem;
  color: var(--text-muted);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.suggestions-list {
  list-style: none;
  margin: 0;
  padding: 0.25rem;
}

.suggestion-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.875rem;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s ease;
  margin: 0.125rem 0;
}

.suggestion-item:hover,
.suggestion-item.highlighted {
  background: rgba(255, 255, 255, 0.06);
}

.suggestion-item.highlighted {
  background: rgba(232, 196, 160, 0.08);
  border: 1px solid rgba(232, 196, 160, 0.15);
}

.suggestion-img {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.suggestion-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.suggestion-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.suggestion-name {
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.suggestion-name :deep(mark) {
  background: rgba(232, 196, 160, 0.25);
  color: var(--accent-gold);
  border-radius: 2px;
  padding: 0 2px;
  font-weight: 600;
}

.suggestion-meta {
  color: var(--text-muted);
  font-size: 0.75rem;
}

.suggestion-arrow {
  color: var(--text-muted);
  opacity: 0;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.suggestion-item:hover .suggestion-arrow,
.suggestion-item.highlighted .suggestion-arrow {
  opacity: 1;
  color: var(--accent-gold);
  transform: translateX(2px);
}

/* Historial */
.suggestion-history {
  gap: 0.625rem;
}

.suggestion-history svg:first-child {
  color: var(--text-muted);
  flex-shrink: 0;
}

.history-remove {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: transparent;
  border: none;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
  margin-left: auto;
}

.suggestion-item:hover .history-remove,
.suggestion-item.highlighted .history-remove {
  opacity: 1;
}

.history-remove:hover {
  background: rgba(251, 113, 133, 0.15);
  color: #fb7185;
}

/* ─── RESULTS HEADER ─── */
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

/* ─── SORT BAR ─── */
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

/* ─── LOADING ─── */
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

.loading-spinner--sm {
  width: 16px;
  height: 16px;
  border-width: 1.5px;
}

/* ─── LISTA ─── */
.productos-lista {
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

/* ─── EMPTY ─── */
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

/* ─── COMPARE FLOAT ─── */
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

/* Scrollbar del dropdown */
.suggestions-dropdown::-webkit-scrollbar {
  width: 4px;
}

.suggestions-dropdown::-webkit-scrollbar-track {
  background: transparent;
}

.suggestions-dropdown::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

@media (max-width: 480px) {
  .page-content { padding: 1rem; gap: 1rem; }
  .page-title { font-size: 1.25rem; }
  .sort-chips { gap: 0.375rem; }
  .sort-chip { padding: 0.35rem 0.625rem; font-size: 0.75rem; }
  .suggestion-item { padding: 0.5rem 0.75rem; }
  .results-count { font-size: 0.75rem; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>