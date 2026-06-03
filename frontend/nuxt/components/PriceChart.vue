<template>
  <div class="price-chart-wrapper">
    <svg
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="xMidYMid meet"
      class="price-chart"
    >
      <defs>
        <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="trendColor" stop-opacity="0.18"/>
          <stop offset="100%" :stop-color="trendColor" stop-opacity="0"/>
        </linearGradient>
        <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="2.5" result="blur"/>
          <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
          </feMerge>
        </filter>
      </defs>

      <!-- Grid horizontal con etiquetas de precio a la izquierda -->
      <g class="grid">
        <g v-for="(item, i) in gridLinesWithLabels" :key="'h-'+i">
          <line
            :x1="paddingLeft"
            :y1="item.y"
            :x2="width - paddingRight"
            :y2="item.y"
            stroke="rgba(255,255,255,0.06)"
            stroke-dasharray="3,4"
          />
          <text
            :x="paddingLeft - 2"
            :y="item.y + 3"
            text-anchor="end"
            font-size="7"
            fill="rgba(245,240,235,0.25)"
          >{{ item.label }}</text>
        </g>
      </g>

      <!-- Área bajo la curva -->
      <path :d="areaPath" fill="url(#areaGradient)" class="area-path" />

      <!-- Línea de tendencia -->
      <path
        :d="linePath"
        fill="none"
        :stroke="trendColor"
        stroke-width="2"
        stroke-linecap="round"
        stroke-linejoin="round"
        class="trend-line"
      />

      <!-- Línea vertical del precio actual (desde el punto hasta el eje X) -->
      <g v-if="lastPoint">
        <line
          :x1="lastPoint.x"
          :y1="lastPoint.y"
          :x2="lastPoint.x"
          :y2="height - paddingBottom"
          stroke="#e8c4a0"
          stroke-width="1"
          stroke-dasharray="3,3"
          opacity="0.4"
        />
      </g>

      <!-- Puntos destacados -->
      <g class="highlight-points">

        <!-- Mínimo -->
        <g v-if="minPoint && minPoint.index !== lastPoint?.index">
          <circle :cx="minPoint.x" :cy="minPoint.y" r="4" fill="#34d399" filter="url(#glow)" />
          <circle :cx="minPoint.x" :cy="minPoint.y" r="9" fill="none" stroke="#34d399" stroke-width="1" opacity="0.3">
            <animate attributeName="r" values="9;13;9" dur="2.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.3;0.05;0.3" dur="2.5s" repeatCount="indefinite"/>
          </circle>
          <!-- Label MÍN con fondo -->
          <rect
            :x="clampX(minPoint.x - 18, 0, width - 36)"
            :y="minPoint.y - 26"
            width="36" height="13"
            rx="3"
            fill="rgba(52,211,153,0.15)"
            stroke="rgba(52,211,153,0.3)"
            stroke-width="0.5"
          />
          <text
            :x="clampX(minPoint.x, 18, width - 18)"
            :y="minPoint.y - 17"
            text-anchor="middle"
            font-size="8"
            font-weight="700"
            fill="#34d399"
          >MÍN {{ formatPrice(minPoint.price) }}</text>
        </g>

        <!-- Máximo -->
        <g v-if="maxPoint && maxPoint.index !== lastPoint?.index">
          <circle :cx="maxPoint.x" :cy="maxPoint.y" r="4" fill="#fb7185" filter="url(#glow)" />
          <circle :cx="maxPoint.x" :cy="maxPoint.y" r="9" fill="none" stroke="#fb7185" stroke-width="1" opacity="0.3">
            <animate attributeName="r" values="9;13;9" dur="2.5s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.3;0.05;0.3" dur="2.5s" repeatCount="indefinite"/>
          </circle>
          <!-- Label MÁX con fondo -->
          <rect
            :x="clampX(maxPoint.x - 18, 0, width - 36)"
            :y="maxPoint.y - 26"
            width="36" height="13"
            rx="3"
            fill="rgba(251,113,133,0.15)"
            stroke="rgba(251,113,133,0.3)"
            stroke-width="0.5"
          />
          <text
            :x="clampX(maxPoint.x, 18, width - 18)"
            :y="maxPoint.y - 17"
            text-anchor="middle"
            font-size="8"
            font-weight="700"
            fill="#fb7185"
          >MÁX {{ formatPrice(maxPoint.price) }}</text>
        </g>

        <!-- ACTUAL — siempre al final de la curva, prominente -->
        <g v-if="lastPoint">
          <!-- Pulso exterior -->
          <circle :cx="lastPoint.x" :cy="lastPoint.y" r="10" fill="none" stroke="#e8c4a0" stroke-width="1.5" opacity="0.2">
            <animate attributeName="r" values="10;16;10" dur="2s" repeatCount="indefinite"/>
            <animate attributeName="opacity" values="0.2;0;0.2" dur="2s" repeatCount="indefinite"/>
          </circle>
          <!-- Círculo blanco interior -->
          <circle :cx="lastPoint.x" :cy="lastPoint.y" r="6" fill="#e8c4a0" filter="url(#glow)" />
          <circle :cx="lastPoint.x" :cy="lastPoint.y" r="3" fill="#0a0a0f" />
          <!-- Etiqueta ACTUAL con fondo sólido — posicionada inteligentemente -->
          <rect
            :x="clampX(lastPoint.x - 24, paddingLeft, width - 48)"
            :y="labelActualY"
            width="48" height="18"
            rx="4"
            fill="#e8c4a0"
          />
          <text
            :x="clampX(lastPoint.x, paddingLeft + 24, width - 24)"
            :y="labelActualY + 7"
            text-anchor="middle"
            font-size="7"
            font-weight="700"
            fill="#0a0a0f"
          >ACTUAL</text>
          <text
            :x="clampX(lastPoint.x, paddingLeft + 24, width - 24)"
            :y="labelActualY + 15"
            text-anchor="middle"
            font-size="8"
            font-weight="700"
            fill="#0a0a0f"
          >{{ formatPrice(lastPoint.price) }}</text>
        </g>

      </g>

      <!-- Eje X con fechas — más etiquetas distribuidas -->
      <g class="x-axis">
        <text
          v-for="(label, i) in xLabels"
          :key="'x-'+i"
          :x="label.x"
          :y="height - 3"
          text-anchor="middle"
          font-size="7.5"
          fill="rgba(245,240,235,0.35)"
        >{{ label.text }}</text>
      </g>

      <!-- Línea base eje X -->
      <line
        :x1="paddingLeft"
        :y1="height - paddingBottom"
        :x2="width - paddingRight"
        :y2="height - paddingBottom"
        stroke="rgba(255,255,255,0.08)"
        stroke-width="1"
      />
    </svg>

    <!-- Leyenda -->
    <div class="chart-legend">
      <div class="legend-item">
        <span class="dot dot-min"></span><span>Mínimo</span>
      </div>
      <div class="legend-item">
        <span class="dot dot-current"></span><span>Actual</span>
      </div>
      <div class="legend-item">
        <span class="dot dot-max"></span><span>Máximo</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface DataPoint {
  fecha: string
  precio: number
}

const props = defineProps<{
  data: DataPoint[]
  width?: number
  height?: number
}>()

const width = computed(() => props.width || 360)
const height = computed(() => props.height || 160)

// Padding generoso: izquierda para labels de precio, arriba para labels de puntos
const paddingLeft   = 28
const paddingRight  = 10
const paddingTop    = 36
const paddingBottom = 22

const chartWidth  = computed(() => width.value  - paddingLeft - paddingRight)
const chartHeight = computed(() => height.value - paddingTop  - paddingBottom)

const prices    = computed(() => props.data.map(d => d.precio))
const minPrice  = computed(() => Math.min(...prices.value))
const maxPrice  = computed(() => Math.max(...prices.value))
const priceRange = computed(() => maxPrice.value - minPrice.value || 1)

const trendColor = computed(() => {
  if (props.data.length < 2) return '#94a3b8'
  const first = props.data[0].precio
  const last  = props.data[props.data.length - 1].precio
  if (last - first > 0.01)  return '#fb7185'
  if (last - first < -0.01) return '#34d399'
  return '#94a3b8'
})

const priceToY = (price: number) => {
  const ratio = (price - minPrice.value) / priceRange.value
  return paddingTop + chartHeight.value - ratio * chartHeight.value
}

const indexToX = (i: number) => {
  if (props.data.length <= 1) return paddingLeft + chartWidth.value / 2
  return paddingLeft + (i / (props.data.length - 1)) * chartWidth.value
}

// Clamp para que las etiquetas no se salgan del SVG
const clampX = (x: number, min: number, max: number) => Math.max(min, Math.min(max, x))

function catmullRom2bezier(pts: {x: number, y: number}[]) {
  const r: string[] = []
  for (let i = 0; i < pts.length - 1; i++) {
    const p0 = pts[Math.max(i - 1, 0)]
    const p1 = pts[i]
    const p2 = pts[i + 1]
    const p3 = pts[Math.min(i + 2, pts.length - 1)]
    const cp1x = p1.x + (p2.x - p0.x) / 6
    const cp1y = p1.y + (p2.y - p0.y) / 6
    const cp2x = p2.x - (p3.x - p1.x) / 6
    const cp2y = p2.y - (p3.y - p1.y) / 6
    if (i === 0) r.push(`M ${p1.x} ${p1.y}`)
    r.push(`C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`)
  }
  return r.join(' ')
}

const points = computed(() =>
  props.data.map((d, i) => ({
    x: indexToX(i),
    y: priceToY(d.precio),
    price: d.precio,
    fecha: d.fecha,
    index: i
  }))
)

const linePath = computed(() => {
  if (points.value.length === 0) return ''
  if (points.value.length === 1) return `M ${points.value[0].x} ${points.value[0].y}`
  return catmullRom2bezier(points.value)
})

const areaPath = computed(() => {
  if (points.value.length === 0) return ''
  const bottomY = height.value - paddingBottom
  if (points.value.length === 1) {
    const p = points.value[0]
    return `M ${p.x} ${p.y} L ${p.x} ${bottomY} Z`
  }
  const line  = catmullRom2bezier(points.value)
  const first = points.value[0]
  const last  = points.value[points.value.length - 1]
  return `${line} L ${last.x} ${bottomY} L ${first.x} ${bottomY} Z`
})

const minPoint = computed(() => points.value.find(pt => pt.price === minPrice.value) ?? null)
const maxPoint = computed(() => points.value.find(pt => pt.price === maxPrice.value) ?? null)
const lastPoint = computed(() => points.value.length ? points.value[points.value.length - 1] : null)

// Posicionar label ACTUAL arriba o abajo según si está cerca del tope
const labelActualY = computed(() => {
  if (!lastPoint.value) return paddingTop
  // Si el punto está en el tercio superior del gráfico, poner label abajo
  const threshold = paddingTop + chartHeight.value * 0.35
  return lastPoint.value.y < threshold
    ? lastPoint.value.y + 12   // debajo del punto
    : lastPoint.value.y - 24   // arriba del punto
})

// Grid lines con etiquetas de precio
const gridLinesWithLabels = computed(() => {
  const steps = 4
  return Array.from({ length: steps + 1 }, (_, i) => {
    const ratio = i / steps
    const price = minPrice.value + ratio * priceRange.value
    const y     = paddingTop + chartHeight.value - ratio * chartHeight.value
    return {
      y,
      label: formatPriceShort(price)
    }
  })
})

// Eje X: mostrar entre 4 y 6 fechas bien distribuidas
const xLabels = computed(() => {
  const n = props.data.length
  if (n === 0) return []

  let positions: number[]
  if (n <= 6) {
    positions = Array.from({ length: n }, (_, i) => i)
  } else {
    const count = Math.min(6, Math.ceil(n / 7))
    positions = Array.from({ length: count }, (_, i) =>
      Math.round(i * (n - 1) / (count - 1))
    )
    // Asegurar que siempre esté el primero y el último
    if (!positions.includes(0))     positions.unshift(0)
    if (!positions.includes(n - 1)) positions.push(n - 1)
  }

  return positions.map(i => ({
    x: indexToX(i),
    text: formatDateShort(props.data[i].fecha)
  }))
})

function formatDateShort(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function formatPrice(price: number): string {
  return '$' + price.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 0 })
}

function formatPriceShort(price: number): string {
  if (price >= 1000) return '$' + Math.round(price / 1000) + 'k'
  return '$' + Math.round(price)
}
</script>

<style scoped>
.price-chart-wrapper { width: 100%; }
.price-chart { width: 100%; height: auto; display: block; }
.trend-line { filter: drop-shadow(0 1px 4px rgba(0,0,0,0.4)); }
.area-path  { transition: fill 0.3s ease; }

.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.25rem;
  margin-top: 0.5rem;
  font-size: 0.7rem;
  color: rgba(245,240,235,0.4);
}
.legend-item { display: flex; align-items: center; gap: 0.3rem; }
.dot { width: 7px; height: 7px; border-radius: 50%; display: inline-block; }
.dot-min     { background: #34d399; }
.dot-current { background: #e8c4a0; }
.dot-max     { background: #fb7185; }
</style>
