<template>
  <div class="categorias-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-top">
          <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div class="header-text">
            <h1 class="page-title">Categorías</h1>
            <p class="page-subtitle">Explorá por tipo de producto</p>
          </div>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando categorías...</p>
      </div>

      <!-- GRID DE CATEGORÍAS -->
      <div v-else class="categorias-grid animate-fade-in-up stagger-1">
        <NuxtLink
          v-for="(cat, index) in categoriasOrdenadas"
          :key="cat.id_cate"
          :to="`/productos/lista?categoria=${encodeURIComponent(cat.nombre_cate)}`"
          class="categoria-card"
          :class="`stagger-${Math.min(index + 2, 8)}`"
        >
          <div class="cat-icon-wrap" :style="{ background: cat.color + '15', borderColor: cat.color + '30' }">
            <span class="cat-icon">{{ cat.icono_cate || getDefaultIcon(cat.nombre_cate) }}</span>
          </div>
          <div class="cat-info">
            <h3 class="cat-name">{{ cat.nombre_cate }}</h3>
            <span class="cat-count">{{ cat.cantidad_prod || 0 }} productos</span>
          </div>
          <svg class="cat-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </NuxtLink>
      </div>

      <!-- EMPTY STATE -->
      <div v-if="!loading && categorias.length === 0" class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"/>
            <path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"/>
            <path d="M12 3v6"/>
          </svg>
        </div>
        <h3>No hay categorías disponibles</h3>
        <p>Volvé a intentar más tarde</p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo } from '#app'

interface Categoria {
  id_cate: string
  nombre_cate: string
  icono_cate: string | null
  color: string | null
  cantidad_prod: number
}

const loading = ref(true)
const categorias = ref<Categoria[]>([])

// Iconos por defecto según nombre
const iconMap: Record<string, string> = {
  'bebidas': '🥤',
  'alimentos': '🍝',
  'limpieza': '🧼',
  'perfumeria': '🧴',
  'lacteos': '🥛',
  'snacks': '🍿',
  'carnes': '🥩',
  'panaderia': '🥐',
  'frutas': '🍎',
  'verduras': '🥬',
  'congelados': '🧊',
  'hogar': '🏠',
  'mascotas': '🐕',
  'bebes': '🍼',
  'farmacia': '💊',
}

const colorMap: Record<string, string> = {
  'bebidas': '#60a5fa',
  'alimentos': '#fbbf24',
  'limpieza': '#34d399',
  'perfumeria': '#a78bfa',
  'lacteos': '#94a3b8',
  'snacks': '#fb923c',
  'carnes': '#f87171',
  'panaderia': '#fbbf24',
  'frutas': '#4ade80',
  'verduras': '#22c55e',
  'congelados': '#38bdf8',
  'hogar': '#a78bfa',
  'mascotas': '#fb923c',
  'bebes': '#f472b6',
  'farmacia': '#ef4444',
}

const getDefaultIcon = (nombre: string): string => {
  const key = nombre.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  return iconMap[key] || '📦'
}

const getColor = (nombre: string): string => {
  const key = nombre.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '')
  return colorMap[key] || '#e8c4a0'
}

// Ordenar alfabéticamente
const categoriasOrdenadas = computed(() => {
  return [...categorias.value]
    .map(c => ({
      ...c,
      color: c.color || getColor(c.nombre_cate),
      icono_cate: c.icono_cate || getDefaultIcon(c.nombre_cate)
    }))
    .sort((a, b) => a.nombre_cate.localeCompare(b.nombre_cate, 'es'))
})

onMounted(async () => {
  try {
    // Intentar cargar desde API
    const { api } = useApi()
    const res = await api<{ count: number; results: Categoria[] }>('/categorias')
    categorias.value = res.results || []
  } catch (err) {
    console.error('Error cargando categorías:', err)
    // Fallback: cargar desde localStorage si existe
    const stored = localStorage.getItem('comparapp_categorias')
    if (stored) {
      try { categorias.value = JSON.parse(stored) } catch {}
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.categorias-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-card-hover: rgba(255, 255, 255, 0.06);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-glow: rgba(232, 196, 160, 0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245, 240, 235, 0.6);
  --text-muted: rgba(245, 240, 235, 0.35);
  --accent-gold: #e8c4a0;
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
  gap: 1.5rem;
  max-width: 600px;
  margin: 0 auto;
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
.stagger-4 { animation-delay: 0.2s; }
.stagger-5 { animation-delay: 0.25s; }
.stagger-6 { animation-delay: 0.3s; }
.stagger-7 { animation-delay: 0.35s; }
.stagger-8 { animation-delay: 0.4s; }

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

/* ─── GRID ─── */
.categorias-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.875rem;
}

/* ─── CARD ─── */
.categoria-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1.25rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  text-decoration: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.categoria-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.categoria-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  box-shadow: var(--shadow-glow);
  transform: translateY(-3px);
}

.categoria-card:active {
  transform: translateY(-1px) scale(0.98);
}

.cat-icon-wrap {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid;
  transition: all 0.25s ease;
}

.categoria-card:hover .cat-icon-wrap {
  transform: scale(1.05);
}

.cat-icon {
  font-size: 1.75rem;
  line-height: 1;
}

.cat-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.cat-name {
  color: var(--text-primary);
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.2;
}

.cat-count {
  color: var(--text-muted);
  font-size: 0.78rem;
}

.cat-arrow {
  position: absolute;
  top: 1.25rem;
  right: 1.25rem;
  color: var(--text-muted);
  opacity: 0;
  transform: translateX(-4px);
  transition: all 0.25s ease;
}

.categoria-card:hover .cat-arrow {
  opacity: 1;
  transform: translateX(0);
  color: var(--text-secondary);
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

/* ─── RESPONSIVE ─── */
@media (max-width: 380px) {
  .categorias-grid { grid-template-columns: 1fr; }
  .page-content { padding: 1rem; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>
