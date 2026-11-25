<template>
  <div class="ing-page">
    <DynamicBackground />

    <main class="page-content">
      <!-- Encabezado -->
      <div class="ing-head">
        <button class="ing-back" @click="volver" aria-label="Volver">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <h1 class="ing-title">Ingesta de flyers</h1>
          <p class="ing-sub">Leé flyers de WhatsApp y aprobá los precios</p>
        </div>
      </div>

      <div v-if="!isAdmin" class="ing-box">
        <p>Esta sección es solo para administradores.</p>
      </div>

      <template v-else>
        <div v-if="sesionVencida" class="ing-alerta">
          <span>Tu sesión venció (dura 1 hora).</span>
          <button @click="navigateTo('/login')">Iniciar sesión</button>
        </div>

        <!-- ═══ SUBIDA ═══ -->
        <section class="ing-card">
          <h2 class="ing-h2">Leer flyers</h2>

          <div v-if="archivos.length" class="ing-previews">
            <div v-for="(a, i) in archivos" :key="a.url" class="ing-prev">
              <img :src="a.url" alt="" />
              <button :disabled="subiendo" aria-label="Quitar" @click="quitarArchivo(i)">✕</button>
            </div>
          </div>

          <label class="ing-drop" :class="{ disabled: subiendo || archivos.length >= MAX_IMAGENES }">
            <input
              type="file" accept="image/*" multiple hidden
              :disabled="subiendo || archivos.length >= MAX_IMAGENES"
              @change="onArchivos"
            />
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect width="18" height="18" x="3" y="3" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.09-3.09a2 2 0 0 0-2.82 0L6 21"/></svg>
            <span>{{ archivos.length ? 'Agregar más imágenes' : 'Elegir imágenes (estados o flyers)' }}</span>
            <small>Hasta {{ MAX_IMAGENES }} por vez</small>
          </label>

          <div class="ing-row">
            <div class="ing-field">
              <label>Comercio</label>
              <select v-model="comercioSubida" :disabled="subiendo">
                <option value="">Detectar del flyer</option>
                <option v-for="c in comercios" :key="c.id_comer" :value="c.id_comer">{{ c.nombre_comer }}</option>
              </select>
            </div>
            <div class="ing-field">
              <label>Origen</label>
              <select v-model="origenSubida" :disabled="subiendo">
                <option value="compartir">Compartido</option>
                <option value="estado">Estado</option>
                <option value="grupo">Grupo</option>
              </select>
            </div>
          </div>

          <button class="btn-main" :disabled="!archivos.length || subiendo" @click="leerFlyers">
            <span v-if="subiendo" class="spin-sm" />
            {{ subiendo ? progreso : textoBotonLeer }}
          </button>

          <ul v-if="resultadosSubida.length" class="ing-res">
            <li v-for="(r, i) in resultadosSubida" :key="i" :class="r.ok ? 'ok' : 'err'">
              <strong>{{ r.archivo }}</strong>
              <span v-if="r.ok">
                {{ r.propuestas }} propuesta(s) ·
                {{ r.comercio_asignado || (r.comercio_leido ? `"${r.comercio_leido}" (sin asignar)` : 'comercio sin detectar') }}
              </span>
              <span v-else>{{ r.error }}</span>
            </li>
          </ul>
        </section>

        <!-- ═══ PESTAÑAS ═══ -->
        <div class="ing-tabs">
          <button
            v-for="t in VISTAS" :key="t.id"
            class="ing-tab" :class="{ active: estadoVista === t.id }"
            @click="cambiarVista(t.id)"
          >
            {{ t.label }}
            <span v-if="t.id === 'pendiente' && estadoVista === 'pendiente' && propuestas.length" class="ing-badge">{{ propuestas.length }}</span>
          </button>
          <button class="ing-tab ing-refresh" :disabled="cargando" aria-label="Recargar" @click="cargarPropuestas">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/><path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/><path d="M16 16h5v-5"/></svg>
          </button>
        </div>

        <div v-if="cargando" class="ing-box">
          <div class="ing-spinner" />
          <span>Cargando propuestas...</span>
        </div>

        <div v-else-if="!lotes.length" class="ing-box">
          <p>{{ estadoVista === 'pendiente' ? 'No hay propuestas pendientes. Subí un flyer arriba.' : 'No hay propuestas en esta lista.' }}</p>
        </div>

        <!-- ═══ LOTES (un flyer = un lote) ═══ -->
        <section v-for="lote in lotes" :key="lote.lote_id" class="ing-lote">
          <div class="lote-head">
            <img
              v-if="lote.imagen_url" :src="lote.imagen_url" class="lote-img" alt="Flyer"
              @click="imagenGrande = lote.imagen_url"
            />
            <div class="lote-info">
              <span class="lote-leido">
                {{ lote.comercio_leido ? `Leído: "${lote.comercio_leido}"` : 'El flyer no dice el comercio' }}
              </span>
              <span class="lote-meta">
                {{ ORIGEN_LABEL[lote.origen] || lote.origen }} · {{ fmtFecha(lote.creado_en) }} · {{ lote.items.length }} producto(s)
              </span>
              <template v-if="estadoVista === 'pendiente'">
                <select
                  v-model="comercioLote[lote.lote_id]"
                  class="lote-select" :class="{ falta: !comercioLote[lote.lote_id] }"
                  @change="onCambioComercioLote(lote)"
                >
                  <option value="">Elegí el comercio…</option>
                  <option v-for="c in comercios" :key="c.id_comer" :value="c.id_comer">{{ c.nombre_comer }}</option>
                </select>
                <button class="lote-rechazar" :disabled="procesando === lote.lote_id" @click="rechazarLote(lote)">
                  {{ procesando === lote.lote_id ? 'Rechazando…' : 'Rechazar todo el flyer' }}
                </button>
              </template>
              <span v-else class="lote-comer">{{ (lote.id_comer && comercioPorId[lote.id_comer]?.nombre_comer) || '—' }}</span>
            </div>
          </div>

          <article v-for="p in lote.items" :key="p.id" class="prop" :class="`conf-${p.confianza}`">
            <div class="prop-top">
              <div class="prop-titulo">
                <strong>{{ p.nombre_leido }}</strong>
                <span v-if="p.marca_leida" class="prop-marca">{{ p.marca_leida }}</span>
              </div>
              <div class="prop-precio">${{ fmt(p.precio_total) }}</div>
            </div>

            <div class="prop-chips">
              <span class="chip">{{ fmtCant(p.cantidad) }} {{ ABREV[p.unidad] || p.unidad }}</span>
              <span class="chip" :class="`tipo-${p.tipo}`">{{ TIPO_LABEL[p.tipo] || p.tipo }}</span>
              <span class="chip" :class="`conf-chip-${p.confianza}`">Confianza {{ p.confianza }}</span>
              <span v-if="p.condicion_oferta" class="chip">{{ p.condicion_oferta }}</span>
              <span v-if="p.precio_anterior_leido" class="chip">Antes ${{ fmt(p.precio_anterior_leido) }}</span>
            </div>

            <p v-if="p.texto_original" class="prop-texto">"{{ p.texto_original }}"</p>

            <!-- Pendiente: decidir -->
            <template v-if="estadoVista === 'pendiente' && ediciones[p.id]">
              <div class="seg">
                <button
                  :class="{ on: ediciones[p.id].accion === 'actualizar' }"
                  :disabled="!comercioLote[p.lote_id]"
                  @click="ediciones[p.id].accion = 'actualizar'"
                >Actualizar existente</button>
                <button
                  :class="{ on: ediciones[p.id].accion === 'crear' }"
                  @click="ediciones[p.id].accion = 'crear'"
                >Crear nuevo</button>
              </div>

              <select
                v-if="ediciones[p.id].accion === 'actualizar'"
                v-model="ediciones[p.id].id_prod" class="prop-select"
              >
                <option value="">{{ cargandoProd[comercioLote[p.lote_id]] ? 'Cargando productos…' : 'Elegí el producto…' }}</option>
                <option v-for="o in opcionesProducto(p)" :key="o.id_prod" :value="o.id_prod">{{ labelOpcion(o) }}</option>
              </select>

              <div class="prop-resumen" :class="{ alerta: resumen(p).alerta }">
                {{ resumen(p).texto }}
                <small v-if="resumen(p).nota">{{ resumen(p).nota }}</small>
              </div>

              <button class="prop-link" @click="ediciones[p.id].abierto = !ediciones[p.id].abierto">
                {{ ediciones[p.id].abierto ? 'Ocultar corrección' : 'Corregir datos leídos' }}
              </button>

              <div v-if="ediciones[p.id].abierto" class="prop-form">
                <div class="ing-field full">
                  <label>Nombre</label>
                  <input v-model="ediciones[p.id].nombre" />
                </div>
                <div class="ing-field">
                  <label>Marca</label>
                  <input v-model="ediciones[p.id].marca" />
                </div>
                <div class="ing-field">
                  <label>Precio total</label>
                  <input v-model.number="ediciones[p.id].precio_total" type="number" step="0.01" min="0" inputmode="decimal" />
                </div>
                <div class="ing-field">
                  <label>Cantidad</label>
                  <input v-model.number="ediciones[p.id].cantidad" type="number" step="any" min="0" inputmode="decimal" />
                </div>
                <div class="ing-field">
                  <label>Unidad</label>
                  <select v-model="ediciones[p.id].unidad">
                    <option v-for="u in UNIDADES" :key="u" :value="u">{{ u }}</option>
                  </select>
                </div>
                <div class="ing-field">
                  <label>Tipo</label>
                  <select v-model="ediciones[p.id].tipo">
                    <option value="precio">Precio</option>
                    <option value="oferta">Oferta</option>
                    <option value="promo_cantidad">Promo x cantidad</option>
                  </select>
                </div>
                <div v-if="ediciones[p.id].tipo !== 'precio'" class="ing-field">
                  <label>Días de oferta</label>
                  <input v-model.number="ediciones[p.id].dias_oferta" type="number" min="1" max="60" inputmode="numeric" />
                </div>
              </div>

              <div class="prop-botones">
                <button class="btn-rech" :disabled="procesando === p.id" @click="rechazar(p)">Rechazar</button>
                <button class="btn-apr" :disabled="procesando === p.id || !puedeAprobar(p)" @click="aprobar(p)">
                  {{ procesando === p.id ? 'Guardando…' : 'Aprobar' }}
                </button>
              </div>
            </template>

            <!-- Historial -->
            <div v-else-if="estadoVista === 'aprobada'" class="prop-final ok">
              {{ p.accion === 'actualizar' ? 'Actualizó un producto' : 'Creó un producto' }} · {{ fmtFecha(p.revisado_en) }}
            </div>
            <div v-else-if="estadoVista === 'rechazada'" class="prop-final err">
              Rechazada · {{ fmtFecha(p.revisado_en) }}
            </div>
          </article>
        </section>
      </template>
    </main>

    <!-- Imagen grande -->
    <Teleport to="body">
      <div v-if="imagenGrande" class="ing-lightbox" @click="imagenGrande = null">
        <img :src="imagenGrande" alt="Flyer" />
      </div>
    </Teleport>

    <!-- Toast -->
    <Teleport to="body">
      <Transition name="ing-toast">
        <div v-if="toast.show" class="ing-toast" :class="toast.tipo">{{ toast.msg }}</div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, onMounted } from 'vue'
import { navigateTo } from '#app'

// ─── Tipos ────────────────────────────────────────────────────
interface Comercio { id_comer: string; nombre_comer: string; [k: string]: any }
interface Candidato {
  id_prod: string
  nombre_prod: string
  marca_prod?: string | null
  unidad_prod?: string | null
  cantidad_prod?: number | null
  precio_prod?: string | number | null
  similitud?: number
}
interface Propuesta {
  id: string
  lote_id: string
  imagen_url: string | null
  origen: string
  comercio_leido: string | null
  id_comer: string | null
  nombre_leido: string
  marca_leida: string | null
  cantidad: number
  unidad: string
  precio_total: number
  precio_anterior_leido: number | null
  tipo: 'precio' | 'promo_cantidad' | 'oferta'
  condicion_oferta: string | null
  texto_original: string | null
  confianza: 'alta' | 'media' | 'baja'
  candidatos: Candidato[] | null
  accion: string | null
  id_prod_sugerido: string | null
  estado: string
  creado_en: string
  revisado_en?: string | null
}
interface Edicion {
  accion: 'actualizar' | 'crear'
  id_prod: string
  nombre: string
  marca: string
  cantidad: number
  unidad: string
  precio_total: number
  tipo: string
  dias_oferta: number
  abierto: boolean
}
interface Lote {
  lote_id: string
  imagen_url: string | null
  comercio_leido: string | null
  id_comer: string | null
  origen: string
  creado_en: string
  items: Propuesta[]
}

// ─── Constantes ───────────────────────────────────────────────
const MAX_IMAGENES = 6
const UNIDADES = ['Kilogramo', 'Gramos', 'Litro', 'Mililitro', 'Unidad', 'Docena', 'Paquete', 'Caja']
const UNIDADES_PROMO = ['Kilogramo', 'Litro', 'Unidad', 'Docena']   // igual que _campos_producto del backend
const ABREV: Record<string, string> = {
  Kilogramo: 'kg', Gramos: 'g', Litro: 'L', Mililitro: 'ml',
  Unidad: 'u', Docena: 'doc', Paquete: 'paq', Caja: 'caja'
}
const TIPO_LABEL: Record<string, string> = { precio: 'Precio', promo_cantidad: 'Promo x cantidad', oferta: 'Oferta' }
const ORIGEN_LABEL: Record<string, string> = { compartir: 'Compartido', estado: 'Estado', grupo: 'Grupo', bot: 'Bot' }
const VISTAS = [
  { id: 'pendiente' as const, label: 'Pendientes' },
  { id: 'aprobada' as const, label: 'Aprobadas' },
  { id: 'rechazada' as const, label: 'Rechazadas' },
]

const { api, apiUrl } = useApi()
const { volver } = useVolver('/admin')

// ─── Sesión ───────────────────────────────────────────────────
const user = ref<any>(null)
const isAdmin = computed(() => user.value?.rol === 'admin')
const sesionVencida = ref(false)

function getToken(): string {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? JSON.parse(stored).access_token || '' : ''
  } catch { return '' }
}

function statusDe(e: any): number | undefined {
  return e?.statusCode ?? e?.status ?? e?.response?.status
}

function errMsg(e: any): string {
  if (statusDe(e) === 401) {
    sesionVencida.value = true
    return 'Tu sesión venció. Volvé a iniciar sesión.'
  }
  return e?.data?.detail || e?.message || 'Error inesperado'
}

// ─── Toast ────────────────────────────────────────────────────
const toast = ref({ show: false, msg: '', tipo: 'ok' as 'ok' | 'error' })
let toastTimer: ReturnType<typeof setTimeout> | null = null
function aviso(msg: string, tipo: 'ok' | 'error' = 'ok') {
  toast.value = { show: true, msg, tipo }
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toast.value.show = false }, 4500)
}

// ─── Formato ──────────────────────────────────────────────────
function fmt(n: any): string {
  return Number(n || 0).toLocaleString('es-AR', { maximumFractionDigits: 2 })
}
function fmtCant(n: any): string {
  return Number(n || 0).toLocaleString('es-AR', { maximumFractionDigits: 3 })
}
function fmtFecha(s?: string | null): string {
  if (!s) return ''
  return new Date(s).toLocaleString('es-AR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// ─── Comercios ────────────────────────────────────────────────
const comercios = ref<Comercio[]>([])
const comercioPorId = computed(() => {
  const m: Record<string, Comercio> = {}
  for (const c of comercios.value) m[c.id_comer] = c
  return m
})

async function cargarComercios() {
  try {
    const r = await api<{ results: Comercio[] }>('/comercios')
    comercios.value = (r.results || []).slice().sort((a, b) => a.nombre_comer.localeCompare(b.nombre_comer))
  } catch (e) {
    console.error('Error cargando comercios:', e)
  }
}

// ─── Subida de imágenes ───────────────────────────────────────
interface ArchivoSel { file: File; url: string }
const archivos = ref<ArchivoSel[]>([])
const comercioSubida = ref('')
const origenSubida = ref('compartir')
const subiendo = ref(false)
const progreso = ref('')
const resultadosSubida = ref<any[]>([])

const textoBotonLeer = computed(() => {
  const n = archivos.value.length
  if (!n) return 'Leer imágenes'
  return n === 1 ? 'Leer 1 imagen' : `Leer ${n} imágenes`
})

function onArchivos(ev: Event) {
  const input = ev.target as HTMLInputElement
  const nuevos = Array.from(input.files || []).filter(f => f.type.startsWith('image/'))
  const lugar = MAX_IMAGENES - archivos.value.length
  if (nuevos.length > lugar) aviso(`Máximo ${MAX_IMAGENES} imágenes por vez`, 'error')
  for (const f of nuevos.slice(0, Math.max(0, lugar))) {
    archivos.value.push({ file: f, url: URL.createObjectURL(f) })
  }
  input.value = ''
}

function quitarArchivo(i: number) {
  URL.revokeObjectURL(archivos.value[i].url)
  archivos.value.splice(i, 1)
}

// Se manda de a UNA imagen por request: así se ve el progreso
// y ningún request queda colgado varios minutos.
async function leerFlyers() {
  if (!archivos.value.length || subiendo.value) return
  subiendo.value = true
  resultadosSubida.value = []
  const lista = [...archivos.value]
  let totalPropuestas = 0

  for (let i = 0; i < lista.length; i++) {
    const a = lista[i]
    progreso.value = `Leyendo ${i + 1} de ${lista.length}… (~30 s c/u)`
    const fd = new FormData()
    fd.append('files', a.file, a.file.name)
    fd.append('origen', origenSubida.value)
    if (comercioSubida.value) fd.append('id_comer', comercioSubida.value)
    try {
      // $fetch directo: useApi fuerza Content-Type JSON y rompe el multipart
      const r = await $fetch<{ resultados: any[] }>(`${apiUrl}/ingesta/imagenes`, {
        method: 'POST',
        body: fd,
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      for (const x of r.resultados || []) {
        resultadosSubida.value.push(x)
        if (x.ok) totalPropuestas += x.propuestas || 0
      }
      // ya procesada: se saca de la selección
      const idx = archivos.value.findIndex(s => s.url === a.url)
      if (idx >= 0) quitarArchivo(idx)
    } catch (e) {
      resultadosSubida.value.push({ archivo: a.file.name, ok: false, error: errMsg(e) })
      if (sesionVencida.value) break
    }
  }

  subiendo.value = false
  progreso.value = ''
  aviso(
    totalPropuestas ? `${totalPropuestas} propuesta(s) nuevas para revisar` : 'No se encontraron precios nuevos',
    totalPropuestas ? 'ok' : 'error'
  )
  if (totalPropuestas) {
    estadoVista.value = 'pendiente'
    await cargarPropuestas()
  }
}

// ─── Propuestas ───────────────────────────────────────────────
const estadoVista = ref<'pendiente' | 'aprobada' | 'rechazada'>('pendiente')
const propuestas = ref<Propuesta[]>([])
const cargando = ref(false)
const ediciones = reactive<Record<string, Edicion>>({})
const comercioLote = reactive<Record<string, string>>({})
const procesando = ref<string | null>(null)   // id de propuesta o lote_id
const imagenGrande = ref<string | null>(null)

const lotes = computed<Lote[]>(() => {
  const m = new Map<string, Lote>()
  for (const p of propuestas.value) {
    let l = m.get(p.lote_id)
    if (!l) {
      l = {
        lote_id: p.lote_id, imagen_url: p.imagen_url, comercio_leido: p.comercio_leido,
        id_comer: p.id_comer, origen: p.origen, creado_en: p.creado_en, items: []
      }
      m.set(p.lote_id, l)
    }
    l.items.push(p)
  }
  return [...m.values()]
})

function edicionInicial(p: Propuesta): Edicion {
  return {
    accion: p.accion === 'actualizar' && p.id_prod_sugerido ? 'actualizar' : 'crear',
    id_prod: p.id_prod_sugerido || '',
    nombre: p.nombre_leido || '',
    marca: p.marca_leida || '',
    cantidad: Number(p.cantidad) || 1,
    unidad: p.unidad || 'Unidad',
    precio_total: Number(p.precio_total) || 0,
    tipo: p.tipo,
    dias_oferta: 7,
    abierto: false
  }
}

async function cargarPropuestas() {
  cargando.value = true
  try {
    const r = await api<{ propuestas: Propuesta[] }>(`/ingesta/propuestas?estado=${estadoVista.value}&limit=300`)
    propuestas.value = r.propuestas || []
    for (const p of propuestas.value) {
      if (!ediciones[p.id]) ediciones[p.id] = edicionInicial(p)
      if (comercioLote[p.lote_id] === undefined) comercioLote[p.lote_id] = p.id_comer || ''
    }
    if (estadoVista.value === 'pendiente') {
      for (const l of lotes.value) {
        const id = comercioLote[l.lote_id]
        if (id && l.items.some(p => !usaCandidatos(p))) cargarProductosComercio(id)
      }
    }
  } catch (e) {
    aviso(errMsg(e), 'error')
  } finally {
    cargando.value = false
  }
}

function cambiarVista(v: 'pendiente' | 'aprobada' | 'rechazada') {
  if (estadoVista.value === v) return
  estadoVista.value = v
  propuestas.value = []
  cargarPropuestas()
}

function quitarPropuesta(id: string) {
  propuestas.value = propuestas.value.filter(x => x.id !== id)
  delete ediciones[id]
}

// ─── Productos del comercio (cuando no hay candidatos del backend) ──
const productosComercio = reactive<Record<string, Candidato[]>>({})
const cargandoProd = reactive<Record<string, boolean>>({})

async function cargarProductosComercio(id_comer: string) {
  if (!id_comer || productosComercio[id_comer] || cargandoProd[id_comer]) return
  const c = comercioPorId.value[id_comer]
  if (!c) return
  cargandoProd[id_comer] = true
  try {
    const r = await api<{ results: Candidato[] }>(`/products?comercio=${encodeURIComponent(c.nombre_comer)}&limit=5000`)
    productosComercio[id_comer] = r.results || []
  } catch (e) {
    console.error('Error cargando productos del comercio:', e)
  } finally {
    cargandoProd[id_comer] = false
  }
}

// Los candidatos del backend solo valen si el comercio del lote sigue siendo el que detectó
function usaCandidatos(p: Propuesta): boolean {
  return !!p.candidatos?.length && comercioLote[p.lote_id] === p.id_comer
}

function palabras(s: string): string[] {
  return (s || '')
    .normalize('NFD').replace(/[̀-ͯ]/g, '')
    .toLowerCase().replace(/[^a-z0-9 ]/g, ' ')
    .split(/\s+/).filter(w => w.length > 2)
}

function parecido(a: string, b: string): number {
  const A = palabras(a)
  if (!A.length) return 0
  const B = new Set(palabras(b))
  return A.filter(w => B.has(w)).length / A.length
}

function opcionesProducto(p: Propuesta): Candidato[] {
  if (usaCandidatos(p)) return p.candidatos || []
  const lista = productosComercio[comercioLote[p.lote_id]] || []
  const nombre = ediciones[p.id]?.nombre || p.nombre_leido
  return lista
    .map(x => ({ ...x, similitud: parecido(nombre, x.nombre_prod) }))
    .sort((a, b) => (b.similitud! - a.similitud!) || a.nombre_prod.localeCompare(b.nombre_prod))
}

function labelOpcion(o: Candidato): string {
  const marca = o.marca_prod ? ` · ${o.marca_prod}` : ''
  const sim = o.similitud ? ` (${Math.round(o.similitud * 100)}%)` : ''
  return `${o.nombre_prod}${marca} — $${fmt(o.precio_prod)}${sim}`
}

function productoElegido(p: Propuesta): Candidato | undefined {
  const id = ediciones[p.id]?.id_prod
  if (!id) return undefined
  return opcionesProducto(p).find(o => o.id_prod === id)
}

function onCambioComercioLote(lote: Lote) {
  const id = comercioLote[lote.lote_id]
  for (const p of lote.items) {
    const ed = ediciones[p.id]
    if (!ed) continue
    if (usaCandidatos(p)) {
      ed.accion = p.accion === 'actualizar' && p.id_prod_sugerido ? 'actualizar' : 'crear'
      ed.id_prod = p.id_prod_sugerido || ''
    } else {
      ed.accion = 'crear'
      ed.id_prod = ''
    }
  }
  if (id) cargarProductosComercio(id)
}

// Mismo cálculo que _campos_producto del backend: promo "2 kg x $3.500" → $1.750 el kg
function precioFinal(ed: Edicion): number {
  const total = Number(ed.precio_total) || 0
  const cant = Number(ed.cantidad) || 1
  if (ed.tipo === 'promo_cantidad' && UNIDADES_PROMO.includes(ed.unidad) && cant !== 1) {
    return Math.round((total / cant) * 100) / 100
  }
  return total
}

function resumen(p: Propuesta): { texto: string; alerta?: boolean; nota?: string } {
  const ed = ediciones[p.id]
  if (!ed) return { texto: '' }
  if (!comercioLote[p.lote_id]) return { texto: 'Elegí arriba el comercio del flyer', alerta: true }

  const nuevo = precioFinal(ed)
  const promo = ed.tipo !== 'precio'

  if (ed.accion === 'actualizar') {
    const o = productoElegido(p)
    if (!o) return { texto: 'Elegí qué producto actualizar', alerta: true }
    const actual = Number(o.precio_prod) || 0
    if (promo && actual > nuevo) {
      return { texto: `Oferta $${fmt(actual)} → $${fmt(nuevo)}`, nota: `El precio normal no cambia; la oferta vence en ${ed.dias_oferta || 7} días` }
    }
    if (Math.abs(actual - nuevo) < 0.005) {
      return { texto: `Precio confirmado $${fmt(nuevo)}`, nota: 'Solo se actualiza la fecha' }
    }
    const pct = actual ? Math.round(((nuevo - actual) / actual) * 100) : 0
    const ratio = actual ? nuevo / actual : 1
    const raro = actual > 0 && (ratio < 0.5 || ratio > 1.6)
    return {
      texto: `Precio $${fmt(actual)} → $${fmt(nuevo)} (${pct > 0 ? '+' : ''}${pct}%)`,
      alerta: raro,
      nota: raro ? 'Diferencia grande: revisá que sea el mismo producto' : ''
    }
  }

  const anterior = Number(p.precio_anterior_leido) || 0
  if (promo && anterior > nuevo) {
    return { texto: `Nuevo: ${ed.nombre} · $${fmt(anterior)}`, nota: `+ oferta a $${fmt(nuevo)} por ${ed.dias_oferta || 7} días` }
  }
  return {
    texto: `Nuevo: ${ed.nombre} · $${fmt(nuevo)}`,
    nota: promo ? 'Es promo pero no se leyó el precio normal: se guarda como precio común' : ''
  }
}

function puedeAprobar(p: Propuesta): boolean {
  const ed = ediciones[p.id]
  if (!ed || !comercioLote[p.lote_id]) return false
  if (!(Number(ed.precio_total) > 0)) return false
  if (ed.accion === 'actualizar' && !ed.id_prod) return false
  if (ed.accion === 'crear' && !ed.nombre.trim()) return false
  return true
}

async function aprobar(p: Propuesta) {
  if (!puedeAprobar(p)) return
  const ed = ediciones[p.id]
  procesando.value = p.id
  try {
    const r = await api<{ ok: boolean; detalle: string[] }>(`/ingesta/propuestas/${p.id}/aprobar`, {
      method: 'POST',
      body: {
        accion: ed.accion,
        id_prod: ed.accion === 'actualizar' ? ed.id_prod : null,
        id_comer: comercioLote[p.lote_id],
        nombre: ed.nombre.trim() || null,
        marca: ed.marca.trim() || null,
        cantidad: Number(ed.cantidad) || null,
        unidad: ed.unidad,
        precio_total: Number(ed.precio_total) || null,
        tipo: ed.tipo,
        dias_oferta: Number(ed.dias_oferta) || 7
      }
    })
    quitarPropuesta(p.id)
    // el producto creado/actualizado cambia la lista del comercio
    delete productosComercio[comercioLote[p.lote_id]]
    aviso((r.detalle && r.detalle.length ? r.detalle : ['Aprobada']).join(' · '))
  } catch (e) {
    if (statusDe(e) === 409) quitarPropuesta(p.id)
    aviso(errMsg(e), 'error')
  } finally {
    procesando.value = null
  }
}

async function rechazar(p: Propuesta) {
  procesando.value = p.id
  try {
    await api(`/ingesta/propuestas/${p.id}/rechazar`, { method: 'POST' })
    quitarPropuesta(p.id)
    aviso('Propuesta rechazada')
  } catch (e) {
    if (statusDe(e) === 409) quitarPropuesta(p.id)
    aviso(errMsg(e), 'error')
  } finally {
    procesando.value = null
  }
}

async function rechazarLote(lote: Lote) {
  if (!confirm(`¿Rechazar las ${lote.items.length} propuestas de este flyer?`)) return
  procesando.value = lote.lote_id
  let n = 0
  for (const p of [...lote.items]) {
    try {
      await api(`/ingesta/propuestas/${p.id}/rechazar`, { method: 'POST' })
      quitarPropuesta(p.id)
      n++
    } catch (e) {
      if (statusDe(e) === 409) { quitarPropuesta(p.id); continue }
      aviso(errMsg(e), 'error')
      break
    }
  }
  procesando.value = null
  if (n) aviso(`${n} propuesta(s) rechazadas`)
}

// ─── Inicio ───────────────────────────────────────────────────
onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch { /* ignore */ }
  }
  if (!isAdmin.value) return
  await cargarComercios()      // primero: se usa para resolver nombres de comercio
  await cargarPropuestas()
})
</script>

<style scoped>
.ing-page { min-height: 100vh; position: relative; }
.page-content { max-width: 560px; margin: 0 auto; padding: 1.25rem 1rem 3rem; position: relative; z-index: 1; }

/* Encabezado */
.ing-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.ing-back {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  color: var(--text-primary, #f4f4f5); cursor: pointer;
}
.ing-title { margin: 0; font-size: 1.35rem; font-weight: 800; color: var(--text-primary, #f4f4f5); }
.ing-sub { margin: 0.1rem 0 0; font-size: 0.85rem; color: var(--text-secondary, #a1a1aa); }

/* Cajas genéricas */
.ing-box {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 2rem 1rem; text-align: center; margin-bottom: 1rem;
  color: var(--text-secondary, #a1a1aa);
  background: var(--bg-card, rgba(255,255,255,0.04));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  border-radius: 16px;
}
.ing-box p { margin: 0; }
.ing-spinner {
  width: 26px; height: 26px; border-radius: 50%;
  border: 3px solid rgba(128,128,128,0.25); border-top-color: var(--brand-lime, #a3e635);
  animation: ing-spin 0.8s linear infinite;
}
.spin-sm {
  display: inline-block; width: 14px; height: 14px; border-radius: 50%;
  border: 2px solid rgba(255,255,255,0.35); border-top-color: #fff;
  animation: ing-spin 0.8s linear infinite;
}
@keyframes ing-spin { to { transform: rotate(360deg); } }

.ing-alerta {
  display: flex; align-items: center; justify-content: space-between; gap: 0.75rem;
  padding: 0.75rem 0.9rem; margin-bottom: 1rem; border-radius: 12px;
  background: rgba(251,113,133,0.12); border: 1px solid rgba(251,113,133,0.35);
  color: #fb7185; font-size: 0.85rem; font-weight: 600;
}
.ing-alerta button {
  padding: 0.4rem 0.8rem; border-radius: 8px; border: none; cursor: pointer;
  background: #fb7185; color: #fff; font-weight: 700; font-size: 0.8rem;
}

/* Tarjeta de subida */
.ing-card {
  padding: 1rem; margin-bottom: 1.25rem; border-radius: 16px;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  display: flex; flex-direction: column; gap: 0.75rem;
}
.ing-h2 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--text-primary, #f4f4f5); }

.ing-previews { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; }
.ing-prev { position: relative; aspect-ratio: 1; border-radius: 10px; overflow: hidden; background: rgba(128,128,128,0.15); }
.ing-prev img { width: 100%; height: 100%; object-fit: cover; display: block; }
.ing-prev button {
  position: absolute; top: 4px; right: 4px; width: 24px; height: 24px; border-radius: 50%;
  border: none; cursor: pointer; background: rgba(0,0,0,0.65); color: #fff; font-size: 0.75rem;
}

.ing-drop {
  display: flex; flex-direction: column; align-items: center; gap: 0.3rem;
  padding: 1.1rem 0.75rem; border-radius: 12px; cursor: pointer; text-align: center;
  border: 2px dashed var(--border-subtle, rgba(255,255,255,0.2));
  color: var(--text-secondary, #a1a1aa); font-size: 0.88rem; font-weight: 600;
}
.ing-drop small { font-weight: 400; font-size: 0.72rem; color: var(--text-muted, #71717a); }
.ing-drop.disabled { opacity: 0.5; cursor: not-allowed; }

.ing-row { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }
.ing-field { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.ing-field.full { grid-column: 1 / -1; }
.ing-field label { font-size: 0.72rem; font-weight: 600; color: var(--text-secondary, #a1a1aa); }
.ing-field input, .ing-field select, .lote-select, .prop-select {
  width: 100%; padding: 0.6rem 0.7rem; border-radius: 10px; font-size: 0.9rem;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-primary, #f4f4f5); font-family: inherit; min-width: 0;
}

.btn-main {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.8rem 1rem; border-radius: 12px; border: none; cursor: pointer;
  background: var(--brand-indigo, #2B2885); color: #fff; font-size: 0.95rem; font-weight: 700;
}
.btn-main:disabled { opacity: 0.55; cursor: not-allowed; }

.ing-res { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.4rem; }
.ing-res li {
  display: flex; flex-direction: column; gap: 0.1rem;
  padding: 0.55rem 0.7rem; border-radius: 10px; font-size: 0.8rem;
}
.ing-res li strong { font-size: 0.78rem; word-break: break-all; }
.ing-res li.ok { background: rgba(74,222,128,0.12); color: #22c55e; }
.ing-res li.err { background: rgba(251,113,133,0.12); color: #fb7185; }

/* Pestañas */
.ing-tabs { display: flex; gap: 0.4rem; margin-bottom: 1rem; }
.ing-tab {
  display: flex; align-items: center; gap: 0.35rem;
  padding: 0.55rem 0.85rem; border-radius: 10px; cursor: pointer;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  color: var(--text-secondary, #a1a1aa); font-size: 0.82rem; font-weight: 600;
}
.ing-tab.active { background: var(--brand-indigo, #2B2885); border-color: transparent; color: #fff; }
.ing-refresh { margin-left: auto; padding: 0.55rem 0.65rem; }
.ing-badge {
  min-width: 18px; height: 18px; padding: 0 5px; border-radius: 999px;
  display: inline-flex; align-items: center; justify-content: center;
  background: var(--brand-lime, #a3e635); color: #1a1a1a; font-size: 0.68rem; font-weight: 800;
}

/* Lote (flyer) */
.ing-lote {
  margin-bottom: 1.25rem; padding: 0.85rem; border-radius: 16px;
  background: var(--bg-card, rgba(255,255,255,0.04));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  display: flex; flex-direction: column; gap: 0.75rem;
}
.lote-head { display: flex; gap: 0.75rem; align-items: flex-start; }
.lote-img {
  width: 76px; height: 76px; border-radius: 10px; object-fit: cover; flex-shrink: 0;
  cursor: zoom-in; background: rgba(128,128,128,0.15);
}
.lote-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.3rem; }
.lote-leido { font-size: 0.88rem; font-weight: 700; color: var(--text-primary, #f4f4f5); }
.lote-meta { font-size: 0.72rem; color: var(--text-muted, #71717a); }
.lote-comer { font-size: 0.82rem; font-weight: 600; color: var(--text-secondary, #a1a1aa); }
.lote-select { padding: 0.5rem 0.6rem; font-size: 0.85rem; }
.lote-select.falta { border-color: #fbbf24; box-shadow: 0 0 0 2px rgba(251,191,36,0.2); }
.lote-rechazar {
  align-self: flex-start; background: none; border: none; padding: 0.1rem 0; cursor: pointer;
  color: #fb7185; font-size: 0.75rem; font-weight: 600; text-decoration: underline;
}
.lote-rechazar:disabled { opacity: 0.5; }

/* Propuesta */
.prop {
  padding: 0.8rem; border-radius: 12px; display: flex; flex-direction: column; gap: 0.5rem;
  background: rgba(128,128,128,0.08);
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
  border-left: 4px solid #4ade80;
}
.prop.conf-media { border-left-color: #fbbf24; }
.prop.conf-baja { border-left-color: #fb7185; }

.prop-top { display: flex; justify-content: space-between; gap: 0.5rem; align-items: baseline; }
.prop-titulo { min-width: 0; display: flex; flex-direction: column; }
.prop-titulo strong { font-size: 0.95rem; color: var(--text-primary, #f4f4f5); }
.prop-marca { font-size: 0.75rem; color: var(--text-secondary, #a1a1aa); }
.prop-precio { font-size: 1.1rem; font-weight: 800; color: var(--text-primary, #f4f4f5); white-space: nowrap; }

.prop-chips { display: flex; flex-wrap: wrap; gap: 0.3rem; }
.chip {
  padding: 0.15rem 0.5rem; border-radius: 999px; font-size: 0.68rem; font-weight: 600;
  background: rgba(128,128,128,0.15); color: var(--text-secondary, #a1a1aa);
}
.chip.tipo-oferta, .chip.tipo-promo_cantidad { background: rgba(251,146,60,0.18); color: #f97316; }
.conf-chip-alta { background: rgba(74,222,128,0.15) !important; color: #22c55e !important; }
.conf-chip-media { background: rgba(251,191,36,0.15) !important; color: #d97706 !important; }
.conf-chip-baja { background: rgba(251,113,133,0.15) !important; color: #e11d48 !important; }

.prop-texto { margin: 0; font-size: 0.75rem; font-style: italic; color: var(--text-muted, #71717a); }

.seg { display: grid; grid-template-columns: 1fr 1fr; gap: 0.3rem; }
.seg button {
  padding: 0.5rem; border-radius: 9px; cursor: pointer; font-size: 0.8rem; font-weight: 600;
  background: transparent; color: var(--text-secondary, #a1a1aa);
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
}
.seg button.on { background: var(--brand-indigo, #2B2885); border-color: transparent; color: #fff; }
.seg button:disabled { opacity: 0.45; cursor: not-allowed; }

.prop-select { font-size: 0.82rem; }

.prop-resumen {
  display: flex; flex-direction: column; gap: 0.15rem;
  padding: 0.5rem 0.65rem; border-radius: 9px; font-size: 0.85rem; font-weight: 700;
  background: rgba(74,222,128,0.1); color: #22c55e;
}
.prop-resumen small { font-weight: 500; font-size: 0.72rem; opacity: 0.9; }
.prop-resumen.alerta { background: rgba(251,191,36,0.14); color: #d97706; }

.prop-link {
  align-self: flex-start; background: none; border: none; padding: 0; cursor: pointer;
  color: var(--text-secondary, #a1a1aa); font-size: 0.78rem; font-weight: 600; text-decoration: underline;
}
.prop-form { display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem; }

.prop-botones { display: grid; grid-template-columns: 1fr 2fr; gap: 0.5rem; }
.btn-rech, .btn-apr {
  padding: 0.7rem; border-radius: 10px; cursor: pointer; font-size: 0.9rem; font-weight: 700;
}
.btn-rech { background: transparent; border: 1px solid rgba(251,113,133,0.45); color: #fb7185; }
.btn-apr { background: #16a34a; border: none; color: #fff; }
.btn-rech:disabled, .btn-apr:disabled { opacity: 0.45; cursor: not-allowed; }

.prop-final { font-size: 0.78rem; font-weight: 600; }
.prop-final.ok { color: #22c55e; }
.prop-final.err { color: #fb7185; }

/* Lightbox */
.ing-lightbox {
  position: fixed; inset: 0; z-index: 3000; background: rgba(0,0,0,0.88);
  display: flex; align-items: center; justify-content: center; padding: 1rem; cursor: zoom-out;
}
.ing-lightbox img { max-width: 100%; max-height: 100%; border-radius: 8px; }

/* Toast */
.ing-toast {
  position: fixed; bottom: 1.5rem; left: 50%; transform: translateX(-50%); z-index: 3100;
  max-width: 92vw; padding: 0.8rem 1.1rem; border-radius: 12px;
  font-size: 0.85rem; font-weight: 600; color: #fff; box-shadow: 0 8px 30px rgba(0,0,0,0.35);
}
.ing-toast.ok { background: #16a34a; }
.ing-toast.error { background: #e11d48; }
.ing-toast-enter-active, .ing-toast-leave-active { transition: all 0.25s ease; }
.ing-toast-enter-from, .ing-toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(16px); }

@media (max-width: 380px) {
  .ing-row, .prop-form { grid-template-columns: 1fr; }
}
</style>
