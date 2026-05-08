<template>
  <div class="perfil-container">
    <div class="perfil-card">
      <img src="/images/avatar_default.png" alt="Perfil" class="avatar" />

      <h2>{{ user.nombre || 'Usuario' }}</h2>
      <p class="email">{{ user.email }}</p>

      <div class="acciones">
        <button @click="editarPerfil" class="btn-editar">Editar Perfil</button>
        <button @click="cerrarSesion" class="btn-salir">Cerrar Sesión</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// Datos del usuario actual
const user = ref({})
const router = useRouter()

// Simula obtener el usuario logueado desde localStorage o backend
onMounted(() => {
  const storedUser = localStorage.getItem('comparapp_user')
  if (storedUser) {
    user.value = JSON.parse(storedUser)
  } else {
    // Si no hay usuario logueado, volver al login
    router.push('/')
  }
})

// Ir a editar perfil (pantalla futura)
const editarPerfil = () => {
  alert('Próximamente podrás editar tu perfil 🛠️')
}

// Cerrar sesión
const cerrarSesion = () => {
  localStorage.removeItem('comparapp_user')
  router.push('/')
}
</script>

<style scoped>
.perfil-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}

.perfil-card {
  background: white;
  padding: 40px;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  text-align: center;
  width: 90%;
  max-width: 380px;
}

.avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin-bottom: 15px;
  object-fit: cover;
  border: 3px solid #667eea;
}

h2 {
  color: #333;
  margin-bottom: 5px;
}

.email {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 20px;
}

.acciones {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

button {
  padding: 12px;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-editar {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-editar:hover {
  opacity: 0.9;
}

.btn-salir {
  background: #f56565;
  color: white;
}

.btn-salir:hover {
  background: #e53e3e;
}
</style>
