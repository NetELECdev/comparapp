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
      <div class="search-wrapper animate-fade-in-up stagger-1" ref="searchWrapperRef">
        <div class="search-bar" :class="{ 'search-focused': searchFocused }">
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
            @focus="searchFocused = true"
            @blur="searchFocused = false"
            @keydown.esc="searchQuery = ''"
            autocomplete="off"
          />
          <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
            </svg>
          </button>
        </div>
      </div>

      <!-- BARRA DE ORDENAMIENTO -->
      <div class="sort-bar animate-fade-in-up stagger-1">
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

      <!-- RESULTADOS -->
      <div class="results-header animate-fade-in-up stagger-2">
        <div class="results-count">
          <span v-if="searchQuery.length >= minChars">
            {{ productosFiltrados.length }} resultado{{ productosFiltrados.length !== 1 ? 's' : '' }} para "{{ searchQuery }}"
          </span>
          <span v-else>
            {{ productos.length }} productos disponibles
          </span>
        </div>
        <!-- ❌ ELIMINADO: badgesComparativos sin sentido -->
      </div>

      <!-- LISTA DE PRODUCTOS -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando productos...</p>
      </div>

      <!-- AGRUPADO POR PROVEEDOR -->
      <template v-else-if="sortBy === 'comercio' && productosAgrupadosPorComercio">
        <div
          v-for="(grupo, comercio) in productosAgrupadosPorComercio"
          :key="comercio"
          class="comercio-grupo animate-fade-in-up stagger-2"
        >
          <div class="comercio-header">
            <span class="comercio-nombre-header">🏪 {{ comercio }}</span>
            <span class="comercio-count">{{ grupo.length }} producto{{ grupo.length !== 1 ? 's' : '' }}</span>
          </div>
          <div class="comercio-items">
            <ProductRow
              v-for="producto in grupo"
              :key="producto.id_prod"
              :product="producto"
              :comparacion="comparacionMap[producto.id_prod]"
              @click="openProductDetail(producto)"
              @compare="agregarAComparacion"
            />
          </div>
        </div>
      </template>

      <!-- LISTA NORMAL -->
      <div v-else-if="productosOrdenados.length > 0" class="productos-lista animate-fade-in-up stagger-2">
        <ProductRow
          v-for="(producto, index) in productosOrdenados"
          :key="producto.id_prod"
          :product="producto"
          :comparacion="comparacionMap[producto.id_prod]"
          :class="'stagger-' + Math.min(index + 3, 8)"
          @click="openProductDetail(producto)"
          @compare="agregarAComparacion"
        />
      </div>

      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <h3>No se encontraron productos</h3>
        <p v-if="searchQuery.length >= minChars">
          Intentá con otro término de búsqueda
        </p>
        <p v-else>
          No hay productos disponibles
        </p>
        <button v-if="searchQuery.length >= minChars" class="back-btn-text" @click="searchQuery = ''">
          Ver todos los productos
        </button>
      </div>

    </main>

    <!-- MODAL DE DETALLE DE PRODUCTO -->
    <ProductDetailModal
      v-if="selectedProduct"
      :product="selectedProduct"
      :comparacion="comparacionMap[selectedProduct.id_prod]"
      @close="selectedProduct = null"
      @compare="agregarAComparacion"
    />

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
import { ref, computed, onMounted } from 'vue'
import { navigateTo } from '#app'
import ProductRow from '~/components/ProductRow.vue'
import ProductDetailModal from '~/components/ProductDetailModal.vue'

interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  cate_prod: string
  imagen_prod: string | null
  comercio_prod: string
  fecha_prod?: string
  activo_prod: boolean
  cantidad_prod?: number
  unidad_prod?: string
}

interface ComparacionItem extends Producto {
  cantidad: number
}

interface ComparacionData {
  esMasBarato: boolean
  esMasCaro: boolean
  pctVsMin: number
  totalCompetidores: number
}

const loading = ref(true)
const productos = ref<Producto[]>([])
const comparacion = ref<ComparacionItem[]>([])
const sortBy = ref('nombre')
const selectedProduct = ref<Producto | null>(null)

const searchQuery = ref('')
const searchFocused = ref(false)
const searchInputRef = ref<HTMLInputElement>()
const searchWrapperRef = ref<HTMLElement>()
const minChars = 2

const userLocation = ref<{ lat: number; lng: number } | null>(null)

const sortOptions = [
  { label: 'Nombre', value: 'nombre' },
  { label: 'Precio ↓', value: 'precio_asc' },
  { label: 'Precio ↑', value: 'precio_desc' },
  { label: 'Fecha', value: 'fecha' },
  { label: 'Categoría', value: 'categoria' },
  { label: 'Marca', value: 'marca' },
  { label: 'Comercio', value: 'comercio' },
]

// ─── FILTRADO POR BÚSQUEDA ───
const productosFiltrados = computed(() => {
  if (searchQuery.value.length < minChars) {
    return productos.value
  }

  const q = searchQuery.value.toLowerCase().trim()
  return productos.value.filter(p =>
    p.nombre_prod.toLowerCase().includes(q) ||
    p.marca_prod.toLowerCase().includes(q) ||
    p.comercio_prod.toLowerCase().includes(q) ||
    p.cate_prod.toLowerCase().includes(q)
  )
})

// ─── ORDENAMIENTO (sobre filtrados) ───
const productosOrdenados = computed(() => {
  const list = [...productosFiltrados.value]

  switch (sortBy.value) {
    case 'nombre':
      return list.sort((a, b) => a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'precio_asc':
      return list.sort((a, b) => Number(a.precio_prod) - Number(b.precio_prod))
    case 'precio_desc':
      return list.sort((a, b) => Number(b.precio_prod) - Number(a.precio_prod))
    case 'categoria':
      return list.sort((a, b) => a.cate_prod.localeCompare(b.cate_prod, 'es'))
    case 'marca':
      return list.sort((a, b) => a.marca_prod.localeCompare(b.marca_prod, 'es'))
    case 'comercio':
      return list.sort((a, b) => a.comercio_prod.localeCompare(b.comercio_prod, 'es') || a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
    case 'fecha':
      return list.sort((a, b) => {
        const dA = a.fecha_prod ? new Date(a.fecha_prod).getTime() : 0
        const dB = b.fecha_prod ? new Date(b.fecha_prod).getTime() : 0
        return dB - dA
      })
    default:
      return list
  }
})

// ─── ✅ NUEVO: MAPA DE COMPARACIONES (reemplaza badgesComparativos) ───
const comparacionMap = computed((): Record<string, ComparacionData> => {
  const map: Record<string, ComparacionData> = {}

  // Agrupar por nombre
  const porNombre: Record<string, Producto[]> = {}
  for (const p of productosFiltrados.value) {
    if (!porNombre[p.nombre_prod]) porNombre[p.nombre_prod] = []
    porNombre[p.nombre_prod].push(p)
  }

  // Calcular comparación para cada producto
  for (const p of productosFiltrados.value) {
    const grupo = porNombre[p.nombre_prod] || [p]
    const precios = grupo.map(x => Number(x.precio_prod))
    const minPrecio = Math.min(...precios)
    const maxPrecio = Math.max(...precios)
    const precioActual = Number(p.precio_prod)

    if (grupo.length > 1) {
      const pctVsMin = minPrecio > 0 && precioActual > minPrecio
        ? Math.round(((precioActual - minPrecio) / minPrecio) * 100)
        : 0

      map[p.id_prod] = {
        esMasBarato: Math.abs(precioActual - minPrecio) < 0.01,
        esMasCaro: Math.abs(precioActual - maxPrecio) < 0.01,
        pctVsMin,
        totalCompetidores: grupo.length
      }
    } else {
      map[p.id_prod] = {
        esMasBarato: true,
        esMasCaro: true,
        pctVsMin: 0,
        totalCompetidores: 1
      }
    }
  }

  return map
})

// ─── AGRUPADO POR PROVEEDOR ───
const productosAgrupadosPorComercio = computed(() => {
  if (sortBy.value !== 'comercio') return null
  const grupos: Record<string, Producto[]> = {}
  for (const p of productosFiltrados.value) {
    const key = p.comercio_prod || 'Sin comercio'
    if (!grupos[key]) grupos[key] = []
    grupos[key].push(p)
  }
  for (const key in grupos) {
    grupos[key].sort((a, b) => a.nombre_prod.localeCompare(b.nombre_prod, 'es'))
  }
  return grupos
})

// ─── ✅ NUEVO: Abrir modal de detalle ───
function openProductDetail(producto: Producto) {
  selectedProduct.value = producto
}

onMounted(async () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => { userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude } },
      () => {}
    )
  }

  const storedComp = localStorage.getItem('comparapp_comparacion')
  if (storedComp) {
    try { comparacion.value = JSON.parse(storedComp) } catch {}
  }

  try {
    const { api } = useApi()
    const res = await api<{ count: number; results: Producto[] }>('/products')
    productos.value = res.results || []
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loading.value = false
  }
})

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

/* ─── SEARCH ─── */
.search-wrapper { position: relative; z-index: 50; }
.search-bar {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.875rem 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
}
.search-bar.search-focused {
  border-color: var(--border-glow);
  box-shadow: 0 0 0 3px rgba(232,196,160,0.08);
  background: rgba(255,255,255,0.05);
}
.search-icon { color: var(--text-muted); flex-shrink: 0; }
.search-bar.search-focused .search-icon { color: var(--accent-gold); }
.search-input {
  flex: 1; background: transparent; border: none; outline: none;
  color: var(--text-primary); font-size: 0.95rem; font-family: inherit;
}
.search-input::placeholder { color: var(--text-muted); }
.search-clear {
  width: 28px; height: 28px; border-radius: 50%;
  background: rgba(255,255,255,0.06); border: 1px solid var(--border-subtle);
  color: var(--text-muted); display: flex; align-items: center;
  justify-content: center; cursor: pointer; transition: all 0.2s;
}
.search-clear:hover { background: rgba(251,113,133,0.1); border-color: rgba(251,113,133,0.3); color: #fb7185; }

/* ─── RESULTS HEADER ─── */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
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

/* ─── PROVEEDOR GRUPO ─── */
.comercio-grupo {
  display: flex;
  flex-direction: column;
  border: 1px solid rgba(167,139,250,0.2);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 0.5rem;
}
.comercio-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.6rem 1rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.12), rgba(167,139,250,0.04));
  border-bottom: 1px solid rgba(167,139,250,0.12);
}
.comercio-nombre-header {
  color: #c4b5fd;
  font-size: 0.85rem;
  font-weight: 600;
}
.comercio-count {
  color: rgba(167,139,250,0.6);
  font-size: 0.75rem;
}
.comercio-items {
  display: flex;
  flex-direction: column;
  gap: 0;
  padding: 0.5rem;
  gap: 0.5rem;
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

@media (max-width: 480px) {
  .page-content { padding: 1rem; gap: 1rem; }
  .page-title { font-size: 1.25rem; }
  .sort-chips { gap: 0.375rem; }
  .sort-chip { padding: 0.35rem 0.625rem; font-size: 0.75rem; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>