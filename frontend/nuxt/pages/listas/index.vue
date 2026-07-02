<template>
  <div class="listas-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/dashboard')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Mis listas</h1>
            <p class="page-subtitle">{{ listas.length }} lista{{ listas.length !== 1 ? 's' : '' }}</p>
          </div>
        </div>
        <button class="add-btn" @click="mostrarNueva = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          Nueva
        </button>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando listas...</span>
      </div>

      <!-- ERROR -->
      <div v-else-if="errorMsg" class="state-box animate-fade-in-up">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
        </svg>
        <p>{{ errorMsg }}</p>
        <button class="btn-gold" @click="cargarListas">Reintentar</button>
      </div>

      <!-- LISTAS -->
      <div v-else-if="listas.length > 0" class="listas-grid animate-fade-in-up stagger-1">
        <article
          v-for="lista in listas"
          :key="lista.id_lista"
          class="lista-card"
          @click="navigateTo(`/listas/${lista.id_lista}`)"
        >
          <div class="lista-icon">🛒</div>
          <div class="lista-info">
            <p class="lista-nombre">{{ lista.nombre_lista }}</p>
            <p class="lista-fecha">{{ formatFecha(lista.fecha_modificacion) }}</p>
          </div>
          <button
            class="lista-delete"
            @click.stop="confirmarEliminar(lista)"
            title="Eliminar lista"
          >
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
              <path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
          <svg class="lista-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </article>
      </div>

      <!-- EMPTY -->
      <div v-else class="state-box animate-fade-in-up stagger-1">
        <div class="empty-icon">🛒</div>
        <h3>No tenés listas aún</h3>
        <p>Creá tu primera lista de compras</p>
        <button class="btn-gold" @click="mostrarNueva = true">Crear lista</button>
      </div>

    </main>

    <!-- MODAL NUEVA LISTA -->
    <Teleport to="body">
      <div v-if="mostrarNueva" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-card">
          <h3 class="modal-title">Nueva lista</h3>
          <input
            v-model="nombreNueva"
            ref="inputNueva"
            type="text"
            class="modal-input"
            placeholder="Ej: Compra semanal"
            maxlength="80"
            @keydown.enter="crearLista"
            @keydown.esc="cerrarModal"
          />
          <p v-if="errorCrear" class="modal-error">{{ errorCrear }}</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="cerrarModal" :disabled="creando">Cancelar</button>
            <button class="btn-gold" @click="crearLista" :disabled="creando || !nombreNueva.trim()">
              <div v-if="creando" class="btn-spinner" />
              {{ creando ? 'Creando...' : 'Crear' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- MODAL CONFIRMAR ELIMINAR -->
    <Teleport to="body">
      <div v-if="listaAEliminar" class="modal-overlay" @click.self="listaAEliminar = null">
        <div class="modal-card">
          <h3 class="modal-title">¿Eliminar lista?</h3>
          <p class="modal-desc">Se eliminará "<strong>{{ listaAEliminar.nombre_lista }}</strong>" y todos sus productos.</p>
          <div class="modal-actions">
            <button class="btn-cancel" @click="listaAEliminar = null">Cancelar</button>
            <button class="btn-danger" @click="eliminarLista" :disabled="eliminando">
              <div v-if="eliminando" class="btn-spinner" />
              {{ eliminando ? 'Eliminando...' : 'Eliminar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { navigateTo } from '#app'

interface Lista {
  id_lista: string
  nombre_lista: string
  fecha_creacion: string
  fecha_modificacion: string
  activa: boolean
}

const { api } = useApi()

const loading = ref(true)
const errorMsg = ref('')
const listas = ref<Lista[]>([])

const mostrarNueva = ref(false)
const nombreNueva = ref('')
const errorCrear = ref('')
const creando = ref(false)
const inputNueva = ref<HTMLInputElement>()

const listaAEliminar = ref<Lista | null>(null)
const eliminando = ref(false)

function formatFecha(iso: string): string {
  if (!iso) return ''
  const d = new Date(iso)
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short', year: 'numeric' })
}

async function cargarListas() {
  // Guard: si no hay sesión activa, redirigir al login en vez de tirar 401
  const stored = typeof window !== 'undefined' ? localStorage.getItem('comparapp_user') : null
  if (!stored) {
    navigateTo('/login')
    return
  }

  loading.value = true
  errorMsg.value = ''
  try {
    const res = await api<{ count: number; results: Lista[] }>('/listas')
    listas.value = res.results || []
  } catch (err: any) {
    // 401 = sesión vencida — redirigir al login en vez de mostrar error
    if (err?.status === 401 || err?.statusCode === 401) {
      navigateTo('/login')
      return
    }
    errorMsg.value = err?.data?.detail || err?.message || 'Error al cargar listas'
  } finally {
    loading.value = false
  }
}

async function crearLista() {
  if (!nombreNueva.value.trim()) return
  creando.value = true
  errorCrear.value = ''
  try {
    const res = await api<{ data: Lista }>('/listas', {
      method: 'POST',
      body: { nombre_lista: nombreNueva.value.trim() }
    })
    listas.value.unshift(res.data)
    cerrarModal()
    navigateTo(`/listas/${res.data.id_lista}`)
  } catch (err: any) {
    errorCrear.value = err?.data?.detail || 'Error al crear la lista'
  } finally {
    creando.value = false
  }
}

function cerrarModal() {
  mostrarNueva.value = false
  nombreNueva.value = ''
  errorCrear.value = ''
}

function confirmarEliminar(lista: Lista) {
  listaAEliminar.value = lista
}

async function eliminarLista() {
  if (!listaAEliminar.value) return
  eliminando.value = true
  try {
    await api(`/listas/${listaAEliminar.value.id_lista}`, { method: 'DELETE' })
    listas.value = listas.value.filter(l => l.id_lista !== listaAEliminar.value!.id_lista)
    listaAEliminar.value = null
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Error al eliminar'
  } finally {
    eliminando.value = false
  }
}

// Focus automático al abrir modal
watch(mostrarNueva, async (val) => {
  if (val) {
    await nextTick()
    inputNueva.value?.focus()
  }
})

onMounted(cargarListas)
</script>

<style scoped>
.listas-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.03);
  --bg-card-hover: rgba(255,255,255,0.06);
  --border-subtle: rgba(255,255,255,0.08);
  --border-glow: rgba(232,196,160,0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.6);
  --text-muted: rgba(245,240,235,0.35);
  --accent-gold: #e8c4a0;
  --accent-error: #fb7185;
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.bg-gradient {
  position: fixed; inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232,196,160,0.08), transparent),
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
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.25rem;
  max-width: 560px; margin: 0 auto;
  padding-bottom: 3rem;
}
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }

/* HEADER */
.page-header { display:flex; align-items:center; justify-content:space-between; padding:0.5rem 0; }
.header-left { display:flex; align-items:center; gap:0.875rem; }
.back-btn {
  width:40px; height:40px; border-radius:50%; flex-shrink:0;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.25s;
}
.back-btn:hover { background:rgba(255,255,255,0.08); border-color:var(--border-glow); color:var(--text-primary); }
.page-title { font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-0.02em; }
.page-subtitle { color:var(--text-secondary); font-size:0.85rem; margin:0; }
.add-btn {
  display:flex; align-items:center; gap:0.4rem;
  padding:0.5rem 1rem; border-radius:999px;
  background:linear-gradient(135deg, rgba(232,196,160,0.18), rgba(232,196,160,0.08));
  border:1px solid rgba(232,196,160,0.35);
  color:var(--accent-gold); font-size:0.85rem; font-weight:600;
  cursor:pointer; transition:all 0.25s;
}
.add-btn:hover { background:linear-gradient(135deg, rgba(232,196,160,0.28), rgba(232,196,160,0.14)); transform:translateY(-1px); }

/* STATE BOX */
.state-box {
  display:flex; flex-direction:column; align-items:center;
  gap:0.875rem; padding:4rem 1rem; text-align:center;
  color:var(--text-muted);
}
.loading-spinner {
  width:28px; height:28px;
  border:2px solid rgba(255,255,255,0.1); border-top-color:var(--accent-gold);
  border-radius:50%; animation:spin 0.8s linear infinite;
}
.empty-icon { font-size:3rem; }
.state-box h3 { color:var(--text-primary); font-size:1.1rem; font-weight:600; margin:0; }
.state-box p { color:var(--text-secondary); font-size:0.85rem; margin:0; }

/* LISTAS */
.listas-grid { display:flex; flex-direction:column; gap:0.75rem; }
.lista-card {
  display:flex; align-items:center; gap:1rem;
  padding:1rem 1.125rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg); cursor:pointer; transition:all 0.25s;
  position:relative;
}
.lista-card:hover {
  background:var(--bg-card-hover); border-color:var(--border-glow);
  transform:translateY(-2px);
}
.lista-icon { font-size:1.5rem; flex-shrink:0; }
.lista-info { flex:1; min-width:0; }
.lista-nombre { color:var(--text-primary); font-size:0.95rem; font-weight:600; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.lista-fecha { color:var(--text-muted); font-size:0.75rem; margin:0.2rem 0 0; }
.lista-delete {
  width:32px; height:32px; border-radius:50%; flex-shrink:0;
  background:rgba(251,113,133,0.08); border:1px solid rgba(251,113,133,0.15);
  color:rgba(251,113,133,0.5);
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.2s;
}
.lista-delete:hover { background:rgba(251,113,133,0.15); border-color:rgba(251,113,133,0.4); color:#fb7185; }
.lista-arrow { color:var(--text-muted); flex-shrink:0; opacity:0.4; transition:all 0.25s; }
.lista-card:hover .lista-arrow { opacity:1; color:var(--accent-gold); }

/* MODAL */
.modal-overlay {
  position:fixed; inset:0; z-index:999;
  background:rgba(0,0,0,0.65); backdrop-filter:blur(8px);
  display:flex; align-items:center; justify-content:center; padding:1.5rem;
}
.modal-card {
  background:#141418; border:1px solid rgba(232,196,160,0.2);
  border-radius:20px; padding:1.75rem; width:100%; max-width:360px;
  display:flex; flex-direction:column; gap:1rem;
}
.modal-title { color:var(--text-primary); font-size:1.1rem; font-weight:700; margin:0; }
.modal-desc { color:var(--text-secondary); font-size:0.85rem; margin:0; }
.modal-desc strong { color:var(--text-primary); }
.modal-input {
  padding:0.875rem 1rem; border-radius:12px;
  background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle);
  color:var(--text-primary); font-size:0.95rem; font-family:inherit;
  outline:none; transition:border-color 0.2s;
}
.modal-input:focus { border-color:var(--border-glow); }
.modal-input::placeholder { color:var(--text-muted); }
.modal-error { color:var(--accent-error); font-size:0.78rem; margin:0; }
.modal-actions { display:flex; gap:0.75rem; margin-top:0.25rem; }

/* BUTTONS */
.btn-cancel {
  flex:1; padding:0.75rem; border-radius:12px;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); font-size:0.9rem; cursor:pointer; transition:all 0.2s;
}
.btn-cancel:hover:not(:disabled) { background:rgba(255,255,255,0.08); }
.btn-gold {
  flex:1; padding:0.75rem; border-radius:12px;
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  background:linear-gradient(135deg, rgba(232,196,160,0.2), rgba(232,196,160,0.1));
  border:1px solid rgba(232,196,160,0.35);
  color:var(--accent-gold); font-size:0.9rem; font-weight:600;
  cursor:pointer; transition:all 0.2s;
}
.btn-gold:hover:not(:disabled) { background:linear-gradient(135deg, rgba(232,196,160,0.3), rgba(232,196,160,0.15)); }
.btn-gold:disabled { opacity:0.5; cursor:not-allowed; }
.btn-danger {
  flex:1; padding:0.75rem; border-radius:12px;
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  background:rgba(251,113,133,0.1); border:1px solid rgba(251,113,133,0.3);
  color:#fb7185; font-size:0.9rem; font-weight:600;
  cursor:pointer; transition:all 0.2s;
}
.btn-danger:hover:not(:disabled) { background:rgba(251,113,133,0.18); }
.btn-danger:disabled { opacity:0.5; cursor:not-allowed; }
.btn-spinner {
  width:14px; height:14px;
  border:2px solid rgba(232,196,160,0.3); border-top-color:var(--accent-gold);
  border-radius:50%; animation:spin 0.7s linear infinite;
}

@media (max-width:480px) { .page-content { padding:1rem; } .page-title { font-size:1.25rem; } }
</style>