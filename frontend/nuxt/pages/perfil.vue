<!-- pages/perfil.vue -->
<template>
  <div class="perfil-page">
    <DynamicBackground />

    <div class="perfil-content">

      <!-- Header -->
      <header class="perfil-header">
        <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h1 class="perfil-title">Mi Perfil</h1>
        <ToggleTema />
      </header>

      <!-- Card principal -->
      <div class="perfil-card glass-card">

        <!-- Avatar -->
        <div class="avatar-wrap">
          <img
            :src="user.avatar_url || user.picture || '/images/avatar_default.png'"
            :alt="displayName"
            class="avatar-img"
            @error="(e) => ((e.target as HTMLImageElement).src = '/images/avatar_default.png')"
          />
          <div class="avatar-badge" :class="rolClass">{{ rolLabel }}</div>
        </div>

        <!-- Nombre y email -->
        <h2 class="perfil-name">{{ displayName }}</h2>
        <p class="perfil-email">{{ user.email || user.email_user || '' }}</p>

        <!-- Stats rápidas -->
        <div class="perfil-stats">
          <div class="stat-item">
            <span class="stat-val">{{ stats.listas }}</span>
            <span class="stat-lbl">Listas</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val">{{ stats.favoritos }}</span>
            <span class="stat-lbl">Favoritos</span>
          </div>
          <div class="stat-divider" />
          <div class="stat-item">
            <span class="stat-val">{{ stats.alertas }}</span>
            <span class="stat-lbl">Alertas</span>
          </div>
        </div>

        <!-- Acciones -->
        <div class="perfil-actions">
          <button class="btn-accion btn-editar" @click="showComingSoon">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            Editar Perfil
          </button>
          <button v-if="!esGoogleUser" class="btn-accion btn-password" @click="mostrarModalPassword = true">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            Cambiar contraseña
          </button>
          <button class="btn-accion btn-salir" @click="cerrarSesion">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
            Cerrar Sesión
          </button>
        </div>

        <!-- Admin link -->
        <button v-if="isAdmin" class="btn-admin" @click="navigateTo('/admin')">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20z"/><path d="M12 8v4l3 3"/></svg>
          Panel de Administración
        </button>

      </div>

      <!-- Info de cuenta -->
      <div class="perfil-info glass-card">
        <div class="info-row">
          <span class="info-label">Miembro desde</span>
          <span class="info-val">{{ memberSince }}</span>
        </div>
        <div class="info-row" v-if="user.comercio_oauth">
          <span class="info-label">Cuenta vinculada</span>
          <span class="info-val info-google">
            <svg width="14" height="14" viewBox="0 0 24 24" aria-hidden="true"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
            Google
          </span>
        </div>
      </div>

      <!-- Ayuda y datos de la empresa -->
      <button class="perfil-link-card glass-card" @click="navigateTo('/ayuda')">
        <div class="perfil-link-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 2-3 4"/><line x1="12" y1="17" x2="12" y2="17.01"/></svg>
        </div>
        <span class="perfil-link-label">Ayuda y datos de la empresa</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="perfil-link-arrow"><path d="m9 18 6-6-6-6"/></svg>
      </button>

    </div>

    <!-- Bottom nav -->
    <nav class="bottom-nav" aria-label="Navegación principal">
      <button class="bnav-btn" @click="navigateTo('/dashboard')" aria-label="Inicio">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Inicio</span>
      </button>
      <button class="bnav-btn" @click="navigateTo('/productos')" aria-label="Productos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
        <span>Productos</span>
      </button>
      <button class="bnav-btn bnav-btn--center" @click="navigateTo('/comparaciones')" aria-label="Comparar">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
      </button>
      <button class="bnav-btn" @click="navigateTo('/favoritos')" aria-label="Favoritos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        <span>Favoritos</span>
      </button>
      <button class="bnav-btn bnav-btn--active" @click="navigateTo('/perfil')" aria-label="Perfil" aria-current="page">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Perfil</span>
      </button>
    </nav>
    <!-- Modal cambio de contraseña -->
    <Teleport to="body">
      <div v-if="mostrarModalPassword" class="modal-overlay-perfil" @click.self="cerrarModalPassword">
        <div class="modal-password">
          <div class="modal-pw-header">
            <h3>Cambiar contraseña</h3>
            <button class="modal-pw-close" @click="cerrarModalPassword">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>
          <div class="modal-pw-body">
            <div class="pw-field">
              <label>Contraseña actual</label>
              <input v-model="pwActual" :type="mostrarPw ? 'text' : 'password'" placeholder="Tu contraseña actual" />
            </div>
            <div class="pw-field">
              <label>Nueva contraseña</label>
              <input v-model="pwNueva" :type="mostrarPw ? 'text' : 'password'" placeholder="Mínimo 6 caracteres" />
            </div>
            <div class="pw-field">
              <label>Repetir nueva contraseña</label>
              <input v-model="pwNuevaRepetir" :type="mostrarPw ? 'text' : 'password'" placeholder="Repetí la nueva contraseña" />
            </div>
            <label class="pw-toggle-mostrar">
              <input type="checkbox" v-model="mostrarPw" />
              <span>Mostrar contraseñas</span>
            </label>
            <p v-if="pwError" class="pw-error">{{ pwError }}</p>
            <p v-if="pwExito" class="pw-exito">{{ pwExito }}</p>
            <div class="pw-actions">
              <button class="pw-btn-cancelar" @click="cerrarModalPassword">Cancelar</button>
              <button class="pw-btn-guardar" :disabled="cambiandoPw" @click="cambiarPassword">
                {{ cambiandoPw ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

useTema()
useBackground()

const user = ref<any>({})
const stats = ref({ listas: 0, favoritos: 0, alertas: 0 })
const config = useRuntimeConfig()

const displayName = computed(() =>
  user.value.nombre_completo ||
  user.value.full_name ||
  user.value.nombre ||
  user.value.name ||
  'Usuario'
)

const isAdmin = computed(() => user.value.rol === 'admin' || user.value.rol_user === 'admin')

const rolClass = computed(() => isAdmin.value ? 'badge-admin' : 'badge-user')
const rolLabel = computed(() => isAdmin.value ? 'Admin' : 'Usuario')

const memberSince = computed(() => {
  const fecha = user.value.created_at || user.value.fecha_registro
  if (!fecha) return 'N/D'
  return new Date(fecha).toLocaleDateString('es-AR', { month: 'long', year: 'numeric' })
})

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (!stored) { navigateTo('/login'); return }
  try { user.value = JSON.parse(stored) } catch {}

  // Cargar stats
  try {
    const [listas, favs] = await Promise.allSettled([
      $fetch<any>(`${config.public.apiBase}/listas`),
      $fetch<any>(`${config.public.apiBase}/favoritos`)
    ])
    if (listas.status === 'fulfilled') stats.value.listas = listas.value?.count || listas.value?.results?.length || 0
    if (favs.status === 'fulfilled') stats.value.favoritos = favs.value?.count || favs.value?.results?.length || 0
  } catch {}
})

function cerrarSesion() {
  localStorage.removeItem('comparapp_user')
  navigateTo('/login')
}

// ─── Cambio de contraseña ───────────────────────────────────
const esGoogleUser = computed(() => {
  // Si el usuario entró con Google no tiene contraseña que gestionar acá
  const providers = user.value?.app_metadata?.providers || []
  if (providers.includes('email')) return false
  // Fallback: si el avatar es de Google, probablemente es cuenta Google
  const avatar = user.value?.avatar_url || ''
  return avatar.includes('googleusercontent.com') && !user.value?.email_user
})

const mostrarModalPassword = ref(false)
const pwActual = ref('')
const pwNueva = ref('')
const pwNuevaRepetir = ref('')
const mostrarPw = ref(false)
const pwError = ref('')
const pwExito = ref('')
const cambiandoPw = ref(false)

function cerrarModalPassword() {
  mostrarModalPassword.value = false
  pwActual.value = ''
  pwNueva.value = ''
  pwNuevaRepetir.value = ''
  mostrarPw.value = false
  pwError.value = ''
  pwExito.value = ''
}

async function cambiarPassword() {
  pwError.value = ''
  pwExito.value = ''

  if (!pwActual.value || !pwNueva.value || !pwNuevaRepetir.value) {
    pwError.value = 'Completá todos los campos'
    return
  }
  if (pwNueva.value.length < 6) {
    pwError.value = 'La nueva contraseña debe tener al menos 6 caracteres'
    return
  }
  if (pwNueva.value !== pwNuevaRepetir.value) {
    pwError.value = 'Las contraseñas nuevas no coinciden'
    return
  }
  if (pwActual.value === pwNueva.value) {
    pwError.value = 'La nueva contraseña debe ser distinta a la actual'
    return
  }

  cambiandoPw.value = true
  try {
    const stored = localStorage.getItem('comparapp_user')
    const token = stored ? JSON.parse(stored).access_token : ''
    await $fetch(`${config.public.apiBase}/change-password`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ password_actual: pwActual.value, password_nueva: pwNueva.value })
    })
    pwExito.value = '✅ Contraseña actualizada correctamente'
    setTimeout(cerrarModalPassword, 2000)
  } catch (err: any) {
    pwError.value = err?.data?.detail || 'No se pudo cambiar la contraseña. Intentá de nuevo.'
  } finally {
    cambiandoPw.value = false
  }
}

function showComingSoon() {
  alert('Próximamente podrás editar tu perfil')
}
</script>

<style scoped>
.perfil-page {
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.perfil-content {
  position: relative;
  z-index: 2;
  padding: 0 16px 120px;
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Header */
.perfil-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  background: var(--bg-deep);
  backdrop-filter: blur(16px);
}
.back-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.back-btn:hover { border-color: var(--border-glow); color: var(--text-primary); }
.perfil-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }

/* Card */
.glass-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}

.perfil-card {
  padding: 28px 20px 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

/* Avatar */
.avatar-wrap { position: relative; margin-bottom: 4px; }
.avatar-img {
  width: 88px; height: 88px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--border-glow);
  box-shadow: 0 0 20px rgba(232,196,160,0.15);
}
.avatar-badge {
  position: absolute;
  bottom: 0; right: -4px;
  font-size: 10px; font-weight: 600;
  padding: 2px 7px; border-radius: 20px;
}
.badge-admin { background: rgba(232,196,160,0.2); color: var(--accent-gold); border: 1px solid var(--border-glow); }
.badge-user  { background: rgba(96,165,250,0.12); color: var(--accent-blue); border: 1px solid rgba(96,165,250,0.25); }

.perfil-name { font-size: 18px; font-weight: 700; color: var(--text-primary); margin: 4px 0 0; }
.perfil-email { font-size: 12px; color: var(--text-secondary); }

/* Stats */
.perfil-stats {
  display: flex;
  align-items: center;
  gap: 0;
  margin: 12px 0 4px;
  background: var(--bg-input);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  width: 100%;
}
.stat-item {
  flex: 1;
  display: flex; flex-direction: column; align-items: center;
  padding: 12px 8px;
  gap: 2px;
}
.stat-val { font-size: 18px; font-weight: 700; color: var(--text-primary); }
.stat-lbl { font-size: 10px; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.stat-divider { width: 1px; height: 32px; background: var(--border-subtle); }

/* Acciones */
.perfil-actions { display: flex; flex-direction: column; gap: 8px; width: 100%; margin-top: 8px; }
.btn-accion {
  display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 12px; border-radius: var(--radius-md);
  font-size: 14px; font-weight: 500; cursor: pointer;
  border: 1px solid var(--border-subtle);
  transition: all 0.2s;
  width: 100%;
}
.btn-editar {
  background: var(--bg-card-hover);
  color: var(--text-primary);
}
.btn-editar:hover { border-color: var(--border-glow); }
.btn-salir {
  background: rgba(251,113,133,0.08);
  color: var(--accent-rose);
  border-color: rgba(251,113,133,0.2);
}
.btn-salir:hover { background: rgba(251,113,133,0.15); }

.btn-admin {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  margin-top: 4px; padding: 8px 16px;
  border-radius: var(--radius-sm);
  font-size: 12px; font-weight: 500;
  background: rgba(232,196,160,0.08);
  border: 1px solid var(--border-glow);
  color: var(--accent-gold); cursor: pointer;
  transition: all 0.2s;
}
.btn-admin:hover { background: rgba(232,196,160,0.15); }

/* Info */
.perfil-info { padding: 16px; display: flex; flex-direction: column; gap: 0; }
.info-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 10px 0;
  border-bottom: 0.5px solid var(--border-subtle);
  font-size: 13px;
}
.info-row:last-child { border-bottom: none; }
.info-label { color: var(--text-muted); }
.info-val { color: var(--text-primary); font-weight: 500; }
.info-google { display: flex; align-items: center; gap: 5px; }

/* Link a Ayuda y datos de la empresa */
.perfil-link-card {
  display: flex; align-items: center; gap: 10px;
  width: 100%;
  padding: 14px 16px;
  cursor: pointer;
  transition: all 0.2s;
}
.perfil-link-card:hover { border-color: var(--border-glow); background: var(--bg-card-hover); }
.perfil-link-icon { color: var(--accent-gold); display: flex; flex-shrink: 0; }
.perfil-link-label { flex: 1; text-align: left; font-size: 13px; font-weight: 500; color: var(--text-primary); }
.perfil-link-arrow { color: var(--text-muted); flex-shrink: 0; }

/* Bottom nav — igual que el dashboard */
.bottom-nav {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 480px;
  display: flex; align-items: center; justify-content: space-around;
  padding: 10px 12px;
  background: var(--bg-overlay);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  z-index: 100;
}
.bnav-btn {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  background: none; border: none;
  color: var(--text-muted); font-size: 10px; font-weight: 500;
  cursor: pointer; padding: 6px 10px; border-radius: var(--radius-sm);
  transition: color 0.2s, background 0.2s;
}
.bnav-btn:hover { color: var(--text-secondary); background: var(--bg-card-hover); }
.bnav-btn--active { color: var(--accent-gold); }
.bnav-btn--center {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--accent-gold-dim);
  border: 1px solid var(--border-glow);
  color: var(--accent-gold); padding: 0;
  display: flex; align-items: center; justify-content: center;
  margin-top: -14px;
  box-shadow: 0 4px 16px rgba(232,196,160,0.25);
}
.btn-password {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}
.btn-password:hover { border-color: var(--border-glow); color: var(--text-primary); }

/* Modal cambio de contraseña */
.modal-overlay-perfil {
  position: fixed; inset: 0; z-index: 200;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 1.25rem;
}
.modal-password {
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg); width: 100%; max-width: 380px;
  box-shadow: var(--shadow-modal);
}
.modal-pw-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.1rem 1.25rem 0.75rem;
  border-bottom: 1px solid var(--border-subtle);
}
.modal-pw-header h3 { margin: 0; font-size: 1rem; font-weight: 700; }
.modal-pw-close {
  width: 30px; height: 30px; border-radius: 50%;
  background: transparent; border: 1px solid var(--border-subtle);
  color: var(--text-muted); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.modal-pw-close:hover { color: var(--text-primary); border-color: var(--border-glow); }
.modal-pw-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 0.875rem; }
.pw-field { display: flex; flex-direction: column; gap: 0.35rem; }
.pw-field label { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); }
.pw-field input {
  padding: 0.625rem 0.875rem;
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm); color: var(--text-primary);
  font-size: 0.9rem; outline: none; transition: border-color 0.2s;
}
.pw-field input:focus { border-color: var(--border-glow); }
.pw-toggle-mostrar {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.78rem; color: var(--text-muted); cursor: pointer;
}
.pw-error { font-size: 0.78rem; color: var(--accent-rose); margin: 0; }
.pw-exito { font-size: 0.78rem; color: var(--accent-emerald); margin: 0; }
.pw-actions { display: flex; gap: 0.75rem; margin-top: 0.25rem; }
.pw-btn-cancelar {
  flex: 1; padding: 0.625rem;
  background: transparent; border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm); color: var(--text-secondary);
  font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.pw-btn-cancelar:hover { border-color: var(--border-glow); color: var(--text-primary); }
.pw-btn-guardar {
  flex: 1; padding: 0.625rem;
  background: var(--accent-gold); border: none;
  border-radius: var(--radius-sm); color: #1a1410;
  font-size: 0.85rem; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.pw-btn-guardar:hover { filter: brightness(1.08); }
.pw-btn-guardar:disabled { opacity: 0.6; cursor: not-allowed; }
</style>