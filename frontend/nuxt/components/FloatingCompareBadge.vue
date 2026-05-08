<template>
  <div v-if="count > 0" class="badge" @click="navigateTo('/compare')">
    Comparar ({{ count }})
  </div>
</template>

<script setup lang="ts">
import { useCompareStore } from '~/stores/compareStore'
import { computed } from 'vue'
const store = useCompareStore()
const count = computed(() => store.items.length)
</script>

<style scoped>
.badge {
  position: fixed;
  bottom: 80px;
  right: 16px;
  background: var(--accent-color);
  color: black;
  padding: 12px 18px;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 0 12px rgba(255, 255, 255, 0.2);
}
</style>
