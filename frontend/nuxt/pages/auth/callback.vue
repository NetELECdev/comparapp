<!-- pages/auth/callback.vue -->
<!-- Página que recibe el redirect de Google OAuth -->
<template>
  <div class="callback-page">
    <div class="callback-card">

      <div v-if="loading" class="callback-loading">
        <div class="spinner" aria-label="Procesando..." />
        <p>Procesando inicio de sesión...</p>
      </div>

      <!-- Pregunta: ¿es dueño de un comercio? -->
      <div v-else-if="preguntandoComercio" class="callback-pregunta">
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"/>
          <path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"/>
        </svg>
        <h2>¿Sos dueño de un comercio?</h2>
        <p>Si tenés un negocio y querés cargar tus propios productos en ComparApp, seleccioná tu comercio acá.</p>

        <button class="btn-secondary" @click="continuarComoUsuario">No, soy un usuario</button>
        <button class="btn-primary" @click="mostrarSelectorComercio">Sí, soy dueño de un comercio</button>
      </div>

      <!-- Selector de comercio -->
      <div v-else-if="seleccionandoComercio" class="callback-selector">
        <h2>Elegí tu comercio</h2>
        <div v-if="loadingComercios" class="select-loading">Cargando comercios...</div>
        <select v-else v-model="idComerElegido" class="comercio-select">
          <option value="">Seleccionar...</option>
          <option v-for="c in comercios" :key="c.id_comer" :value="c.id_comer">
            {{ c.nombre_comer }} — {{ c.direccion_comer }}
          </option>
        </select>
        <p v-if="!loadingComercios && comercios.length === 0" class="form-hint form-hint--warning">
          No hay comercios disponibles. Contactá al administrador para que cargue tu comercio primero.
        </p>
        <p v-if="errorMsg" class="error-text">{{ errorMsg }}</p>
        <div class="selector-actions">
          <button class="btn-secondary" @click="preguntandoComercio = true; seleccionandoComercio = false">Volver</button>
          <button class="btn-primary" :disabled="!idComerElegido || confirmando" @click="confirmarComercio">
            {{ confirmando ? 'Confirmando...' : 'Confirmar' }}
          </button>
        </div>
      </div>

      <div v-else-if="error" class="callback-error">
        <p>{{ error }}</p>
        <button @click="navigateTo('/login')">Volver al login</button>
      </div>

    </div>
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

const loading = ref(true)
const error = ref('')
const preguntandoComercio = ref(false)
const seleccionandoComercio = ref(false)
const comercios = ref<Comercio[]>([])
const loadingComercios = ref(false)
const idComerElegido = ref('')
const confirmando = ref(false)
const errorMsg = ref('')

let sessionGuardada: any = null

const config = useRuntimeConfig()

async function continuarComoUsuario() {
  await navigateTo('/dashboard')
}

async function mostrarSelectorComercio() {
  preguntandoComercio.value = false
  seleccionandoComercio.value = true
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

async function confirmarComercio() {
  if (!idComerElegido.value || !sessionGuardada) return
  confirmando.value = true
  errorMsg.value = ''
  try {
    const res = await $fetch<any>(`${config.public.apiBase}/register-comercio-google`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        access_token: sessionGuardada.access_token,
        email: sessionGuardada.user?.email,
        nombre_completo: sessionGuardada.user?.user_metadata?.full_name || sessionGuardada.user?.email,
        id_comer: idComerElegido.value
      }
    })

    const userToSave = { ...res.user, access_token: sessionGuardada.access_token }
    localStorage.setItem('comparapp_user', JSON.stringify(userToSave))

    await navigateTo('/comercio-panel')
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo vincular el comercio. Intentá de nuevo.'
  } finally {
    confirmando.value = false
  }
}

onMounted(async () => {
  try {
    const { getSession } = useSupabaseAuth()
    const session = await getSession()

    if (!session?.access_token) {
      error.value = 'No se pudo obtener la sesión. Intentá de nuevo.'
      loading.value = false
      return
    }

    sessionGuardada = session

    // Sincronizar con el backend como usuario normal — registrar/actualizar el usuario
    try {
      const userData = await $fetch<any>(`${config.public.apiBase}/auth/google/callback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: {
          access_token: session.access_token,
          email: session.user?.email,
          nombre_completo: session.user?.user_metadata?.full_name || session.user?.email
        }
      })

      const userToSave = { ...userData.user, access_token: session.access_token }
      localStorage.setItem('comparapp_user', JSON.stringify(userToSave))

      // Si ya es un comercio verificado, va directo a su panel — no preguntamos de nuevo
      if (userData.user?.es_comercio_user && userData.user?.comercio_verificado_user) {
        await navigateTo('/comercio-panel')
        return
      }
      // Si ya tiene una solicitud de comercio pendiente, tampoco preguntamos de nuevo
      if (userData.user?.es_comercio_user) {
        await navigateTo('/comercio-panel')
        return
      }
    } catch (backendErr) {
      console.warn('Backend sync failed, using Supabase session directly')
      const userToSave = {
        id: session.user?.id,
        email: session.user?.email,
        nombre_completo: session.user?.user_metadata?.full_name || session.user?.email,
        access_token: session.access_token,
        rol: 'usuario'
      }
      localStorage.setItem('comparapp_user', JSON.stringify(userToSave))
    }

    // Usuario nuevo o existente sin vínculo a comercio — preguntamos
    loading.value = false
    preguntandoComercio.value = true

  } catch (err: any) {
    console.error('Callback error:', err)
    error.value = 'Error al procesar el inicio de sesión.'
    loading.value = false
  }
})
</script>

<style scoped>
/* Esta pantalla siempre es oscura, sin importar el tema del resto de la app —
   el cambio de tema solo vive en el dashboard, nunca en las pantallas de auth */
.callback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0f;
  padding: 1.5rem;
}
.callback-card {
  padding: 2rem;
  text-align: center;
  color: #f5f0eb;
  max-width: 380px;
  width: 100%;
}
.callback-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.callback-loading p { color: #f5f0eb; }
.spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255,255,255,0.1);
  border-top-color: #e8c4a0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.callback-error { display: flex; flex-direction: column; gap: 1rem; }
.callback-error p { color: #f5f0eb; }
.callback-error button {
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  background: rgba(232,196,160,0.12);
  border: 1px solid rgba(232,196,160,0.25);
  color: #e8c4a0;
  cursor: pointer;
}

.callback-pregunta, .callback-selector {
  display: flex; flex-direction: column; align-items: center; gap: 0.875rem;
}
.callback-pregunta svg { color: #e8c4a0; }
.callback-pregunta h2, .callback-selector h2 { font-size: 1.1rem; font-weight: 700; margin: 0; color: #f5f0eb; }
.callback-pregunta p { font-size: 0.85rem; color: rgba(245,240,235,0.6); margin: 0; }

.btn-primary {
  width: 100%; padding: 0.825rem; border-radius: 12px;
  background: rgba(232,196,160,0.18); border: 1px solid rgba(232,196,160,0.35);
  color: #e8c4a0; font-size: 0.9rem; font-weight: 700; cursor: pointer; transition: all 0.2s;
}
.btn-primary:hover:not(:disabled) { background: rgba(232,196,160,0.28); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary {
  width: 100%; padding: 0.825rem; border-radius: 12px;
  background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
  color: rgba(245,240,235,0.7); font-size: 0.9rem; cursor: pointer; transition: all 0.2s;
}
.btn-secondary:hover { background: rgba(255,255,255,0.08); }

.comercio-select {
  width: 100%; padding: 0.75rem 1rem; border-radius: 10px;
  background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.08);
  color: #f5f0eb; font-size: 0.9rem;
}
.comercio-select option { background: #1a1a1f; color: #f5f0eb; }
.select-loading { font-size: 0.82rem; color: rgba(245,240,235,0.5); }
.form-hint--warning { font-size: 0.78rem; color: #fbbf24; margin: 0; }
.error-text { font-size: 0.8rem; color: #fb7185; margin: 0; }
.selector-actions { display: flex; gap: 0.625rem; width: 100%; }
</style>