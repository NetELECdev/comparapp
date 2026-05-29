<template>
  <div class="nuevo-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/proveedores')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div>
          <h1 class="page-title">Nuevo proveedor</h1>
          <p class="page-subtitle">Completá los datos del comercio</p>
        </div>
      </header>

      <!-- FORMULARIO -->
      <div class="form-card animate-fade-in-up stagger-1">

        <!-- Nombre -->
        <div class="field-group">
          <label class="field-label">Nombre del comercio <span class="required">*</span></label>
          <input
            v-model="form.nombre_provee"
            type="text"
            class="field-input"
            :class="{ error: errors.nombre_provee }"
            placeholder="Ej: Supermercado Central"
            maxlength="100"
          />
          <span v-if="errors.nombre_provee" class="field-error">{{ errors.nombre_provee }}</span>
        </div>

        <!-- Categoría -->
        <div class="field-group">
          <label class="field-label">Categoría <span class="required">*</span></label>
          <div class="select-wrapper">
            <select v-model="form.cate_provee" class="field-select" :class="{ error: errors.cate_provee }">
              <option value="" disabled>Seleccioná una categoría</option>
              <option v-for="cat in categorias" :key="cat" :value="cat">{{ cat }}</option>
            </select>
            <svg class="select-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m6 9 6 6 6-6"/>
            </svg>
          </div>
          <span v-if="errors.cate_provee" class="field-error">{{ errors.cate_provee }}</span>
        </div>

        <!-- Dirección -->
        <div class="field-group">
          <label class="field-label">Dirección <span class="required">*</span></label>
          <input
            v-model="form.direccion_provee"
            type="text"
            class="field-input"
            :class="{ error: errors.direccion_provee }"
            placeholder="Ej: Av. San Martín 450"
            maxlength="200"
          />
          <span v-if="errors.direccion_provee" class="field-error">{{ errors.direccion_provee }}</span>
        </div>

        <!-- Coordenadas -->
        <div class="field-row">
          <div class="field-group">
            <label class="field-label">Latitud</label>
            <input
              v-model="form.lat"
              type="number"
              step="0.000001"
              class="field-input"
              placeholder="-34.843"
            />
          </div>
          <div class="field-group">
            <label class="field-label">Longitud</label>
            <input
              v-model="form.lng"
              type="number"
              step="0.000001"
              class="field-input"
              placeholder="-67.768"
            />
          </div>
        </div>
        <p class="field-hint">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
          </svg>
          Las coordenadas permiten mostrar distancia a los usuarios. Buscalas en Google Maps.
        </p>

        <!-- Teléfono -->
        <div class="field-group">
          <label class="field-label">Teléfono</label>
          <input
            v-model="form.te_provee"
            type="tel"
            class="field-input"
            placeholder="Ej: 2604-123456"
            maxlength="50"
          />
        </div>

        <!-- Email -->
        <div class="field-group">
          <label class="field-label">Email</label>
          <input
            v-model="form.email_provee"
            type="email"
            class="field-input"
            :class="{ error: errors.email_provee }"
            placeholder="contacto@comercio.com"
            maxlength="100"
          />
          <span v-if="errors.email_provee" class="field-error">{{ errors.email_provee }}</span>
        </div>

        <!-- Representante -->
        <div class="field-group">
          <label class="field-label">Representante / Contacto</label>
          <input
            v-model="form.representa_provee"
            type="text"
            class="field-input"
            placeholder="Nombre del encargado"
            maxlength="100"
          />
        </div>

        <!-- URL Logo -->
        <div class="field-group">
          <label class="field-label">URL del logo</label>
          <input
            v-model="form.logo_provee"
            type="url"
            class="field-input"
            placeholder="https://..."
          />
          <!-- Preview del logo -->
          <div v-if="form.logo_provee" class="logo-preview">
            <img
              :src="form.logo_provee"
              alt="Preview logo"
              class="logo-preview-img"
              @error="logoError = true"
              @load="logoError = false"
            />
            <span v-if="logoError" class="logo-preview-error">URL inválida o imagen no accesible</span>
          </div>
        </div>

        <!-- Activo -->
        <div class="field-group">
          <label class="toggle-label">
            <div class="toggle-info">
              <span class="field-label" style="margin:0">Activo</span>
              <span class="toggle-desc">El proveedor será visible para los usuarios</span>
            </div>
            <div class="toggle-switch" :class="{ on: form.activo_provee }" @click="form.activo_provee = !form.activo_provee">
              <div class="toggle-thumb" />
            </div>
          </label>
        </div>

      </div>

      <!-- ERROR GLOBAL -->
      <div v-if="errorMsg" class="alert-error animate-fade-in-up">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/><path d="M12 8v4"/><path d="M12 16h.01"/>
        </svg>
        {{ errorMsg }}
      </div>

      <!-- ÉXITO -->
      <div v-if="successMsg" class="alert-success animate-fade-in-up">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M20 6 9 17l-5-5"/>
        </svg>
        {{ successMsg }}
      </div>

      <!-- ACCIONES -->
      <div class="form-actions animate-fade-in-up stagger-2">
        <button class="btn-cancel" @click="navigateTo('/proveedores')" :disabled="saving">
          Cancelar
        </button>
        <button class="btn-submit" @click="guardar" :disabled="saving">
          <div v-if="saving" class="btn-spinner" />
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20 6 9 17l-5-5"/>
          </svg>
          {{ saving ? 'Guardando...' : 'Guardar proveedor' }}
        </button>
      </div>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { navigateTo } from '#app'

// Mismo patrón que productos/index.vue
const { api } = useApi()

// Guard: leer usuario desde localStorage (mismo patrón que dashboard.vue)
const user = ref<any>(null)

onMounted(() => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch {}
  }
  // Si no es admin, redirigir
  if (user.value?.rol !== 'admin') {
    navigateTo('/proveedores')
  }
})

// ─── Categorías disponibles ───
const categorias = [
  'Supermercado',
  'Almacén',
  'Carnicería',
  'Verdulería',
  'Farmacia',
  'Ferretería',
  'Panadería',
  'Kiosco',
  'Mayorista',
  'Otro',
]

// ─── Estado del formulario ───
const form = reactive({
  nombre_provee: '',
  cate_provee: '',
  direccion_provee: '',
  lat: null as number | null,
  lng: null as number | null,
  te_provee: '',
  email_provee: '',
  representa_provee: '',
  logo_provee: '',
  activo_provee: true,
})

const errors = reactive({} as { [key: string]: string })
const errorMsg = ref('')
const successMsg = ref('')
const saving = ref(false)
const logoError = ref(false)

// ─── Validación ───
function validar(): boolean {
  Object.keys(errors).forEach(k => delete errors[k])

  if (!form.nombre_provee.trim())
    errors.nombre_provee = 'El nombre es obligatorio'

  if (!form.cate_provee)
    errors.cate_provee = 'Seleccioná una categoría'

  if (!form.direccion_provee.trim())
    errors.direccion_provee = 'La dirección es obligatoria'

  if (form.email_provee && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email_provee))
    errors.email_provee = 'El email no es válido'

  return Object.keys(errors).length === 0
}

// ─── Guardar via API ───
async function guardar() {
  errorMsg.value = ''
  successMsg.value = ''

  if (!validar()) return

  saving.value = true
  try {
    const payload = {
      nombre_provee:       form.nombre_provee.trim(),
      cate_provee:         form.cate_provee,
      direccion_provee:    form.direccion_provee.trim(),
      te_provee:           form.te_provee.trim() || '',
      email_provee:        form.email_provee.trim() || '',
      representa_provee:   form.representa_provee.trim() || '',
      logo_provee:         form.logo_provee.trim() || '',
      activo_provee:       form.activo_provee,
      fechaIngreso_provee: new Date().toISOString().split('T')[0],
    }

    await api('/proveedores', { method: 'POST', body: payload })

    successMsg.value = '✅ Proveedor guardado correctamente'
    setTimeout(() => navigateTo('/proveedores'), 1500)

  } catch (err: any) {
    console.error('Error guardando proveedor:', err)
    errorMsg.value = err?.data?.detail || err?.message || 'Error desconocido'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.nuevo-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.03);
  --border-subtle: rgba(255,255,255,0.08);
  --border-glow: rgba(232,196,160,0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.6);
  --text-muted: rgba(245,240,235,0.35);
  --accent-gold: #e8c4a0;
  --accent-error: #fb7185;
  --accent-success: #34d399;
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
.stagger-2 { animation-delay: 0.1s; }

/* ─── HEADER ─── */
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
.page-title { font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-0.02em; }
.page-subtitle { color:var(--text-secondary); font-size:0.83rem; margin:0; }

/* ─── FORM CARD ─── */
.form-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.25rem;
}

/* ─── FIELDS ─── */
.field-group { display: flex; flex-direction: column; gap: 0.4rem; }
.field-row { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }

.field-label {
  color: var(--text-muted);
  font-size: 0.75rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em;
}
.required { color: var(--accent-error); }

.field-input, .field-select {
  padding: 0.75rem 1rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  font-size: 0.92rem; font-family: inherit;
  outline: none; transition: border-color 0.2s, background 0.2s;
  width: 100%;
}
.field-input:focus, .field-select:focus {
  border-color: var(--border-glow);
  background: rgba(255,255,255,0.07);
}
.field-input.error, .field-select.error { border-color: rgba(251,113,133,0.5); }
.field-input::placeholder { color: var(--text-muted); }

.field-error { color: var(--accent-error); font-size: 0.78rem; }

.field-hint {
  display: flex; align-items: center; gap: 0.375rem;
  color: var(--text-muted); font-size: 0.75rem; margin: 0;
}
.field-hint svg { flex-shrink: 0; color: var(--accent-gold); }

/* ─── SELECT ─── */
.select-wrapper { position: relative; }
.field-select { appearance: none; padding-right: 2.5rem; cursor: pointer; }
.select-icon {
  position: absolute; right: 0.875rem; top: 50%; transform: translateY(-50%);
  color: var(--text-muted); pointer-events: none;
}
.field-select option { background: #1a1a20; color: var(--text-primary); }

/* ─── LOGO PREVIEW ─── */
.logo-preview {
  display: flex; align-items: center; gap: 0.75rem;
  margin-top: 0.5rem;
}
.logo-preview-img {
  width: 52px; height: 52px; border-radius: var(--radius-sm);
  object-fit: cover;
  border: 1px solid var(--border-subtle);
  background: rgba(255,255,255,0.06);
}
.logo-preview-error { color: var(--accent-error); font-size: 0.78rem; }

/* ─── TOGGLE ─── */
.toggle-label {
  display: flex; align-items: center; justify-content: space-between;
  cursor: pointer; gap: 1rem;
}
.toggle-info { display: flex; flex-direction: column; gap: 0.2rem; }
.toggle-desc { color: var(--text-muted); font-size: 0.78rem; }
.toggle-switch {
  width: 44px; height: 24px; border-radius: 999px;
  background: rgba(255,255,255,0.1); border: 1px solid var(--border-subtle);
  position: relative; flex-shrink: 0; transition: all 0.3s ease; cursor: pointer;
}
.toggle-switch.on {
  background: rgba(232,196,160,0.25);
  border-color: rgba(232,196,160,0.4);
}
.toggle-thumb {
  position: absolute; top: 2px; left: 2px;
  width: 18px; height: 18px; border-radius: 50%;
  background: var(--text-muted);
  transition: all 0.3s ease;
}
.toggle-switch.on .toggle-thumb {
  left: calc(100% - 20px);
  background: var(--accent-gold);
}

/* ─── ALERTS ─── */
.alert-error, .alert-success {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.875rem 1rem; border-radius: var(--radius-md);
  font-size: 0.875rem; font-weight: 500;
}
.alert-error {
  background: rgba(251,113,133,0.1);
  border: 1px solid rgba(251,113,133,0.25);
  color: #fb7185;
}
.alert-success {
  background: rgba(52,211,153,0.1);
  border: 1px solid rgba(52,211,153,0.25);
  color: var(--accent-success);
}

/* ─── ACCIONES ─── */
.form-actions {
  display: flex; gap: 0.75rem;
}
.btn-cancel {
  flex: 1; padding: 0.875rem;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary); font-size: 0.9rem; font-weight: 500;
  cursor: pointer; transition: all 0.25s;
}
.btn-cancel:hover:not(:disabled) {
  background: rgba(255,255,255,0.08);
  color: var(--text-primary);
}
.btn-submit {
  flex: 2; padding: 0.875rem;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  background: linear-gradient(135deg, rgba(232,196,160,0.2), rgba(232,196,160,0.1));
  border: 1px solid rgba(232,196,160,0.35);
  border-radius: var(--radius-md);
  color: var(--accent-gold); font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: all 0.25s;
}
.btn-submit:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(232,196,160,0.3), rgba(232,196,160,0.15));
  border-color: rgba(232,196,160,0.5);
  transform: translateY(-1px);
}
.btn-submit:disabled, .btn-cancel:disabled {
  opacity: 0.5; cursor: not-allowed; transform: none;
}
.btn-spinner {
  width: 16px; height: 16px;
  border: 2px solid rgba(232,196,160,0.3);
  border-top-color: var(--accent-gold);
  border-radius: 50%; animation: spin 0.7s linear infinite;
}

@media (max-width: 480px) {
  .page-content { padding: 1rem; }
  .field-row { grid-template-columns: 1fr; }
  .page-title { font-size: 1.2rem; }
}
</style>