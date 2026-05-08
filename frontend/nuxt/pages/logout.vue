<template>
  <div class="logout-page">
    <h2>Cerrar sesión</h2>
    <div class="logout-content">
      <p>¿Estás seguro de que deseas cerrar sesión?</p>
      <button @click="logout" class="logout-btn">Cerrar sesión</button>
      <button @click="cancel" class="cancel-btn">Cancelar</button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const error = ref('')

async function logout() {
  error.value = ''
  try {
    // Limpiar datos de usuario del localStorage
    localStorage.removeItem('user')
    
    // Opcional: Hacer una llamada al backend para cerrar sesión
    // const config = useRuntimeConfig()
    // await fetch(`${config.public.apiBase}/logout`, {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json' },
    //   credentials: 'include'
    // })
    
    // Redirigir al login o página principal
    navigateTo('/login')
  } catch (e: any) {
    error.value = e.message
  }
}

function cancel() {
  navigateTo('/')
}
</script>

<style scoped>
.logout-page {
  max-width: 400px;
  margin: 100px auto;
  background: var(--card-bg);
  padding: 24px;
  border-radius: var(--radius);
}

.logout-content {
  text-align: center;
}

.logout-content p {
  margin-bottom: 20px;
  color: var(--text-color);
}

.logout-btn {
  width: 100%;
  padding: 12px;
  margin: 10px 0;
  border-radius: var(--radius);
  border: none;
  background: #e74c3c;
  color: white;
  cursor: pointer;
  font-weight: bold;
}

.logout-btn:hover {
  background: #c0392b;
}

.cancel-btn {
  width: 100%;
  padding: 12px;
  margin: 10px 0;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  background: transparent;
  color: var(--text-color);
  cursor: pointer;
}

.cancel-btn:hover {
  background: var(--bg-color);
}

.error {
  color: tomato;
  margin-top: 12px;
  text-align: center;
}
</style>