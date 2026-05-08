<!-- components/dashboard/AppSearch.vue -->
<template>
  <div class="search-sticky">
    <div class="search-box">
      <span class="search-icon">🔍</span>
      <input
        :value="modelValue"
        type="text"
        placeholder="¿Qué querés comparar hoy?"
        class="search-input"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        @keyup.enter="$emit('search', modelValue)"
      />
      <button class="scan-btn" @click="$emit('scan')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 7V5a2 2 0 0 1 2-2h2"/>
          <path d="M17 3h2a2 2 0 0 1 2 2v2"/>
          <path d="M21 17v2a2 2 0 0 1-2 2h-2"/>
          <path d="M7 21H5a2 2 0 0 1-2-2v-2"/>
          <line x1="7" y1="12" x2="17" y2="12"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps({
  modelValue: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue', 'search', 'scan'])
</script>

<style scoped>
.search-sticky {
  position: sticky;
  top: 57px;
  z-index: 99;
  padding: 0.75rem 1rem;
  background: rgba(10, 10, 15, 0.9);
  backdrop-filter: blur(10px);
}

.search-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 0.75rem 1rem;
}

.search-icon {
  font-size: 1.1rem;
  opacity: 0.6;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 1rem;
  outline: none;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.4);
}

.scan-btn {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.scan-btn:active {
  transform: scale(0.95);
}
</style>