<template>
  <div 
    class="glass-card"
    :class="{ 'glass-card--accent': accent, [customClass]: customClass }"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  accent?: boolean
  customClass?: string
}

defineProps<Props>()
</script>

<style scoped>
.glass-card {
  background: var(--app-bg-card, rgba(255, 255, 255, 0.03));
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--app-border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: var(--app-radius-lg, 20px);
  box-shadow: var(--app-shadow-card, 0 4px 24px rgba(0, 0, 0, 0.2));
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.glass-card:hover {
  background: var(--app-bg-card-hover, rgba(255, 255, 255, 0.06));
  border-color: var(--app-border-glow, rgba(232, 196, 160, 0.25));
  box-shadow: var(--app-shadow-glow, 0 0 20px rgba(232, 196, 160, 0.12));
  transform: translateY(-2px);
}

.glass-card--accent {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.08), rgba(232, 196, 160, 0.03));
  border-color: rgba(232, 196, 160, 0.2);
}

.glass-card--accent:hover {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.12), rgba(232, 196, 160, 0.05));
  border-color: rgba(232, 196, 160, 0.35);
  box-shadow: 0 0 30px rgba(232, 196, 160, 0.15);
}
</style>