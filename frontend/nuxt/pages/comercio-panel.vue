<template>
  <div class="comercio-panel-page">
    <DynamicBackground />

    <main class="page-content">
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div>
          <h1 class="page-title">Mis productos</h1>
          <p class="page-subtitle">{{ miComercio?.nombre_comer || 'Panel de comercio' }}</p>
        </div>
      </header>

      <!-- ESTADO: pendiente de aprobación -->
      <div v-if="estadoCargado && !estaVerificado" class="pendiente-box animate-fade-in-up">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
        </svg>
        <h2>Tu cuenta está en revisión</h2>
        <p v-if="motivoRechazo">
          Tu solicitud fue rechazada. Motivo: {{ motivoRechazo }}
        </p>
        <p v-else>
          El administrador todavía no aprobó tu acceso para cargar productos. Te avisaremos por email cuando esté listo.
        </p>
        <button class="btn-secondary" @click="navigateTo('/dashboard')">Volver al inicio</button>
      </div>

      <!-- PANEL APROBADO -->
      <template v-else-if="estadoCargado && estaVerificado">

        <!-- Mi competitividad -->
        <section class="competitividad-section animate-fade-in-up">
          <button class="competitividad-toggle" @click="toggleCompetitividad">
            <span class="competitividad-titulo">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
              Mi competitividad
            </span>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" :style="{ transform: mostrarCompetitividad ? 'rotate(180deg)' : 'none' }" class="competitividad-chevron"><path d="m6 9 6 6 6-6"/></svg>
          </button>

          <div v-if="mostrarCompetitividad" class="competitividad-body">
            <div class="competitividad-rango">
              <span class="competitividad-rango-label">Comparar contra precios de los últimos:</span>
              <div class="rango-chips">
                <button
                  v-for="opt in rangoOpciones"
                  :key="opt.value"
                  class="rango-chip"
                  :class="{ active: diasSeleccionados === opt.value }"
                  @click="cambiarRango(opt.value)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </div>

            <div v-if="loadingCompetitividad" class="competitividad-loading">
              <div class="loading-spinner" />
              <span>Comparando tus precios...</span>
            </div>

            <div v-else-if="competitividad.length === 0" class="competitividad-empty">
              <p>Todavía no hay datos para comparar.</p>
            </div>

            <div v-else class="competitividad-tabla">
              <div class="comp-row comp-row--header">
                <span>Producto</span>
                <span>Tu precio</span>
                <span>Más barato</span>
                <span>Más caro</span>
                <span>Posición</span>
              </div>
              <div v-for="item in competitividad" :key="item.id_prod" class="comp-item">
                <div class="comp-row">
                  <span class="comp-nombre">{{ item.nombre_prod }}</span>
                  <span class="comp-precio">${{ formatPrice(item.mi_precio) }}</span>
                  <span class="comp-precio">{{ item.precio_min_mercado !== null ? '$' + formatPrice(item.precio_min_mercado) : '—' }}</span>
                  <span class="comp-precio">{{ item.precio_max_mercado !== null ? '$' + formatPrice(item.precio_max_mercado) : '—' }}</span>
                  <span class="comp-badge" :class="`comp-badge--${item.posicion}`">
                    {{
                      item.posicion === 'mas_barato' ? 'Más barato' :
                      item.posicion === 'mas_caro' ? 'Más caro' :
                      item.posicion === 'medio' ? 'En el medio' :
                      'Único'
                    }}
                    <template v-if="item.pct_vs_min !== null && item.pct_vs_min > 0">
                      · +{{ item.pct_vs_min }}%
                    </template>
                  </span>
                </div>
                <p v-if="item.tiene_dato_antiguo" class="comp-aviso-antiguo">
                  ⚠️ Este producto tiene más de 7 días de antigüedad en el sistema
                  <span v-if="item.fecha_mas_antigua" class="comp-fecha">
                    (dato más viejo usado: {{ formatFechaCorta(item.fecha_mas_antigua) }})
                  </span>
                </p>
              </div>
            </div>
          </div>
        </section>

        <div class="toolbar animate-fade-in-up stagger-1">
          <div class="search-bar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input v-model="searchQuery" placeholder="Buscar mis productos..." />
          </div>
          <button class="btn-primary" @click="abrirModalNuevo">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M12 5v14M5 12h14"/></svg>
            Nuevo
          </button>
        </div>

        <div v-if="loadingProductos" class="state-box">
          <div class="loading-spinner" />
          <span>Cargando productos...</span>
        </div>

        <div v-else-if="productosFiltrados.length === 0" class="state-box">
          <p>Todavía no cargaste productos.</p>
          <button class="btn-primary" @click="abrirModalNuevo">Cargar el primero</button>
        </div>

        <div v-else class="productos-lista animate-fade-in-up stagger-2">
          <article v-for="p in productosFiltrados" :key="p.id_prod" class="producto-item" :class="{ 'producto-pausado': !p.activo_prod }">
            <img :src="p.imagen_prod || '/images/avatar_default.png'" class="item-thumb" @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'" />
            <div class="item-info">
              <span class="item-name">{{ p.nombre_prod }}</span>
              <span class="item-meta">{{ p.marca_prod }} · {{ p.cate_prod }}</span>
              <span class="item-price">${{ formatPrice(p.precio_prod) }}</span>
              <span v-if="ofertaDeProducto(p.id_prod)" class="item-oferta-badge">
                🏷️ En oferta hasta {{ formatFechaCorta(ofertaDeProducto(p.id_prod)!.fecha_fin) }}
              </span>
            </div>
            <button
              class="item-oferta-toggle"
              :class="{ 'tiene-oferta': !!ofertaDeProducto(p.id_prod) }"
              :aria-label="ofertaDeProducto(p.id_prod) ? 'Editar oferta' : 'Convertir en oferta'"
              :title="ofertaDeProducto(p.id_prod) ? 'Editar oferta' : 'Convertir en oferta'"
              @click="abrirModalOferta(p)"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20.59 13.41 11 3.83A2 2 0 0 0 9.59 3.24L3 3a1 1 0 0 0-1 1l.24 6.59a2 2 0 0 0 .59 1.41l9.58 9.58a2 2 0 0 0 2.82 0l6.36-6.36a2 2 0 0 0 0-2.81Z"/>
                <circle cx="7.5" cy="7.5" r="1.5"/>
              </svg>
            </button>
            <button
              class="item-pause-toggle"
              :class="{ 'is-paused': !p.activo_prod }"
              :disabled="pausandoId === p.id_prod"
              :aria-label="p.activo_prod ? 'Pausar producto (sin stock)' : 'Reactivar producto'"
              :title="p.activo_prod ? 'Pausar — sin stock' : 'Pausado — tocar para reactivar'"
              @click="togglePausa(p)"
            >
              <svg v-if="p.activo_prod" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="6" y="4" width="4" height="16" rx="1"/><rect x="14" y="4" width="4" height="16" rx="1"/></svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"/></svg>
            </button>
            <button class="item-edit" @click="editarProducto(p)" aria-label="Editar">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.12 2.12 0 0 1 3 3L12 15l-4 1 1-4Z"/></svg>
            </button>
          </article>
        </div>
      </template>

      <div v-else class="state-box">
        <div class="loading-spinner" />
        <span>Verificando tu cuenta...</span>
      </div>
    </main>

    <!-- MODAL: Nuevo/Editar producto -->
    <Teleport to="body">
      <div v-if="modalOpen" class="modal-overlay" @click.self="cerrarModal">
        <div class="modal-container">
          <div class="modal-header">
            <h3>{{ editandoId ? 'Editar producto' : 'Nuevo producto' }}</h3>
            <button class="modal-close" @click="cerrarModal">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>
          <form class="modal-body form-grid" @submit.prevent="guardarProducto">
            <div class="form-group full">
              <label>Nombre *</label>
              <input v-model="form.nombre_prod" required placeholder="Ej: Crema de Leche" />
            </div>

            <div class="form-group">
              <label>Categoría *</label>
              <select v-model="form.cate_prod" required>
                <option value="">Seleccionar...</option>
                <option v-for="cat in categorias" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
              </select>
            </div>

            <div class="form-group">
              <label>Marca *</label>
              <input v-model="form.marca_prod" required placeholder="Ej: Tonadita" />
            </div>

            <div class="form-group">
              <label>Precio *</label>
              <input v-model="form.precio_prod" type="number" step="0.01" required placeholder="1499.00" />
            </div>

            <div class="form-group">
              <label>Cantidad del envase</label>
              <input v-model="form.cantidad_prod" type="number" placeholder="200" />
            </div>

            <div class="form-group">
              <label>Unidad de medida</label>
              <select v-model="form.unidad_prod">
                <option v-for="m in medidas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
              </select>
            </div>

            <div class="form-group full">
              <label>Código de barras (EAN) — opcional</label>
              <input v-model="form.ean_prod" type="text" placeholder="Ej: 7791234567890" inputmode="numeric" />
              <p class="form-hint">Si tu producto tiene código de barras, lo podés escribir o pegar acá. No es obligatorio.</p>
            </div>

            <!-- Comercio: fijo, no editable — siempre el del usuario logueado -->
            <div class="form-group full">
              <label>Comercio</label>
              <input :value="miComercio?.nombre_comer" disabled class="input-disabled" />
              <p class="form-hint">Tus productos se cargan automáticamente a tu comercio</p>
            </div>

            <div class="form-group full">
              <label>Descripción</label>
              <textarea v-model="form.describe_prod" rows="2" placeholder="Descripción..."></textarea>
            </div>

            <!-- Selector de imagen real — sube directo al bucket -->
            <div class="form-group full">
              <label>Foto del producto</label>
              <div class="image-upload-wrap">
                <div v-if="form.imagen_prod" class="image-preview">
                  <img :src="form.imagen_prod" />
                  <button type="button" class="image-remove" @click="form.imagen_prod = ''">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
                  </button>
                </div>
                <label v-else class="image-upload-btn">
                  <input type="file" accept="image/jpeg,image/png,image/webp" @change="subirImagen" hidden :disabled="subiendoImagen" />
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
                  <span>{{ subiendoImagen ? 'Subiendo...' : 'Subir foto' }}</span>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input v-model="form.activo_prod" type="checkbox" />
                <span>Activo</span>
              </label>
            </div>

            <p v-if="errorMsg" class="error-msg full">{{ errorMsg }}</p>

            <div class="form-actions full">
              <button type="button" class="btn-secondary" @click="cerrarModal">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="guardando">
                {{ guardando ? 'Guardando...' : 'Guardar' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- MODAL: Crear/editar oferta -->
    <Teleport to="body">
      <div v-if="modalOfertaOpen" class="modal-overlay" @click.self="cerrarModalOferta">
        <div class="modal-container modal-oferta">
          <div class="modal-header">
            <h3>{{ ofertaEditandoId ? 'Editar oferta' : 'Convertir en oferta' }}</h3>
            <button class="modal-close" @click="cerrarModalOferta">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
            </button>
          </div>
          <form class="modal-body form-grid" @submit.prevent="guardarOferta">
            <div class="form-group full">
              <label>Producto</label>
              <input :value="productoParaOferta?.nombre_prod" disabled class="input-disabled" />
            </div>

            <div class="form-group">
              <label>Precio normal</label>
              <input :value="formatPrice(formOferta.precio_normal)" disabled class="input-disabled" />
              <p class="form-hint">El precio de tu producto no cambia — esto no lo modifica.</p>
            </div>

            <div class="form-group">
              <label>Precio oferta *</label>
              <input v-model="formOferta.precio_oferta" type="number" step="0.01" required placeholder="Ej: 1199.00" />
            </div>

            <div class="form-group full" v-if="descuentoCalculado !== null">
              <p class="form-hint descuento-hint">
                Descuento: <strong>{{ descuentoCalculado }}%</strong> sobre el precio normal
              </p>
            </div>

            <div class="form-group full">
              <label>Hasta cuándo dura la oferta *</label>
              <input v-model="formOferta.fecha_fin" type="date" required :min="fechaMinima" />
              <p class="form-hint">Pasada esta fecha, la oferta deja de mostrarse automáticamente. El producto sigue intacto.</p>
            </div>

            <p v-if="errorMsgOferta" class="error-msg full">{{ errorMsgOferta }}</p>

            <div class="form-actions full">
              <button
                v-if="ofertaEditandoId"
                type="button"
                class="btn-secondary btn-eliminar-oferta"
                :disabled="guardandoOferta"
                @click="eliminarOferta"
              >
                Quitar oferta
              </button>
              <button type="button" class="btn-secondary" @click="cerrarModalOferta">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="guardandoOferta">
                {{ guardandoOferta ? 'Guardando...' : 'Guardar oferta' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo, useRuntimeConfig } from '#app'

interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  marca_prod: string
  precio_prod: string
  cantidad_prod?: number
  unidad_prod?: string
  comercio_prod: string
  describe_prod?: string | null
  imagen_prod: string | null
  activo_prod: boolean
  ean_prod?: string | null
}

const config = useRuntimeConfig()

const estadoCargado = ref(false)
const estaVerificado = ref(false)
const motivoRechazo = ref('')
const miComercio = ref<{ id_comer: string; nombre_comer: string } | null>(null)

const productos = ref<Producto[]>([])
const loadingProductos = ref(true)
const searchQuery = ref('')

// Mi competitividad — comparación de precios vs el resto de los comercios
interface ItemCompetitividad {
  id_prod: string
  nombre_prod: string
  mi_precio: number
  precio_min_mercado: number | null
  precio_max_mercado: number | null
  pct_vs_min: number | null
  total_comercios: number
  posicion: 'mas_barato' | 'mas_caro' | 'medio' | 'unico'
  fecha_mas_antigua: string | null
  tiene_dato_antiguo: boolean
}
const mostrarCompetitividad = ref(false)
const loadingCompetitividad = ref(false)
const competitividad = ref<ItemCompetitividad[]>([])
let competitividadCargada = false

// Rango de días elegido por el comerciante para comparar precios
const rangoOpciones = [
  { label: '7 días', value: 7 },
  { label: '15 días', value: 15 },
  { label: '30 días', value: 30 },
  { label: '60 días', value: 60 },
]
const diasSeleccionados = ref(15)
const categorias = ref<{ id: number; nombre: string }[]>([])
const medidas = ref<{ id: number; nombre: string }[]>([])

const modalOpen = ref(false)
const editandoId = ref<string | null>(null)
const guardando = ref(false)
const subiendoImagen = ref(false)
const errorMsg = ref('')

const form = ref<Partial<Producto>>({
  nombre_prod: '', cate_prod: '', marca_prod: '', precio_prod: '',
  cantidad_prod: 1, unidad_prod: 'Unidad', describe_prod: '', imagen_prod: '', activo_prod: true, ean_prod: ''
})

// ─── Ofertas ──────────────────────────────────────────────────
interface Oferta {
  id: string
  id_prod: string
  precio_normal: number
  precio_oferta: number
  descuento_pct: number | null
  fecha_inicio: string
  fecha_fin: string
  activa: boolean
}

const misOfertas = ref<Oferta[]>([])
const modalOfertaOpen = ref(false)
const ofertaEditandoId = ref<string | null>(null)
const productoParaOferta = ref<Producto | null>(null)
const guardandoOferta = ref(false)
const errorMsgOferta = ref('')
const formOferta = ref<{ precio_normal: number; precio_oferta: string; fecha_fin: string }>({
  precio_normal: 0, precio_oferta: '', fecha_fin: ''
})

const fechaMinima = computed(() => new Date().toISOString().slice(0, 10))

const descuentoCalculado = computed(() => {
  const normal = Number(formOferta.value.precio_normal)
  const oferta = Number(formOferta.value.precio_oferta)
  if (!normal || !oferta || oferta >= normal) return null
  return Math.round(((normal - oferta) / normal) * 100)
})

// Encuentra la oferta vigente de un producto, si tiene una — usado para
// mostrar el badge "En oferta" y decidir si el modal abre en modo edición
function ofertaDeProducto(idProd: string): Oferta | null {
  const ahora = new Date()
  return misOfertas.value.find(o =>
    o.id_prod === idProd && o.activa && new Date(o.fecha_fin) >= ahora
  ) || null
}

function abrirModalOferta(producto: Producto) {
  errorMsgOferta.value = ''
  productoParaOferta.value = producto
  const existente = ofertaDeProducto(producto.id_prod)

  if (existente) {
    ofertaEditandoId.value = existente.id
    formOferta.value = {
      precio_normal: Number(producto.precio_prod),
      precio_oferta: String(existente.precio_oferta),
      fecha_fin: existente.fecha_fin.slice(0, 10)
    }
  } else {
    ofertaEditandoId.value = null
    formOferta.value = {
      precio_normal: Number(producto.precio_prod),
      precio_oferta: '',
      fecha_fin: ''
    }
  }
  modalOfertaOpen.value = true
}

function cerrarModalOferta() {
  modalOfertaOpen.value = false
  ofertaEditandoId.value = null
  productoParaOferta.value = null
  errorMsgOferta.value = ''
}

async function cargarMisOfertas() {
  if (!miComercio.value) return
  try {
    const res = await $fetch<{ count: number; results: Oferta[] }>(
      `${config.public.apiBase}/ofertas/historial`,
      { params: { comercio: miComercio.value.nombre_comer, incluir_vencidas: false } }
    )
    misOfertas.value = res.results || []
  } catch (err) {
    console.error('Error cargando ofertas:', err)
  }
}

async function guardarOferta() {
  if (!productoParaOferta.value) return

  const precioOferta = Number(formOferta.value.precio_oferta)
  const precioNormal = Number(formOferta.value.precio_normal)

  if (!formOferta.value.precio_oferta || !formOferta.value.fecha_fin) {
    errorMsgOferta.value = 'Completá el precio de oferta y la fecha de finalización'
    return
  }
  if (precioOferta >= precioNormal) {
    errorMsgOferta.value = 'El precio de oferta debe ser menor al precio normal'
    return
  }

  guardandoOferta.value = true
  errorMsgOferta.value = ''
  try {
    const token = getToken()
    // fecha_fin con hora de fin del día, para que la oferta sea válida todo ese día
    const fechaFinISO = `${formOferta.value.fecha_fin}T23:59:59`

    const payload = {
      id_prod: productoParaOferta.value.id_prod,
      precio_normal: precioNormal,
      precio_oferta: precioOferta,
      fecha_fin: fechaFinISO,
    }

    if (ofertaEditandoId.value) {
      await $fetch(`${config.public.apiBase}/ofertas/${ofertaEditandoId.value}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
        body: payload
      })
    } else {
      await $fetch(`${config.public.apiBase}/ofertas`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: payload
      })
    }

    cerrarModalOferta()
    await cargarMisOfertas()
  } catch (err: any) {
    errorMsgOferta.value = err?.data?.detail || 'No se pudo guardar la oferta'
  } finally {
    guardandoOferta.value = false
  }
}

async function eliminarOferta() {
  if (!ofertaEditandoId.value) return
  guardandoOferta.value = true
  errorMsgOferta.value = ''
  try {
    const token = getToken()
    await $fetch(`${config.public.apiBase}/ofertas/${ofertaEditandoId.value}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` }
    })
    cerrarModalOferta()
    await cargarMisOfertas()
  } catch (err: any) {
    errorMsgOferta.value = err?.data?.detail || 'No se pudo quitar la oferta'
  } finally {
    guardandoOferta.value = false
  }
}

function getToken() {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? JSON.parse(stored).access_token || '' : ''
  } catch { return '' }
}

function formatPrice(p: string | number) {
  return Number(p).toLocaleString('es-AR')
}

function formatFechaCorta(fechaIso: string): string {
  const d = new Date(fechaIso)
  return d.toLocaleDateString('es-AR', { day: '2-digit', month: 'short' })
}

function toggleCompetitividad() {
  mostrarCompetitividad.value = !mostrarCompetitividad.value
  if (mostrarCompetitividad.value && !competitividadCargada) {
    cargarCompetitividad()
  }
}

async function cargarCompetitividad() {
  loadingCompetitividad.value = true
  try {
    const token = getToken()
    const res = await $fetch<{ count: number; results: ItemCompetitividad[] }>(
      `${config.public.apiBase}/mi-comercio/competitividad`,
      {
        headers: { Authorization: `Bearer ${token}` },
        params: { dias: diasSeleccionados.value }
      }
    )
    competitividad.value = res.results || []
    competitividadCargada = true
  } catch (err) {
    console.error('Error cargando competitividad:', err)
  } finally {
    loadingCompetitividad.value = false
  }
}

function cambiarRango(dias: number) {
  if (diasSeleccionados.value === dias) return
  diasSeleccionados.value = dias
  cargarCompetitividad()
}

const productosFiltrados = computed(() => {
  if (!searchQuery.value.trim()) return productos.value
  const q = searchQuery.value.toLowerCase()
  return productos.value.filter(p =>
    p.nombre_prod.toLowerCase().includes(q) || p.marca_prod.toLowerCase().includes(q)
  )
})

async function cargarEstadoComercio() {
  try {
    const token = getToken()
    const res = await $fetch<any>(`${config.public.apiBase}/mi-comercio`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    estaVerificado.value = !!res.comercio_verificado_user
    motivoRechazo.value = res.motivo_rechazo_comercio || ''
    miComercio.value = res.comercio || null
  } catch (err) {
    console.error('Error cargando estado de comercio:', err)
  } finally {
    estadoCargado.value = true
  }
}

async function cargarProductos() {
  if (!miComercio.value) return
  loadingProductos.value = true
  try {
    const res = await $fetch<{ count: number; results: Producto[] }>(
      `${config.public.apiBase}/products/search`,
      { params: { q: miComercio.value.nombre_comer, limit: 100 } }
    )
    productos.value = (res.results || []).filter(p => p.comercio_prod === miComercio.value?.nombre_comer)
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loadingProductos.value = false
  }
}

async function cargarCategoriasYMedidas() {
  try {
    const [catsRes, medidasRes] = await Promise.all([
      $fetch<any[]>(`${config.public.apiBase}/categorias`).catch(() => []),
      $fetch<any[]>(`${config.public.apiBase}/medidas`).catch(() => [])
    ])
    categorias.value = (catsRes || []).map((c: any) => ({ id: c.id_cate, nombre: c.nombre_cate }))
    medidas.value = medidasRes || []
  } catch (err) {
    console.error('Error cargando categorías/medidas:', err)
  }
}

function abrirModalNuevo() {
  editandoId.value = null
  errorMsg.value = ''
  form.value = {
    nombre_prod: '', cate_prod: '', marca_prod: '', precio_prod: '',
    cantidad_prod: 1, unidad_prod: 'Unidad', describe_prod: '', imagen_prod: '', activo_prod: true, ean_prod: ''
  }
  modalOpen.value = true
}

function editarProducto(p: Producto) {
  editandoId.value = p.id_prod
  errorMsg.value = ''
  form.value = { ...p }
  modalOpen.value = true
}

function cerrarModal() {
  modalOpen.value = false
  editandoId.value = null
  errorMsg.value = ''
}

async function subirImagen(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  subiendoImagen.value = true
  errorMsg.value = ''
  try {
    const token = getToken()
    const formData = new FormData()
    formData.append('file', file)

    const res = await $fetch<{ url: string }>(`${config.public.apiBase}/upload-imagen-producto`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: formData
    })
    form.value.imagen_prod = res.url
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo subir la imagen'
  } finally {
    subiendoImagen.value = false
  }
}

const pausandoId = ref<string | null>(null)

async function togglePausa(producto: Producto) {
  pausandoId.value = producto.id_prod
  errorMsg.value = ''
  const nuevoEstado = !producto.activo_prod
  try {
    const token = getToken()
    await $fetch(`${config.public.apiBase}/products/${producto.id_prod}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
      body: {
        nombre_prod: producto.nombre_prod,
        cate_prod: producto.cate_prod,
        marca_prod: producto.marca_prod,
        precio_prod: String(producto.precio_prod),
        cantidad_prod: producto.cantidad_prod || 1,
        unidad_prod: producto.unidad_prod || 'Unidad',
        comercio_prod: producto.comercio_prod,
        describe_prod: producto.describe_prod || null,
        imagen_prod: producto.imagen_prod || null,
        activo_prod: nuevoEstado,
      }
    })
    // Actualizar localmente sin recargar toda la lista
    producto.activo_prod = nuevoEstado
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo cambiar el estado del producto'
  } finally {
    pausandoId.value = null
  }
}

async function guardarProducto() {
  if (!miComercio.value) {
    errorMsg.value = 'No se encontró tu comercio asignado'
    return
  }
  guardando.value = true
  errorMsg.value = ''
  try {
    const token = getToken()
    const payload = {
      nombre_prod: form.value.nombre_prod?.trim(),
      cate_prod: form.value.cate_prod?.trim(),
      marca_prod: form.value.marca_prod?.trim(),
      precio_prod: String(form.value.precio_prod || 0),
      cantidad_prod: Number(form.value.cantidad_prod) || 1,
      unidad_prod: form.value.unidad_prod || 'Unidad',
      comercio_prod: miComercio.value.nombre_comer,
      describe_prod: form.value.describe_prod?.trim() || null,
      imagen_prod: form.value.imagen_prod?.trim() || null,
      activo_prod: !!form.value.activo_prod,
      ean_prod: form.value.ean_prod?.trim() || null,
    }

    if (!payload.nombre_prod || !payload.cate_prod || !payload.marca_prod || !payload.precio_prod) {
      errorMsg.value = 'Completá todos los campos requeridos (*)'
      guardando.value = false
      return
    }

    if (editandoId.value) {
      await $fetch(`${config.public.apiBase}/products/${editandoId.value}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
        body: payload
      })
    } else {
      await $fetch(`${config.public.apiBase}/products`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` },
        body: payload
      })
    }

    cerrarModal()
    await cargarProductos()
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'Error al guardar el producto'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarEstadoComercio()
  if (estaVerificado.value) {
    await Promise.all([cargarProductos(), cargarCategoriasYMedidas(), cargarMisOfertas()])
  }
})
</script>

<style scoped>
.comercio-panel-page {
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page-content {
  position: relative; z-index: 2;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.25rem;
  max-width: 560px; margin: 0 auto;
  padding-bottom: 6rem;
}
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }

.page-header { display: flex; align-items: center; gap: 0.875rem; }
.back-btn {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg-card-hover); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s; flex-shrink: 0;
}
.back-btn:hover { border-color: var(--border-glow); color: var(--text-primary); }
.page-title { font-size: 1.35rem; font-weight: 700; margin: 0; }
.page-subtitle { color: var(--text-secondary); font-size: 0.82rem; margin: 0; }

.pendiente-box, .state-box {
  display: flex; flex-direction: column; align-items: center; gap: 0.875rem;
  text-align: center; padding: 3rem 1.5rem;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
}
.pendiente-box svg { color: #fbbf24; }
.pendiente-box h2 { font-size: 1.1rem; font-weight: 700; margin: 0; }
.pendiente-box p { font-size: 0.85rem; color: var(--text-secondary); margin: 0; }

.loading-spinner {
  width: 28px; height: 28px;
  border: 2px solid var(--border-subtle); border-top-color: var(--accent-gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}

/* ─── MI COMPETITIVIDAD ─── */
.competitividad-section {
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md); overflow: hidden;
}
.competitividad-toggle {
  width: 100%; display: flex; align-items: center; justify-content: space-between;
  padding: 0.875rem 1rem; background: none; border: none; cursor: pointer;
}
.competitividad-titulo {
  display: flex; align-items: center; gap: 0.5rem;
  color: var(--text-primary); font-size: 0.9rem; font-weight: 700;
}
.competitividad-titulo svg { color: #a78bfa; }
.competitividad-chevron { color: var(--text-muted); transition: transform 0.2s; flex-shrink: 0; }
.competitividad-body { padding: 0 1rem 1rem; border-top: 1px solid var(--border-subtle); }

.competitividad-rango { padding: 0.75rem 0 0.5rem; display: flex; flex-direction: column; gap: 0.5rem; }
.competitividad-rango-label { font-size: 0.72rem; color: var(--text-muted); }
.rango-chips { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.rango-chip {
  padding: 0.3rem 0.7rem; border-radius: 999px;
  border: 1px solid var(--border-subtle); background: var(--bg-card);
  color: var(--text-secondary); font-size: 0.72rem; font-weight: 600;
  cursor: pointer; transition: all 0.2s;
}
.rango-chip:hover { border-color: var(--border-glow); color: var(--text-primary); }
.rango-chip.active {
  background: rgba(167, 139, 250, 0.18); border-color: rgba(167, 139, 250, 0.4);
  color: #c4b5fd;
}
.competitividad-loading {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 1.25rem 0; color: var(--text-secondary); font-size: 0.85rem;
}
.competitividad-empty { padding: 1.25rem 0; color: var(--text-secondary); font-size: 0.85rem; text-align: center; }

.competitividad-tabla { display: flex; flex-direction: column; padding-top: 0.75rem; }
.comp-item { border-bottom: 1px solid var(--border-subtle); }
.comp-item:last-child { border-bottom: none; }
.comp-row {
  display: grid; grid-template-columns: 1.6fr 0.9fr 0.9fr 0.9fr 1fr;
  gap: 0.5rem; padding: 0.625rem 0.25rem; align-items: center;
  font-size: 0.78rem;
}
.comp-row--header {
  font-size: 0.68rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: 0.03em; color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}
.comp-aviso-antiguo {
  margin: -0.25rem 0 0.625rem 0.25rem;
  font-size: 0.7rem;
  color: #fbbf24;
  display: flex; flex-wrap: wrap; gap: 0.25rem; align-items: center;
}
.comp-fecha { color: var(--text-muted); font-weight: 500; }
.comp-nombre { color: var(--text-primary); font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.comp-precio { color: var(--text-secondary); font-weight: 600; }
.comp-badge {
  display: inline-flex; align-items: center; justify-content: center;
  padding: 0.2rem 0.5rem; border-radius: 999px;
  font-size: 0.68rem; font-weight: 700; text-align: center;
}
.comp-badge--mas_barato { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.comp-badge--mas_caro { background: rgba(251, 113, 133, 0.15); color: #fb7185; }
.comp-badge--medio { background: rgba(251, 191, 36, 0.15); color: #fbbf24; }
.comp-badge--unico { background: var(--bg-card-hover); color: var(--text-muted); }

@media (max-width: 480px) {
  .comp-row { grid-template-columns: 1.4fr 0.8fr 0.8fr; }
  .comp-row > span:nth-child(4) { display: none; }
}

.toolbar { display: flex; gap: 0.75rem; }
.search-bar {
  flex: 1; display: flex; align-items: center; gap: 0.625rem;
  padding: 0.7rem 1rem; background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.search-bar svg { color: var(--text-muted); flex-shrink: 0; }
.search-bar input { flex: 1; background: none; border: none; outline: none; color: var(--text-primary); font-size: 0.9rem; }

.btn-primary {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.7rem 1.1rem; border-radius: var(--radius-md);
  background: var(--accent-gold-dim); border: 1px solid var(--border-glow);
  color: var(--accent-gold); font-size: 0.88rem; font-weight: 700;
  cursor: pointer; transition: all 0.2s; white-space: nowrap;
}
.btn-primary:hover:not(:disabled) { background: var(--bg-card-hover); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secondary {
  padding: 0.7rem 1.1rem; border-radius: var(--radius-md);
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); font-size: 0.88rem; cursor: pointer; transition: all 0.2s;
}
.btn-secondary:hover { background: var(--bg-card-hover); }

.productos-lista { display: flex; flex-direction: column; gap: 0.625rem; }
.producto-item {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.75rem; background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  transition: opacity 0.2s;
}
.producto-pausado { opacity: 0.55; }
.producto-pausado .item-thumb { filter: grayscale(0.6); }
.item-thumb { width: 48px; height: 48px; border-radius: var(--radius-sm); object-fit: cover; background: var(--bg-card-hover); flex-shrink: 0; }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 0.125rem; min-width: 0; }
.item-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.item-meta { font-size: 0.75rem; color: var(--text-secondary); }
.item-price { font-size: 0.85rem; font-weight: 700; color: var(--accent-gold); }
.item-oferta-badge {
  font-size: 0.68rem; font-weight: 700; color: #fb923c;
  margin-top: 0.1rem;
}
.item-oferta-toggle {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: var(--bg-card-hover); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.item-oferta-toggle:hover { border-color: rgba(251, 146, 60, 0.5); color: #fb923c; }
.item-oferta-toggle.tiene-oferta {
  background: rgba(251, 146, 60, 0.15); border-color: rgba(251, 146, 60, 0.35);
  color: #fb923c;
}
.item-pause-toggle {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: rgba(74, 222, 128, 0.12); border: 1px solid rgba(74, 222, 128, 0.3);
  color: #4ade80; display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.item-pause-toggle:hover:not(:disabled) { background: rgba(74, 222, 128, 0.22); }
.item-pause-toggle.is-paused {
  background: rgba(251, 191, 36, 0.12); border-color: rgba(251, 191, 36, 0.3);
  color: #fbbf24;
}
.item-pause-toggle.is-paused:hover:not(:disabled) { background: rgba(251, 191, 36, 0.22); }
.item-pause-toggle:disabled { opacity: 0.5; cursor: wait; }
.item-edit {
  width: 36px; height: 36px; border-radius: 50%; flex-shrink: 0;
  background: var(--bg-card-hover); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.item-edit:hover { border-color: var(--border-glow); color: var(--accent-gold); }

/* ─── MODAL ─── */
.modal-overlay {
  position: fixed; inset: 0; z-index: 999;
  background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 1.25rem;
  overflow-y: auto;
}
.modal-container {
  background: var(--bg-card); backdrop-filter: blur(20px);
  border: 1px solid var(--border-glow); border-radius: 20px;
  width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border-subtle);
}
.modal-header h3 { margin: 0; font-size: 1.05rem; font-weight: 700; color: var(--text-primary); }
.modal-close {
  width: 32px; height: 32px; border-radius: 50%; background: var(--bg-card-hover);
  border: none; color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer;
}
.modal-body { padding: 1.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group { display: flex; flex-direction: column; gap: 0.4rem; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 0.78rem; font-weight: 600; color: var(--text-secondary); }
.form-group input, .form-group select, .form-group textarea {
  padding: 0.65rem 0.875rem; border-radius: var(--radius-sm);
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  color: var(--text-primary); font-size: 0.88rem; outline: none; transition: border-color 0.2s;
}
.form-group select option {
  background: #1a1a1f;
  color: #f5f0eb;
}
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--border-glow); }
.form-group textarea { resize: vertical; font-family: inherit; }
.input-disabled { opacity: 0.6; cursor: not-allowed; }
.form-hint { font-size: 0.72rem; color: var(--text-muted); margin: 0; }
.descuento-hint { color: #fb923c; font-size: 0.82rem; }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; flex-direction: row; cursor: pointer; }
.checkbox-label input { width: auto; }

.image-upload-wrap { display: flex; }
.image-upload-btn {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem;
  width: 100%; padding: 1.5rem; border-radius: var(--radius-md);
  border: 1.5px dashed var(--border-subtle); background: var(--bg-input);
  color: var(--text-secondary); font-size: 0.85rem; cursor: pointer; transition: all 0.2s;
}
.image-upload-btn:hover { border-color: var(--border-glow); color: var(--accent-gold); }
.image-preview { position: relative; width: 100%; }
.image-preview img { width: 100%; max-height: 180px; object-fit: contain; border-radius: var(--radius-md); background: var(--bg-input); }
.image-remove {
  position: absolute; top: 8px; right: 8px;
  width: 28px; height: 28px; border-radius: 50%;
  background: rgba(0,0,0,0.6); border: none; color: #fff;
  display: flex; align-items: center; justify-content: center; cursor: pointer;
}

.error-msg {
  color: #fb7185; font-size: 0.82rem;
  background: rgba(251,113,133,0.1); border: 1px solid rgba(251,113,133,0.25);
  border-radius: var(--radius-sm); padding: 0.625rem 0.875rem; margin: 0;
}

.form-actions { display: flex; gap: 0.75rem; margin-top: 0.5rem; flex-wrap: wrap; }
.form-actions .btn-secondary, .form-actions .btn-primary { flex: 1; justify-content: center; min-width: 110px; }
.btn-eliminar-oferta {
  color: #fb7185; border-color: rgba(251, 113, 133, 0.3);
}
.btn-eliminar-oferta:hover:not(:disabled) { background: rgba(251, 113, 133, 0.1); }
</style>