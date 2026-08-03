<template>
  <div class="comercio-page">
    <DynamicBackground />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/comercios')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div>
          <h1 class="page-title">{{ editando ? 'Editar comercio' : 'Detalle comercio' }}</h1>
          <p class="page-subtitle">{{ form.nombre_comer || 'Cargando...' }}</p>
        </div>
        <!-- Botón editar solo para admin -->
        <button v-if="isAdmin && !editando" class="edit-btn" @click="editando = true">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
          Editar
        </button>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando comercio...</span>
      </div>

      <!-- ERROR -->
      <div v-else-if="errorCarga" class="state-box animate-fade-in-up">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
        </svg>
        <p>{{ errorCarga }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- CONTENIDO -->
      <template v-else>

        <!-- LOGO -->
        <div class="logo-section animate-fade-in-up stagger-1">
          <div class="logo-wrap">
            <img
              :src="form.logo_comer || '/images/avatar_default.png'"
              :alt="form.nombre_comer"
              class="logo-img"
              @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'"
            />
          </div>
          <div class="logo-info">
            <span class="logo-cat">{{ form.cate_comer }}</span>
            <span class="logo-status" :class="form.activo_comer ? 'active' : 'inactive'">
              {{ form.activo_comer ? '● Activo' : '● Inactivo' }}
            </span>
          </div>
        </div>

        <!-- Ver vitrina pública -->
        <a
          v-if="!editando"
          :href="`/c/${id}`"
          target="_blank"
          rel="noopener"
          class="vitrina-btn animate-fade-in-up stagger-1"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/>
          </svg>
          Ver vitrina pública
        </a>

        <!-- FORMULARIO / VISTA -->
        <div class="form-card animate-fade-in-up stagger-2">

          <!-- Nombre -->
          <div class="field-group">
            <label class="field-label">Nombre del comercio</label>
            <input v-if="editando" v-model="form.nombre_comer" type="text" class="field-input" maxlength="100" />
            <p v-else class="field-value">{{ form.nombre_comer }}</p>
          </div>

          <!-- Categoría -->
          <div class="field-group">
            <label class="field-label">Categoría</label>
            <div v-if="editando" class="select-wrapper">
              <select v-model="form.cate_comer" class="field-select">
                <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
              </select>
              <svg class="select-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="m6 9 6 6 6-6"/>
              </svg>
            </div>
            <p v-else class="field-value">{{ form.cate_comer }}</p>
          </div>

          <!-- Dirección -->
          <div class="field-group">
            <label class="field-label">Dirección</label>
            <input v-if="editando" v-model="form.direccion_comer" type="text" class="field-input" maxlength="200" />
            <p v-else class="field-value">{{ form.direccion_comer || '—' }}</p>
          </div>

          <!-- Coordenadas (NUEVO: lat/lng) -->
          <div v-if="editando" class="field-row">
            <div class="field-group">
              <label class="field-label">Latitud</label>
              <input v-model="form.lat" type="number" step="0.000001" class="field-input" placeholder="-34.843" />
            </div>
            <div class="field-group">
              <label class="field-label">Longitud</label>
              <input v-model="form.lng" type="number" step="0.000001" class="field-input" placeholder="-67.768" />
            </div>
          </div>
          <p v-if="editando" class="field-hint">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
            </svg>
            Las coordenadas permiten mostrar distancia a los usuarios. Buscalas en Google Maps.
          </p>
          <!-- Vista de coordenadas -->
          <div v-if="!editando && (form.lat || form.lng)" class="field-group">
            <label class="field-label">Ubicación</label>
            <p class="field-value">
              📍 {{ form.lat?.toFixed(6) }}, {{ form.lng?.toFixed(6) }}
            </p>
          </div>

          <!-- Teléfono -->
          <div class="field-group">
            <label class="field-label">Teléfono</label>
            <input v-if="editando" v-model="form.te_comer" type="tel" class="field-input" maxlength="50" />
            <p v-else class="field-value">{{ form.te_comer || '—' }}</p>
          </div>

          <!-- Email -->
          <div class="field-group">
            <label class="field-label">Email</label>
            <input v-if="editando" v-model="form.email_comer" type="email" class="field-input" maxlength="100" />
            <p v-else class="field-value">{{ form.email_comer || '—' }}</p>
          </div>

          <!-- Representante -->
          <div class="field-group">
            <label class="field-label">Representante</label>
            <input v-if="editando" v-model="form.representa_comer" type="text" class="field-input" maxlength="100" />
            <p v-else class="field-value">{{ form.representa_comer || '—' }}</p>
          </div>

          <!-- URL Logo (solo visible al editar — campo técnico, no aporta valor al usuario) -->
          <div v-if="editando" class="field-group">
            <label class="field-label">URL del logo</label>
            <input v-model="form.logo_comer" type="url" class="field-input" />
          </div>

          <!-- Activo (solo edición) -->
          <div v-if="editando" class="field-group">
            <label class="toggle-label">
              <div class="toggle-info">
                <span class="field-label" style="margin:0">Activo</span>
                <span class="toggle-desc">Visible para los usuarios</span>
              </div>
              <div class="toggle-switch" :class="{ on: form.activo_comer }" @click="form.activo_comer = !form.activo_comer">
                <div class="toggle-thumb" />
              </div>
            </label>
          </div>

        </div>

        <!-- ALERTAS -->
        <div v-if="errorMsg" class="alert-error animate-fade-in-up">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
          </svg>
          {{ errorMsg }}
        </div>
        <div v-if="successMsg" class="alert-success animate-fade-in-up">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
          {{ successMsg }}
        </div>

        <!-- ACCIONES EDICIÓN -->
        <div v-if="editando" class="form-actions animate-fade-in-up">
          <button class="btn-secondary" @click="cancelarEdicion" :disabled="saving">Cancelar</button>
          <button class="btn-primary" @click="guardar" :disabled="saving">
            <div v-if="saving" class="btn-spinner" />
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5"/>
            </svg>
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>

      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { navigateTo, useRoute } from '#app'

const { api } = useApi()
const route = useRoute()
const id = route.params.id as string

// Admin
const user = ref<any>(null)
const isAdmin = ref(false)

// Estado
const loading = ref(true)
const errorCarga = ref('')
const errorMsg = ref('')
const successMsg = ref('')
const saving = ref(false)
const editando = ref(false)

// Categorías (hardcodeadas por ahora, podrían cargarse de /categorias)
const categorias = [
  'Supermercado', 'Almacén', 'Carnicería', 'Verdulería',
  'Farmacia', 'Ferretería', 'Panadería', 'Kiosco', 'Mayorista',
  'Comercio', 'Otro',
]

// Formulario
const form = reactive({
  nombre_comer: '',
  cate_comer: '',
  direccion_comer: '',
  lat: null as number | null,
  lng: null as number | null,
  te_comer: '',
  email_comer: '',
  representa_comer: '',
  logo_comer: '',
  activo_comer: true,
  fechaIngreso_comer: '',
})

// Copia para cancelar
let formOriginal = { ...form }

async function cargar() {
  loading.value = true
  errorCarga.value = ''
  try {
    const data = await api<any>(`/comercios/${id}`)
    form.nombre_comer    = data.nombre_comer    || ''
    form.cate_comer      = data.cate_comer      || ''
    form.direccion_comer = data.direccion_comer || ''
    form.lat              = data.lat              ?? null
    form.lng              = data.lng              ?? null
    form.te_comer        = data.te_comer        || ''
    form.email_comer     = data.email_comer     || ''
    form.representa_comer = data.representa_comer || ''
    form.logo_comer      = data.logo_comer      || ''
    form.activo_comer    = data.activo_comer    ?? true
    form.fechaIngreso_comer = data.fechaIngreso_comer || ''
    formOriginal = { ...form }
  } catch (err: any) {
    errorCarga.value = err?.data?.detail || err?.message || 'No se pudo cargar el comercio'
  } finally {
    loading.value = false
  }
}

function cancelarEdicion() {
  Object.assign(form, formOriginal)
  editando.value = false
  errorMsg.value = ''
}

async function guardar() {
  errorMsg.value = ''
  successMsg.value = ''
  saving.value = true
  try {
    const payload: Record<string, any> = {
      nombre_comer:     form.nombre_comer.trim(),
      cate_comer:       form.cate_comer,
      direccion_comer:  form.direccion_comer.trim(),
      te_comer:         form.te_comer.trim() || '',
      email_comer:      form.email_comer.trim() || '',
      representa_comer: form.representa_comer.trim() || '',
      logo_comer:       form.logo_comer.trim() || '',
      activo_comer:     form.activo_comer,
    }

    // Agregar lat/lng si existen para que el backend actualice ubicacion_comer
    if (form.lat !== null && form.lng !== null) {
      payload.lat = Number(form.lat)
      payload.lng = Number(form.lng)
    }

    await api(`/comercios/${id}`, { method: 'PUT', body: payload })
    formOriginal = { ...form }
    editando.value = false
    successMsg.value = '✅ Proveedor actualizado correctamente'
    setTimeout(() => successMsg.value = '', 3000)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || err?.message || 'Error al guardar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try {
      user.value = JSON.parse(stored)
      isAdmin.value = user.value?.rol === 'admin'
    } catch {}
  }
  await cargar()
})
</script>

<style scoped>
/* Sin tokens locales — usa las variables globales del tema */
.comercio-page {
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
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
.stagger-2 { animation-delay: 0.1s; }

/* HEADER */
.page-header {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.5rem 0;
}
.back-btn {
  width:40px; height:40px; border-radius:50%; flex-shrink:0;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.25s;
}
.back-btn:hover { background:rgba(255,255,255,0.08); border-color:var(--border-glow); color:var(--text-primary); }
.page-title { font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-0.02em; flex:1; }
.page-subtitle { color:var(--text-secondary); font-size:0.83rem; margin:0; }
.edit-btn {
  display:flex; align-items:center; gap:0.4rem;
  padding:0.4rem 0.875rem; border-radius:999px;
  background:rgba(232,196,160,0.1); border:1px solid rgba(232,196,160,0.25);
  color:var(--accent-gold); font-size:0.8rem; font-weight:600;
  cursor:pointer; transition:all 0.25s; white-space:nowrap; flex-shrink:0;
}
.edit-btn:hover { background:rgba(232,196,160,0.18); border-color:rgba(232,196,160,0.4); }

/* STATE BOX */
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

/* LOGO */
.logo-section {
  display:flex; align-items:center; gap:1rem;
  padding:1rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg);
}
.logo-wrap {
  width:72px; height:72px; border-radius:var(--radius-md);
  overflow:hidden; flex-shrink:0;
  background:rgba(255,255,255,0.06); border:1px solid var(--border-subtle);
}
.logo-img { width:100%; height:100%; object-fit:cover; }
.logo-info { display:flex; flex-direction:column; gap:0.4rem; }
.logo-cat { color:var(--text-secondary); font-size:0.85rem; }
.logo-status { font-size:0.8rem; font-weight:600; }
.logo-status.active { color:var(--accent-success); }
.logo-status.inactive { color:var(--accent-error); }

/* FORM */
.form-card {
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg); padding:1.5rem;
  display:flex; flex-direction:column; gap:1.25rem;
}
.field-group { display:flex; flex-direction:column; gap:0.4rem; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.field-label {
  color:var(--text-muted); font-size:0.75rem; font-weight:600;
  text-transform:uppercase; letter-spacing:0.06em;
}
.field-value {
  color:var(--text-primary); font-size:0.95rem; margin:0;
  padding:0.5rem 0; border-bottom:1px solid var(--border-subtle);
}
.url-value { font-size:0.78rem; word-break:break-all; color:var(--text-secondary); }
.field-input, .field-select {
  padding:0.75rem 1rem;
  background:rgba(255,255,255,0.05); border:1px solid var(--border-subtle);
  border-radius:var(--radius-sm);
  color:var(--text-primary); font-size:0.92rem; font-family:inherit;
  outline:none; transition:border-color 0.2s, background 0.2s; width:100%;
}
.field-input:focus, .field-select:focus {
  border-color:var(--border-glow); background:rgba(255,255,255,0.07);
}
.field-input::placeholder { color:var(--text-muted); }

/* Coordenadas hint */
.field-hint {
  display: flex; align-items: center; gap: 0.375rem;
  color: var(--text-muted); font-size: 0.75rem; margin: 0;
}
.field-hint svg { flex-shrink: 0; color: var(--accent-gold); }

/* SELECT */
.select-wrapper { position:relative; }
.field-select { appearance:none; padding-right:2.5rem; cursor:pointer; }
.select-icon {
  position:absolute; right:0.875rem; top:50%; transform:translateY(-50%);
  color:var(--text-muted); pointer-events:none;
}
.field-select option { background:#1a1a20; color:var(--text-primary); }

/* TOGGLE */
.toggle-label {
  display:flex; align-items:center; justify-content:space-between;
  cursor:pointer; gap:1rem;
}
.toggle-info { display:flex; flex-direction:column; gap:0.2rem; }
.toggle-desc { color:var(--text-muted); font-size:0.78rem; }
.toggle-switch {
  width:44px; height:24px; border-radius:999px;
  background:rgba(255,255,255,0.1); border:1px solid var(--border-subtle);
  position:relative; flex-shrink:0; transition:all 0.3s; cursor:pointer;
}
.toggle-switch.on { background:rgba(232,196,160,0.25); border-color:rgba(232,196,160,0.4); }
.toggle-thumb {
  position:absolute; top:2px; left:2px;
  width:18px; height:18px; border-radius:50%;
  background:var(--text-muted); transition:all 0.3s;
}
.toggle-switch.on .toggle-thumb { left:calc(100% - 20px); background:var(--accent-gold); }

/* ALERTS */
.alert-error, .alert-success {
  display:flex; align-items:center; gap:0.625rem;
  padding:0.875rem 1rem; border-radius:var(--radius-md);
  font-size:0.875rem; font-weight:500;
}
.alert-error { background:rgba(251,113,133,0.1); border:1px solid rgba(251,113,133,0.25); color:#fb7185; }
.alert-success { background:rgba(52,211,153,0.1); border:1px solid rgba(52,211,153,0.25); color:var(--accent-success); }

/* ACCIONES */
.form-actions { display:flex; gap:0.75rem; }
.btn-secondary {
  flex:1; padding:0.875rem;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  border-radius:var(--radius-md);
  color:var(--text-secondary); font-size:0.9rem; font-weight:500;
  cursor:pointer; transition:all 0.25s;
}
.btn-secondary:hover:not(:disabled) { background:rgba(255,255,255,0.08); color:var(--text-primary); }
.btn-primary {
  flex:2; padding:0.875rem;
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  background:linear-gradient(135deg, rgba(232,196,160,0.2), rgba(232,196,160,0.1));
  border:1px solid rgba(232,196,160,0.35); border-radius:var(--radius-md);
  color:var(--accent-gold); font-size:0.9rem; font-weight:600;
  cursor:pointer; transition:all 0.25s;
}
.btn-primary:hover:not(:disabled) {
  background:linear-gradient(135deg, rgba(232,196,160,0.3), rgba(232,196,160,0.15));
  border-color:rgba(232,196,160,0.5); transform:translateY(-1px);
}
.btn-primary:disabled, .btn-secondary:disabled { opacity:0.5; cursor:not-allowed; transform:none; }
.btn-spinner {
  width:16px; height:16px;
  border:2px solid rgba(232,196,160,0.3); border-top-color:var(--accent-gold);
  border-radius:50%; animation:spin 0.7s linear infinite;
}

@media (max-width:480px) {
  .page-content { padding:1rem; }
  .page-title { font-size:1.2rem; }
  .field-row { grid-template-columns: 1fr; }
}

/* Botón ver vitrina pública */
.vitrina-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.875rem; border-radius: var(--radius-md);
  background: rgba(232,196,160,0.1); border: 1px solid rgba(232,196,160,0.3);
  color: var(--accent-gold); font-size: 0.9rem; font-weight: 600;
  text-decoration: none; transition: all 0.25s;
}
.vitrina-btn:hover {
  background: rgba(232,196,160,0.18); border-color: rgba(232,196,160,0.5);
  transform: translateY(-1px);
}

</style>