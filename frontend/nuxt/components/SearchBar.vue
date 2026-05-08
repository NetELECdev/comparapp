<template>
  <div class="search-bar">
    <input
      v-model="query"
      @input="onInput"
      type="text"
      placeholder="🔍 Buscar producto o marca..."
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
const emit = defineEmits(['search'])
const query = ref('')
let timer: any = null

function onInput() {
  clearTimeout(timer)
  timer = setTimeout(() => emit('search', query.value.trim()), 400)
}
</script>

<style scoped>
.search-bar {
  position: sticky;
  top: 0;
  background: var(--bg-color);
  padding: 10px;
}
input {
  width: 100%;
  padding: 12px;
  font-size: 16px;
  border-radius: var(--radius);
  border: none;
  background: var(--card-bg);
  color: var(--text-color);
}
</style>
