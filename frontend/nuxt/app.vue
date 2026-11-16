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

// useTema() registra inicializar() en onMounted: el tema reactivo se aplica DESPUES
// de hidratar, asi Vue actualiza clases e iconos sin desfasaje.
// El color visual ya lo puso el script del <head> en nuxt.config.ts.
useTema()
const { } = useBackground()
const route = useRoute()

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

/* Color base por tema: coincide con el final del degradado de DynamicBackground (modo liso) */
html,
body {
  background: #0D0E12;
}
html[data-tema="light"],
html[data-tema="light"] body {
  background: #E8ECE4;
}

/* Espacio inferior para que el contenido no quede tapado por el nav */
.page-content,
.dash-main,
.perfil-content {
  padding-bottom: 90px;
}
</style>
