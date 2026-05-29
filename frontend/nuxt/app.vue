<template>
  <div class="min-h-screen relative">
    <!-- Fondo dinámico cíclico con transición suave -->
    <DynamicBackground />

    <!-- Contenido de la app -->
    <NuxtPage />
  </div>
</template>

<script setup lang="ts">
const { inicializar } = useTema()
const { } = useBackground()

if (import.meta.client) {
  inicializar()
}
</script>

<style>
html, body, #__nuxt {
  height: 100%;
}

/* Fallback: si el fondo dinámico falla, queda un color base oscuro */
body {
  background: #0a0a0f;
}
</style>
