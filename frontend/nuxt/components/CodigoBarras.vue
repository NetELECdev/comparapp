<template>
  <div class="codigo-barras" :class="{ 'cb-invalido': !valido && ean }">
    <!-- Barras (solo si el EAN es válido) -->
    <svg v-show="valido" ref="svgRef" class="cb-svg"></svg>

    <!-- Fallback: EAN inválido o no reconocido -->
    <span v-if="ean && !valido" class="cb-fallback">{{ ean }}</span>

    <!-- Sin EAN -->
    <span v-else-if="!ean" class="cb-sin">sin código</span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  ean: string | null | undefined
  height?: number       // alto de las barras en px
  fontSize?: number     // tamaño del número debajo
  mostrarNumero?: boolean
}>(), {
  height: 40,
  fontSize: 12,
  mostrarNumero: true,
})

const svgRef = ref<SVGElement | null>(null)
const valido = ref(false)

// ── Validación EAN-13 / EAN-8 (dígito verificador) ────────────
// Un escáner rechaza códigos cuyo verificador no cierra, así que solo
// dibujamos barras cuando el número es un EAN válido de verdad.
function eanValido(code: string): { ok: boolean; formato: 'EAN13' | 'EAN8' | null } {
  const s = (code || '').trim()
  if (!/^\d+$/.test(s)) return { ok: false, formato: null }
  if (s.length !== 13 && s.length !== 8) return { ok: false, formato: null }

  const digits = s.split('').map(Number)
  const check = digits.pop() as number
  // EAN-13: pesos 1,3,1,3...  EAN-8: pesos 3,1,3,1...
  const empiezaEn3 = s.length === 8
  let suma = 0
  digits.forEach((d, i) => {
    const peso = (i % 2 === 0) ? (empiezaEn3 ? 3 : 1) : (empiezaEn3 ? 1 : 3)
    suma += d * peso
  })
  const verificador = (10 - (suma % 10)) % 10
  return { ok: verificador === check, formato: s.length === 13 ? 'EAN13' : 'EAN8' }
}

// ── Carga de JsBarcode por CDN (una sola vez, compartida) ─────
let jsbarcodePromise: Promise<any> | null = null
function cargarJsBarcode(): Promise<any> {
  if ((window as any).JsBarcode) return Promise.resolve((window as any).JsBarcode)
  if (jsbarcodePromise) return jsbarcodePromise
  jsbarcodePromise = new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://cdn.jsdelivr.net/npm/jsbarcode@3.11.6/dist/JsBarcode.all.min.js'
    s.onload = () => resolve((window as any).JsBarcode)
    s.onerror = reject
    document.head.appendChild(s)
  })
  return jsbarcodePromise
}

async function render() {
  const code = (props.ean || '').trim()
  const check = eanValido(code)
  valido.value = check.ok

  if (!check.ok || !check.formato) return

  try {
    const JsBarcode = await cargarJsBarcode()
    await nextTick()
    if (!svgRef.value) return
    JsBarcode(svgRef.value, code, {
      format: check.formato,          // 'EAN13' o 'EAN8'
      height: props.height,
      displayValue: props.mostrarNumero,
      fontSize: props.fontSize,
      margin: 4,
      background: 'transparent',
      lineColor: '#0a0a0a',
    })
  } catch (e) {
    // Si el CDN falla, queda el número como fallback
    valido.value = false
    console.error('No se pudo renderizar el código de barras:', e)
  }
}

onMounted(render)
watch(() => props.ean, render)
</script>

<style scoped>
.codigo-barras {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  /* Fondo blanco: los escáneres necesitan contraste barras oscuras / fondo claro */
  background: #ffffff;
  border-radius: 6px;
  padding: 4px 6px;
  min-width: 90px;
  min-height: 44px;
}
.cb-svg { display: block; max-width: 100%; height: auto; }
.cb-fallback {
  font-family: 'Courier New', monospace;
  font-size: 0.72rem;
  color: #0a0a0a;
  letter-spacing: 0.05em;
}
.cb-sin {
  font-size: 0.7rem;
  color: #9ca3af;
  font-style: italic;
}
.cb-invalido { background: #fef2f2; }
</style>