<template>
  <div class="alertas-page">
    <DynamicBackground />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/dashboard')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div class="header-center">
          <h1 class="page-title">🔔 Alertas</h1>
          <p class="page-subtitle">{{ alertasNoLeidas }} alerta{{ alertasNoLeidas !== 1 ? 's' : '' }} sin leer</p>
        </div>
      </header>

      <!-- FILTROS -->
      <div class="filter-chips animate-fade-in-up stagger-1">
        <button
          v-for="f in filtros"
          :key="f.value"
          class="filter-chip"
          :class="{ active: filtroActivo === f.value }"
          @click="filtroActivo = f.value"
        >
          {{ f.icon }} {{ f.label }}
          <span class="chip-count">{{ contarPorTipo(f.value) }}</span>
        </button>
      </div>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando alertas...</span>
      </div>

      <template v-else>
        <!-- LISTA DE ALERTAS -->
        <div v-if="alertasFiltradas.length > 0" class="alertas-lista animate-fade-in-up stagger-2">
          <div
            v-for="alerta in alertasFiltradas"
            :key="alerta.id_alerta"
            class="alerta-card"
            :class="{ noleida: !alerta.leida }"
            @click="marcarLeida(alerta)"
          >
            <!-- Icono tipo -->
            <div class="alerta-icon" :class="alerta.tipo">
              <span v-if="alerta.tipo === 'precio'">💰</span>
              <span v-else-if="alerta.tipo === 'stock'">📦</span>
              <span v-else-if="alerta.tipo === 'lista'">🛒</span>
              <span v-else>🔔</span>
            </div>

            <!-- Info -->
            <div class="alerta-info">
              <p class="alerta-titulo">{{ alerta.titulo }}</p>
              <p class="alerta-desc">{{ alerta.descripcion }}</p>
              <div class="alerta-meta">
                <span class="alerta-fecha">{{ formatFecha(alerta.fecha_creacion) }}</span>
                <span v-if="!alerta.leida" class="alerta-badge">Nueva</span>
              </div>
            </div>

            <!-- Acciones -->
            <div class="alerta-actions">
              <button
                v-if="alerta.tipo === 'precio' && alerta.id_prod"
                class="alerta-action-btn"
                title="Ver producto"
                @click.stop="navigateTo(`/productos/${alerta.id_prod}`)"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>
                  <polyline points="15 3 21 3 21 9"/>
                  <line x1="10" y1="14" x2="21" y2="3"/>
                </svg>
              </button>
              <button
                v-if="alerta.id_lista"
                class="alerta-action-btn"
                title="Ver lista"
                @click.stop="navigateTo(`/listas/${alerta.id_lista}`)"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M9 11l3 3L22 4"/>
                  <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                </svg>
              </button>
              <button
                class="alerta-delete-btn"
                title="Eliminar"
                @click.stop="eliminarAlerta(alerta.id_alerta)"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <!-- VACÍO -->
        <div v-else class="state-box animate-fade-in-up stagger-2">
          <div class="empty-icon">🔕</div>
          <h3>Sin alertas</h3>
          <p v-if="filtroActivo === 'todas'">No tenés alertas configuradas</p>
          <p v-else>No hay alertas de tipo {{ filtroActivo }}</p>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo } from '#app'

interface Alerta {
  id_alerta: string
  user_id: string
  tipo: 'precio' | 'stock' | 'lista' | 'sistema'
  titulo: string
  descripcion: string
  id_prod?: string | null
  id_lista?: string | null
  leida: boolean
  fecha_creacion: string
}

const { api } = useApi()

const loading = ref(true)
const alertas = ref<Alerta[]>([])
const filtroActivo = ref('todas')

const filtros = [
  { value: 'todas', label: 'Todas', icon: '🔔' },
  { value: 'precio', label: 'Precios', icon: '💰' },
  { value: 'stock', label: 'Stock', icon: '📦' },
  { value: 'lista', label: 'Listas', icon: '🛒' },
]

const alertasFiltradas = computed(() => {
  if (filtroActivo.value === 'todas') return alertas.value
  return alertas.value.filter(a => a.tipo === filtroActivo.value)
})

const alertasNoLeidas = computed(() => alertas.value.filter(a => !a.leida).length)

function contarPorTipo(tipo: string) {
  if (tipo === 'todas') return alertas.value.length
  return alertas.value.filter(a => a.tipo === tipo).length
}

function formatFecha(fecha: string) {
  const d = new Date(fecha)
  const ahora = new Date()
  const diff = ahora.getTime() - d.getTime()
  const min = Math.floor(diff / 60000)
  const hrs = Math.floor(diff / 3600000)
  const dias = Math.floor(diff / 86400000)
  if (min < 1) return 'Ahora'
  if (min < 60) return `Hace ${min} min`
  if (hrs < 24) return `Hace ${hrs} h`
  if (dias < 7) return `Hace ${dias} d`
  return d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

async function cargar() {
  loading.value = true
  try {
    const data = await api<{ alertas: Alerta[] }>('/alertas')
    alertas.value = data.alertas || []
  } catch (err) {
    console.error('Error cargando alertas:', err)
  } finally {
    loading.value = false
  }
}

async function marcarLeida(alerta: Alerta) {
  if (alerta.leida) return
  try {
    await api(`/alertas/${alerta.id_alerta}/leer`, { method: 'POST' })
    alerta.leida = true
  } catch {}
}

async function eliminarAlerta(id: string) {
  try {
    await api(`/alertas/${id}`, { method: 'DELETE' })
    alertas.value = alertas.value.filter(a => a.id_alerta !== id)
  } catch {}
}

onMounted(cargar)
</script>

<style scoped>
/* Sin tokens locales — usa las variables globales del tema */
.alertas-page {
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page-content {
  position: relative; z-index: 2;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1rem;
  max-width: 560px; margin: 0 auto;
  padding-bottom: 5rem;
}

/* HEADER */
.page-header { display:flex; align-items:flex-start; gap:0.875rem; padding:0.5rem 0; }
.back-btn {
  width:40px; height:40px; border-radius:50%; flex-shrink:0; margin-top:0.2rem;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.25s;
}
.back-btn:hover { background:rgba(255,255,255,0.08); border-color:var(--border-glow); color:var(--text-primary); }
.header-center { flex:1; min-width:0; }
.page-title { font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-0.02em; }
.page-subtitle { color:var(--text-secondary); font-size:0.82rem; margin:0.25rem 0 0; }

/* FILTROS */
.filter-chips { display:flex; gap:0.5rem; flex-wrap:wrap; }
.filter-chip {
  display:flex; align-items:center; gap:0.375rem;
  padding:0.375rem 0.75rem; border-radius:999px;
  border:1px solid var(--border-subtle);
  background:rgba(255,255,255,0.02);
  color:var(--text-secondary); font-size:0.78rem; font-weight:500;
  cursor:pointer; transition:all 0.2s;
}
.filter-chip.active {
  background:rgba(232,196,160,0.12); border-color:rgba(232,196,160,0.3);
  color:var(--accent-gold);
}
.chip-count {
  background:rgba(255,255,255,0.08); border-radius:999px;
  padding:0.1rem 0.4rem; font-size:0.7rem;
}

/* ALERTAS LISTA */
.alertas-lista { display:flex; flex-direction:column; gap:0.5rem; }
.alerta-card {
  display:flex; align-items:flex-start; gap:0.875rem;
  padding:1rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-md); transition:all 0.2s;
  cursor:pointer;
}
.alerta-card:hover { background:var(--bg-card-hover); border-color:rgba(255,255,255,0.12); }
.alerta-card.noleida {
  background:rgba(232,196,160,0.04);
  border-left:3px solid var(--accent-gold);
}

.alerta-icon {
  width:40px; height:40px; border-radius:var(--radius-sm); flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:1.2rem; background:rgba(255,255,255,0.04);
  border:1px solid var(--border-subtle);
}
.alerta-icon.precio { background:rgba(52,211,153,0.08); border-color:rgba(52,211,153,0.2); }
.alerta-icon.stock { background:rgba(96,165,250,0.08); border-color:rgba(96,165,250,0.2); }
.alerta-icon.lista { background:rgba(232,196,160,0.08); border-color:rgba(232,196,160,0.2); }

.alerta-info { flex:1; min-width:0; }
.alerta-titulo { color:var(--text-primary); font-size:0.9rem; font-weight:600; margin:0; }
.alerta-desc { color:var(--text-secondary); font-size:0.8rem; margin:0.2rem 0 0; line-height:1.4; }
.alerta-meta { display:flex; align-items:center; gap:0.5rem; margin-top:0.4rem; }
.alerta-fecha { color:var(--text-muted); font-size:0.72rem; }
.alerta-badge {
  background:var(--accent-gold); color:#1a1a1a;
  font-size:0.65rem; font-weight:700; text-transform:uppercase;
  padding:0.15rem 0.4rem; border-radius:4px;
}

.alerta-actions {
  display:flex; flex-direction:column; gap:0.375rem;
  opacity:0; transition:opacity 0.2s;
}
.alerta-card:hover .alerta-actions { opacity:1; }
.alerta-action-btn, .alerta-delete-btn {
  width:28px; height:28px; border-radius:6px;
  display:flex; align-items:center; justify-content:center;
  background:transparent; border:1px solid var(--border-subtle);
  color:var(--text-muted); cursor:pointer; transition:all 0.2s;
}
.alerta-action-btn:hover { background:rgba(232,196,160,0.1); color:var(--accent-gold); border-color:rgba(232,196,160,0.3); }
.alerta-delete-btn:hover { background:rgba(251,113,133,0.1); color:var(--accent-error); border-color:rgba(251,113,133,0.3); }

/* STATES */
.state-box {
  display:flex; flex-direction:column; align-items:center; gap:0.75rem;
  padding:2.5rem 1rem; text-align:center;
}
.state-box span { color:var(--text-secondary); font-size:0.9rem; }
.state-box h3 { margin:0; font-size:1.1rem; color:var(--text-primary); }
.state-box p { margin:0; color:var(--text-muted); font-size:0.85rem; }
.empty-icon { font-size:2.5rem; }

/* LOADING */
.loading-spinner {
  width:28px; height:28px; border-radius:50%;
  border:2px solid rgba(255,255,255,0.08);
  border-top-color:var(--accent-gold);
  animation:spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ANIMATIONS */
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }

@media (max-width: 480px) {
  .alerta-actions { opacity:1; }
}
</style>