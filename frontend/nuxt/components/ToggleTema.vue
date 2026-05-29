<!--
  components/ToggleTema.vue
  Botón toggle para cambiar entre modo oscuro y claro.
  Uso: <ToggleTema />
-->
<template>
  <button
    class="toggle-tema"
    :class="{ 'is-light': !esDark }"
    @click="toggleTema"
    :aria-label="esDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'"
    :title="esDark ? 'Modo claro' : 'Modo oscuro'"
  >
    <!-- Luna (dark mode activo) -->
    <Transition name="icon-swap" mode="out-in">
      <svg v-if="esDark" key="moon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>
      </svg>
      <!-- Sol (light mode activo) -->
      <svg v-else key="sun" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="4"/>
        <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
      </svg>
    </Transition>
  </button>
</template>

<script setup lang="ts">
const { esDark, toggleTema } = useTema()
</script>

<style scoped>
.toggle-tema {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--toggle-bg);
  border: 1px solid var(--border-subtle);
  color: var(--toggle-icon);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.toggle-tema:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  color: var(--accent-gold);
  transform: scale(1.05);
}

.toggle-tema.is-light {
  color: var(--accent-amber);
  background: var(--accent-gold-dim);
  border-color: var(--border-glow);
}

/* Animación del ícono al cambiar */
.icon-swap-enter-active,
.icon-swap-leave-active {
  transition: all 0.2s ease;
}
.icon-swap-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}
.icon-swap-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}
</style>