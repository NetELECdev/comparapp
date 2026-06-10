<!-- components/ProductRow.vue -->
<template>
  <div class="product-row">
    <div class="product-img" @click="$emit('compare', { ...product, cantidad: cantidad })">
      <img :src="product.imagen_prod || '/images/avatar_default.png'" class="thumb" />
    </div>
    <div class="product-info" @click="$emit('compare', { ...product, cantidad: cantidad })">
      <h4 class="product-name">{{ product.nombre_prod }}</h4>
      <p class="product-brand">{{ product.marca_prod }}</p>
      <p class="product-venue">{{ product.comercio_prod }}</p>
    </div>
    <div class="product-actions">
      <div class="quantity-selector">
        <button
          class="qty-btn qty-minus"
          :disabled="cantidad <= 1"
          @click="cantidad--"
          aria-label="Restar"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
          </svg>
        </button>
        <span class="qty-value">{{ cantidad }}</span>
        <button
          class="qty-btn qty-plus"
          @click="cantidad++"
          aria-label="Sumar"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="M12 5v14"/>
          </svg>
        </button>
      </div>
      <div class="price-action">
        <span class="price">${{ formatPrice(product.precio_prod) }}</span>
        <button
          class="compare-btn"
          :class="{ compared: wasAdded }"
          @click="handleCompare"
          :disabled="comparing"
        >
          <span v-if="comparing" class="btn-loading">
            <span class="loading-spinner loading-spinner--sm" />
          </span>
          <span v-else-if="wasAdded" class="compared-text">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 6 9 17l-5-5"/>
            </svg>
            Agregado
          </span>
          <span v-else class="compare-text">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 6h18"/>
              <path d="M7 12h10"/>
              <path d="M10 18h4"/>
            </svg>
            Comparar
          </span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['compare'])

const cantidad = ref(1)
const comparing = ref(false)
const wasAdded = ref(false)

const formatPrice = (price) => {
  return Number(price)?.toLocaleString('es-AR') || '0'
}

const handleCompare = () => {
  comparing.value = true

  emit('compare', {
    ...props.product,
    cantidad: cantidad.value
  })

  wasAdded.value = true
  comparing.value = false

  setTimeout(() => {
    wasAdded.value = false
    cantidad.value = 1
  }, 2000)
}
</script>

<style scoped>
.product-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem;
  background: rgba(255, 255, 255, 0.03);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 16px;
  transition: all 0.25s ease;
}

.product-row:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(232, 196, 160, 0.15);
  box-shadow: 0 0 20px rgba(232, 196, 160, 0.06);
}

.product-img {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
  cursor: pointer;
}

.product-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-info {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}

.product-name {
  color: #f5f0eb;
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0 0 0.15rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-brand {
  color: rgba(245, 240, 235, 0.5);
  font-size: 0.78rem;
  margin: 0 0 0.1rem;
}

.product-venue {
  color: rgba(245, 240, 235, 0.35);
  font-size: 0.72rem;
  margin: 0;
}

.product-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.5rem;
  flex-shrink: 0;
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  overflow: hidden;
}

.qty-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(245, 240, 235, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.qty-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: #f5f0eb;
}

.qty-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.qty-minus { border-right: 1px solid rgba(255, 255, 255, 0.06); }
.qty-plus { border-left: 1px solid rgba(255, 255, 255, 0.06); }

.qty-value {
  min-width: 28px;
  text-align: center;
  color: #f5f0eb;
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0 0.25rem;
}

.price-action {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.375rem;
}

.price {
  color: #4ade80;
  font-size: 0.95rem;
  font-weight: 700;
}

.compare-btn {
  padding: 0.4rem 0.875rem;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(167, 139, 250, 0.1));
  border: 1px solid rgba(167, 139, 250, 0.3);
  color: #c4b5fd;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 100px;
  justify-content: center;
}

.compare-btn:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(167, 139, 250, 0.2));
  border-color: rgba(167, 139, 250, 0.5);
  color: #ddd6fe;
  transform: translateY(-1px);
}

.compare-btn.compared {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.15), rgba(52, 211, 153, 0.1));
  border-color: rgba(52, 211, 153, 0.3);
  color: #6ee7b7;
}

.compare-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.compare-text, .compared-text {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-spinner {
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: #e8c4a0;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.loading-spinner--sm {
  width: 14px;
  height: 14px;
  border-width: 1.5px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@media (max-width: 380px) {
  .product-row { gap: 0.625rem; padding: 0.75rem; }
  .product-img { width: 44px; height: 44px; }
  .product-name { font-size: 0.85rem; }
}
</style>
