<<template>
  <button
    class="fav-btn"
    :class="{ active: isFav }"
    @click.stop="handleClick"
    :aria-label="isFav ? 'Quitar de favoritos' : 'Agregar a favoritos'"
  >
    <svg
      width="18"
      height="18"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    >
      <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z" />
    </svg>
  </button>
</template>

<script setup>
const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const { esFavorito, toggleFavorito } = useFavoritos()

const isFav = computed(() => {
  const hasId = !!props.product?.id_prod
  if (!hasId) {
    console.warn('⚠️ Producto sin id_prod:', props.product?.nombre_prod, props.product)
  }
  return hasId && esFavorito(props.product.id_prod)
})

const handleClick = () => {
  console.log('🖱️ Click favorito:', {
    id: props.product?.id_prod,
    nombre: props.product?.nombre_prod,
    productoCompleto: props.product
  })
  toggleFavorito(props.product)
}
</script>

<style scoped>
.fav-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: rgba(245, 240, 235, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.fav-btn:hover {
  background: rgba(251, 113, 133, 0.1);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
  transform: scale(1.1);
}

.fav-btn.active {
  background: rgba(251, 113, 133, 0.15);
  border-color: rgba(251, 113, 133, 0.4);
  color: #fb7185;
}

.fav-btn.active svg {
  fill: rgba(251, 113, 133, 0.25);
}

.fav-btn svg {
  transition: all 0.2s ease;
}

.fav-btn:active {
  transform: scale(0.9);
}
</style>