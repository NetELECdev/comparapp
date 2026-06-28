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
          <h1 class="page-title">🔔 Alertas de precio</h1>
          <p class="page-subtitle">{{ alertas.length }} alerta{{ alertas.length !== 1 ? 's' : '' }} activa{{ alertas.length !== 1 ? 's' : '' }}</p>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando alertas...</span>
      </div>

      <template v-else>
        <!-- LISTA DE ALERTAS -->
        <div v-if="alertas.length > 0" class="alertas-lista animate-fade-in-up stagger-2">
          <div
            v-for="alerta in alertas"
            :key="alerta.id"
            class="alerta-card"
            @click="alerta.id_prod && navigateTo(`/productos/${alerta.id_prod}`)"
          >
            <!-- Imagen del producto -->
            <div class="alerta-img">
              <img
                :src="alerta.producto?.imagen_prod || '/images/avatar_default.png'"
                :alt="alerta.producto?.nombre_prod"
                loading="lazy"
                @error="(e) => ((e.target as HTMLImageElement).src = '/images/avatar_default.png')"
              />
            </div>

            <!-- Info -->
            <div class="alerta-info">
              <p class="alerta-titulo">{{ alerta.producto?.nombre_prod || 'Producto' }}</p>
              <p v-if="alerta.producto?.comercio_prod" class="alerta-desc">🏪 {{ alerta.producto.comercio_prod }}</p>
              <div class="alerta-precios">
                <span class="alerta-precio-actual">${{ Number(alerta.producto?.precio_prod || 0).toLocaleString('es-AR') }}</span>
                <span class="alerta-precio-flecha">→</span>
                <span class="alerta-precio-objetivo">${{ Number(alerta.precio_objetivo).toLocaleString('es-AR') }}</span>
              </div>
              <div class="alerta-meta">
                <span class="alerta-fecha">Creada {{ formatFecha(alerta.fecha_creacion) }}</span>
                <span v-if="alerta.notificada" class="alerta-badge">✅ Llegó al precio</span>
              </div>
            </div>

            <!-- Acciones -->
            <div class="alerta-actions">
              <button
                class="alerta-delete-btn"
                title="Eliminar alerta"
                @click.stop="eliminarAlerta(alerta.id)"
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
          <p>Todavía no tenés alertas de precio configuradas. Creá una desde la página de un producto.</p>
        </div>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { navigateTo } from '#app'

interface Alerta {
  id: string
  user_id: string
  id_prod: string
  precio_objetivo: number
  activa: boolean
  notificada: boolean
  fecha_creacion: string
  producto?: {
    nombre_prod: string
    precio_prod: number
    imagen_prod: string | null
    comercio_prod: string
  }
}

const { api } = useApi()

const loading = ref(true)
const alertas = ref<Alerta[]>([])

function formatFecha(fecha: string) {
  const d = new Date(fecha)
  const ahora = new Date()
  const diff = ahora.getTime() - d.getTime()
  const min = Math.floor(diff / 60000)
  const hrs = Math.floor(diff / 3600000)
  const dias = Math.floor(diff / 86400000)
  if (min < 1) return 'ahora'
  if (min < 60) return `hace ${min} min`
  if (hrs < 24) return `hace ${hrs} h`
  if (dias < 7) return `hace ${dias} d`
  return d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

async function cargar() {
  loading.value = true
  try {
    const data = await api<{ count: number; results: Alerta[] }>('/alertas')
    alertas.value = data.results || []
  } catch (err) {
    console.error('Error cargando alertas:', err)
  } finally {
    loading.value = false
  }
}

async function eliminarAlerta(id: string) {
  try {
    await api(`/alertas/${id}`, { method: 'DELETE' })
    alertas.value = alertas.value.filter(a => a.id !== id)
  } catch (err) {
    console.error('Error eliminando alerta:', err)
  }
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

.alerta-img {
  width:48px; height:48px; border-radius:var(--radius-sm); flex-shrink:0;
  overflow:hidden; background:var(--bg-input);
  display:flex; align-items:center; justify-content:center;
}
.alerta-img img { width:100%; height:100%; object-fit:cover; }

.alerta-info { flex:1; min-width:0; }
.alerta-titulo { color:var(--text-primary); font-size:0.9rem; font-weight:600; margin:0; }
.alerta-desc { color:var(--text-secondary); font-size:0.78rem; margin:0.2rem 0 0; }
.alerta-precios {
  display:flex; align-items:center; gap:6px;
  margin-top:0.4rem; font-size:0.85rem; font-weight:600;
}
.alerta-precio-actual { color:var(--text-muted); text-decoration:line-through; font-weight:500; }
.alerta-precio-flecha { color:var(--text-muted); font-size:0.75rem; }
.alerta-precio-objetivo { color:var(--accent-emerald); }
.alerta-meta { display:flex; align-items:center; gap:0.5rem; margin-top:0.4rem; flex-wrap: wrap; }
.alerta-fecha { color:var(--text-muted); font-size:0.72rem; }
.alerta-badge {
  background:var(--accent-emerald); color:#0a0a0a;
  font-size:0.65rem; font-weight:700;
  padding:0.15rem 0.4rem; border-radius:4px;
}

.alerta-actions {
  display:flex; flex-direction:column; gap:0.375rem;
  opacity:0; transition:opacity 0.2s;
}
.alerta-card:hover .alerta-actions { opacity:1; }
.alerta-delete-btn {
  width:28px; height:28px; border-radius:6px;
  display:flex; align-items:center; justify-content:center;
  background:transparent; border:1px solid var(--border-subtle);
  color:var(--text-muted); cursor:pointer; transition:all 0.2s;
}
.alerta-delete-btn:hover { background:rgba(251,113,133,0.1); color:var(--accent-rose); border-color:rgba(251,113,133,0.3); }

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