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
        <h2 class="login-title">¿Olvidaste tu contraseña?</h2>
        <p class="login-subtitle">Te enviaremos un enlace para restablecerla</p>
      </div>

      <!-- FORMULARIO -->
      <form @submit.prevent="sendResetLink" class="login-form animate-fade-in-up stagger-2">
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

        <button type="submit" class="btn-primary" :disabled="loading">
          <span v-if="loading" class="btn-loading">
            <span class="loading-spinner loading-spinner--sm" />
            Enviando...
          </span>
          <span v-else>Enviar enlace de recuperación</span>
        </button>
      </form>

      <p v-if="error" class="login-error animate-fade-in-up">{{ error }}</p>
      <p v-if="success" class="login-success animate-fade-in-up">{{ success }}</p>

      <!-- BACK TO LOGIN -->
      <div class="back-link animate-fade-in-up stagger-3">
        <NuxtLink to="/login" class="back-link-inner">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
          Volver al inicio de sesión
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRuntimeConfig } from '#app'

const config = useRuntimeConfig()
const email = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)
const showFallback = ref(false)

async function sendResetLink() {
  error.value = ''
  success.value = ''
  loading.value = true

  try {
    const response = await $fetch(`${config.public.apiBase}/forgot-password`, {
      method: 'POST',
      query: { email: email.value }
    })

    if (response?.message) {
      success.value = response.message
      email.value = ''
    } else {
      error.value = 'No se pudo enviar el enlace. Intentá de nuevo.'
    }
  } catch (err: any) {
    handleError(err)
  } finally {
    loading.value = false
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
  } else if (err.status === 404) {
    error.value = 'No encontramos una cuenta con ese email'
  } else if (err.status === 422) {
    error.value = 'Email inválido'
  } else if (err.status === 429) {
    error.value = 'Demasiados intentos. Esperá unos minutos.'
  } else if (err.message?.includes('fetch') || err.message?.includes('Failed to fetch')) {
    error.value = 'No se pudo conectar al servidor. Verificá que el backend esté corriendo.'
  } else {
    error.value = err.message || 'Error inesperado al enviar el enlace'
  }
}
</script>

<style scoped>
/* ─── FORGOT PASSWORD — Design System Vitaria ─── */

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
  margin-bottom: 2rem;
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
  margin-top: 1rem;
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
  margin-top: 1rem;
}

/* ─── BACK LINK ─── */
.back-link {
  margin-top: 2rem;
}

.back-link-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: var(--app-text-secondary);
  font-size: 0.9rem;
  text-decoration: none;
  transition: color 0.25s;
}

.back-link-inner:hover {
  color: var(--app-gold);
}

.back-link-inner svg {
  transition: transform 0.25s;
}

.back-link-inner:hover svg {
  transform: translateX(-3px);
}

/* ─── RESPONSIVE ─── */
@media (max-width: 480px) {
  .login-content { padding: 1rem; }
  .login-title { font-size: 1.5rem; }
  .logo-wrap { width: 80px; height: 80px; }
  .logo-img { width: 55px; height: 55px; }
}
</style>
