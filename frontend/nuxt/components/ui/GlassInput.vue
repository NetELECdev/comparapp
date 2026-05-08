<template>
  <div class="glass-input-wrap" :class="{ 'glass-input-wrap--focus': focused }">
    <svg 
      v-if="icon === 'search'" 
      class="search-icon" 
      width="18" 
      height="18" 
      viewBox="0 0 24 24" 
      fill="none" 
      stroke="currentColor" 
      stroke-width="2" 
      stroke-linecap="round" 
      stroke-linejoin="round"
    >
      <circle cx="11" cy="11" r="8"/>
      <path d="m21 21-4.3-4.3"/>
    </svg>

    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      class="glass-input"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      @focus="focused = true"
      @blur="focused = false"
      @keyup.enter="$emit('submit')"
    />

    <button 
      v-if="showSubmit" 
      class="btn-search" 
      @click="$emit('submit')" 
      :aria-label="submitLabel"
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <path d="M5 12h14"/>
        <path d="m12 5 7 7-7 7"/>
      </svg>
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface Props {
  modelValue: string
  placeholder?: string
  type?: string
  icon?: 'search' | null
  showSubmit?: boolean
  submitLabel?: string
}

withDefaults(defineProps<Props>(), {
  placeholder: 'Buscar...',
  type: 'text',
  icon: 'search',
  showSubmit: true,
  submitLabel: 'Buscar'
})

defineEmits<{
  'update:modelValue': [value: string]
  'submit': []
}>()

const focused = ref(false)
</script>

<style scoped>
.glass-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.2rem 0.2rem 0.2rem 1rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 24px;
  transition: all 0.25s ease;
}

.glass-input-wrap:focus-within,
.glass-input-wrap--focus {
  border-color: rgba(232, 196, 160, 0.25);
  box-shadow: 0 0 20px rgba(232, 196, 160, 0.12), 0 0 0 4px rgba(232, 196, 160, 0.05);
  background: rgba(255, 255, 255, 0.05);
}

.search-icon {
  color: rgba(245, 240, 235, 0.35);
  flex-shrink: 0;
}

.glass-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #f5f0eb;
  font-size: 0.95rem;
  padding: 0.6rem 0;
  outline: none;
  font-family: inherit;
}

.glass-input::placeholder {
  color: rgba(245, 240, 235, 0.35);
}

.btn-search {
  width: 42px;
  height: 42px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(245, 240, 235, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.btn-search:hover {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.2), rgba(232, 196, 160, 0.1));
  border-color: rgba(232, 196, 160, 0.25);
  color: #e8c4a0;
  transform: scale(1.05);
}
</style>