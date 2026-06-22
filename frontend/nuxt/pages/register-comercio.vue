<template>
  <div class="register-comercio-page">
    <div class="auth-bg-fixed" aria-hidden="true" />

    <main class="page-content">
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/login')" aria-label="Volver">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div>
          <h1 class="page-title">Registrá tu comercio</h1>
          <p class="page-subtitle">Cargá tus propios productos en ComparApp</p>
        </div>
      </header>

      <!-- ESTADO: ya enviado -->
      <div v-if="enviado" class="success-box animate-fade-in-up">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><path d="M9 12l2 2 4-4"/>
        </svg>
        <h2>Solicitud enviada</h2>
        <p>{{ mensajeExito }}</p>
        <button class="btn-primary" @click="navigateTo('/login')">Ir a iniciar sesión</button>
      </div>

      <!-- FORMULARIO -->
      <form v-else class="form-card animate-fade-in-up stagger-1" @submit.prevent="enviarRegistro">

        <div class="form-group">
          <label>Tu comercio *</label>
          <div v-if="loadingComercios" class="select-loading">Cargando comercios...</div>
          <select v-else v-model="form.id_comer" required>
            <option value="">Seleccioná tu comercio...</option>
            <option v-for="c in comercios" :key="c.id_comer" :value="c.id_comer">
              {{ c.nombre_comer }} — {{ c.direccion_comer }}
            </option>
          </select>
          <p v-if="!loadingComercios && comercios.length === 0" class="form-hint form-hint--warning">
            No hay comercios disponibles todavía. Contactá al administrador para que cargue tu comercio antes de registrarte.
          </p>
          <p v-else class="form-hint">
            ¿No encontrás tu comercio en la lista? Contactá al administrador para que lo agregue primero.
          </p>
        </div>

        <div class="form-group">
          <label>Nombre completo *</label>
          <input v-model="form.nombre_completo" required placeholder="Tu nombre y apellido" />
        </div>

        <div class="form-group">
          <label>Email *</label>
          <input v-model="form.email" type="email" required placeholder="tu@email.com" />
        </div>

        <div class="form-group">
          <label>Teléfono</label>
          <input v-model="form.telefono" type="tel" placeholder="Opcional" />
        </div>

        <div class="form-group">
          <label>Contraseña *</label>
          <input v-model="form.password" type="password" required minlength="6" placeholder="Mínimo 6 caracteres" />
        </div>

        <div class="form-group">
          <label>Confirmar contraseña *</label>
          <input v-model="confirmPassword" type="password" required minlength="6" placeholder="Repetí tu contraseña" />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="btn-primary" :disabled="enviando || comercios.length === 0">
          {{ enviando ? 'Enviando...' : 'Enviar solicitud' }}
        </button>

        <p class="aviso-aprobacion">
          ⏳ Tu acceso quedará pendiente de aprobación por el administrador antes de poder cargar productos.
        </p>
      </form>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { navigateTo, useRuntimeConfig } from '#app'

interface Comercio {
  id_comer: string
  nombre_comer: string
  direccion_comer: string
}

const config = useRuntimeConfig()

const comercios = ref<Comercio[]>([])
const loadingComercios = ref(true)
const enviando = ref(false)
const enviado = ref(false)
const errorMsg = ref('')
const mensajeExito = ref('')
const confirmPassword = ref('')
const form = ref({
  id_comer: '',
  nombre_completo: '',
  email: '',
  telefono: '',
  password: '',
})

async function cargarComercios() {
  loadingComercios.value = true
  try {
    const res = await $fetch<{ count: number; results: Comercio[] }>(
      `${config.public.apiBase}/comercios-disponibles`
    )
    comercios.value = res.results || []
  } catch (err) {
    console.error('Error cargando comercios:', err)
  } finally {
    loadingComercios.value = false
  }
}

async function enviarRegistro() {
  errorMsg.value = ''

  if (form.value.password !== confirmPassword.value) {
    errorMsg.value = 'Las contraseñas no coinciden'
    return
  }
  if (!form.value.id_comer) {
    errorMsg.value = 'Seleccioná tu comercio'
    return
  }

  enviando.value = true
  try {
    const res = await $fetch<{ message: string }>(`${config.public.apiBase}/register-comercio`, {
      method: 'POST',
      body: {
        email: form.value.email,
        password: form.value.password,
        nombre_completo: form.value.nombre_completo,
        telefono: form.value.telefono || null,
        id_comer: form.value.id_comer,
      }
    })
    mensajeExito.value = res.message || 'Tu solicitud fue enviada y está pendiente de aprobación.'
    enviado.value = true
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo completar el registro. Intentá de nuevo.'
  } finally {
    enviando.value = false
  }
}

onMounted(() => {
  cargarComercios()
})
</script>

<style scoped>
/* Pantalla de ingreso siempre oscura — el cambio de tema solo vive en el dashboard.
   Estos overrides fijan los tokens del tema únicamente dentro de esta página. */
.register-comercio-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.04);
  --bg-card-hover: rgba(255,255,255,0.08);
  --bg-input: rgba(255,255,255,0.06);
  --border-subtle: rgba(255,255,255,0.08);
  --border-glow: rgba(232,196,160,0.3);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.65);
  --text-muted: rgba(245,240,235,0.4);
  --accent-gold: #e8c4a0;
  --accent-gold-dim: rgba(232,196,160,0.18);
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 18px;
}
.register-comercio-page {
  background: var(--bg-deep);
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.auth-bg-fixed {
  position: fixed; inset: 0; z-index: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232,196,160,0.08), transparent),
              linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 100%);
}
.page-content {
  position: relative; z-index: 2;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.25rem;
  max-width: 480px; margin: 0 auto;
  padding-bottom: 3rem;
}
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }

.page-header { display: flex; align-items: center; gap: 0.875rem; }
.back-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg-card-hover); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s; flex-shrink: 0;
}
.back-btn:hover { border-color: var(--border-glow); color: var(--text-primary); }
.page-title { font-size: 1.4rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
.page-subtitle { color: var(--text-secondary); font-size: 0.82rem; margin: 0; }

.form-card {
  display: flex; flex-direction: column; gap: 1.1rem;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); padding: 1.5rem;
}
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group label { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); }
.form-group input, .form-group select {
  padding: 0.75rem 1rem; border-radius: var(--radius-md);
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  color: var(--text-primary); font-size: 0.92rem; outline: none; transition: border-color 0.2s;
}
.form-group input:focus, .form-group select:focus { border-color: var(--border-glow); }
.form-hint { font-size: 0.74rem; color: var(--text-muted); margin: 0; }
.form-hint--warning { color: #fbbf24; }
.select-loading { font-size: 0.85rem; color: var(--text-muted); padding: 0.5rem 0; }

.error-msg {
  color: #fb7185; font-size: 0.82rem;
  background: rgba(251,113,133,0.1); border: 1px solid rgba(251,113,133,0.25);
  border-radius: var(--radius-sm); padding: 0.625rem 0.875rem; margin: 0;
}

.btn-primary {
  padding: 0.875rem; border-radius: var(--radius-md);
  background: var(--accent-gold-dim); border: 1px solid var(--border-glow);
  color: var(--accent-gold); font-size: 0.95rem; font-weight: 700;
  cursor: pointer; transition: all 0.25s;
}
.btn-primary:hover:not(:disabled) { background: var(--bg-card-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-google {
  display: flex; align-items: center; justify-content: center; gap: 0.625rem;
  padding: 0.825rem; border-radius: var(--radius-md);
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-primary); font-size: 0.9rem; font-weight: 600;
  cursor: pointer; transition: all 0.25s;
}
.btn-google:hover:not(:disabled) { background: var(--bg-card-hover); border-color: var(--border-glow); }
.btn-google:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-google-content { display: flex; align-items: center; gap: 0.625rem; }
.btn-loading { display: flex; align-items: center; gap: 0.5rem; }
.loading-spinner--sm {
  width: 16px; height: 16px;
  border: 2px solid var(--border-subtle); border-top-color: var(--accent-gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.divider { display: flex; align-items: center; gap: 0.75rem; }
.divider-line { flex: 1; height: 1px; background: var(--border-subtle); }
.divider-text { font-size: 0.72rem; color: var(--text-muted); white-space: nowrap; }

.aviso-aprobacion {
  text-align: center; font-size: 0.78rem; color: var(--text-muted);
  margin: 0; line-height: 1.4;
}

.success-box {
  display: flex; flex-direction: column; align-items: center; gap: 0.875rem;
  text-align: center; padding: 3rem 1.5rem;
  background: var(--bg-card); border: 1px solid var(--border-glow);
  border-radius: var(--radius-lg);
}
.success-box svg { color: #4ade80; }
.success-box h2 { font-size: 1.2rem; font-weight: 700; margin: 0; color: var(--text-primary); }
.success-box p { font-size: 0.88rem; color: var(--text-secondary); margin: 0; }
</style>