<template>
  <Teleport to="body">
    <div v-if="abierto" class="eb-overlay" @click.self="cerrar">
      <div class="eb-box">
        <div class="eb-head">
          <span>{{ titulo }}</span>
          <button class="eb-close" @click="cerrar" aria-label="Cerrar">✕</button>
        </div>

        <div class="eb-view">
          <!-- BarcodeDetector nativo usa este <video> -->
          <video v-show="motor === 'nativo'" ref="videoRef" playsinline muted></video>
          <!-- html5-qrcode monta su propia cámara acá -->
          <div v-show="motor === 'libreria'" id="eb-scanner-region"></div>
          <div class="eb-guide"></div>
        </div>

        <p v-if="scannerError" class="eb-err">{{ scannerError }}</p>
        <p v-else class="eb-hint">Apuntá al código de barras del producto.</p>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, watch, onBeforeUnmount, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  abierto: boolean
  titulo?: string
}>(), {
  titulo: 'Escaneá un producto'
})

const emit = defineEmits<{
  (e: 'detectado', ean: string): void
  (e: 'cerrar'): void
}>()

const scannerError = ref('')
const motor = ref<'nativo' | 'libreria'>('nativo')
const videoRef = ref<HTMLVideoElement | null>(null)

let stream: MediaStream | null = null
let rafId: number | null = null
let html5qr: any = null

// Validación EAN-13 / EAN-8 (dígito verificador). Igual que en CodigosPendientes.
function eanValido(code: string): boolean {
  const s = (code || '').trim()
  if (!/^\d+$/.test(s)) return false
  if (s.length !== 13 && s.length !== 8) return false
  const digits = s.split('').map(Number)
  const check = digits.pop() as number
  const empiezaEn3 = s.length === 8
  let suma = 0
  digits.forEach((d, i) => {
    const peso = (i % 2 === 0) ? (empiezaEn3 ? 3 : 1) : (empiezaEn3 ? 1 : 3)
    suma += d * peso
  })
  return ((10 - (suma % 10)) % 10) === check
}

function cargarHtml5Qrcode(): Promise<any> {
  if ((window as any).Html5Qrcode) return Promise.resolve((window as any).Html5Qrcode)
  return new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://unpkg.com/html5-qrcode@2.3.8/html5-qrcode.min.js'
    s.onload = () => resolve((window as any).Html5Qrcode)
    s.onerror = reject
    document.head.appendChild(s)
  })
}

async function iniciar() {
  scannerError.value = ''
  await nextTick()
  const tieneNativo = 'BarcodeDetector' in window
  motor.value = tieneNativo ? 'nativo' : 'libreria'
  try {
    if (tieneNativo) await iniciarNativo()
    else await iniciarLibreria()
  } catch (e: any) {
    scannerError.value = mensajeCamaraError(e)
  }
}

async function iniciarNativo() {
  // @ts-ignore
  const detector = new window.BarcodeDetector({ formats: ['ean_13', 'ean_8'] })
  stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
  const video = videoRef.value!
  video.srcObject = stream
  await video.play()

  const loop = async () => {
    if (!props.abierto || !videoRef.value) return
    try {
      const codes = await detector.detect(videoRef.value)
      if (codes && codes.length) {
        onCodigoDetectado(codes[0].rawValue)
        return
      }
    } catch { /* frame sin código, seguimos */ }
    rafId = requestAnimationFrame(loop)
  }
  rafId = requestAnimationFrame(loop)
}

async function iniciarLibreria() {
  const Html5Qrcode = await cargarHtml5Qrcode()
  const formatos = (window as any).Html5QrcodeSupportedFormats
  html5qr = new Html5Qrcode('eb-scanner-region', {
    formatsToSupport: formatos ? [formatos.EAN_13, formatos.EAN_8] : undefined,
    verbose: false,
  })
  await html5qr.start(
    { facingMode: 'environment' },
    { fps: 10, qrbox: { width: 250, height: 150 } },
    (texto: string) => onCodigoDetectado(texto),
    () => { /* frame sin lectura, ignorar */ }
  )
}

function onCodigoDetectado(raw: string) {
  const code = (raw || '').trim()
  if (!eanValido(code)) {
    scannerError.value = 'Código leído inválido, probá de nuevo.'
    return  // seguimos escaneando
  }
  emit('detectado', code)
  cerrar()
}

function mensajeCamaraError(e: any): string {
  const name = e?.name || ''
  if (name === 'NotAllowedError') return 'Diste permiso denegado a la cámara. Habilitalo en el navegador.'
  if (name === 'NotFoundError') return 'No se encontró una cámara en el dispositivo.'
  if (location.protocol !== 'https:' && location.hostname !== 'localhost')
    return 'La cámara solo funciona con HTTPS. Probá desde la app publicada.'
  return 'No se pudo abrir la cámara. Podés buscar el producto por nombre.'
}

async function detener() {
  if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
  if (html5qr) {
    try { await html5qr.stop(); html5qr.clear() } catch { /* ya estaba parado */ }
    html5qr = null
  }
  scannerError.value = ''
}

function cerrar() {
  detener()
  emit('cerrar')
}

// Abrir/cerrar la cámara según la prop `abierto`
watch(() => props.abierto, (abierto) => {
  if (abierto) iniciar()
  else detener()
})

onBeforeUnmount(detener)
</script>

<style scoped>
.eb-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.eb-box {
  background: #16161a; border-radius: 16px; padding: 1rem;
  width: 100%; max-width: 380px;
}
.eb-head {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
  margin-bottom: 0.75rem; color: #f4f4f5; font-size: 0.9rem; font-weight: 600;
}
.eb-close {
  background: none; border: none; color: #a1a1aa; font-size: 1.2rem; cursor: pointer; line-height: 1;
}
.eb-view {
  position: relative; width: 100%; aspect-ratio: 4 / 3;
  background: #000; border-radius: 10px; overflow: hidden;
}
.eb-view video, .eb-view :deep(video) { width: 100%; height: 100%; object-fit: cover; }
.eb-guide {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 70%; height: 30%; border: 2px solid rgba(232, 196, 160, 0.9); border-radius: 8px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.25);
}
.eb-hint { text-align: center; color: #a1a1aa; font-size: 0.82rem; margin: 0.75rem 0 0; }
.eb-err { text-align: center; color: #fb7185; font-size: 0.85rem; margin: 0.75rem 0 0; }
</style>