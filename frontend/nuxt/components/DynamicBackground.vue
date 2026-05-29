<template>
  <div
    class="fixed inset-0 -z-10 transition-opacity duration-700 ease-in-out"
    :class="[isVisible ? 'opacity-100' : 'opacity-0']"
  >
    <!-- Imagen de fondo -->
    <div
      class="absolute inset-0 bg-cover bg-center bg-no-repeat"
      :style="{ backgroundImage: `url('${fondoActual.valor}')` }"
    />
    <!-- Overlay segun tema -->
    <div class="absolute inset-0 transition-colors duration-500" :class="overlayClass" />
  </div>
</template>

<script setup lang="ts">
const { fondoActual, isVisible, overlayClass } = useBackground()
</script>
