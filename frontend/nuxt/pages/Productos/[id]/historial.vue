<template>
  <div class="historial-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="goBack" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Historial de precios</h1>
            <p class="page-subtitle">{{ productName }}</p>
          </div>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="pending" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando historial...</p>
      </div>

      <!-- ERROR -->
      <div v-else-if="error" class="empty-state animate-fade-in-up">
        <div class="empty-icon">📊</div>
        <h3>Error al cargar el historial</h3>
        <p>No se pudieron obtener los datos del producto</p>
        <button class="back-btn-text" @click="refresh()">Reintentar</button>
      </div>

      <template v-else-if="data">
        <!-- Hero de variación -->
        <div class="variacion-hero animate-fade-in-up stagger-1">
          <div class="hero-precio">{{ formatPrice(data.stats.current_price) }}</div>
          <div class="hero-stats-row">
            <div class="hero-stat">
              <span class="hero-stat-label">Mínimo</span>
              <span class="hero-stat-value min">{{ formatPrice(data.stats.min_price) }}</span>
            </div>
            <div class="hero-stat-sep" />
            <div class="hero-stat">
              <span class="hero-stat-label">Máximo</span>
              <span class="hero-stat-value max">{{ formatPrice(data.stats.max_price) }}</span>
            </div>
            <div class="hero-stat-sep" />
            <div class="hero-stat">
              <span class="hero-stat-label">Variación</span>
              <span class="hero-stat-value" :class="data.stats.price_change >= 0 ? 'sube' : 'baja'">
                {{ data.stats.price_change >= 0 ? '+' : '' }}{{ data.stats.price_change.toFixed(1) }}%
              </span>
            </div>
            <div class="hero-stat-sep" />
            <div class="hero-stat">
              <span class="hero-stat-label">Registros</span>
              <span class="hero-stat-value">{{ data.stats.total_records }}</span>
            </div>
          </div>
        </div>

        <!-- Gráfico -->
        <div class="chart-section animate-fade-in-up stagger-2">
          <PriceChart :data="data.series" />
        </div>

        <!-- Tabla de precios -->
        <div class="tabla-section animate-fade-in-up stagger-3">
          <h3 class="section-title">Registro de cambios</h3>
          <div class="precios-lista">
            <div
              v-for="(item, index) in reversedSeries"
              :key="index"
              class="precio-row"
              :class="{
                'precio-actual': index === 0,
                'precio-min': item.precio === data.stats.min_price,
                'precio-max': item.precio === data.stats.max_price
              }"
            >
              <div class="precio-fecha">
                <span class="fecha-dia">{{ formatDia(item.fecha) }}</span>
                <span class="fecha-hora">{{ formatHora(item.fecha) }}</span>
              </div>
              <div class="precio-valor">
                {{ formatPrice(item.precio) }}
              </div>
              <div class="precio-badge">
                <span v-if="index === 0" class="badge-actual">ACTUAL</span>
                <span v-else-if="item.precio === data.stats.min_price" class="badge-min">MÍN</span>
                <span v-else-if="item.precio === data.stats.max_price" class="badge-max">MÁX</span>
              </div>
              <div v-if="index < reversedSeries.length - 1" class="precio-delta" :class="getDeltaClass(item.precio, reversedSeries[index + 1].precio)">
                <svg v-if="item.precio > reversedSeries[index + 1].precio" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M5 10l7-7m0 0l7 7m-7-7v18"/>
                </svg>
                <svg v-else-if="item.precio < reversedSeries[index + 1].precio" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M19 14l-7 7m0 0l-7-7m7 7V3"/>
                </svg>
                <svg v-else width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M5 12h14"/>
                </svg>
                {{ getDeltaText(item.precio, reversedSeries[index + 1].precio) }}
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- Sin datos -->
      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon">📊</div>
        <h3>No hay historial disponible</h3>
        <p>Este producto aún no tiene registros de precios</p>
        <button class="back-btn-text" @click="goBack">Volver</button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, navigateTo, useRuntimeConfig } from '#app'

const route = useRoute()
const config = useRuntimeConfig()

const productId = computed(() => route.params.id as string)

const { data, pending, error, refresh } = await useFetch(
  () => `${config.public.apiBase}/api/v1/products/${productId.value}/price-full`,
  {
    key: `price-full-${productId.value}`,
    server: false,
    lazy: true
  }
)

const productName = computed(() => {
  if (!data.value?.product) return 'Producto'
  return data.value.product.nombre || 'Producto'
})

const reversedSeries = computed(() => {
  if (!data.value?.series) return []
  return [...data.value.series].reverse()
})

function formatPrice(price: number): string {
  return '$' + price.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function formatDia(iso: string): string {
  try {
    return new Date(iso).toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
  } catch { return '' }
}

function formatHora(iso: string): string {
  try {
    return new Date(iso).toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' })
  } catch { return '' }
}

function getDeltaClass(current: number, previous: number): string {
  if (current > previous) return 'delta-sube'
  if (current < previous) return 'delta-baja'
  return 'delta-igual'
}

function getDeltaText(current: number, previous: number): string {
  const diff = current - previous
  const pct = previous !== 0 ? ((diff / previous) * 100).toFixed(1) : '0.0'
  if (diff > 0) return `+${pct}%`
  if (diff < 0) return `${pct}%`
  return '0%'
}

function goBack() {
  navigateTo(`/productos/${productId.value}`)
}
</script>

<style scoped>
.historial-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.03);
  --border-subtle: rgba(255,255,255,0.08);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.6);
  --text-muted: rgba(245,240,235,0.35);
  --accent-gold: #e8c4a0;
  --accent-emerald: #34d399;
  --accent-rose: #fb7185;
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;

  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.bg-gradient {
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232, 196, 160, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167, 139, 250, 0.05), transparent),
    linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 40%, #0a0a0f 100%);
  z-index: 0;
}

.bg-noise {
  position: fixed; inset: 0; opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  z-index: 1; pointer-events: none;
}

.page-content {
  position: relative; z-index: 2;
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

.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }

/* HEADER */
.page-header { display: flex; align-items: center; padding: 0.5rem 0; }
.header-left { display: flex; align-items: center; gap: 0.875rem; }
.back-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s; flex-shrink: 0;
}
.back-btn:hover { background: rgba(255,255,255,0.08); border-color: rgba(232,196,160,0.25); color: var(--text-primary); transform: scale(1.05); }
.page-title { font-size: 1.4rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
.page-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin: 0.15rem 0 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 260px; }

/* LOADING */
.loading-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.875rem; padding: 4rem 1rem; color: var(--text-muted);
}
.loading-spinner {
  width: 32px; height: 32px;
  border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--accent-gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

/* VARIACIÓN HERO */
.variacion-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  padding: 1.5rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  text-align: center;
}

.hero-precio {
  font-size: 2.5rem;
  font-weight: 800;
  color: var(--accent-gold);
  letter-spacing: -0.03em;
}

.hero-stats-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
}

.hero-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.15rem;
}

.hero-stat-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.hero-stat-value {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
}

.hero-stat-value.min { color: var(--accent-emerald); }
.hero-stat-value.max { color: var(--accent-rose); }
.hero-stat-value.sube { color: var(--accent-rose); }
.hero-stat-value.baja { color: var(--accent-emerald); }

.hero-stat-sep {
  width: 1px;
  height: 24px;
  background: var(--border-subtle);
}

/* CHART SECTION */
.chart-section {
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.25rem 1rem;
}

/* TABLA DE PRECIOS */
.tabla-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.section-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.precios-lista {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.precio-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  transition: all 0.2s;
}

.precio-row.precio-actual {
  background: rgba(232, 196, 160, 0.05);
  border-color: rgba(232, 196, 160, 0.18);
}

.precio-row.precio-min {
  background: rgba(52, 211, 153, 0.04);
  border-color: rgba(52, 211, 153, 0.12);
}

.precio-row.precio-max {
  background: rgba(251, 113, 133, 0.04);
  border-color: rgba(251, 113, 133, 0.12);
}

.precio-fecha {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
  min-width: 55px;
}

.fecha-dia {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-primary);
}

.fecha-hora {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.precio-valor {
  flex: 1;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
}

.precio-badge {
  display: flex;
  align-items: center;
}

.badge-actual {
  padding: 0.2rem 0.5rem;
  background: rgba(232, 196, 160, 0.12);
  border: 1px solid rgba(232, 196, 160, 0.25);
  border-radius: 999px;
  color: var(--accent-gold);
  font-size: 0.6rem;
  font-weight: 700;
}

.badge-min {
  padding: 0.2rem 0.5rem;
  background: rgba(52, 211, 153, 0.12);
  border: 1px solid rgba(52, 211, 153, 0.25);
  border-radius: 999px;
  color: var(--accent-emerald);
  font-size: 0.6rem;
  font-weight: 700;
}

.badge-max {
  padding: 0.2rem 0.5rem;
  background: rgba(251, 113, 133, 0.12);
  border: 1px solid rgba(251, 113, 133, 0.25);
  border-radius: 999px;
  color: var(--accent-rose);
  font-size: 0.6rem;
  font-weight: 700;
}

.precio-delta {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.delta-sube { color: var(--accent-rose); }
.delta-baja { color: var(--accent-emerald); }
.delta-igual { color: var(--text-muted); }

/* EMPTY */
.empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 4rem 1rem; text-align: center;
}
.empty-icon { font-size: 3rem; }
.empty-state h3 { color: var(--text-primary); font-size: 1.1rem; font-weight: 600; margin: 0; }
.empty-state p { color: var(--text-secondary); font-size: 0.85rem; margin: 0; }
.back-btn-text {
  margin-top: 0.75rem; padding: 0.625rem 1.25rem;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm); color: var(--text-secondary);
  font-size: 0.85rem; font-weight: 500; cursor: pointer;
  transition: all 0.25s;
}
.back-btn-text:hover { background: rgba(255,255,255,0.06); border-color: rgba(232,196,160,0.25); color: var(--text-primary); }

@media (max-width: 480px) {
  .page-content { padding: 1rem; }
  .hero-precio { font-size: 2rem; }
  .hero-stats-row { gap: 0.5rem; }
  .hero-stat-sep { display: none; }
  .precio-row { padding: 0.625rem 0.875rem; }
  .precio-delta { display: none; }
}
</style>
