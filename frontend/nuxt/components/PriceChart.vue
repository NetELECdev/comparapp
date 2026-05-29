<template>
  <div class="price-chart-wrapper">
    <svg
      :viewBox="`0 0 ${width} ${height}`"
      preserveAspectRatio="xMidYMid meet"
      class="price-chart"
    >
      <!-- Defs: gradients y filtros -->
      <defs>
        <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" :stop-color="trendColor" stop-opacity="0.2"/>
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

      <!-- Grid horizontal -->
      <g class="grid">
        <line
          v-for="y in gridLines"
          :key="'h-'+y"
          :x1="paddingLeft"
          :y1="y"
          :x2="width - paddingRight"
          :y2="y"
          stroke="rgba(255,255,255,0.06)"
          stroke-dasharray="3,4"
        />
      </g>

      <!-- Área bajo la curva -->
      <path
        :d="areaPath"
        fill="url(#areaGradient)"
        class="area-path"
      />

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

      <!-- Puntos destacados: MIN / ACTUAL / MAX -->
      <g class="highlight-points">
        <!-- Mínimo -->
        <g v-if="minPoint" class="point-min">
          <circle
            :cx="minPoint.x"
            :cy="minPoint.y"
            r="4"
            fill="#34d399"
            filter="url(#glow)"
          />
          <circle
            :cx="minPoint.x"
            :cy="minPoint.y"
            r="9"
            fill="none"
            stroke="#34d399"
            stroke-width="1"
            opacity="0.35"
          >
            <animate
              attributeName="r"
              values="9;13;9"
              dur="2.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.35;0.05;0.35"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          <text
            :x="minPoint.x"
            :y="minPoint.y - 16"
            text-anchor="middle"
            font-size="9"
            font-weight="600"
            fill="#34d399"
          >
            MÍN
          </text>
          <text
            :x="minPoint.x"
            :y="minPoint.y - 5"
            text-anchor="middle"
            font-size="8"
            fill="rgba(245,240,235,0.5)"
          >
            {{ formatPrice(minPoint.price) }}
          </text>
        </g>

        <!-- Actual -->
        <g v-if="lastPoint" class="point-current">
          <circle
            :cx="lastPoint.x"
            :cy="lastPoint.y"
            r="4"
            fill="#e8c4a0"
            filter="url(#glow)"
          />
          <circle
            :cx="lastPoint.x"
            :cy="lastPoint.y"
            r="9"
            fill="none"
            stroke="#e8c4a0"
            stroke-width="1"
            opacity="0.35"
          >
            <animate
              attributeName="r"
              values="9;13;9"
              dur="2.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.35;0.05;0.35"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          <text
            :x="lastPoint.x"
            :y="lastPoint.y - 16"
            text-anchor="middle"
            font-size="9"
            font-weight="600"
            fill="#e8c4a0"
          >
            ACTUAL
          </text>
          <text
            :x="lastPoint.x"
            :y="lastPoint.y - 5"
            text-anchor="middle"
            font-size="8"
            fill="rgba(245,240,235,0.5)"
          >
            {{ formatPrice(lastPoint.price) }}
          </text>
        </g>

        <!-- Máximo -->
        <g v-if="maxPoint" class="point-max">
          <circle
            :cx="maxPoint.x"
            :cy="maxPoint.y"
            r="4"
            fill="#fb7185"
            filter="url(#glow)"
          />
          <circle
            :cx="maxPoint.x"
            :cy="maxPoint.y"
            r="9"
            fill="none"
            stroke="#fb7185"
            stroke-width="1"
            opacity="0.35"
          >
            <animate
              attributeName="r"
              values="9;13;9"
              dur="2.5s"
              repeatCount="indefinite"
            />
            <animate
              attributeName="opacity"
              values="0.35;0.05;0.35"
              dur="2.5s"
              repeatCount="indefinite"
            />
          </circle>
          <text
            :x="maxPoint.x"
            :y="maxPoint.y - 16"
            text-anchor="middle"
            font-size="9"
            font-weight="600"
            fill="#fb7185"
          >
            MÁX
          </text>
          <text
            :x="maxPoint.x"
            :y="maxPoint.y - 5"
            text-anchor="middle"
            font-size="8"
            fill="rgba(245,240,235,0.5)"
          >
            {{ formatPrice(maxPoint.price) }}
          </text>
        </g>
      </g>

      <!-- Fechas en eje X -->
      <g class="x-axis">
        <text
          v-for="(label, i) in xLabels"
          :key="'x-'+i"
          :x="label.x"
          :y="height - 4"
          text-anchor="middle"
          font-size="8"
          fill="rgba(245,240,235,0.3)"
        >
          {{ label.text }}
        </text>
      </g>
    </svg>

    <!-- Leyenda -->
    <div class="chart-legend">
      <div class="legend-item">
        <span class="dot dot-min"></span>
        <span>Mínimo</span>
      </div>
      <div class="legend-item">
        <span class="dot dot-current"></span>
        <span>Actual</span>
      </div>
      <div class="legend-item">
        <span class="dot dot-max"></span>
        <span>Máximo</span>
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
const height = computed(() => props.height || 150)
const paddingLeft = 10
const paddingRight = 10
const paddingTop = 32
const paddingBottom = 20

const chartWidth = computed(() => width.value - paddingLeft - paddingRight)
const chartHeight = computed(() => height.value - paddingTop - paddingBottom)

const prices = computed(() => props.data.map(d => d.precio))
const minPrice = computed(() => Math.min(...prices.value))
const maxPrice = computed(() => Math.max(...prices.value))
const priceRange = computed(() => maxPrice.value - minPrice.value || 1)

// Tendencia para color del gradiente
const trendColor = computed(() => {
  if (props.data.length < 2) return '#94a3b8'
  const first = props.data[0].precio
  const last = props.data[props.data.length - 1].precio
  const diff = last - first
  if (diff > 0.01) return '#fb7185'   // subió → rojo (malo para precio)
  if (diff < -0.01) return '#34d399'  // bajó → verde (bueno)
  return '#94a3b8'                     // estable → gris
})

// Mapear precio a coordenada Y (invertido)
const priceToY = (price: number) => {
  const ratio = (price - minPrice.value) / priceRange.value
  return paddingTop + chartHeight.value - (ratio * chartHeight.value)
}

// Mapear índice a coordenada X
const indexToX = (i: number) => {
  if (props.data.length <= 1) return paddingLeft + chartWidth.value / 2
  return paddingLeft + (i / (props.data.length - 1)) * chartWidth.value
}

// Catmull-Rom spline → Bezier
function catmullRom2bezier(points: {x: number, y: number}[]) {
  const result: string[] = []
  for (let i = 0; i < points.length - 1; i++) {
    const p0 = points[Math.max(i - 1, 0)]
    const p1 = points[i]
    const p2 = points[i + 1]
    const p3 = points[Math.min(i + 2, points.length - 1)]

    const cp1x = p1.x + (p2.x - p0.x) / 6
    const cp1y = p1.y + (p2.y - p0.y) / 6
    const cp2x = p2.x - (p3.x - p1.x) / 6
    const cp2y = p2.y - (p3.y - p1.y) / 6

    if (i === 0) {
      result.push(`M ${p1.x} ${p1.y}`)
    }
    result.push(`C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${p2.x} ${p2.y}`)
  }
  return result.join(' ')
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
  if (points.value.length === 1) {
    const p = points.value[0]
    return `M ${p.x} ${p.y}`
  }
  return catmullRom2bezier(points.value)
})

const areaPath = computed(() => {
  if (points.value.length === 0) return ''
  const bottomY = height.value - paddingBottom
  if (points.value.length === 1) {
    const p = points.value[0]
    return `M ${p.x} ${p.y} L ${p.x} ${bottomY} Z`
  }
  const line = catmullRom2bezier(points.value)
  const first = points.value[0]
  const last = points.value[points.value.length - 1]
  return `${line} L ${last.x} ${bottomY} L ${first.x} ${bottomY} Z`
})

// Puntos destacados
const minPoint = computed(() => {
  const p = points.value.find(pt => pt.price === minPrice.value)
  return p || null
})

const maxPoint = computed(() => {
  const p = points.value.find(pt => pt.price === maxPrice.value)
  return p || null
})

const lastPoint = computed(() => {
  if (points.value.length === 0) return null
  return points.value[points.value.length - 1]
})

// Grid lines
const gridLines = computed(() => {
  const lines = 3
  const step = chartHeight.value / lines
  return Array.from({ length: lines + 1 }, (_, i) => paddingTop + i * step)
})

// Labels eje X (distribuidos)
const xLabels = computed(() => {
  const n = props.data.length
  if (n === 0) return []
  if (n <= 4) {
    return props.data.map((d, i) => ({
      x: indexToX(i),
      text: formatDateShort(d.fecha)
    }))
  }
  const labels: {x: number, text: string}[] = []
  const positions = n <= 8 ? [0, Math.floor(n/2), n-1] : [0, Math.floor(n/3), Math.floor(2*n/3), n-1]
  positions.forEach(i => {
    labels.push({
      x: indexToX(i),
      text: formatDateShort(props.data[i].fecha)
    })
  })
  return labels
})

function formatDateShort(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function formatPrice(price: number): string {
  return '$' + price.toLocaleString('es-AR', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.price-chart-wrapper {
  width: 100%;
}
.price-chart {
  width: 100%;
  height: auto;
  display: block;
}
.trend-line {
  filter: drop-shadow(0 1px 3px rgba(0,0,0,0.3));
}
.area-path {
  transition: fill 0.3s ease;
}
.chart-legend {
  display: flex;
  justify-content: center;
  gap: 1.5rem;
  margin-top: 0.75rem;
  font-size: 0.72rem;
  color: rgba(245,240,235,0.4);
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  display: inline-block;
}
.dot-min { background: #34d399; }
.dot-current { background: #e8c4a0; }
.dot-max { background: #fb7185; }
</style>
