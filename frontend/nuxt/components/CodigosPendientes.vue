<template>
  <section class="cod-pend">
    <header class="cp-header">
      <div class="cp-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M3 5v14M8 5v14M12 5v14M17 5v14M21 5v14"/>
        </svg>
        <span>Códigos pendientes</span>
        <span v-if="pendientes.length" class="cp-count">{{ pendientes.length }}</span>
      </div>
      <p class="cp-sub">
        Estos productos todavía no tienen código de barras (EAN). Escaneá el envase con la cámara
        o escribí el número a mano. Los productos frescos (carne, verdura) no tienen código: es normal que queden algunos.
      </p>
    </header>

    <!-- Nada pendiente -->
    <div v-if="!pendientes.length" class="cp-empty">
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      <p>No hay productos sin código pendientes de cargar.</p>
    </div>

    <!-- Grilla de pendientes -->
    <div v-else class="cp-grid">
      <article v-for="p in pendientesVisibles" :key="p.id_prod" class="cp-card">
        <div class="cp-cardhead">
          <img :src="thumb(p)" :alt="p.nombre_prod" class="cp-thumb" />
          <div class="cp-info">
            <span class="cp-name">{{ p.nombre_prod }}</span>
            <span class="cp-cat">{{ p.cate_prod }}</span>
          </div>
        </div>

        <div class="cp-actions">
          <button class="cp-scan-btn" :disabled="subiendoId !== null" @click="abrirScanner(p)">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M3 7V5a2 2 0 0 1 2-2h2M17 3h2a2 2 0 0 1 2 2v2M21 17v2a2 2 0 0 1-2 2h-2M7 21H5a2 2 0 0 1-2-2v-2"/><path d="M7 12h10"/>
            </svg>
            Escanear
          </button>

          <div class="cp-manual">
            <input
              v-model="manualEan[p.id_prod]"
              type="text"
              inputmode="numeric"
              maxlength="13"
              placeholder="o escribí el EAN"
              class="cp-input"
              :class="{ 'cp-input-err': errores[p.id_prod] }"
              @keyup.enter="guardarEan(p, manualEan[p.id_prod])"
            />
            <button
              class="cp-save"
              :disabled="subiendoId !== null || !manualEan[p.id_prod]"
              @click="guardarEan(p, manualEan[p.id_prod])"
            >
              <span v-if="subiendoId === p.id_prod" class="cp-spinner" />
              <span v-else>OK</span>
            </button>
          </div>
        </div>

        <p v-if="errores[p.id_prod]" class="cp-carderr">{{ errores[p.id_prod] }}</p>
      </article>
    </div>

    <button
      v-if="pendientes.length > visiblesCp"
      class="cp-mostrar-mas"
      @click="mostrarMasCp"
    >
      Mostrar más ({{ pendientes.length - visiblesCp }} restantes)
    </button>

    <p v-if="okMsg" class="cp-ok">{{ okMsg }}</p>

    <!-- MODAL ESCÁNER -->
    <Teleport to="body">
      <div v-if="scannerProd" class="cp-scanner-overlay" @click.self="cerrarScanner">
        <div class="cp-scanner-box">
          <div class="cp-scanner-head">
            <span>Escaneando: {{ scannerProd.nombre_prod }}</span>
            <button class="cp-scanner-close" @click="cerrarScanner">✕</button>
          </div>

          <div class="cp-scanner-view">
            <!-- BarcodeDetector nativo usa este <video> -->
            <video v-show="motor === 'nativo'" ref="videoRef" playsinline muted></video>
            <!-- html5-qrcode monta su propia cámara acá -->
            <div v-show="motor === 'libreria'" id="cp-scanner-region"></div>
            <div class="cp-scanner-guide"></div>
          </div>

          <p v-if="scannerError" class="cp-scanner-err">{{ scannerError }}</p>
          <p v-else class="cp-scanner-hint">Apuntá al código de barras del envase.</p>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onBeforeUnmount, nextTick } from 'vue'
import { useRuntimeConfig } from '#app'

interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  ean_prod?: string | null
  [key: string]: any
}

const props = defineProps<{
  productos: Producto[]
  imagenPorCategoria?: Record<string, string>
}>()

const emit = defineEmits<{ (e: 'actualizado'): void }>()

const config = useRuntimeConfig()
const API = config.public.apiBase

const subiendoId = ref<string | null>(null)
const okMsg = ref('')
const manualEan = reactive<Record<string, string>>({})
const errores = reactive<Record<string, string>>({})

// Productos SIN código
const pendientes = computed(() =>
  (props.productos || []).filter(p => !p.ean_prod)
)

// Paginación: mostrar de a 24
const visiblesCp = ref(24)
const pendientesVisibles = computed(() => pendientes.value.slice(0, visiblesCp.value))
function mostrarMasCp() { visiblesCp.value += 24 }

function getToken(): string {
  try {
    const s = localStorage.getItem('comparapp_user')
    return s ? (JSON.parse(s).access_token || '') : ''
  } catch { return '' }
}

function thumb(p: Producto): string {
  const map = props.imagenPorCategoria || {}
  return map[(p.cate_prod || '').toLowerCase().trim()] || '/images/avatar_default.png'
}

// ── Validación EAN-13 / EAN-8 (dígito verificador) ────────────
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

// ── Guardar EAN en el producto ────────────────────────────────
async function guardarEan(p: Producto, code: string | undefined) {
  const ean = (code || '').trim()
  errores[p.id_prod] = ''

  if (!eanValido(ean)) {
    errores[p.id_prod] = 'Código inválido. Un EAN válido tiene 8 o 13 dígitos.'
    return
  }

  subiendoId.value = p.id_prod
  try {
    await $fetch(`${API}/products/${p.id_prod}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: { ean_prod: ean },
    })
    okMsg.value = `Código cargado en "${p.nombre_prod}"`
    setTimeout(() => (okMsg.value = ''), 2500)
    delete manualEan[p.id_prod]
    emit('actualizado')
  } catch (err: any) {
    errores[p.id_prod] = err?.data?.detail || 'No se pudo guardar el código.'
  } finally {
    subiendoId.value = null
  }
}

// ── ESCÁNER (híbrido: BarcodeDetector nativo → html5-qrcode CDN) ──
const scannerProd = ref<Producto | null>(null)
const scannerError = ref('')
const motor = ref<'nativo' | 'libreria'>('nativo')
const videoRef = ref<HTMLVideoElement | null>(null)

let stream: MediaStream | null = null
let rafId: number | null = null
let html5qr: any = null

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

async function abrirScanner(p: Producto) {
  scannerProd.value = p
  scannerError.value = ''
  await nextTick()

  const tieneNativo = 'BarcodeDetector' in window
  motor.value = tieneNativo ? 'nativo' : 'libreria'

  try {
    if (tieneNativo) {
      await iniciarNativo()
    } else {
      await iniciarLibreria()
    }
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
    if (!scannerProd.value || !videoRef.value) return
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
  html5qr = new Html5Qrcode('cp-scanner-region', {
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
  const prod = scannerProd.value
  cerrarScanner()
  if (prod) guardarEan(prod, code)
}

function mensajeCamaraError(e: any): string {
  const name = e?.name || ''
  if (name === 'NotAllowedError') return 'Diste permiso denegado a la cámara. Habilitalo en el navegador.'
  if (name === 'NotFoundError') return 'No se encontró una cámara en el dispositivo.'
  if (location.protocol !== 'https:' && location.hostname !== 'localhost')
    return 'La cámara solo funciona con HTTPS. Probá desde la app publicada.'
  return 'No se pudo abrir la cámara. Podés cargar el código a mano.'
}

async function cerrarScanner() {
  if (rafId !== null) { cancelAnimationFrame(rafId); rafId = null }
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null }
  if (html5qr) {
    try { await html5qr.stop(); html5qr.clear() } catch { /* ya estaba parado */ }
    html5qr = null
  }
  scannerProd.value = null
  scannerError.value = ''
}

onBeforeUnmount(cerrarScanner)
</script>

<style scoped>
.cod-pend {
  background: var(--bg-card, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  padding: 1.25rem;
  color: var(--text-primary, #f4f4f5);
}

.cp-header { margin-bottom: 1rem; }
.cp-title { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; font-size: 1.05rem; }
.cp-title svg { color: var(--accent-gold, #e8c4a0); }
.cp-count {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 22px; height: 22px; padding: 0 7px;
  background: rgba(96, 165, 250, 0.15); border: 1px solid rgba(96, 165, 250, 0.35);
  color: #60a5fa; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
}
.cp-sub { margin: 0.35rem 0 0; font-size: 0.82rem; color: var(--text-secondary, #a1a1aa); line-height: 1.45; }

.cp-empty {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 2rem 1rem; text-align: center; color: var(--text-secondary, #a1a1aa);
}
.cp-empty svg { color: #4ade80; }

.cp-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 0.75rem;
}
.cp-card {
  display: flex; flex-direction: column; gap: 0.6rem;
  background: var(--bg-input, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: 12px; padding: 0.75rem;
}
.cp-cardhead { display: flex; align-items: center; gap: 0.6rem; min-width: 0; }
.cp-thumb { width: 42px; height: 42px; border-radius: 8px; object-fit: cover; flex-shrink: 0; opacity: 0.85; }
.cp-info { display: flex; flex-direction: column; gap: 0.1rem; min-width: 0; }
.cp-name {
  font-size: 0.86rem; font-weight: 600; line-height: 1.25; color: var(--text-primary, #f4f4f5);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.cp-cat { font-size: 0.72rem; color: var(--text-muted, #71717a); }

.cp-actions { display: flex; flex-direction: column; gap: 0.5rem; }
.cp-scan-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.4rem;
  padding: 0.5rem; border-radius: 8px;
  background: rgba(96, 165, 250, 0.12); border: 1px solid rgba(96, 165, 250, 0.3);
  color: #60a5fa; font-size: 0.82rem; font-weight: 600; cursor: pointer;
  transition: background 0.2s;
}
.cp-scan-btn:hover:not(:disabled) { background: rgba(96, 165, 250, 0.2); }
.cp-scan-btn:disabled { opacity: 0.5; cursor: not-allowed; }

.cp-manual { display: flex; gap: 0.4rem; }
.cp-input {
  flex: 1; min-width: 0; padding: 0.45rem 0.6rem; border-radius: 8px;
  background: var(--bg-card, rgba(0, 0, 0, 0.2));
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.15));
  color: var(--text-primary, #f4f4f5); font-size: 0.85rem; font-family: 'Courier New', monospace;
}
.cp-input-err { border-color: #fb7185; }
.cp-save {
  min-width: 42px; padding: 0.45rem; border-radius: 8px; border: none;
  background: var(--accent-gold, #e8c4a0); color: #1a1a1a; font-weight: 700; font-size: 0.82rem; cursor: pointer;
}
.cp-save:disabled { opacity: 0.5; cursor: not-allowed; }

.cp-spinner {
  display: inline-block; width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid rgba(0, 0, 0, 0.3); border-top-color: #1a1a1a;
  animation: cp-spin 0.7s linear infinite;
}
@keyframes cp-spin { to { transform: rotate(360deg); } }

.cp-carderr { margin: 0; font-size: 0.76rem; color: #fb7185; }
.cp-ok { color: #4ade80; font-size: 0.85rem; margin: 0.75rem 0 0; }

/* Scanner modal */
.cp-scanner-overlay {
  position: fixed; inset: 0; z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex; align-items: center; justify-content: center; padding: 1rem;
}
.cp-scanner-box {
  background: #16161a; border-radius: 16px; padding: 1rem;
  width: 100%; max-width: 380px;
}
.cp-scanner-head {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
  margin-bottom: 0.75rem; color: #f4f4f5; font-size: 0.9rem; font-weight: 600;
}
.cp-scanner-close {
  background: none; border: none; color: #a1a1aa; font-size: 1.2rem; cursor: pointer; line-height: 1;
}
.cp-scanner-view {
  position: relative; width: 100%; aspect-ratio: 4 / 3;
  background: #000; border-radius: 10px; overflow: hidden;
}
.cp-scanner-view video, .cp-scanner-view :deep(video) { width: 100%; height: 100%; object-fit: cover; }
.cp-scanner-guide {
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  width: 70%; height: 30%; border: 2px solid rgba(232, 196, 160, 0.9); border-radius: 8px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.25);
}
.cp-scanner-hint { text-align: center; color: #a1a1aa; font-size: 0.82rem; margin: 0.75rem 0 0; }
.cp-scanner-err { text-align: center; color: #fb7185; font-size: 0.85rem; margin: 0.75rem 0 0; }

.cp-mostrar-mas {
  display: block; width: 100%; margin-top: 1rem; padding: 0.7rem;
  border-radius: 10px; cursor: pointer;
  background: var(--bg-input, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-primary, #f4f4f5); font-size: 0.88rem; font-weight: 600;
}
.cp-mostrar-mas:hover { background: rgba(255,255,255,0.1); }
</style>