import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useCompareStore = defineStore('compare', () => {
  const items = ref<any[]>([])

  function add(product: any) {
    if (!items.value.find(p => p.id_prod === product.id_prod)) {
      items.value.push(product)
    }
  }

  function remove(id: string) {
    items.value = items.value.filter(p => p.id_prod !== id)
  }

  function clear() {
    items.value = []
  }

  return { items, add, remove, clear }
})
