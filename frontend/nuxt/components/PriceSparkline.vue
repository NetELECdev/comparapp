<template>
  <div class="price-sparkline" :class="{ 'has-data': hasData }">
    <!-- Variación porcentual -->
    <div v-if="variacion !== null" class="sparkline-badge" :class="badgeClass">
      <svg v-if="variacion > 0" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
        <path d="M12 19V5M5 12l7-7 7 7"/>
      </svg>
      <svg v-else-if="variacion < 0" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
        <path d="M12 5v14M5 12l7 7 7-7"/>
      </svg>
      <svg v-else width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
        <path d="M5 12h14"/>
      </svg>
      {{ Math.abs(variacion) }}%
    </div>

    <!-- Gráfico SVG mini -->
    <svg
      v-if="hasData"
      class="sparkline-svg"
      :viewBox="`0 0 ${W} ${H}`"
      preserveAspectRatio="none"
    >
      <!-- Área bajo la curva -->
      <defs>
        <linearGradient :id="gradientId" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="lineColor" stop-opacity="0.2"/>
          <stop offset="100%" :stop-color="lineColor" stop-opacity="0"/>
        </linearGradient>
      </defs>

      <path
        :d="areaPath"
        :fill="`url(#${gradientId})`"
      />

      <path
        :d="linePath"
        fill="none"
        :stroke="lineColor"
        stroke-width="1.5"
        stroke-linecap="round"
        stroke-linejoin="round"
      />

      <!-- Punto final -->
      <circle
        :cx="lastPoint.x"
        :cy="lastPoint.y"
        r="2"
        :fill="lineColor"
      />
    </svg>

    <!-- Sin datos -->
    <span v-else class="sparkline-empty">—</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  history?: Array<{ precio: number; fecha_registro: string }>
  variacion?: number | null
}

const props = withDefaults(defineProps<Props>(), {
  history: () => [],
  variacion: null
})

const W = 80
const H = 28
const PAD = 3

const hasData = computed(() => props.history && props.history.length >= 2)

const gradientId = computed(() => `spark-grad-${Math.random().toString(36).slice(2, 8)}`)

const lineColor = computed(() => {
  if (props.variacion === null || props.variacion === undefined) return '#e8c4a0'
  return props.variacion > 0 ? '#fb7185' : props.variacion < 0 ? '#34d399' : '#94a3b8'
})

const badgeClass = computed(() => {
  if (props.variacion === null || props.variacion === undefined) return ''
  if (props.variacion > 0) return 'sube'
  if (props.variacion < 0) return 'baja'
  return 'igual'
})

const points = computed(() => {
  if (!hasData.value) return []
  const precios = props.history.map(p => p.precio)
  const min = Math.min(...precios)
  const max = Math.max(...precios)
  const range = max - min || 1

  return props.history.map((p, i) => ({
    x: PAD + (i / (precios.length - 1)) * (W - PAD * 2),
    y: H - PAD - ((p.precio - min) / range) * (H - PAD * 2)
  }))
})

const linePath = computed(() => {
  const pts = points.value
  if (pts.length < 2) return ''
  return pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
})

const areaPath = computed(() => {
  const pts = points.value
  if (pts.length < 2) return ''
  const line = pts.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(' ')
  const last = pts[pts.length - 1]
  const first = pts[0]
  return `${line} L ${last.x.toFixed(1)} ${H} L ${first.x.toFixed(1)} ${H} Z`
})

const lastPoint = computed(() => {
  const pts = points.value
  return pts.length > 0 ? pts[pts.length - 1] : { x: W - PAD, y: H / 2 }
})
</script>

<style scoped>
.price-sparkline {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  min-width: 0;
}

.sparkline-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.15rem;
  padding: 0.15rem 0.4rem;
  border-radius: 999px;
  font-size: 0.65rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}

.sparkline-badge.sube {
  background: rgba(251, 113, 133, 0.12);
  border: 1px solid rgba(251, 113, 133, 0.25);
  color: #fb7185;
}

.sparkline-badge.baja {
  background: rgba(52, 211, 153, 0.12);
  border: 1px solid rgba(52, 211, 153, 0.25);
  color: #34d399;
}

.sparkline-badge.igual {
  background: rgba(148, 163, 184, 0.12);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: #94a3b8;
}

.sparkline-svg {
  width: 48px;
  height: 18px;
  flex-shrink: 0;
}

.sparkline-empty {
  font-size: 0.7rem;
  color: var(--text-muted, rgba(245, 240, 235, 0.35));
}
</style>
