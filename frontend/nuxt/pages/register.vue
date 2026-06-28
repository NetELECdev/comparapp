<template>
  <div class="app-page">
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
        <h2 class="login-title">Crea tu cuenta</h2>
        <p class="login-subtitle">Empezá a comparar y ahorrar</p>
      </div>

      <!-- FORMULARIO -->
      <form @submit.prevent="register" class="login-form animate-fade-in-up stagger-2">
        <div class="avatar-picker">
          <button type="button" class="avatar-picker-btn" @click="avatarInput?.click()">
            <img v-if="avatarPreview" :src="avatarPreview" alt="" class="avatar-picker-img" />
            <svg v-else width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/>
            </svg>
            <span class="avatar-picker-badge">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 5v14M5 12h14"/></svg>
            </span>
          </button>
          <input
            ref="avatarInput"
            type="file"
            accept="image/png, image/jpeg, image/webp"
            class="avatar-picker-input"
            @change="onAvatarSelected"
          />
          <span class="avatar-picker-label">{{ avatarPreview ? 'Cambiar foto' : 'Foto de perfil (opcional)' }}</span>
        </div>

        <div class="field">
          <label class="field-label">Nombre completo</label>
          <div class="field-input-wrap">
            <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
            <input
              v-model="nombre"
              type="text"
              placeholder="Tu nombre"
              class="field-input"
              required
            />
          </div>
        </div>

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
              placeholder="Mínimo 8 caracteres"
              class="field-input"
              minlength="8"
              required
            />
          </div>
        </div>

        <div class="field">
          <label class="field-label">Confirmar contraseña</label>
          <div class="field-input-wrap">
            <svg class="field-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <rect width="18" height="11" x="3" y="11" rx="2" ry="2"/>
              <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              <path d="m9 17 2 2 4-4"/>
            </svg>
            <input
              v-model="passwordConfirm"
              type="password"
              placeholder="Repetí tu contraseña"
              class="field-input"
              required
            />
          </div>
        </div>

        <div class="terms-field">
          <label class="terms-label">
            <input v-model="acceptTerms" type="checkbox" class="terms-checkbox" required />
            <span>Acepto los <NuxtLink to="/terms">términos y condiciones</NuxtLink></span>
          </label>
        </div>

        <button type="submit" class="btn-primary" :disabled="loading || !passwordsMatch">
          <span v-if="loading" class="btn-loading">
            <span class="loading-spinner loading-spinner--sm" />
            Creando cuenta...
          </span>
          <span v-else>Registrarme</span>
        </button>
      </form>

      <!-- DIVIDER -->
      <div class="divider animate-fade-in-up stagger-3">
        <span class="divider-line" />
        <span class="divider-text">o</span>
        <span class="divider-line" />
      </div>

      <!-- GOOGLE REGISTER -->
      <button 
        class="btn-google animate-fade-in-up stagger-3" 
        @click="registerWithGoogle"
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
      <p v-if="success" class="login-success animate-fade-in-up">{{ success }}</p>

      <p class="login-link animate-fade-in-up stagger-4">
        ¿Ya tenés cuenta? <NuxtLink to="/login">Iniciá sesión</NuxtLink>
      </p>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

const config = useRuntimeConfig()
const nombre = ref('')
const email = ref('')
const password = ref('')
const passwordConfirm = ref('')
const acceptTerms = ref(false)
const error = ref('')
const success = ref('')
const loading = ref(false)
const loadingGoogle = ref(false)
const showFallback = ref(false)

const avatarInput = ref<HTMLInputElement | null>(null)
const avatarFile = ref<File | null>(null)
const avatarPreview = ref<string | null>(null)

function onAvatarSelected(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
    error.value = 'La foto debe ser PNG, JPG o WEBP'
    return
  }
  if (file.size > 5 * 1024 * 1024) {
    error.value = 'La foto no puede pesar más de 5 MB'
    return
  }
  avatarFile.value = file
  avatarPreview.value = URL.createObjectURL(file)
}

const passwordsMatch = computed(() => password.value === passwordConfirm.value && password.value.length >= 8)

async function register() {
  error.value = ''
  success.value = ''

  if (!passwordsMatch.value) {
    error.value = 'Las contraseñas no coinciden'
    return
  }
  if (!acceptTerms.value) {
    error.value = 'Debes aceptar los términos y condiciones'
    return
  }

  loading.value = true

  try {
    const formData = new FormData()
    formData.append('email', email.value)
    formData.append('password', password.value)
    formData.append('nombre_completo', nombre.value)
    if (avatarFile.value) {
      formData.append('avatar', avatarFile.value)
    }

    const response = await $fetch(`${config.public.apiBase}/register`, {
      method: 'POST',
      body: formData
    })

    if (response?.message === 'Registro exitoso') {
      success.value = '¡Cuenta creada! Redirigiendo...'
      setTimeout(() => navigateTo('/login'), 2000)
    } else {
      error.value = response?.message || 'Error en el registro'
    }
  } catch (err: any) {
    handleError(err)
  } finally {
    loading.value = false
  }
}

async function registerWithGoogle() {
  error.value = ''
  loadingGoogle.value = true
  try {
    const { loginWithGoogle: oauthGoogle } = useSupabaseAuth()
    await oauthGoogle()
    // Si no tiró error, el redirect a Google ya está en curso — no es un error.
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
  } else if (err.status === 400) {
    error.value = err.data?.detail || 'Error en el registro. Verificá los datos.'
  } else if (err.status === 409) {
    error.value = 'Ya existe una cuenta con este email'
  } else if (err.status === 422) {
    error.value = 'Datos incompletos o incorrectos'
  } else if (err.message?.includes('fetch') || err.message?.includes('Failed to fetch')) {
    error.value = 'No se pudo conectar al servidor. Verificá que el backend esté corriendo.'
  } else {
    error.value = err.message || 'Error inesperado al registrarse'
  }
}
</script>

<style scoped>
/* ─── REGISTER — Design System Vitaria ─── */

.login-content {
  position: relative;
  z-index: 2;
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
  margin-bottom: 1.5rem;
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
  margin-bottom: 1.5rem;
}

.login-title {
  color: var(--app-text-primary);
  font-size: 1.2rem;
  font-weight: 700;
  margin: 0 0 0.25rem;
  letter-spacing: -0.02em;
}

.login-subtitle {
  color: var(--app-text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

/* ─── FORMULARIO ─── */
.login-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* ─── AVATAR PICKER ─── */
.avatar-picker {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}
.avatar-picker-btn {
  position: relative;
  width: 76px;
  height: 76px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--app-border-subtle);
  color: var(--app-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.25s ease;
}
.avatar-picker-btn:hover {
  border-color: var(--app-border-glow);
  color: #e8c4a0;
}
.avatar-picker-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.avatar-picker-badge {
  position: absolute;
  bottom: -1px;
  right: -1px;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #e8c4a0;
  color: #1a1410;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #0a0a0f;
}
.avatar-picker-input {
  display: none;
}
.avatar-picker-label {
  color: var(--app-text-muted);
  font-size: 0.75rem;
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

/* ─── TERMS ─── */
.terms-field {
  margin-top: 0.25rem;
}

.terms-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--app-text-secondary);
  font-size: 0.85rem;
  cursor: pointer;
}

.terms-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--app-gold);
  cursor: pointer;
}

.terms-label a {
  color: var(--app-gold);
  text-decoration: none;
}

.terms-label a:hover {
  text-decoration: underline;
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

/* ─── MESSAGES ─── */
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

.login-success {
  color: #4ade80;
  background: rgba(74, 222, 128, 0.1);
  border: 1px solid rgba(74, 222, 128, 0.2);
  border-radius: var(--app-radius-sm);
  padding: 0.875rem;
  text-align: center;
  font-size: 0.9rem;
  width: 100%;
}

/* ─── LINK LOGIN ─── */
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