<template>
  <div class="ofertas-page">
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
            <h1 class="page-title">🔥 Ofertas</h1>
            <p class="page-subtitle">{{ ofertas.length }} ofertas vigentes</p>
          </div>
        </div>
      </header>

      <!-- FILTROS -->
      <div class="filters animate-fade-in-up stagger-1">
        <button 
          v-for="cat in categorias" 
          :key="cat"
          class="filter-chip"
          :class="{ active: categoriaActiva === cat }"
          @click="categoriaActiva = cat === 'Todas' ? null : cat"
        >
          {{ cat }}
        </button>
      </div>

      <!-- LISTA DE OFERTAS -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando ofertas...</p>
      </div>

      <div v-else-if="ofertasFiltradas.length > 0" class="ofertas-grid animate-fade-in-up stagger-2">
        <div 
          v-for="(oferta, index) in ofertasFiltradas" 
          :key="oferta.id_prod"
          class="oferta-card"
          :class="'stagger-' + Math.min(index + 3, 8)"
        >
          <!-- Badge de descuento -->
          <div class="descuento-badge" v-if="oferta.descuento_pct > 0">
            -{{ oferta.descuento_pct }}%
          </div>

          <!-- Imagen -->
          <div class="oferta-img" @click="navigateTo(`/productos/lista?q=${encodeURIComponent(oferta.producto?.nombre_prod || '')}`)">
            <img :src="oferta.producto?.imagen_prod || '/images/avatar_default.png'" :alt="oferta.producto?.nombre_prod || ''" />
          </div>

          <!-- Info -->
          <div class="oferta-info">
            <span class="oferta-categoria">{{ oferta.producto?.cate_prod }}</span>
            <h3 class="oferta-nombre">{{ oferta.producto?.nombre_prod }}</h3>
            <p class="oferta-proveedor" v-if="oferta.producto?.provee_prod">
              🏪 {{ oferta.producto.provee_prod }}
            </p>

            <!-- Precios -->
            <div class="oferta-precios">
              <span class="precio-normal">${{ formatPrice(oferta.precio_normal) }}</span>
              <span class="precio-oferta">${{ formatPrice(oferta.precio_oferta) }}</span>
            </div>

            <!-- Fecha fin -->
            <p class="oferta-vence" v-if="oferta.fecha_fin">
              Válido hasta {{ new Date(oferta.fecha_fin).toLocaleDateString('es-AR') }}
            </p>
          </div>

          <!-- Acciones -->
          <div class="oferta-actions">
            <button class="ver-btn" @click="navigateTo(`/productos/lista?q=${encodeURIComponent(oferta.producto?.nombre_prod || '')}`)">
              Ver producto
            </button>
          </div>
        </div>
      </div>

      <!-- EMPTY STATE -->
      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">🔥</div>
        <h3>No hay ofertas vigentes</h3>
        <p>Volvé más tarde para ver nuevas promociones</p>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { navigateTo, useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const loading = ref(true)
const ofertas = ref([])
const categoriaActiva = ref(null)

const categorias = computed(() => {
  const cats = ['Todas', ...new Set(ofertas.value.map(o => o.cate_prod || o.producto?.cate_prod).filter(Boolean))]
  return cats
})

const ofertasFiltradas = computed(() => {
  if (!categoriaActiva.value) return ofertas.value
  return ofertas.value.filter(o => (o.cate_prod || o.producto?.cate_prod) === categoriaActiva.value)
})

onMounted(async () => {
  try {
    const res = await $fetch(`${config.public.apiBase}/ofertas`)
    ofertas.value = res.results || []
  } catch (err) {
    console.error('Error cargando ofertas:', err)
  } finally {
    loading.value = false
  }
})

function formatPrice(price) {
  return Number(price)?.toLocaleString('es-AR') || '0'
}

function calcularDescuento(normal, oferta) {
  const n = Number(normal) || 0
  const o = Number(oferta) || 0
  if (n > 0 && o > 0 && o < n) {
    return Math.round((n - o) / n * 100)
  }
  return 0
}
</script>

<style scoped>
.ofertas-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245, 240, 235, 0.6);
  --accent-gold: #e8c4a0;
  --accent-fire: #fb923c;

  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', sans-serif;
}

.bg-gradient {
  position: fixed; inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(251, 146, 60, 0.08), transparent),
              radial-gradient(ellipse 60% 40% at 80% 80%, rgba(232, 196, 160, 0.05), transparent),
              linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 100%);
  z-index: 0;
}

.bg-noise {
  position: fixed; inset: 0; opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  z-index: 1; pointer-events: none;
}

.page-content {
  position: relative; z-index: 2;
  padding: 1.5rem; max-width: 600px; margin: 0 auto;
  display: flex; flex-direction: column; gap: 1.25rem;
  padding-bottom: 2.5rem;
}

/* Header */
.page-header {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.5rem 0;
}

.back-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s;
}

.back-btn:hover {
  background: rgba(255,255,255,0.08); border-color: rgba(232,196,160,0.25);
  color: var(--text-primary); transform: scale(1.05);
}

.page-title { font-size: 1.5rem; font-weight: 700; margin: 0; }
.page-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin: 0.15rem 0 0; }

/* Filtros */
.filters {
  display: flex; gap: 0.5rem; flex-wrap: wrap;
}

.filter-chip {
  padding: 0.4rem 0.875rem; border-radius: 999px;
  border: 1px solid var(--border-subtle);
  background: rgba(255,255,255,0.02);
  color: var(--text-secondary); font-size: 0.8rem;
  cursor: pointer; transition: all 0.25s;
}

.filter-chip:hover, .filter-chip.active {
  background: rgba(251, 146, 60, 0.15);
  border-color: rgba(251, 146, 60, 0.3);
  color: var(--accent-fire);
}

/* Grid */
.ofertas-grid {
  display: flex; flex-direction: column; gap: 0.875rem;
}

.oferta-card {
  position: relative;
  display: flex; gap: 1rem;
  padding: 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: 16px;
  transition: all 0.3s;
  overflow: hidden;
}

.oferta-card:hover {
  background: rgba(255,255,255,0.05);
  border-color: rgba(251, 146, 60, 0.2);
  transform: translateY(-2px);
}

/* Badge descuento */
.descuento-badge {
  position: absolute; top: 0.75rem; right: 0.75rem;
  padding: 0.25rem 0.625rem;
  background: linear-gradient(135deg, #ef4444, #dc2626);
  color: white; font-size: 0.8rem; font-weight: 700;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.3);
}

/* Imagen */
.oferta-img {
  width: 80px; height: 80px;
  border-radius: 12px; overflow: hidden;
  background: rgba(255,255,255,0.05);
  flex-shrink: 0; cursor: pointer;
}

.oferta-img img {
  width: 100%; height: 100%; object-fit: cover;
}

/* Info */
.oferta-info {
  flex: 1; min-width: 0;
  display: flex; flex-direction: column; gap: 0.2rem;
}

.oferta-categoria {
  display: inline-flex; align-self: flex-start;
  padding: 0.15rem 0.5rem;
  background: rgba(251, 146, 60, 0.1);
  border: 1px solid rgba(251, 146, 60, 0.2);
  border-radius: 999px;
  color: var(--accent-fire); font-size: 0.7rem; font-weight: 600;
}

.oferta-nombre {
  font-size: 0.95rem; font-weight: 600; margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.oferta-marca { color: var(--text-secondary); font-size: 0.8rem; margin: 0; }
.oferta-proveedor { color: rgba(245,240,235,0.4); font-size: 0.75rem; margin: 0; }

/* Precios */
.oferta-precios {
  display: flex; align-items: baseline; gap: 0.75rem; margin-top: 0.25rem;
}

.precio-normal {
  color: rgba(245,240,235,0.4); font-size: 0.85rem;
  text-decoration: line-through;
}

.precio-oferta {
  color: #4ade80; font-size: 1.2rem; font-weight: 700;
}

/* Acciones */
.oferta-actions {
  display: flex; flex-direction: column; gap: 0.5rem;
  align-items: flex-end; justify-content: center;
}

.ver-btn {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, rgba(251,146,60,0.2), rgba(251,146,60,0.1));
  border: 1px solid rgba(251,146,60,0.3);
  border-radius: 10px;
  color: var(--accent-fire); font-size: 0.8rem; font-weight: 600;
  cursor: pointer; transition: all 0.25s;
}

.ver-btn:hover {
  background: linear-gradient(135deg, rgba(251,146,60,0.3), rgba(251,146,60,0.2));
  transform: translateY(-1px);
}

/* Loading & Empty */
.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 4rem 1rem; text-align: center;
}

.loading-spinner {
  width: 32px; height: 32px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: var(--accent-fire); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.empty-icon-wrap {
  font-size: 3rem;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* Animaciones */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-up {
  opacity: 0; animation: fadeInUp 0.5s ease-out forwards;
}

.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }
.stagger-4 { animation-delay: 0.2s; }
.stagger-5 { animation-delay: 0.25s; }
.stagger-6 { animation-delay: 0.3s; }
.stagger-7 { animation-delay: 0.35s; }
.stagger-8 { animation-delay: 0.4s; }
</style>