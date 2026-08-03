<template>
  <div class="comercios-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />
    <main class="page-content">
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/dashboard')">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Comercios</h1>
            <p class="page-subtitle">Comercios y supermercados</p>
          </div>
        </div>
        <div class="header-right">
          <div class="sort-btns">
            <button class="sort-btn" :class="{ active: sortMode === 'distancia' }" @click="sortMode = 'distancia'">📍 Cercanos</button>
            <button class="sort-btn" :class="{ active: sortMode === 'nombre' }" @click="sortMode = 'nombre'">A-Z</button>
          </div>
          <!-- Botón solo visible para admin -->
          <button v-if="isAdmin" class="add-btn" @click="navigateTo('/comercios/nuevo')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 5v14M5 12h14"/>
            </svg>
            Nuevo
          </button>
        </div>
      </header>

      <!-- BARRA DE UBICACIÓN -->
      <div class="location-bar animate-fade-in-up stagger-1">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
        </svg>
        <span v-if="userLocation" class="location-text">
          📍 {{ userLocation.lat.toFixed(4) }}, {{ userLocation.lng.toFixed(4) }}
        </span>
        <span v-else class="location-text muted">Sin ubicación</span>
        <button class="location-edit-btn" @click="showLocationModal = true">Ajustar</button>
      </div>

      <!-- BÚSQUEDA -->
      <div class="search-bar animate-fade-in-up stagger-2" :class="{ focused: searchFocused }">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar comercio..."
          class="search-input"
          @focus="searchFocused = true"
          @blur="searchFocused = false"
        />
        <button v-if="searchQuery" class="search-clear" @click="searchQuery = ''">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
          </svg>
        </button>
      </div>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando comercios...</span>
      </div>

      <!-- ERROR -->
      <div v-else-if="errorMsg" class="state-box animate-fade-in-up">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
        </svg>
        <p>{{ errorMsg }}</p>
        <button class="retry-btn" @click="cargarComercios">Reintentar</button>
      </div>

      <!-- LISTA -->
      <div v-else-if="comerciosFiltrados.length > 0" class="comercios-lista animate-fade-in-up stagger-3">
        <article
          v-for="p in comerciosFiltrados"
          :key="p.id_comer"
          class="comercio-card"
          @click="navigateTo(`/comercios/${p.id_comer}`)"
        >
          <div class="comercio-logo-wrap">
            <img
              :src="p.logo_comer || '/images/avatar_default.png'"
              :alt="p.nombre_comer"
              class="comercio-logo"
              @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'"
            />
          </div>
          <div class="comercio-info">
            <p class="comercio-nombre">{{ p.nombre_comer }}</p>
            <p class="comercio-dir">{{ p.direccion_comer }}</p>
            <div class="comercio-meta">
              <span class="comercio-cat">{{ p.cate_comer }}</span>
              <span v-if="p.distancia !== null && p.distancia !== undefined" class="comercio-dist">
                📍 {{ formatDistancia(p.distancia) }}
              </span>
              <span v-else-if="sortMode === 'distancia'" class="comercio-dist muted">Sin ubicación</span>
            </div>
            <button class="ver-prod-btn" @click.stop="navigateTo(`/c/${p.id_comer}`)">
              Ver productos
            </button>
          </div>
          <svg class="comercio-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </article>
      </div>

      <!-- EMPTY -->
      <div v-else class="state-box animate-fade-in-up">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"/>
          <path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"/>
        </svg>
        <p>No se encontraron comercios</p>
        <button v-if="isAdmin" class="retry-btn" @click="navigateTo('/comercios/nuevo')">Agregar el primero</button>
      </div>

    </main>

    <!-- MODAL AJUSTE UBICACIÓN -->
    <Teleport to="body">
      <div v-if="showLocationModal" class="modal-overlay" @click.self="showLocationModal = false">
        <div class="modal-card">
          <h3 class="modal-title">Ajustar ubicación</h3>
          <p class="modal-desc">Ingresá tus coordenadas para ordenar por cercanía correctamente.</p>
          <div class="modal-field">
            <label>Latitud</label>
            <input v-model="manualLat" type="number" step="0.0001" placeholder="-34.843" class="modal-input" />
          </div>
          <div class="modal-field">
            <label>Longitud</label>
            <input v-model="manualLng" type="number" step="0.0001" placeholder="-67.768" class="modal-input" />
          </div>
          <p class="modal-hint">Para Real del Padre: -34.843 / -67.768</p>
          <div class="modal-actions">
            <button class="modal-btn-cancel" @click="showLocationModal = false">Cancelar</button>
            <button class="modal-btn-confirm" @click="aplicarUbicacionManual">Aplicar</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo } from '#app'

interface Comercio {
  id_comer: string
  nombre_comer: string
  direccion_comer: string
  te_comer: string | null
  email_comer: string | null
  representa_comer: string
  cate_comer: string
  logo_comer: string | null
  activo_comer: boolean
  lat: number | null
  lng: number | null
  distancia?: number | null
}

// Mismo patrón que productos/index.vue
const { api } = useApi()

// Mismo patrón que dashboard.vue — rol guardado en localStorage
const user = ref<any>(null)
const isAdmin = computed(() => user.value?.rol === 'admin')

const loading = ref(true)
const errorMsg = ref('')
const comercios = ref<Comercio[]>([])
const searchQuery = ref('')
const searchFocused = ref(false)
const sortMode = ref<'distancia' | 'nombre'>('nombre')
const userLocation = ref<{ lat: number; lng: number } | null>(null)
const showLocationModal = ref(false)
const manualLat = ref('')
const manualLng = ref('')

function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng/2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

function formatDistancia(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)} m`
  return `${km.toFixed(1)} km`
}

const comerciosConDistancia = computed(() =>
  comercios.value.map(p => ({
    ...p,
    distancia: (userLocation.value && p.lat !== null && p.lng !== null)
      ? haversine(userLocation.value.lat, userLocation.value.lng, p.lat!, p.lng!)
      : null
  }))
)

const comerciosFiltrados = computed(() => {
  let list = [...comerciosConDistancia.value]
  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase()
    list = list.filter(p =>
      p.nombre_comer.toLowerCase().includes(q) ||
      p.direccion_comer?.toLowerCase().includes(q) ||
      p.cate_comer?.toLowerCase().includes(q)
    )
  }
  if (sortMode.value === 'distancia' && userLocation.value) {
    list.sort((a, b) => (a.distancia ?? Infinity) - (b.distancia ?? Infinity))
  } else {
    list.sort((a, b) => a.nombre_comer.localeCompare(b.nombre_comer, 'es'))
  }
  return list
})

const aplicarUbicacionManual = () => {
  const lat = parseFloat(manualLat.value)
  const lng = parseFloat(manualLng.value)
  if (isNaN(lat) || isNaN(lng)) return
  userLocation.value = { lat, lng }
  sortMode.value = 'distancia'
  showLocationModal.value = false
  localStorage.setItem('comparapp_user_location', JSON.stringify({ lat, lng }))
}

async function cargarComercios() {
  loading.value = true
  errorMsg.value = ''
  try {
    const res = await api<{ count: number; results: Comercio[] }>('/comercios')
    comercios.value = res.results || []
  } catch (err: any) {
    console.error('Error cargando comercios:', err)
    errorMsg.value = err?.message || 'No se pudieron cargar los comercios'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Leer usuario (mismo patrón que dashboard.vue)
  const storedUser = localStorage.getItem('comparapp_user')
  if (storedUser) {
    try { user.value = JSON.parse(storedUser) } catch {}
  }

  // Recuperar ubicación guardada
  const savedLocation = localStorage.getItem('comparapp_user_location')
  if (savedLocation) {
    try {
      userLocation.value = JSON.parse(savedLocation)
      sortMode.value = 'distancia'
    } catch {}
  } else if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        userLocation.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
        sortMode.value = 'distancia'
      },
      () => {}
    )
  }
  await cargarComercios()
})
</script>

<style scoped>
.comercios-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.03);
  --bg-card-hover: rgba(255,255,255,0.06);
  --border-subtle: rgba(255,255,255,0.08);
  --border-glow: rgba(232,196,160,0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.6);
  --text-muted: rgba(245,240,235,0.35);
  --accent-gold: #e8c4a0;
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
  max-width: 600px; margin: 0 auto;
  padding-bottom: 3rem;
}
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }

/* ─── HEADER ─── */
.page-header { display:flex; align-items:center; justify-content:space-between; gap:0.75rem; }
.header-left { display:flex; align-items:center; gap:0.875rem; min-width:0; }
.header-right { display:flex; align-items:center; gap:0.625rem; flex-shrink:0; }
.back-btn {
  width:40px; height:40px; border-radius:50%;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.25s; flex-shrink:0;
}
.back-btn:hover { background:rgba(255,255,255,0.08); border-color:var(--border-glow); color:var(--text-primary); }
.page-title { font-size:1.5rem; font-weight:700; margin:0; letter-spacing:-0.02em; }
.page-subtitle { color:var(--text-secondary); font-size:0.85rem; margin:0; }

.sort-btns { display:flex; gap:0.5rem; }
.sort-btn {
  padding:0.4rem 0.875rem; border-radius:999px;
  border:1px solid var(--border-subtle);
  background:rgba(255,255,255,0.02);
  color:var(--text-secondary); font-size:0.8rem; font-weight:500;
  cursor:pointer; transition:all 0.25s;
}
.sort-btn.active {
  background:rgba(232,196,160,0.12); border-color:rgba(232,196,160,0.3);
  color:var(--accent-gold);
}

/* ─── BOTÓN NUEVO (admin) ─── */
.add-btn {
  display:flex; align-items:center; gap:0.4rem;
  padding:0.4rem 0.875rem; border-radius:999px;
  background:linear-gradient(135deg, rgba(232,196,160,0.18), rgba(232,196,160,0.08));
  border:1px solid rgba(232,196,160,0.35);
  color:var(--accent-gold); font-size:0.8rem; font-weight:600;
  cursor:pointer; transition:all 0.25s; white-space:nowrap;
}
.add-btn:hover {
  background:linear-gradient(135deg, rgba(232,196,160,0.28), rgba(232,196,160,0.14));
  border-color:rgba(232,196,160,0.5);
  transform:translateY(-1px);
}

/* ─── LOCATION ─── */
.location-bar {
  display:flex; align-items:center; gap:0.75rem;
  padding:0.75rem 1rem;
  background:rgba(255,255,255,0.03);
  border:1px solid var(--border-subtle);
  border-radius:var(--radius-md);
  font-size:0.82rem;
}
.location-text { flex:1; color:var(--text-secondary); font-size:0.8rem; }
.location-text.muted { color:var(--text-muted); }
.location-bar svg { color:var(--accent-gold); flex-shrink:0; }
.location-edit-btn {
  padding:0.3rem 0.875rem; border-radius:999px;
  background:rgba(232,196,160,0.1); border:1px solid rgba(232,196,160,0.25);
  color:var(--accent-gold); font-size:0.78rem; font-weight:600;
  cursor:pointer; transition:all 0.2s; white-space:nowrap;
}
.location-edit-btn:hover { background:rgba(232,196,160,0.18); }

/* ─── SEARCH ─── */
.search-bar {
  display:flex; align-items:center; gap:0.75rem;
  padding:0.875rem 1rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg); transition:all 0.3s;
}
.search-bar.focused { border-color:var(--border-glow); background:rgba(255,255,255,0.05); }
.search-bar svg { color:var(--text-muted); flex-shrink:0; }
.search-input { flex:1; background:transparent; border:none; outline:none; color:var(--text-primary); font-size:0.95rem; }
.search-input::placeholder { color:var(--text-muted); }
.search-clear {
  width:28px; height:28px; border-radius:50%;
  background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle);
  color:var(--text-muted); display:flex; align-items:center; justify-content:center; cursor:pointer;
}

/* ─── STATE BOX ─── */
.state-box {
  display:flex; flex-direction:column; align-items:center;
  gap:0.75rem; padding:3rem 0;
  color:var(--text-muted); font-size:0.9rem; text-align:center;
}
.loading-spinner {
  width:28px; height:28px;
  border:2px solid rgba(255,255,255,0.1); border-top-color:var(--accent-gold);
  border-radius:50%; animation:spin 0.8s linear infinite;
}
.retry-btn {
  padding:0.625rem 1.25rem; border-radius:var(--radius-md);
  background:rgba(232,196,160,0.1); border:1px solid rgba(232,196,160,0.25);
  color:var(--accent-gold); font-size:0.85rem; font-weight:500;
  cursor:pointer; transition:all 0.25s;
}
.retry-btn:hover { background:rgba(232,196,160,0.18); }

/* ─── LISTA ─── */
.comercios-lista { display:flex; flex-direction:column; gap:0.75rem; }
.comercio-card {
  display:flex; align-items:center; gap:1rem;
  padding:1rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg); cursor:pointer; transition:all 0.25s;
}
.comercio-card:hover {
  background:var(--bg-card-hover); border-color:var(--border-glow);
  transform:translateY(-2px);
}
.comercio-logo-wrap {
  width:52px; height:52px; border-radius:var(--radius-sm);
  overflow:hidden; flex-shrink:0;
  background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle);
}
.comercio-logo { width:100%; height:100%; object-fit:cover; }
.comercio-info { flex:1; min-width:0; }
.comercio-nombre { color:var(--text-primary); font-size:0.95rem; font-weight:600; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.comercio-dir { color:var(--text-secondary); font-size:0.78rem; margin:0.2rem 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.comercio-meta { display:flex; align-items:center; gap:0.75rem; }
.comercio-cat { color:var(--text-muted); font-size:0.75rem; }
.comercio-dist { color:var(--accent-gold); font-size:0.75rem; font-weight:500; }
.comercio-dist.muted { color:var(--text-muted); }
.comercio-arrow { color:var(--text-muted); flex-shrink:0; opacity:0.5; }
.comercio-card:hover .comercio-arrow { opacity:1; color:var(--accent-gold); }

/* ─── MODAL ─── */
.modal-overlay {
  position:fixed; inset:0; z-index:999;
  background:rgba(0,0,0,0.6); backdrop-filter:blur(8px);
  display:flex; align-items:center; justify-content:center; padding:1.5rem;
}
.modal-card {
  background:#141418; border:1px solid rgba(232,196,160,0.2);
  border-radius:20px; padding:1.75rem; width:100%; max-width:360px;
  display:flex; flex-direction:column; gap:1rem;
}
.modal-title { color:var(--text-primary); font-size:1.1rem; font-weight:700; margin:0; }
.modal-desc { color:var(--text-secondary); font-size:0.85rem; margin:0; }
.modal-field { display:flex; flex-direction:column; gap:0.4rem; }
.modal-field label { color:var(--text-muted); font-size:0.78rem; text-transform:uppercase; letter-spacing:0.05em; }
.modal-input {
  padding:0.75rem 1rem; border-radius:12px;
  background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle);
  color:var(--text-primary); font-size:0.95rem; outline:none; transition:border-color 0.2s;
}
.modal-input:focus { border-color:var(--border-glow); }
.modal-hint { color:var(--text-muted); font-size:0.75rem; margin:0; }
.modal-actions { display:flex; gap:0.75rem; margin-top:0.5rem; }
.modal-btn-cancel {
  flex:1; padding:0.75rem; border-radius:12px;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); font-size:0.9rem; cursor:pointer;
}
.modal-btn-confirm {
  flex:1; padding:0.75rem; border-radius:12px;
  background:linear-gradient(135deg, rgba(232,196,160,0.2), rgba(232,196,160,0.1));
  border:1px solid rgba(232,196,160,0.3);
  color:var(--accent-gold); font-size:0.9rem; font-weight:600; cursor:pointer; transition:all 0.2s;
}
.modal-btn-confirm:hover { background:linear-gradient(135deg, rgba(232,196,160,0.3), rgba(232,196,160,0.15)); }

@media (max-width:480px) {
  .page-content { padding:1rem; }
  .page-title { font-size:1.25rem; }
  .sort-btns { display:none; } /* en mobile los sort quedan solo en el header-right si hay espacio */
}

/* Botón ver productos (vitrina pública) en la tarjeta */
.ver-prod-btn {
  margin-top: 0.5rem;
  padding: 0.35rem 0.85rem;
  border-radius: 999px;
  background: rgba(232,196,160,0.12);
  border: 1px solid rgba(232,196,160,0.3);
  color: var(--accent-gold);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}
.ver-prod-btn:hover {
  background: rgba(232,196,160,0.2);
  border-color: rgba(232,196,160,0.5);
}

</style>