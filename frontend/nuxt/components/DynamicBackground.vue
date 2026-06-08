<template>
  <div class="dynamic-bg" :class="{ visible: isVisible }">
    <div class="dynamic-bg-img" :style="{ backgroundImage: `url('${fondoActual.valor}')` }" />
    <div class="dynamic-bg-overlay" :style="overlayStyle" />
  </div>
</template>

<script setup lang="ts">
const { fondoActual, isVisible, overlayClass } = useBackground()

// Convertir la clase Tailwind a un estilo CSS real
const overlayStyle = computed(() => {
  if (overlayClass.value.includes('black/40')) return { background: 'rgba(0,0,0,0.40)' }
  if (overlayClass.value.includes('black/60')) return { background: 'rgba(0,0,0,0.60)' }
  if (overlayClass.value.includes('black/70')) return { background: 'rgba(0,0,0,0.70)' }
  if (overlayClass.value.includes('black/80')) return { background: 'rgba(0,0,0,0.80)' }
  if (overlayClass.value.includes('white/25')) return { background: 'rgba(255,255,255,0.25)' }
  if (overlayClass.value.includes('white/60')) return { background: 'rgba(255,255,255,0.60)' }
  return { background: 'rgba(0,0,0,0.40)' }
})
</script>

<style scoped>
.dynamic-bg {
  position: fixed;
  inset: 0;
  z-index: -10;
  opacity: 0;
  transition: opacity 0.7s ease-in-out;
  pointer-events: none;
}
.dynamic-bg.visible { opacity: 1; }
.dynamic-bg-img {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.dynamic-bg-overlay {
  position: absolute;
  inset: 0;
  transition: background 0.5s;
}
</style>
