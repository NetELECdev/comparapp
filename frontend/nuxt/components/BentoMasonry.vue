<!-- components/dashboard/BentoMasonry.vue -->
<template>
  <div class="masonry" ref="masonryEl">
    <slot />
  </div>
</template>

<script setup lang="ts">
const masonryEl = ref<HTMLElement | null>(null)
</script>

<style scoped>
.masonry {
  columns: 1;
  column-gap: 12px;
}

/* Tablet */
@media (min-width: 640px) {
  .masonry {
    columns: 2;
    column-gap: 14px;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .masonry {
    columns: 3;
    column-gap: 16px;
  }
}

/* Wide */
@media (min-width: 1440px) {
  .masonry {
    columns: 4;
    column-gap: 20px;
  }
}

/* Cada hijo no se parte entre columnas y tiene margen inferior */
.masonry :deep(.pin) {
  break-inside: avoid;
  margin-bottom: 12px;
  display: block;
}

@media (min-width: 640px) {
  .masonry :deep(.pin) { margin-bottom: 14px; }
}

@media (min-width: 1024px) {
  .masonry :deep(.pin) { margin-bottom: 16px; }
}
</style>