<!-- components/AppBottomNav.vue -->
<template>
  <nav class="bottom-nav" aria-label="Navegación principal">

    <!-- Inicio -->
    <button
      class="bnav-btn"
      :class="{ 'bnav-btn--active': isActive('/dashboard') }"
      @click="navigateTo('/dashboard')"
      aria-label="Inicio"
      :aria-current="isActive('/dashboard') ? 'page' : undefined"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
        <polyline points="9 22 9 12 15 12 15 22"/>
      </svg>
      <span>Inicio</span>
    </button>

    <!-- Productos -->
    <button
      class="bnav-btn"
      :class="{ 'bnav-btn--active': isActive('/productos') }"
      @click="navigateTo('/productos')"
      aria-label="Productos"
      :aria-current="isActive('/productos') ? 'page' : undefined"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="m7.5 4.27 9 5.15"/>
        <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
        <path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
      </svg>
      <span>Productos</span>
    </button>

    <!-- Comparar (centro destacado) -->
    <button
      class="bnav-btn bnav-btn--center"
      :class="{ 'bnav-btn--center--active': isActive('/comparaciones') }"
      @click="navigateTo('/comparaciones')"
      aria-label="Comparar"
      :aria-current="isActive('/comparaciones') ? 'page' : undefined"
    >
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
        <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
        <path d="M7 21h10"/><path d="M12 3v18"/>
        <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
      </svg>
    </button>

    <!-- Listas -->
    <button
      class="bnav-btn"
      :class="{ 'bnav-btn--active': isActive('/listas') }"
      @click="navigateTo('/listas')"
      aria-label="Listas"
      :aria-current="isActive('/listas') ? 'page' : undefined"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M9 5H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V7a2 2 0 0 0-2-2h-2"/>
        <rect x="9" y="3" width="6" height="4" rx="2"/>
        <path d="M9 12h6"/><path d="M9 16h4"/>
      </svg>
      <span>Listas</span>
    </button>

    <!-- Ofertas -->
    <button
      class="bnav-btn"
      :class="{ 'bnav-btn--active': isActive('/ofertas') }"
      @click="navigateTo('/ofertas')"
      aria-label="Ofertas"
      :aria-current="isActive('/ofertas') ? 'page' : undefined"
    >
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
      </svg>
      <span>Ofertas</span>
    </button>

  </nav>
</template>

<script setup lang="ts">
import { navigateTo, useRoute } from '#app'

const route = useRoute()

const isActive = (path: string) => {
  return route.path === path || route.path.startsWith(path + '/')
}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 480px;
  display: flex;
  align-items: center;
  justify-content: space-around;
  padding: 10px 12px;
  background: var(--bg-overlay);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  z-index: 100;
}

.bnav-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 3px;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 500;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: color 0.2s, background 0.2s;
}
.bnav-btn:hover { color: var(--text-secondary); background: var(--bg-card-hover); }
.bnav-btn--active { color: var(--accent-gold); }

.bnav-btn--center {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--accent-gold-dim);
  border: 1px solid var(--border-glow);
  color: var(--accent-gold);
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: -14px;
  box-shadow: 0 4px 16px rgba(232, 196, 160, 0.25);
}
.bnav-btn--center:hover { background: rgba(232, 196, 160, 0.2); }
.bnav-btn--center--active {
  background: rgba(232, 196, 160, 0.3);
  border-color: var(--accent-gold);
}

@media (min-width: 480px) {
  .bottom-nav { max-width: 520px; }
}
</style>
