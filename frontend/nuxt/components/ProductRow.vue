<template>
  <div 
    class="product-row" 
    :class="{ 
      'mejor-precio': comparacion?.esMasBarato && comparacion?.totalCompetidores > 1, 
      'peor-precio': comparacion?.esMasCaro && !comparacion?.esMasBarato && comparacion?.totalCompetidores > 1 
    }" 
    @click="$emit('click')"
  >
    <div class="row-img">
      <img :src="product.imagen_prod || '/images/avatar_default.png'" :alt="product.nombre_prod" @error="onImageError" />
    </div>

    <div class="row-info">
      <div class="row-top">
        <span class="row-categoria">{{ product.cate_prod }}</span>

        <!-- BADGE: Mejor precio (solo si hay competencia y es el mas barato) -->
        <span 
          v-if="comparacion?.esMasBarato && comparacion?.totalCompetidores > 1" 
          class="badge badge-mejor"
        >
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12l7 7 7-7"/></svg>
          Mejor precio
        </span>

        <!-- BADGE: % mas caro (si NO es el mas barato y hay competencia) -->
        <span 
          v-else-if="comparacion && !comparacion.esMasBarato && comparacion.totalCompetidores > 1 && comparacion.pctVsMin > 0" 
          class="badge badge-carro"
        >
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
          +{{ comparacion.pctVsMin }}%
        </span>

        <!-- BADGE: Unico proveedor (solo 1 competidor = el mismo) -->
        <span 
          v-else-if="comparacion?.totalCompetidores === 1 || (!comparacion && product.total_competidores === 1)" 
          class="badge badge-unico"
        >
          Unico
        </span>
      </div>

      <h3 class="row-nombre">{{ product.nombre_prod }}</h3>
      <p class="row-marca">{{ product.marca_prod }} · {{ product.provee_prod }}</p>

      <div class="row-bottom">
        <span class="row-precio">${{ formatPrice(product.precio_prod) }}</span>
        <span v-if="product.cantidad_prod" class="row-unidad">{{ product.cantidad_prod }} {{ product.unidad_prod }}</span>

        <!-- ✅ FECHA -->
        <span v-if="product.fecha_prod" class="row-fecha">
          {{ formatDate(product.fecha_prod) }}
        </span>

        <!-- Indicador de competencia -->
        <span v-if="comparacion?.totalCompetidores > 1" class="competencia-indicador">
          {{ comparacion.totalCompetidores }} proveedores
        </span>
        <span v-else-if="product.total_competidores > 1" class="competencia-indicador">
          {{ product.total_competidores }} proveedores
        </span>
      </div>
    </div>

    <div class="row-actions">
      <button class="compare-btn" @click.stop="$emit('compare', { ...product, cantidad: 1 })" title="Comparar">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M3 6h18"/><path d="M7 12h10"/><path d="M10 18h4"/>
        </svg>
      </button>
      <svg class="row-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="m9 18 6-6-6-6"/>
      </svg>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ComparacionData {
  esMasBarato: boolean
  esMasCaro: boolean
  pctVsMin: number
  totalCompetidores: number
}

defineProps<{
  product: any
  comparacion?: ComparacionData
}>()

defineEmits(['compare', 'click'])

function formatPrice(price: string | number): string {
  if (price === null || price === undefined) return '0'
  return Number(price)?.toLocaleString('es-AR') || '0'
}

function formatDate(fecha: string | undefined): string {
  if (!fecha) return ''
  const d = new Date(fecha)
  const hoy = new Date()
  const diffMs = hoy.getTime() - d.getTime()
  const diffDias = Math.floor(diffMs / (1000 * 60 * 60 * 24))
  
  if (diffDias === 0) return 'Hoy'
  if (diffDias === 1) return 'Ayer'
  if (diffDias < 7) return `Hace ${diffDias} días`
  if (diffDias < 30) return `Hace ${Math.floor(diffDias / 7)} semanas`
  
  return d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function onImageError(e: Event) {
  (e.target as HTMLImageElement).src = '/images/avatar_default.png'
}
</script>

<style scoped>
.product-row {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  padding: 0.875rem 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  transition: all 0.25s ease;
  cursor: pointer;
}

.product-row:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  transform: translateY(-1px);
}

.product-row.mejor-precio {
  border-color: rgba(52, 211, 153, 0.3);
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.05), var(--bg-card));
}

.product-row.peor-precio {
  border-color: rgba(251, 113, 133, 0.2);
}

.row-img {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.row-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.row-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.row-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.row-categoria {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.row-fecha {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin-left: auto;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.68rem;
  font-weight: 700;
}

.badge-mejor {
  background: rgba(52, 211, 153, 0.15);
  border: 1px solid rgba(52, 211, 153, 0.3);
  color: #34d399;
}

.badge-carro {
  background: rgba(251, 113, 133, 0.12);
  border: 1px solid rgba(251, 113, 133, 0.25);
  color: #fb7185;
}

.badge-unico {
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: #94a3b8;
  font-size: 0.65rem;
}

.row-nombre {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-marca {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-bottom {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.25rem;
  flex-wrap: wrap;
}

.row-precio {
  font-size: 1rem;
  font-weight: 700;
  color: var(--accent-gold);
}

.row-unidad {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.competencia-indicador {
  font-size: 0.7rem;
  color: var(--text-muted);
  background: rgba(255, 255, 255, 0.05);
  padding: 0.1rem 0.4rem;
  border-radius: 999px;
}

.row-actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
}

.compare-btn {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(167, 139, 250, 0.1);
  border: 1px solid rgba(167, 139, 250, 0.2);
  color: #a78bfa;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.compare-btn:hover {
  background: rgba(167, 139, 250, 0.2);
  transform: scale(1.05);
}

.row-arrow {
  color: var(--text-muted);
  opacity: 0.4;
  transition: all 0.2s;
}

.product-row:hover .row-arrow {
  opacity: 1;
  color: var(--accent-gold);
  transform: translateX(2px);
}
</style>
