<template>
  <div class="login-wrapper">
    <div class="login-bg-fixed" aria-hidden="true" />
    <main class="login-content">
      <!-- LOGO -->
      <div class="logo-section animate-fade-in-up">
        <div class="logo-wrap">
          <img
            src="/images/capp3D_elec.png"
            alt="ComparApp"
            class="logo-img"
            @error="showFallback = true"
          />
        </div>
        <h1 v-if="showFallback" class="logo-fallback">ComparApp</h1>
      </div>

      <!-- TITULO -->
      <div class="title-section animate-fade-in-up stagger-1">
        <h2 class="login-title">Tu plataforma de ahorro inteligente</h2>
      </div>

      <!-- FORMULARIO -->
      <form @submit.prevent="login" class="login-form animate-fade-in-up stagger-2">
        <div class="field">
          <label class="field-label">Email</label>
          <div class="field-input-wrap">
            <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="20" height="16" x="2" y="4" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
            <input
              v-model="email"
              type="email"
              placeholder="tu@email.com"
              class="field-input"
              required
            />
          </div>
        </div>

        <div class="field">
          <label class="field-label">Contraseña</label>
          <div class="field-input-wrap">
            <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              v-model="password"
              type="password"
              placeholder="••••••••"
              class="field-input"
              required
            />
          </div>
        </div>

        <div class="forgot-link">
          <NuxtLink to="/forgot-password">¿Olvidaste tu contraseña?</NuxtLink>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="btn-loading">
            <span class="loading-spinner loading-spinner--sm" />
            Ingresando...
          </span>
          <span v-else>Iniciar Sesión</span>
        </button>
      </form>

      <!-- DIVIDER -->
      <div class="divider animate-fade-in-up stagger-3">
        <span class="divider-line" />
        <span class="divider-text">o</span>
        <span class="divider-line" />
      </div>

      <!-- GOOGLE LOGIN -->
      <button 
        class="btn-google animate-fade-in-up stagger-3" 
        @click="loginWithGoogle"
        :disabled="loadingGoogle"
      >
        <span v-if="loadingGoogle" class="btn-loading">
          <span class="loading-spinner loading-spinner--sm" />
          Conectando...
        </span>
        <span v-else class="btn-google-content">
          <svg class="google-icon" width="20" height="20" viewBox="0 0 24 24">
            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"/>
            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
          </svg>
          Continuar con Google
        </span>
      </button>

      <p v-if="error" class="login-error animate-fade-in-up">{{ error }}</p>

      <p class="login-link animate-fade-in-up stagger-4">
        ¿No tienes cuenta? <NuxtLink to="/register">Registrate</NuxtLink>
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

interface LoginResponse {
  message: string
  user: {
    id?: string
    email?: string
    user_metadata?: {
      nombre_completo?: string
      email?: string
      email_verified?: boolean
      phone_verified?: boolean
      sub?: string
    }
    access_token?: string
    id_user?: string
    email_user?: string
    nombre_completo_user?: string
    telefono_user?: string
    fecha_registro_user?: string
    ultima_conexion_user?: string
    rol_user?: string
    direccion_user?: string | null
    ciudad_user?: string | null
    provincia_user?: string | null
    pais_user?: string | null
    es_comercio_user?: boolean
    comercio_verificado_user?: boolean
    comercio_id_user?: string | null
    avatar_url_user?: string | null
    preferencias_user?: string
    activo_user?: boolean
    fecha_actualizacion_user?: string
  }
}

const config = useRuntimeConfig()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const loadingGoogle = ref(false)
const showFallback = ref(false)

async function login() {
  error.value = ''
  loading.value = true

  try {
    const response = await $fetch<LoginResponse>(`${config.public.apiBase}/login`, {
      method: 'POST',
      headers: {
    'Content-Type': 'application/json'
    },
    body: JSON.stringify({ 
      email: email.value, 
      password: password.value 
    })
    })

    if (response?.message === 'Login exitoso' && response?.user) {
      const userData = {
        id: response.user.id_user || response.user.id || '',
        email: response.user.email_user || response.user.email || '',
        nombre_completo: response.user.nombre_completo_user || 
                        response.user.user_metadata?.nombre_completo || 
                        'Usuario',
        telefono: response.user.telefono_user || '',
        avatar_url: response.user.avatar_url_user || null,
        direccion: response.user.direccion_user || null,
        ciudad: response.user.ciudad_user || null,
        provincia: response.user.provincia_user || null,
        pais: response.user.pais_user || null,
        rol: response.user.rol_user || 'usuario',
        activo: response.user.activo_user ?? true,
        es_comercio: response.user.es_comercio_user || false,
        comercio_verificado: response.user.comercio_verificado_user || false,
        fecha_registro: response.user.fecha_registro_user || null,
        ultima_conexion: response.user.ultima_conexion_user || null,
        access_token: response.user.access_token || ''
      }

      localStorage.setItem('comparapp_user', JSON.stringify(userData))
      console.log('Usuario guardado:', userData)
      await navigateTo('/dashboard')
    } else {
      error.value = response?.message || 'Error desconocido en el login'
    }
  } catch (err: any) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

async function loginWithGoogle() {
  error.value = ''
  loadingGoogle.value = true
  try {
    const { loginWithGoogle: oauthGoogle } = useSupabaseAuth()
    await oauthGoogle()
    // Si no tiró error, el redirect a Google ya está en curso (window.location
    // está cambiando). No es un error — antes esto seteaba un mensaje de error
    // que se veía un instante en pantalla antes de que la página navegara afuera.
  } catch (err: any) {
    error.value = 'Google OAuth no está configurado aún. Usá email y contraseña.'
    console.error('Google OAuth error:', err)
  } finally {
    loadingGoogle.value = false
  }
}

function handleError(err: any) {
  console.error('Error:', err)

  if (err?.data?.detail) {
    if (Array.isArray(err.data.detail)) {
      error.value = err.data.detail.map((d: any) => d.msg).join(', ')
    } else {
      error.value = err.data.detail
    }
  } else if (err.status === 401) {
    error.value = 'Email o contraseña incorrectos'
  } else if (err.status === 422) {
    error.value = 'Datos incompletos o incorrectos'
  } else if (err.message?.includes('fetch') || err.message?.includes('Failed to fetch')) {
    error.value = 'No se pudo conectar al servidor. Verificá que el backend esté corriendo.'
  } else {
    error.value = err.message || 'Error inesperado al iniciar sesión'
  }
}
</script>

<style scoped>
/* ─── LOGIN SIEMPRE OSCURO ───
   El login no debe depender del tema global del dashboard — queda fijo en
   oscuro sin importar el modo claro/oscuro del resto de la app. */
.login-wrapper {
  --app-text-primary: #f5f0eb;
  --app-text-secondary: rgba(245, 240, 235, 0.65);
  --app-text-muted: rgba(245, 240, 235, 0.4);
  --app-border-subtle: rgba(255, 255, 255, 0.08);
  --app-border-glow: rgba(232, 196, 160, 0.3);
  --app-gold: #e8c4a0;
  --app-radius-sm: 10px;
  --app-radius-md: 14px;
  --app-shadow-glow: 0 0 20px rgba(232, 196, 160, 0.12);
}
.login-bg-fixed {
  position: fixed; inset: 0; z-index: -1;
  background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232, 196, 160, 0.08), transparent),
              linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 100%);
}

/* ─── LOGIN WRAPPER — contenedor raíz transparente ─── */
/* ← CAMBIO: reemplaza .app-page, sin fondo propio para dejar ver el fondo global de app.vue */
.login-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  /* Sin background — el fondo lo provee #app-background en app.vue */
}

/* ─── LOGIN CONTENT ─── */
.login-content {
  position: relative;
  /* ← CAMBIO: eliminado z-index: 2, no es necesario con #app-background en z-index: -1 */
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  max-width: 420px;
  margin: 0 auto;
}

/* ─── LOGO ─── */
.logo-section {
  text-align: center;
  margin-bottom: 2rem;
}

.logo-wrap {
  width: 160px;
  height: 100px;
  border-radius: 24px;
  background: rgba(232, 196, 160, 0.01);
  border: 1px solid rgba(12, 11, 11, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 1rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}

.logo-img {
  width: 150px;
  height: 150px;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
}

.logo-fallback {
  color: var(--app-text-primary);
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
}

/* ─── TITULO ─── */
.title-section {
  text-align: center;
  margin-bottom: 2rem;
}

.login-title {
  color: var(--app-text-primary);
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.5rem;
  letter-spacing: -0.02em;
}

/* ─── FORMULARIO ─── */
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  color: var(--app-text-secondary);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.field-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0 1rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  border: 1px solid var(--app-border-subtle);
  border-radius: var(--app-radius-md);
  transition: all 0.3s ease;
}

.field-input-wrap:focus-within {
  border-color: var(--app-border-glow);
  box-shadow: var(--app-shadow-glow), 0 0 0 4px rgba(232, 196, 160, 0.05);
  background: rgba(255, 255, 255, 0.05);
}

.field-icon {
  color: var(--app-text-muted);
  flex-shrink: 0;
}

.field-input {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--app-text-primary);
  font-size: 0.95rem;
  padding: 0.875rem 0;
  outline: none;
  font-family: inherit;
}

.field-input::placeholder {
  color: var(--app-text-muted);
}

/* ─── LINKS ─── */
.forgot-link {
  text-align: right;
  font-size: 0.85rem;
}

.forgot-link a {
  color: var(--app-text-secondary);
  text-decoration: none;
  transition: color 0.25s;
}

.forgot-link a:hover {
  color: var(--app-gold);
}

/* ─── BOTONES ─── */
.btn-primary {
  width: 100%;
  padding: 1rem;
  border: none;
  border-radius: var(--app-radius-md);
  background: linear-gradient(135deg, rgba(255,255,255,0.12), rgba(255,255,255,0.06));
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--app-text-primary);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
  transition: left 0.5s ease;
}

.btn-primary:hover::before {
  left: 100%;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.2), rgba(232, 196, 160, 0.1));
  border-color: var(--app-border-glow);
  box-shadow: var(--app-shadow-glow);
  transform: translateY(-2px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

/* ─── DIVIDER ─── */
.divider {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0;
}

.divider-line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
}

.divider-text {
  color: var(--app-text-muted);
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

/* ─── GOOGLE BUTTON ─── */
.btn-google {
  width: 100%;
  padding: 0.875rem;
  border-radius: var(--app-radius-md);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--app-border-subtle);
  color: var(--app-text-primary);
  font-size: 0.95rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-google:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--app-border-glow);
  transform: translateY(-2px);
}

.btn-google:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-google-content {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.google-icon {
  flex-shrink: 0;
}

/* ─── ERROR ─── */
.login-error {
  color: #fb7185;
  background: rgba(251, 113, 133, 0.1);
  border: 1px solid rgba(251, 113, 133, 0.2);
  border-radius: var(--app-radius-sm);
  padding: 0.875rem;
  text-align: center;
  font-size: 0.9rem;
  width: 100%;
}

/* ─── LINK REGISTRO ─── */
.login-link {
  text-align: center;
  color: var(--app-text-secondary);
  font-size: 0.9rem;
  margin-top: 1.5rem;
}

.login-link a {
  color: var(--app-gold);
  text-decoration: none;
  font-weight: 600;
  transition: all 0.25s;
}

.login-link a:hover {
  text-decoration: underline;
}

/* ─── RESPONSIVE ─── */
@media (max-width: 480px) {
  .login-content { padding: 1rem; }
  .login-title { font-size: 1.5rem; }
  .logo-wrap { width: 80px; height: 80px; }
  .logo-img { width: 55px; height: 55px; }
}
</style>