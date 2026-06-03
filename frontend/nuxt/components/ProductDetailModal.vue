<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="product" class="modal-overlay" @click.self="close">
        <div class="modal-content">
          <!-- Header -->
          <div class="modal-header">
            <div class="header-info">
              <span class="modal-categoria">{{ product.cate_prod }}</span>
              <h2 class="modal-title">{{ product.nombre_prod }}</h2>
              <p class="modal-subtitle">{{ product.marca_prod }} · {{ product.provee_prod }}</p>
            </div>
            <div class="header-actions">
              <FavoritoButton :product="product" />
              <button class="close-btn" @click="close" aria-label="Cerrar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 6 6 18M6 6l12 12"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Precio y badges -->
          <div class="price-section">
            <div class="price-main">
              <span class="current-price">${{ formatPrice(product.precio_prod) }}</span>
              <span v-if="product.cantidad_prod" class="unit-badge">
                {{ product.cantidad_prod }} {{ product.unidad_prod }}
              </span>
            </div>

            <!-- Badge de comparación -->
            <div class="comparison-badges">
              <span v-if="comparacion?.esMasBarato && comparacion?.totalCompetidores > 1" class="badge badge-mejor">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 5v14M5 12l7 7 7-7"/>
                </svg>
                Mejor precio · {{ comparacion.totalCompetidores }} proveedores
              </span>
              <span v-else-if="comparacion?.pctVsMin > 0" class="badge badge-carro">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 19V5M5 12l7-7 7 7"/>
                </svg>
                +{{ comparacion.pctVsMin }}% más caro que el mínimo
              </span>
              <span v-else-if="comparacion?.totalCompetidores === 1" class="badge badge-unico">
                Único proveedor
              </span>
            </div>

            <!-- Configurar alerta de precio -->
            <div class="alerta-precio-section">
            <button v-if="!mostrarAlertaForm" class="btn-alerta" @click="mostrarAlertaForm = true">
                🔔 Avisame si baja de...
            </button>
            <div v-else class="alerta-form">
                <input
                v-model.number="precioAlerta"
                type="number"
                placeholder="Precio objetivo"
                class="alerta-input"
                @keydown.enter="crearAlerta"
                />
                <button class="btn-alerta-confirm" @click="crearAlerta" :disabled="creandoAlerta">
                {{ creandoAlerta ? '...' : 'Guardar' }}
                </button>
                <button class="btn-alerta-cancel" @click="mostrarAlertaForm = false">✕</button>
            </div>
            <p v-if="alertaMensaje" class="alerta-msg" :class="alertaMensaje.tipo">{{ alertaMensaje.texto }}</p>
            </div>

            <!-- Sparkline de variación -->
            <PriceSparkline
              v-if="priceHistory.length >= 2"
              :history="priceHistory"
              :variacion="variacion30d"
            />
          </div>

          <!-- GRÁFICO PRINCIPAL -->
            <div class="chart-section">
            <div class="section-header">
                <h3>📈 Comparación de precios por proveedor</h3>
                <div class="chart-tabs">
                <button
                    v-for="tab in tabs"
                    :key="tab.dias"
                    :class="{ active: diasActivo === tab.dias }"
                    @click="cargarHistorial(tab.dias)"
                >
                    {{ tab.label }}
                </button>
                </div>
            </div>

            <div v-if="loading" class="loading-state">
                <div class="spinner"></div>
                <span>Cargando...</span>
            </div>

            <!-- ✅ NUEVO: Mensaje cuando no hay competidores -->
            <div v-else-if="competidores.length <= 1" class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                <circle cx="12" cy="12" r="10"/>
                <path d="M12 8v4M12 16h.01"/>
                </svg>
                <p>Sin competidores para comparar</p>
                <span class="hint">Este producto solo tiene un proveedor registrado</span>
            </div>

            <div v-else-if="chartData.length === 0" class="empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.3">
                <path d="M3 3v18h18"/>
                <path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"/>
                </svg>
                <p>No hay datos disponibles</p>
            </div>

            <PriceChart
                v-else
                :data="chartData"
                :width="520"
                :height="180"
            />
            </div>

          <!-- Estadísticas -->
          <div v-if="stats" class="stats-grid">
            <div class="stat-card">
              <span class="stat-label">Precio mínimo</span>
              <span class="stat-value min">${{ formatPrice(stats.min) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Precio máximo</span>
              <span class="stat-value max">${{ formatPrice(stats.max) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Promedio</span>
              <span class="stat-value avg">${{ formatPrice(stats.avg) }}</span>
            </div>
            <div class="stat-card">
              <span class="stat-label">Variación 30d</span>
              <span class="stat-value" :class="stats.variacion30d >= 0 ? 'sube' : 'baja'">
                {{ stats.variacion30d >= 0 ? '+' : '' }}{{ stats.variacion30d?.toFixed(1) }}%
              </span>
            </div>
          </div>

          <!-- Competidores (mismo nombre) -->
          <div v-if="competidores.length > 1" class="competitors-section">
            <h3>🏪 Comparación por proveedor</h3>
            <div class="competitors-list">
              <div
                v-for="comp in competidoresOrdenados"
                :key="comp.id_prod"
                class="competitor-row"
                :class="{ 'es-actual': comp.id_prod === product.id_prod }"
              >
                <div class="comp-info">
                  <span class="comp-proveedor">{{ comp.provee_prod }}</span>
                  <span v-if="comp.es_mejor_precio" class="comp-tag tag-mejor">Más barato</span>
                  <span v-else-if="comp.es_peor_precio" class="comp-tag tag-carro">Más caro</span>
                </div>
                <div class="comp-precio">
                  <span class="comp-monto">${{ formatPrice(comp.precio_prod) }}</span>
                  <span v-if="comp.pct_vs_min > 0" class="comp-pct">+{{ comp.pct_vs_min }}%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Descripción -->
          <div v-if="product.describe_prod" class="description-section">
            <h3>📝 Descripción</h3>
            <p>{{ product.describe_prod }}</p>
          </div>

          <!-- Footer actions -->
          <div class="modal-footer">
            <button class="btn-compare" @click="addToCompare">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
              </svg>
              Agregar a comparar
            </button>
            <button class="btn-close" @click="close">Cerrar</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'

// ── Props ──
interface ComparacionData {
  esMasBarato: boolean
  esMasCaro: boolean
  pctVsMin: number
  totalCompetidores: number
}

const props = defineProps<{
  product: any
  comparacion?: ComparacionData
}>()

const emit = defineEmits(['close', 'compare'])

// ── Estado ──
const loading = ref(false)
const priceHistory = ref<any[]>([])
const chartData = ref<any[]>([])
const competidores = ref<any[]>([])
const stats = ref<any>(null)
const diasActivo = ref(30)

const tabs = [
  { dias: 7, label: '7 días' },
  { dias: 30, label: '30 días' },
  { dias: 90, label: '3 meses' }
]

// ── Computed ──
const variacion30d = computed(() => stats.value?.variacion30d ?? null)

const competidoresOrdenados = computed(() => {
  return [...competidores.value].sort((a, b) => {
    const pa = parseFloat(a.precio_prod) || 0
    const pb = parseFloat(b.precio_prod) || 0
    return pa - pb
  })
})

// ── Métodos ──
function close() {
  emit('close')
}

function addToCompare() {
  emit('compare', { ...props.product, cantidad: 1 })
}

function formatPrice(price: any): string {
  if (price === null || price === undefined) return '0'
  const num = typeof price === 'string' ? parseFloat(price) : price
  return num?.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 }) || '0'
}

// ✅ NUEVO: Construye serie de precios desde competidores (siempre hay datos)
function buildSeriesFromCompetidores() {
  // Tomar los precios actuales de todos los competidores como puntos de datos
  const puntos = competidores.value.map((c: any) => ({
    fecha: c.fecha_prod || new Date().toISOString(),
    precio: parseFloat(c.precio_prod) || 0
  }))

  // Ordenar por precio para que la curva tenga sentido
  puntos.sort((a: any, b: any) => a.precio - b.precio)

  return puntos
}

async function cargarHistorial(dias: number) {
  if (!props.product?.id_prod) return
  diasActivo.value = dias
  loading.value = true

  try {
    const { api } = useApi()

    // 1. PRIMERO: Obtener competidores (same-name) — ESTO SIEMPRE TRAE DATOS
    const sameNameData = await api(`/products/${props.product.id_prod}/same-name`)
    competidores.value = sameNameData.results || []

    // 2. Construir serie desde competidores (precios actuales de todos)
    let serieCompetidores = buildSeriesFromCompetidores()

    // 3. Cargar historial de TODOS los competidores (mismo nombre, todos los proveedores)
    // Así la curva refleja la evolución del precio del producto en general,
    // no solo de un proveedor. El punto ACTUAL marca el precio del producto seleccionado.
    let serieHistorial: any[] = []
    try {
      // Intentar endpoint de historial combinado (todos los proveedores del mismo producto)
      const fullData = await api(`/products/${props.product.id_prod}/price-history?dias=${dias}&todos_proveedores=true`)
      serieHistorial = (fullData.series || []).map((s: any) => ({
        fecha: s.fecha,
        precio: s.precio
      }))
    } catch (e) {
      // Fallback: historial solo del proveedor actual
      try {
        const fullData = await api(`/products/${props.product.id_prod}/price-full?dias=${dias}`)
        serieHistorial = (fullData.series || []).map((s: any) => ({
          fecha: s.fecha,
          precio: s.precio
        }))
      } catch (e2) {
        console.log('Sin historial, usando precios actuales de competidores')
      }
    }

    // 4. COMBINAR: priorizar historial real sobre snapshot de competidores
    // El último punto siempre es el precio actual del producto seleccionado
    const precioActual = {
      fecha: new Date().toISOString(),
      precio: parseFloat(props.product.precio_prod) || 0
    }

    if (serieHistorial.length >= 2) {
      // Asegurar que el último punto sea el precio actual de este producto
      chartData.value = [...serieHistorial, precioActual]
    } else {
      // Sin historial: mostrar evolución de precios entre competidores + precio actual
      chartData.value = [...serieCompetidores, precioActual]
    }

    priceHistory.value = chartData.value

    // 5. Calcular stats
    const precios = chartData.value.map((p: any) => p.precio).filter((p: number) => p > 0)
    const min = precios.length ? Math.min(...precios) : 0
    const max = precios.length ? Math.max(...precios) : 0
    const avg = precios.length ? precios.reduce((a: number, b: number) => a + b, 0) / precios.length : 0

    // Variación: primer vs último punto
    let variacion30d = 0
    if (precios.length >= 2) {
      const first = precios[0]
      const last = precios[precios.length - 1]
      if (first > 0) variacion30d = ((last - first) / first) * 100
    }

    stats.value = {
      min,
      max,
      avg: Math.round(avg * 100) / 100,
      variacion30d: Math.round(variacion30d * 10) / 10
    }

  } catch (err) {
    console.error('Error cargando detalle:', err)
    // Fallback: al menos mostrar el producto actual
    chartData.value = [{
      fecha: props.product.fecha_prod || new Date().toISOString(),
      precio: parseFloat(props.product.precio_prod) || 0
    }]
    priceHistory.value = chartData.value
    stats.value = {
      min: parseFloat(props.product.precio_prod) || 0,
      max: parseFloat(props.product.precio_prod) || 0,
      avg: parseFloat(props.product.precio_prod) || 0,
      variacion30d: 0
    }
  } finally {
    loading.value = false
  }
}

// Alertas
const mostrarAlertaForm = ref(false)
const precioAlerta = ref<number | null>(null)
const creandoAlerta = ref(false)
const alertaMensaje = ref<{ texto: string; tipo: string } | null>(null)

async function crearAlerta() {
  if (!precioAlerta.value || precioAlerta.value <= 0) return
  creandoAlerta.value = true
  try {
    const { api } = useApi()
    await api('/alertas', {
      method: 'POST',
      body: {
        id_prod: props.product.id_prod,
        precio_objetivo: precioAlerta.value
      }
    })
    alertaMensaje.value = { texto: '✅ Alerta guardada', tipo: 'success' }
    mostrarAlertaForm.value = false
    precioAlerta.value = null
    setTimeout(() => alertaMensaje.value = null, 3000)
  } catch (err: any) {
    alertaMensaje.value = { texto: err?.data?.detail || 'Error', tipo: 'error' }
  } finally {
    creandoAlerta.value = false
  }
}

// ── Watchers ──
watch(() => props.product, (newProd) => {
  if (newProd?.id_prod) {
    cargarHistorial(30)
  }
}, { immediate: true })

// ── Lifecycle ──
onMounted(() => {
  if (props.product?.id_prod) {
    cargarHistorial(30)
  }
})
</script>

<style scoped>
/* ── Overlay ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(12px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
  overflow-y: auto;
}

/* ── Content ── */
.modal-content {
  background: var(--bg-card, #16162a);
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

/* ── Header ── */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.header-info {
  min-width: 0;
}

.modal-categoria {
  font-size: 0.7rem;
  color: var(--text-muted, rgba(245,240,235,0.4));
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.modal-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--text-primary, #f5f0eb);
  margin: 0.25rem 0 0;
  line-height: 1.2;
}

.modal-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary, rgba(245,240,235,0.6));
  margin: 0.25rem 0 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
}

/* ── Price Section ── */
.price-section {
  margin-bottom: 1.5rem;
}

.price-main {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.current-price {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--accent-gold, #e8c4a0);
  letter-spacing: -0.02em;
}

.unit-badge {
  font-size: 0.8rem;
  color: var(--text-muted);
  background: rgba(255,255,255,0.05);
  padding: 0.2rem 0.6rem;
  border-radius: 8px;
}

.comparison-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.75rem;
  font-weight: 700;
}

.badge-mejor {
  background: rgba(52, 211, 153, 0.12);
  border: 1px solid rgba(52, 211, 153, 0.25);
  color: #34d399;
}

.badge-carro {
  background: rgba(251, 113, 133, 0.1);
  border: 1px solid rgba(251, 113, 133, 0.2);
  color: #fb7185;
}

.badge-unico {
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

/* ── Chart Section ── */
.chart-section {
  background: rgba(0, 0, 0, 0.2);
  border-radius: 16px;
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.section-header h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chart-tabs {
  display: flex;
  gap: 0.25rem;
}

.chart-tabs button {
  padding: 0.3rem 0.7rem;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.chart-tabs button:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-secondary);
}

.chart-tabs button.active {
  background: rgba(167, 139, 250, 0.15);
  color: #a78bfa;
  font-weight: 600;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 2rem;
  color: var(--text-muted);
}

.spinner {
  width: 28px;
  height: 28px;
  border: 2px solid rgba(167, 139, 250, 0.2);
  border-top-color: #a78bfa;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--text-muted);
  text-align: center;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

.empty-state .hint {
  font-size: 0.75rem;
  opacity: 0.6;
}

/* ── Stats Grid ── */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.stat-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  padding: 0.875rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-value.min { color: #34d399; }
.stat-value.max { color: #fb7185; }
.stat-value.avg { color: #a78bfa; }
.stat-value.sube { color: #fb7185; }
.stat-value.baja { color: #34d399; }

/* ── Competitors ── */
.competitors-section {
  margin-bottom: 1.25rem;
}

.competitors-section h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.75rem;
}

.competitors-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.competitor-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.625rem 0.875rem;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 10px;
  transition: all 0.2s;
}

.competitor-row.es-actual {
  background: rgba(167, 139, 250, 0.08);
  border-color: rgba(167, 139, 250, 0.2);
}

.comp-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.comp-proveedor {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
}

.comp-tag {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 0.1rem 0.4rem;
  border-radius: 6px;
}

.tag-mejor {
  background: rgba(52, 211, 153, 0.12);
  color: #34d399;
}

.tag-carro {
  background: rgba(251, 113, 133, 0.12);
  color: #fb7185;
}

.comp-precio {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.comp-monto {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.comp-pct {
  font-size: 0.7rem;
  color: #fb7185;
  background: rgba(251, 113, 133, 0.1);
  padding: 0.1rem 0.35rem;
  border-radius: 6px;
}

/* ── Description ── */
.description-section {
  margin-bottom: 1.25rem;
}

.description-section h3 {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.description-section p {
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0;
}

.alerta-precio-section { margin-top: 0.75rem; }
.btn-alerta {
  padding: 0.4rem 0.875rem;
  border-radius: 999px;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.25);
  color: #fbbf24;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.btn-alerta:hover { background: rgba(251, 191, 36, 0.18); }
.alerta-form {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}
.alerta-input {
  width: 120px;
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 0.85rem;
}
.btn-alerta-confirm {
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  background: rgba(52, 211, 153, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-alerta-cancel {
  padding: 0.4rem;
  background: none;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}
.alerta-msg {
  font-size: 0.75rem;
  margin: 0.35rem 0 0;
}
.alerta-msg.success { color: #34d399; }
.alerta-msg.error { color: #fb7185; }

/* ── Footer ── */
.modal-footer {
  display: flex;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(255,255,255,0.06);
}

.btn-compare {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: 12px;
  background: rgba(167, 139, 250, 0.12);
  border: 1px solid rgba(167, 139, 250, 0.25);
  color: #a78bfa;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-compare:hover {
  background: rgba(167, 139, 250, 0.2);
  transform: translateY(-1px);
}

.btn-close {
  padding: 0.75rem 1.25rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  color: var(--text-muted);
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-close:hover {
  background: rgba(255,255,255,0.08);
  color: var(--text-secondary);
}

/* ── Transitions ── */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.modal-enter-active .modal-content,
.modal-leave-active .modal-content {
  transition: all 0.3s ease;
}

/* Scrollbar */
.modal-content::-webkit-scrollbar {
  width: 6px;
}

.modal-content::-webkit-scrollbar-track {
  background: transparent;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(255,255,255,0.1);
  border-radius: 3px;
}

/* Responsive */
@media (max-width: 480px) {
  .modal-content {
    padding: 1rem;
    border-radius: 16px;
  }
  
  .current-price {
    font-size: 1.8rem;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>