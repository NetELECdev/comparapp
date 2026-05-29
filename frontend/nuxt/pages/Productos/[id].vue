<template>
  <div class="producto-detalle-page">
    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/productos/lista')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Detalle</h1>
            <p class="page-subtitle">{{ producto?.nombre_prod || 'Producto' }}</p>
          </div>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando producto...</p>
      </div>

      <!-- DETALLE DEL PRODUCTO -->
      <div v-else-if="producto" class="detalle-card animate-fade-in-up stagger-1">
        <!-- Imagen -->
        <div class="detalle-img">
          <img
            :src="producto.imagen_prod || '/images/avatar_default.png'"
            :alt="producto.nombre_prod"
            @error="onImageError"
          />
        </div>

        <!-- Info principal -->
        <div class="detalle-info">
          <span class="detalle-categoria">{{ producto.cate_prod }}</span>
          <h2 class="detalle-nombre">{{ producto.nombre_prod }}</h2>
          <p class="detalle-marca">{{ producto.marca_prod }}</p>

          <div class="detalle-precio-wrap">
            <span class="detalle-precio">${{ formatPrice(producto.precio_prod) }}</span>
            <span class="detalle-unidad">{{ producto.cantidad_prod }} {{ producto.unidad_prod }}</span>
            <!-- Badge variacion 30d -->
            <span
              v-if="historial?.variacion_30d !== null && historial?.variacion_30d !== undefined"
              class="variacion-badge"
              :class="historial.variacion_30d > 0 ? 'sube' : historial.variacion_30d < 0 ? 'baja' : 'igual'"
            >
              <svg v-if="historial.variacion_30d > 0" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              <svg v-else-if="historial.variacion_30d < 0" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              {{ Math.abs(historial.variacion_30d) }}% vs 30d
            </span>
          </div>

          <p class="detalle-proveedor">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 7h-9"/><path d="M14 17H5"/>
              <circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>
            </svg>
            {{ producto.provee_prod }}
          </p>

          <p v-if="producto.describe_prod" class="detalle-descripcion">
            {{ producto.describe_prod }}
          </p>
        </div>

        <!-- COMPARACION POR PROVEEDOR (mismo nombre) -->
        <div v-if="mismoNombreLoading" class="same-name-loading">
          <div class="loading-spinner-sm" />
          <span>Buscando comparacion...</span>
        </div>

        <div v-else-if="mismoNombre && mismoNombre.results && mismoNombre.results.length > 1" class="same-name-section">
          <div class="same-name-header">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
            </svg>
            <span>Comparacion por proveedor</span>
            <span class="same-name-count">{{ mismoNombre.results.length }} opciones</span>
          </div>

          <div class="same-name-stats" v-if="mismoNombre.stats">
            <span class="sns-item sns-min">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
              Min: ${{ formatPrice(mismoNombre.stats.min) }}
            </span>
            <span class="sns-item sns-max">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
              Max: ${{ formatPrice(mismoNombre.stats.max) }}
            </span>
            <span class="sns-item sns-avg" v-if="mismoNombre.stats.avg">
              Prom: ${{ formatPrice(mismoNombre.stats.avg) }}
            </span>
            <span class="sns-item sns-diff" v-if="mismoNombre.stats.diff_pct > 0">
              Dif: {{ mismoNombre.stats.diff_pct }}%
            </span>
          </div>

          <div class="same-name-list">
            <div
              v-for="p in mismoNombre.results"
              :key="p.id_prod"
              class="same-name-item"
              :class="{ 'es-mejor': p.es_mejor_precio, 'es-peor': p.es_peor_precio, 'es-actual': p.id_prod === producto.id_prod }"
              @click="p.id_prod !== producto.id_prod && irADetalle(p.id_prod)"
            >
              <div class="sni-info">
                <span class="sni-proveedor">{{ p.provee_prod }}</span>
                <span v-if="p.es_mejor_precio" class="sni-badge mejor">Mejor</span>
                <span v-if="p.id_prod === producto.id_prod" class="sni-badge actual">Actual</span>
              </div>
              <div class="sni-precio-wrap">
                <span class="sni-precio">${{ formatPrice(p.precio_prod) }}</span>
                <span v-if="p.pct_vs_min > 0" class="sni-pct">+{{ p.pct_vs_min }}%</span>
              </div>
            </div>
          </div>
        </div>
        <!-- FIN COMPARACION POR PROVEEDOR -->

        <!-- HISTORIAL DE PRECIOS -->
        <div class="historial-section">
          <div class="historial-header-row">
            <div class="historial-header">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
                <path d="M3 3v5h5"/><path d="M12 7v5l4 2"/>
              </svg>
              <span>Historial de precios</span>
            </div>
            <NuxtLink
              :to="`/productos/${route.params.id}/historial`"
              class="historial-link-btn"
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 3v5h5"/>
                <path d="M3.05 13A9 9 0 1 0 6 5.3L3 8"/>
                <path d="M12 7v5l4 2"/>
              </svg>
              Ver completo
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="m9 18 6-6-6-6"/>
              </svg>
            </NuxtLink>
          </div>

          <!-- Loading historial -->
          <div v-if="loadingHistorial" class="historial-loading">
            <div class="loading-spinner-sm" />
            <span>Cargando historial...</span>
          </div>

          <!-- Sin historial -->
          <div v-else-if="!historial || historial.total_cambios === 0" class="historial-empty">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
            </svg>
            Sin historial registrado aun
          </div>

          <!-- Con historial -->
          <template v-else>
            <!-- Stats rapidas -->
            <div class="historial-stats">
              <div class="hstat-item">
                <span class="hstat-label">Actual</span>
                <span class="hstat-value precio-actual">${{ formatPrice(historial.precio_actual) }}</span>
              </div>
              <div v-if="historial.precio_7d !== null && historial.precio_7d !== undefined" class="hstat-item">
                <span class="hstat-label">Hace 7d</span>
                <span class="hstat-value" :class="getVariacionClass(historial.variacion_7d)">
                  ${{ formatPrice(historial.precio_7d) }}
                  <small v-if="historial.variacion_7d !== null && historial.variacion_7d !== undefined">
                    ({{ historial.variacion_7d > 0 ? '+' : '' }}{{ historial.variacion_7d }}%)
                  </small>
                </span>
              </div>
              <div v-if="historial.precio_30d !== null && historial.precio_30d !== undefined" class="hstat-item">
                <span class="hstat-label">Hace 30d</span>
                <span class="hstat-value" :class="getVariacionClass(historial.variacion_30d)">
                  ${{ formatPrice(historial.precio_30d) }}
                  <small v-if="historial.variacion_30d !== null && historial.variacion_30d !== undefined">
                    ({{ historial.variacion_30d > 0 ? '+' : '' }}{{ historial.variacion_30d }}%)
                  </small>
                </span>
              </div>
            </div>

            <!-- Min / Max -->
            <div class="historial-minmax">
              <span class="minmax-item minmax-min">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
                Min: ${{ formatPrice(historial.precio_minimo) }}
              </span>
              <span class="minmax-sep">·</span>
              <span class="minmax-item minmax-max">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
                Max: ${{ formatPrice(historial.precio_maximo) }}
              </span>
              <span class="minmax-sep">·</span>
              <span class="minmax-cambios">{{ historial.total_cambios }} cambios</span>
            </div>

            <!-- Grafico SVG de evolucion -->
            <div class="grafico-wrap" v-if="historial.serie && historial.serie.length >= 2">
              <svg
                class="grafico-svg"
                :viewBox="`0 0 ${CHART_W} ${CHART_H}`"
                preserveAspectRatio="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <!-- Defs -->
                <defs>
                  <linearGradient id="grad-historial" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" :stop-color="colorLinea" stop-opacity="0.2"/>
                    <stop offset="100%" :stop-color="colorLinea" stop-opacity="0"/>
                  </linearGradient>
                </defs>

                <!-- Guías horizontales -->
                <g>
                  <line
                    v-for="(g, gi) in guiasHorizontales"
                    :key="'g' + gi"
                    :x1="PAD_X"
                    :y1="g.y"
                    :x2="CHART_W - PAD_X"
                    :y2="g.y"
                    stroke="rgba(255,255,255,0.07)"
                    stroke-width="1"
                    stroke-dasharray="3 4"
                  />
                </g>

                <!-- Area rellena -->
                <path :d="areaPath" fill="url(#grad-historial)" />

                <!-- Linea principal -->
                <path
                  :d="linePath"
                  fill="none"
                  :stroke="colorLinea"
                  stroke-width="1.75"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                />

                <!-- Punto mínimo (verde) -->
                <g v-if="puntoMin">
                  <circle :cx="puntoMin.x" :cy="puntoMin.y" r="4" fill="#34d399" />
                  <circle :cx="puntoMin.x" :cy="puntoMin.y" r="7" fill="#34d399" fill-opacity="0.15" />
                </g>

                <!-- Punto máximo (rojo) -->
                <g v-if="puntoMax">
                  <circle :cx="puntoMax.x" :cy="puntoMax.y" r="4" fill="#fb7185" />
                  <circle :cx="puntoMax.x" :cy="puntoMax.y" r="7" fill="#fb7185" fill-opacity="0.15" />
                </g>

                <!-- Punto actual (dorado) — encima de todo -->
                <circle :cx="puntoActual.x" :cy="puntoActual.y" r="10" fill="#e8c4a0" fill-opacity="0.12" />
                <circle :cx="puntoActual.x" :cy="puntoActual.y" r="4.5" fill="#e8c4a0" />
                <circle :cx="puntoActual.x" :cy="puntoActual.y" r="2" fill="#fff" fill-opacity="0.8" />
              </svg>

              <!-- Leyenda de puntos -->
              <div class="grafico-leyenda">
                <span v-if="puntoMin" class="gl-item gl-min">
                  <svg width="7" height="7" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="#34d399"/></svg>
                  Mín · {{ formatFechaCorta(puntoMin.fecha) }}
                </span>
                <span v-if="puntoMax" class="gl-item gl-max">
                  <svg width="7" height="7" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="#fb7185"/></svg>
                  Máx · {{ formatFechaCorta(puntoMax.fecha) }}
                </span>
                <span class="gl-item gl-actual">
                  <svg width="7" height="7" viewBox="0 0 10 10"><circle cx="5" cy="5" r="5" fill="#e8c4a0"/></svg>
                  Hoy
                </span>
              </div>

              <!-- Etiquetas de fecha eje X -->
              <div class="grafico-fechas">
                <span>{{ formatFechaCorta(historial.serie[0].fecha) }}</span>
                <span>{{ formatFechaCorta(historial.serie[Math.floor(historial.serie.length / 2)].fecha) }}</span>
                <span>Hoy</span>
              </div>
            </div>
          </template>
        </div>
        <!-- FIN HISTORIAL -->

        <!-- Acciones -->
        <div class="detalle-acciones">
          <div class="quantity-selector">
            <button class="qty-btn qty-minus" :disabled="cantidad <= 1" @click="cantidad--">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14"/></svg>
            </button>
            <span class="qty-value">{{ cantidad }}</span>
            <button class="qty-btn qty-plus" @click="cantidad++">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12h14"/><path d="M12 5v14"/>
              </svg>
            </button>
          </div>

          <button
            class="compare-btn-detalle"
            :class="{ added: wasAdded }"
            @click="agregarAComparacion"
            :disabled="wasAdded"
          >
            <span v-if="wasAdded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
              Agregado
            </span>
            <span v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
              </svg>
              Comparar
            </span>
          </button>
        </div>
      </div>

      <!-- ERROR -->
      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <h3>Producto no encontrado</h3>
        <p>El producto que buscas no existe o fue eliminado</p>
        <button class="back-btn-text" @click="navigateTo('/productos/lista')">Volver al listado</button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, navigateTo, useRuntimeConfig } from '#app'

// ─── Interfaces ───────────────────────────────────────────────

interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  cate_prod: string
  imagen_prod: string | null
  provee_prod: string
  activo_prod: boolean
  describe_prod?: string
  cantidad_prod?: number
  unidad_prod?: string
}

interface PuntoHistorial { precio: number; fecha: string }

interface Historial {
  id_prod: string
  precio_actual: number
  precio_7d: number | null
  precio_30d: number | null
  variacion_7d: number | null
  variacion_30d: number | null
  precio_minimo: number | null
  precio_maximo: number | null
  total_cambios: number
  serie: PuntoHistorial[]
}

interface SameNameResponse {
  nombre: string
  count: number
  stats: {
    min: number
    max: number
    avg: number
    diff_max_min: number
    diff_pct: number
  }
  results: Array<{
    id_prod: string
    nombre_prod: string
    precio_prod: number
    provee_prod: string
    es_mejor_precio: boolean
    es_peor_precio: boolean
    pct_vs_min: number
  }>
}

// ─── Estado ───────────────────────────────────────────────────

const route = useRoute()
const config = useRuntimeConfig()

const loading = ref(true)
const loadingHistorial = ref(false)
const mismoNombreLoading = ref(false)
const producto = ref<Producto | null>(null)
const historial = ref<Historial | null>(null)
const mismoNombre = ref<SameNameResponse | null>(null)
const cantidad = ref(1)
const wasAdded = ref(false)

// ─── API helper con prefix correcto ────────────────────────────
async function api<T>(endpoint: string, opts?: any): Promise<T> {
  const base = config.public.apiBase || ''
  const url = endpoint.startsWith('/api/v1/') ? endpoint : `/api/v1${endpoint}`
  const fullUrl = `${base}${url}`
  const res = await $fetch<T>(fullUrl, opts)
  return res
}

// ─── Gráfico SVG ─────────────────────────────────────────────

const CHART_W = 300
const CHART_H = 110
const PAD_X = 8
const PAD_Y = 14

const colorLinea = computed(() => {
  if (!historial.value?.variacion_30d) return '#e8c4a0'
  return historial.value.variacion_30d > 0 ? '#fb7185' : '#34d399'
})

const puntosGrafico = computed((): Array<{x: number, y: number, precio: number, fecha: string}> => {
  const serie = historial.value?.serie
  if (!serie || serie.length < 2) return []

  const precios = serie.map(p => p.precio)
  const minP = Math.min(...precios)
  const maxP = Math.max(...precios)
  const rangoP = maxP - minP || 1

  return serie.map((p, i) => ({
    x: PAD_X + (i / (serie.length - 1)) * (CHART_W - PAD_X * 2),
    y: CHART_H - PAD_Y - ((p.precio - minP) / rangoP) * (CHART_H - PAD_Y * 2),
    precio: p.precio,
    fecha: p.fecha,
  }))
})

const linePath = computed((): string => {
  const pts = puntosGrafico.value
  if (pts.length < 2) return ''
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
})

const areaPath = computed((): string => {
  const pts = puntosGrafico.value
  if (pts.length < 2) return ''
  const line = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
  const last = pts[pts.length - 1]
  const first = pts[0]
  return `${line} L ${last.x.toFixed(1)} ${CHART_H} L ${first.x.toFixed(1)} ${CHART_H} Z`
})

const puntoActual = computed(() => {
  const pts = puntosGrafico.value
  return pts.length > 0 ? pts[pts.length - 1] : { x: CHART_W - PAD_X, y: PAD_Y, precio: 0, fecha: '' }
})

// Punto mínimo y máximo del gráfico
const puntoMin = computed(() => {
  const pts = puntosGrafico.value
  if (pts.length === 0) return null
  return pts.reduce((min, p) => p.precio < min.precio ? p : min, pts[0])
})

const puntoMax = computed(() => {
  const pts = puntosGrafico.value
  if (pts.length === 0) return null
  return pts.reduce((max, p) => p.precio > max.precio ? p : max, pts[0])
})

// Guías horizontales (3 líneas: min, mid, max del rango)
const guiasHorizontales = computed((): Array<{y: number, label: string}> => {
  const serie = historial.value?.serie
  if (!serie || serie.length < 2) return []
  const precios = serie.map(p => p.precio)
  const minP = Math.min(...precios)
  const maxP = Math.max(...precios)
  const midP = (minP + maxP) / 2
  const rangoP = maxP - minP || 1
  const toY = (p: number) => CHART_H - PAD_Y - ((p - minP) / rangoP) * (CHART_H - PAD_Y * 2)
  return [
    { y: toY(maxP), label: `$${formatPrice(maxP)}` },
    { y: toY(midP), label: `$${formatPrice(midP)}` },
    { y: toY(minP), label: `$${formatPrice(minP)}` },
  ]
})

// ─── Helpers ──────────────────────────────────────────────────

function formatPrice(price: string | number | null | undefined): string {
  if (price === null || price === undefined) return '0'
  return Number(price).toLocaleString('es-AR')
}

function onImageError(e: Event) {
  (e.target as HTMLImageElement).src = '/images/avatar_default.png'
}

function getVariacionClass(v: number | null): string {
  if (v === null || v === undefined) return ''
  if (v > 0) return 'precio-sube'
  if (v < 0) return 'precio-baja'
  return ''
}

function formatFechaCorta(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
  } catch { return '' }
}

async function irADetalle(id: string) {
  await navigateTo(`/productos/${id}`)
}

function agregarAComparacion() {
  if (!producto.value) return
  const item = { ...producto.value, cantidad: cantidad.value }
  const stored = localStorage.getItem('comparapp_comparacion')
  let comparacion: any[] = []
  try { comparacion = stored ? JSON.parse(stored) : [] } catch {}
  const existente = comparacion.find((p: any) => p.id_prod === item.id_prod)
  if (existente) existente.cantidad = item.cantidad
  else comparacion.push(item)
  localStorage.setItem('comparapp_comparacion', JSON.stringify(comparacion))
  wasAdded.value = true
  setTimeout(() => { wasAdded.value = false; cantidad.value = 1 }, 2000)
}

// ─── Carga de datos ───────────────────────────────────────────

onMounted(async () => {
  const id = route.params.id as string
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuidRegex.test(id)) { loading.value = false; return }

  try {
    producto.value = await api<Producto>(`/products/${id}`)
  } catch (err) {
    console.error('Error cargando producto:', err)
    producto.value = null
  } finally {
    loading.value = false
  }

  // Cargar historial en paralelo (no bloquea el render del producto)
  if (producto.value) {
    loadingHistorial.value = true
    try {
      historial.value = await api<Historial>(`/historial/${id}?dias=90`)
    } catch (err) {
      console.error('Sin historial:', err)
      historial.value = null
    } finally {
      loadingHistorial.value = false
    }

    // Cargar comparacion por proveedor (mismo nombre)
    mismoNombreLoading.value = true
    try {
      mismoNombre.value = await api<SameNameResponse>(`/products/${id}/same-name`)
    } catch (err) {
      console.error('Sin comparacion por proveedor:', err)
      mismoNombre.value = null
    } finally {
      mismoNombreLoading.value = false
    }
  }
})
</script>

<style scoped>
/* Usa variables de tokens.css — sin fondos duplicados */
.producto-detalle-page {
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.page-content {
  position: relative;
  z-index: 1;
  padding: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  padding-bottom: 2.5rem;
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

.stagger-1 { animation-delay: 0.1s; }

/* ─── HEADER ─── */
.page-header { display: flex; align-items: center; padding: 0.5rem 0; }
.header-left { display: flex; align-items: center; gap: 0.875rem; }
.back-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center;
  justify-content: center; cursor: pointer; transition: all 0.25s ease; flex-shrink: 0;
}
.back-btn:hover { background: var(--bg-card-hover); border-color: var(--border-glow); color: var(--text-primary); transform: scale(1.05); }
.page-title { font-size: 1.5rem; font-weight: 700; margin: 0; line-height: 1.2; letter-spacing: -0.02em; }
.page-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin: 0.15rem 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px; }

/* ─── LOADING ─── */
.loading-state { display: flex; flex-direction: column; align-items: center; gap: 0.875rem; padding: 4rem 1rem; color: var(--text-muted); font-size: 0.9rem; }
.loading-spinner { width: 32px; height: 32px; border: 2px solid var(--border-subtle); border-top-color: var(--accent-gold); border-radius: 50%; animation: spin 0.8s linear infinite; }

/* ─── DETALLE CARD ─── */
.detalle-card {
  display: flex; flex-direction: column; gap: 1.25rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 1.5rem; position: relative; overflow: hidden;
}
.detalle-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

/* ─── IMAGEN ─── */
.detalle-img {
  width: 100%; aspect-ratio: 1; border-radius: var(--radius-lg);
  overflow: hidden; background: var(--bg-input);
  display: flex; align-items: center; justify-content: center;
}
.detalle-img img { width: 100%; height: 100%; object-fit: contain; padding: 1rem; }

/* ─── INFO ─── */
.detalle-info { display: flex; flex-direction: column; gap: 0.375rem; }
.detalle-categoria {
  display: inline-flex; align-self: flex-start; padding: 0.25rem 0.75rem;
  background: var(--accent-gold-dim); border: 1px solid rgba(232,196,160,0.2);
  border-radius: 999px; color: var(--accent-gold);
  font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;
}
.detalle-nombre { font-size: 1.35rem; font-weight: 700; margin: 0.25rem 0 0; line-height: 1.2; letter-spacing: -0.01em; }
.detalle-marca { color: var(--text-secondary); font-size: 0.9rem; margin: 0; }
.detalle-precio-wrap { display: flex; align-items: baseline; gap: 0.75rem; margin-top: 0.5rem; flex-wrap: wrap; }
.detalle-precio { color: var(--accent-emerald); font-size: 1.85rem; font-weight: 700; letter-spacing: -0.02em; }
.detalle-unidad { color: var(--text-muted); font-size: 0.8rem; }
.detalle-proveedor { display: flex; align-items: center; gap: 0.375rem; color: var(--text-secondary); font-size: 0.85rem; margin: 0.5rem 0 0; }
.detalle-proveedor svg { color: var(--accent-violet); }
.detalle-descripcion { color: var(--text-secondary); font-size: 0.9rem; line-height: 1.5; margin: 0.75rem 0 0; padding-top: 0.75rem; border-top: 1px solid var(--border-subtle); }

/* ─── BADGE VARIACIÓN ─── */
.variacion-badge {
  display: inline-flex; align-items: center; gap: 0.25rem;
  padding: 0.2rem 0.55rem; border-radius: 999px;
  font-size: 0.72rem; font-weight: 700;
}
.variacion-badge.sube { background: rgba(251,113,133,0.12); border: 1px solid rgba(251,113,133,0.25); color: #fb7185; }
.variacion-badge.baja { background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.25); color: #34d399; }
.variacion-badge.igual { background: var(--bg-input); border: 1px solid var(--border-subtle); color: var(--text-muted); }

/* ─── SAME NAME SECTION (Comparacion por proveedor) ─── */
.same-name-loading {
  display: flex; align-items: center; gap: 0.5rem;
  color: var(--text-muted); font-size: 0.82rem;
  padding: 1rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.same-name-section {
  display: flex; flex-direction: column; gap: 0.75rem;
  padding: 1rem;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}

.same-name-header {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem; font-weight: 600; color: var(--text-secondary);
}

.same-name-header svg { color: var(--accent-violet); }

.same-name-count {
  margin-left: auto;
  font-size: 0.7rem;
  color: var(--text-muted);
  background: rgba(167,139,250,0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
}

.same-name-stats {
  display: flex; gap: 0.75rem; flex-wrap: wrap;
}

.sns-item {
  display: flex; align-items: center; gap: 0.25rem;
  font-size: 0.75rem; font-weight: 600;
}

.sns-min { color: #34d399; }
.sns-max { color: #fb7185; }
.sns-avg { color: var(--accent-gold); }
.sns-diff {
  color: var(--accent-gold);
  background: rgba(232,196,160,0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
}

.same-name-list {
  display: flex; flex-direction: column; gap: 0.375rem;
}

.same-name-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.625rem 0.875rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.same-name-item:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  transform: translateY(-1px);
}

.same-name-item.es-mejor {
  border-color: rgba(52,211,153,0.3);
  background: linear-gradient(135deg, rgba(52,211,153,0.05), var(--bg-card));
}

.same-name-item.es-peor {
  border-color: rgba(251,113,133,0.2);
}

.same-name-item.es-actual {
  border-color: rgba(232,196,160,0.3);
  background: linear-gradient(135deg, rgba(232,196,160,0.05), var(--bg-card));
}

.sni-info {
  display: flex; align-items: center; gap: 0.5rem;
}

.sni-proveedor {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
}

.sni-badge {
  display: inline-flex; align-items: center; gap: 0.2rem;
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
  font-size: 0.65rem; font-weight: 700;
}

.sni-badge.mejor {
  background: rgba(52,211,153,0.15);
  border: 1px solid rgba(52,211,153,0.3);
  color: #34d399;
}

.sni-badge.actual {
  background: rgba(232,196,160,0.15);
  border: 1px solid rgba(232,196,160,0.3);
  color: var(--accent-gold);
}

.sni-precio-wrap {
  display: flex; align-items: center; gap: 0.5rem;
}

.sni-precio {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.sni-pct {
  font-size: 0.7rem;
  color: #fb7185;
  font-weight: 600;
}

/* ─── HISTORIAL SECTION ─── */
.historial-section {
  display: flex; flex-direction: column; gap: 0.875rem;
  padding: 1rem; background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
}

/* Header row con boton de historial completo */
.historial-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.historial-header {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.82rem; font-weight: 600; color: var(--text-secondary);
}

/* Boton ver historial completo */
.historial-link-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.35rem 0.75rem;
  background: rgba(232, 196, 160, 0.08);
  border: 1px solid rgba(232, 196, 160, 0.2);
  border-radius: 999px;
  color: var(--accent-gold);
  font-size: 0.72rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.25s ease;
  flex-shrink: 0;
}
.historial-link-btn:hover {
  background: rgba(232, 196, 160, 0.15);
  border-color: rgba(232, 196, 160, 0.35);
  transform: translateY(-1px);
}

.historial-loading { display: flex; align-items: center; gap: 0.5rem; color: var(--text-muted); font-size: 0.82rem; }
.loading-spinner-sm { width: 16px; height: 16px; border: 1.5px solid var(--border-subtle); border-top-color: var(--accent-gold); border-radius: 50%; animation: spin 0.8s linear infinite; }
.historial-empty { color: var(--text-muted); font-size: 0.82rem; display: flex; align-items: center; gap: 0.4rem; }

/* Stats */
.historial-stats { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.hstat-item { display: flex; flex-direction: column; gap: 0.2rem; flex: 1; min-width: 70px; }
.hstat-label { font-size: 0.68rem; color: var(--text-muted); font-weight: 500; text-transform: uppercase; letter-spacing: 0.04em; }
.hstat-value { font-size: 0.88rem; font-weight: 600; color: var(--text-primary); }
.hstat-value small { font-size: 0.7rem; font-weight: 500; }
.precio-actual { color: var(--accent-gold); }
.precio-sube { color: var(--accent-rose); }
.precio-baja { color: var(--accent-emerald); }

/* Min / Max */
.historial-minmax { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; font-size: 0.75rem; }
.minmax-item { display: flex; align-items: center; gap: 0.25rem; font-weight: 600; }
.minmax-min { color: var(--accent-emerald); }
.minmax-max { color: var(--accent-rose); }
.minmax-sep { color: var(--text-muted); }
.minmax-cambios { color: var(--text-muted); }

/* Grafico */
.grafico-wrap { display: flex; flex-direction: column; gap: 0.3rem; }
.grafico-svg { width: 100%; height: 110px; border-radius: 8px; overflow: visible; }
.grafico-fechas {
  display: flex; justify-content: space-between;
  font-size: 0.65rem; color: var(--text-muted); padding: 0 2px;
}
.grafico-leyenda {
  display: flex; gap: 0.875rem; flex-wrap: wrap;
  padding: 0 2px;
}
.gl-item {
  display: flex; align-items: center; gap: 0.3rem;
  font-size: 0.68rem; font-weight: 500;
}
.gl-min { color: #34d399; }
.gl-max { color: #fb7185; }
.gl-actual { color: var(--accent-gold); }

/* ─── ACCIONES ─── */
.detalle-acciones {
  display: flex; align-items: center; gap: 0.875rem;
  margin-top: 0.5rem; padding-top: 1rem; border-top: 1px solid var(--border-subtle);
}
.quantity-selector {
  display: flex; align-items: center;
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  border-radius: 10px; overflow: hidden;
}
.qty-btn { width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; background: transparent; border: none; color: var(--text-secondary); cursor: pointer; transition: all 0.2s ease; }
.qty-btn:hover:not(:disabled) { background: var(--bg-card-hover); color: var(--text-primary); }
.qty-btn:disabled { opacity: 0.3; cursor: not-allowed; }
.qty-minus { border-right: 1px solid var(--border-subtle); }
.qty-plus  { border-left:  1px solid var(--border-subtle); }
.qty-value { min-width: 36px; text-align: center; color: var(--text-primary); font-size: 0.95rem; font-weight: 600; padding: 0 0.25rem; }

.compare-btn-detalle {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(167,139,250,0.1));
  border: 1px solid rgba(167,139,250,0.3); border-radius: var(--radius-md);
  color: #c4b5fd; font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: all 0.25s ease;
}
.compare-btn-detalle:hover:not(:disabled) { background: linear-gradient(135deg, rgba(167,139,250,0.3), rgba(167,139,250,0.2)); border-color: rgba(167,139,250,0.5); color: #ddd6fe; transform: translateY(-2px); }
.compare-btn-detalle.added { background: linear-gradient(135deg, rgba(52,211,153,0.15), rgba(52,211,153,0.1)); border-color: rgba(52,211,153,0.3); color: #6ee7b7; }
.compare-btn-detalle:disabled { cursor: default; }

/* ─── EMPTY STATE ─── */
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; padding: 4rem 1rem; text-align: center; }
.empty-icon-wrap { width: 64px; height: 64px; border-radius: var(--radius-lg); background: var(--bg-card); border: 1px solid var(--border-subtle); display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.empty-state h3 { color: var(--text-primary); font-size: 1.1rem; font-weight: 600; margin: 0; }
.empty-state p  { color: var(--text-secondary); font-size: 0.85rem; margin: 0; }
.back-btn-text { margin-top: 0.75rem; padding: 0.625rem 1.25rem; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.25s ease; }
.back-btn-text:hover { background: var(--bg-card-hover); border-color: var(--border-glow); color: var(--text-primary); }

@media (max-width: 480px) {
  .page-content { padding: 1rem; }
  .detalle-card { padding: 1.25rem; }
  .detalle-precio { font-size: 1.6rem; }
  .page-subtitle { max-width: 200px; }
  .historial-stats { gap: 0.5rem; }
  .historial-header-row { flex-wrap: wrap; }
  .historial-link-btn { font-size: 0.68rem; padding: 0.3rem 0.6rem; }
  .same-name-stats { gap: 0.5rem; }
}
</style>