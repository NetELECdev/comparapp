<!-- pages/auth/callback.vue -->
<!-- Página que recibe el redirect de Google OAuth -->
<template>
  <div class="callback-page">
    <div class="callback-card">
      <div v-if="loading" class="callback-loading">
        <div class="spinner" aria-label="Procesando..." />
        <p>Procesando inicio de sesión...</p>
      </div>
      <div v-else-if="error" class="callback-error">
        <p>{{ error }}</p>
        <button @click="navigateTo('/login')">Volver al login</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { getSession } = useSupabaseAuth()
    const session = await getSession()

    if (!session?.access_token) {
      error.value = 'No se pudo obtener la sesión. Intentá de nuevo.'
      loading.value = false
      return
    }

    // Sincronizar con el backend — registrar/actualizar el usuario
    const config = useRuntimeConfig()
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

      // Guardar en localStorage igual que el login normal
      const userToSave = {
        ...userData.user,
        access_token: session.access_token
      }
      localStorage.setItem('comparapp_user', JSON.stringify(userToSave))
    } catch (backendErr) {
      // Si el backend falla, igual guardamos la sesión de Supabase
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

    await navigateTo('/dashboard')
  } catch (err: any) {
    console.error('Callback error:', err)
    error.value = 'Error al procesar el inicio de sesión.'
    loading.value = false
  }
})
</script>

<style scoped>
.callback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-deep, #0a0a0f);
}
.callback-card {
  padding: 2rem;
  text-align: center;
  color: var(--text-primary, #f5f0eb);
}
.callback-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
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
.callback-error button {
  padding: 0.75rem 1.5rem;
  border-radius: 12px;
  background: rgba(232,196,160,0.12);
  border: 1px solid rgba(232,196,160,0.25);
  color: #e8c4a0;
  cursor: pointer;
}
</style>
