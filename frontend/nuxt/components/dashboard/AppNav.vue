<!-- components/dashboard/TabNav.vue -->
<template>
  <nav class="tab-nav">
    <button
      v-for="item in navItems"
      :key="item.id"
      class="tab-item"
      :class="{ active: active === item.id, center: item.center }"
      @click="$emit('changeTab', item.id)"
    >
      <div v-if="item.center" class="tab-center-btn">
        <span class="tab-icon">{{ item.icon }}</span>
      </div>
      <template v-else>
        <span class="tab-icon">{{ item.icon }}</span>
        <span class="tab-label">{{ item.label }}</span>
      </template>
    </button>
  </nav>
</template>

<script setup lang="ts">
defineProps({
  active: {
    type: String,
    default: 'explore'
  }
})

defineEmits(['changeTab'])

const navItems = [
  { id: 'explore', label: 'Explorar', icon: '🏠' },
  { id: 'tracking', label: 'Seguimiento', icon: '🔔' },
  { id: 'compare', label: 'Comparar', icon: '⚖️', center: true },
  { id: 'history', label: 'Historial', icon: '📋' },
  { id: 'venues', label: 'Proveedores', icon: '📍' }
]
</script>

<style scoped>
.tab-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 0.5rem 0 1rem;
  background: rgba(10, 10, 15, 0.95);
  backdrop-filter: blur(20px);
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  z-index: 1000;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  font-size: 0.7rem;
  cursor: pointer;
  transition: color 0.2s;
  padding: 0.25rem 0.5rem;
}

.tab-item.active {
  color: #a78bfa;
}

.tab-icon {
  font-size: 1.3rem;
  line-height: 1;
}

.tab-label {
  font-size: 0.65rem;
}

.tab-item.center {
  position: relative;
  top: -20px;
}

.tab-center-btn {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.4);
  transition: transform 0.2s;
}

.tab-center-btn .tab-icon {
  font-size: 1.5rem;
}

.tab-item.center:active .tab-center-btn {
  transform: scale(0.95);
}
</style>