<template>
  <button 
    class="btn-icon"
    :class="[`btn-icon--${size}`, customClass]"
    :aria-label="ariaLabel"
    @click="$emit('click')"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  ariaLabel: string
  size?: 'sm' | 'md' | 'lg'
  customClass?: string
}

withDefaults(defineProps<Props>(), {
  size: 'md',
  customClass: ''
})

defineEmits<{
  'click': []
}>()
</script>

<style scoped>
.btn-icon {
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(245, 240, 235, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(232, 196, 160, 0.25);
  color: #f5f0eb;
  transform: scale(1.05);
}

.btn-icon--sm { width: 36px; height: 36px; }
.btn-icon--md { width: 42px; height: 42px; }
.btn-icon--lg { width: 48px; height: 48px; }
</style>