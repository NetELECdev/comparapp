<template>
  <div class="min-h-screen relative">
    <!-- Fondo dinámico cíclico con transición suave -->
    <DynamicBackground />

    <!-- Contenido de la app -->
    <NuxtPage />

    <!-- Bottom nav global — oculto en páginas de auth -->
    <ClientOnly>
      <AppBottomNav v-if="mostrarNav" />
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from '#app'

const { inicializar } = useTema()
const { } = useBackground()
const route = useRoute()

if (import.meta.client) {
  inicializar()
}

// Rutas donde NO mostrar el bottom nav
const rutasSinNav = ['/login', '/register', '/intro', '/logout', '/auth/callback', '/forgot-password']

const mostrarNav = computed(() => {
  return !rutasSinNav.some(r => route.path === r || route.path.startsWith(r))
})
</script>

<style>
html, body, #__nuxt {
  height: 100%;
}

body {
  background: #0a0a0f;
}

/* Espacio inferior para que el contenido no quede tapado por el nav */
.page-content,
.dash-main,
.perfil-content {
  padding-bottom: 90px;
}
</style>
