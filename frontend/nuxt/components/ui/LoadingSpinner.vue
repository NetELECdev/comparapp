<template>
  <div class="loading-state">
    <div class="loading-spinner" :class="`loading-spinner--${size}`" />
    <span v-if="text">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
  text?: string
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  text: 'Cargando...'
})
</script>

<style scoped>
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  padding: 4rem 1rem;
  color: rgba(245, 240, 235, 0.35);
  font-size: 0.9rem;
}

.loading-spinner {
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #e8c4a0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner--sm { width: 20px; height: 20px; border-width: 1.5px; }
.loading-spinner--md { width: 32px; height: 32px; border-width: 2px; }
.loading-spinner--lg { width: 48px; height: 48px; border-width: 3px; }

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>