<template>
  <div class="lista-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <button class="back-btn" @click="navigateTo('/listas')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m15 18-6-6 6-6"/>
          </svg>
        </button>
        <div class="header-center">
          <h1 v-if="!editandoNombre" class="page-title" @click="editandoNombre = true">
            {{ lista?.nombre_lista || 'Cargando...' }}
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="edit-icon">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </h1>
          <input
            v-else
            v-model="nombreEditado"
            ref="inputNombre"
            class="title-input"
            @blur="guardarNombre"
            @keydown.enter="guardarNombre"
            @keydown.esc="cancelarNombre"
          />
          <p class="page-subtitle">{{ items.length }} producto{{ items.length !== 1 ? 's' : '' }} · Total: <strong>{{ formatPrecio(totalLista) }}</strong></p>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="state-box animate-fade-in-up">
        <div class="loading-spinner" />
        <span>Cargando lista...</span>
      </div>

      <template v-else>

        <!-- BOTÓN OPTIMIZAR -->
        <button v-if="items.length > 0" class="btn-optimizar animate-fade-in-up stagger-1" @click="mostrarOptimizador = true">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
          Optimizar compra
        </button>

        <!-- BARRA DE PROGRESO -->
        <div v-if="items.length > 0" class="progress-bar animate-fade-in-up stagger-1">
          <div class="progress-info">
            <span>{{ itemsComprados }} de {{ items.length }} comprados</span>
            <span class="progress-pct">{{ Math.round(itemsComprados / items.length * 100) }}%</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: `${itemsComprados / items.length * 100}%` }" />
          </div>
        </div>

        <!-- FILTROS DE ESTADO -->
        <div v-if="items.length > 0" class="filter-chips animate-fade-in-up stagger-1">
          <button
            v-for="f in filtros"
            :key="f.value"
            class="filter-chip"
            :class="{ active: filtroActivo === f.value }"
            @click="filtroActivo = f.value"
          >
            {{ f.icon }} {{ f.label }}
            <span class="chip-count">{{ contarPorEstado(f.value) }}</span>
          </button>
        </div>

        <!-- LISTA DE ITEMS -->
        <div v-if="itemsFiltrados.length > 0" class="items-lista animate-fade-in-up stagger-2">
          <div
            v-for="item in itemsFiltrados"
            :key="item.id_item"
            class="item-card"
            :class="item.estado"
          >
            <!-- Estado toggle -->
            <button class="item-estado-btn" @click="ciclarEstado(item)" :title="item.estado">
              <span v-if="item.estado === 'pendiente'">□</span>
              <span v-else-if="item.estado === 'agregado'">✓</span>
              <span v-else>🛒</span>
            </button>

            <!-- Info producto -->
            <div class="item-info">
              <p class="item-nombre">{{ item.nombre_item }}</p>
              <div class="item-meta">
                <span class="item-cantidad">{{ item.cantidad }} {{ item.unidad }}</span>
                <span v-if="item.marca" class="item-marca">· {{ item.marca }}</span>
                <span class="item-prioridad" :class="item.prioridad">{{ item.prioridad }}</span>
              </div>
              <p v-if="item.notas" class="item-notas">💬 {{ item.notas }}</p>
              <p v-if="item.precio_referencia" class="item-precio">
                ${{ Number(item.precio_referencia).toLocaleString('es-AR') }}
              </p>
            </div>

            <!-- Acciones -->
            <div class="item-actions">
              <button class="item-edit-btn" @click="abrirEditarItem(item)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
                </svg>
              </button>
              <button class="item-delete-btn" @click="eliminarItem(item.id_item)">
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
                </svg>
              </button>
            </div>
          </div>
        </div>

        <div v-else-if="items.length === 0" class="state-box animate-fade-in-up stagger-2">
          <div class="empty-icon">📋</div>
          <h3>Lista vacía</h3>
          <p>Agregá productos desde el catálogo</p>
        </div>

        <!-- BOTÓN AGREGAR PRODUCTO -->
        <button class="btn-agregar animate-fade-in-up stagger-3" @click="mostrarBuscador = true">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 5v14M5 12h14"/>
          </svg>
          Agregar producto
        </button>

      </template>
    </main>

    <!-- MODAL BUSCADOR DE PRODUCTOS -->
    <Teleport to="body">
      <div v-if="mostrarBuscador" class="modal-overlay modal-buscador-overlay" @click.self="mostrarBuscador = false">
        <div class="modal-card modal-large">
          <div class="modal-header">
            <h3 class="modal-title">Agregar producto</h3>
            <button class="modal-close" @click="mostrarBuscador = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>

          <!-- Buscador -->
          <div class="search-bar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input
              v-model="queryProducto"
              type="text"
              placeholder="Buscar por nombre, marca..."
              class="search-input"
              @input="buscarProductos"
            />
          </div>

          <!-- Resultados -->
          <div v-if="loadingProductos" class="state-box-mini">
            <div class="loading-spinner-sm" />
          </div>
          <div v-else-if="productosBuscados.length > 0" class="productos-lista">
            <div
              v-for="prod in productosBuscados"
              :key="prod.id_prod"
              class="producto-row"
              @click="seleccionarProducto(prod)"
            >
              <img
                :src="prod.imagen_prod || '/images/avatar_default.png'"
                :alt="prod.nombre_prod"
                class="prod-img"
                @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'"
              />
              <div class="prod-info">
                <p class="prod-nombre">{{ prod.nombre_prod }}</p>
                <p class="prod-meta">{{ prod.marca_prod }} · {{ prod.provee_prod }}</p>
              </div>
              <span class="prod-precio">${{ Number(prod.precio_prod).toLocaleString('es-AR') }}</span>
            </div>
          </div>
          <div v-else-if="queryProducto.length >= 2" class="state-box-mini">
            <p>Sin resultados</p>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- MODAL CONFIGURAR ITEM -->
    <Teleport to="body">
      <div v-if="itemEditando" class="modal-overlay modal-config-overlay" @click.self="itemEditando = null">
        <div class="modal-card">
          <h3 class="modal-title">{{ itemEditando.id_item ? 'Editar' : 'Agregar' }}: {{ itemEditando.nombre_item }}</h3>

          <div class="form-row">
            <div class="field-group">
              <label class="field-label">Cantidad</label>
              <input v-model.number="itemEditando.cantidad" type="number" min="1" class="field-input" />
            </div>
            <div class="field-group">
              <label class="field-label">Unidad</label>
              <input v-model="itemEditando.unidad" type="text" class="field-input" placeholder="kg, lt, un..." />
            </div>
          </div>

          <div class="field-group">
            <label class="field-label">Marca</label>
            <input v-model="itemEditando.marca" type="text" class="field-input" placeholder="Opcional" />
          </div>

          <div class="field-group">
            <label class="field-label">Prioridad</label>
            <div class="priority-chips">
              <button
                v-for="p in prioridades"
                :key="p.value"
                class="priority-chip"
                :class="{ active: itemEditando.prioridad === p.value, [`p-${p.value}`]: true }"
                @click="itemEditando.prioridad = p.value"
              >
                {{ p.label }}
              </button>
            </div>
          </div>

          <div class="field-group">
            <label class="field-label">Notas</label>
            <input v-model="itemEditando.notas" type="text" class="field-input" placeholder="Sin azúcar, integral..." />
          </div>

          <div class="field-group">
            <label class="toggle-label">
              <div>
                <span class="field-label" style="margin:0">Acepta sustitución</span>
                <p class="toggle-desc">Si no hay, aceptar otra marca</p>
              </div>
              <div class="toggle-switch" :class="{ on: itemEditando.acepta_sustitucion }" @click="itemEditando.acepta_sustitucion = !itemEditando.acepta_sustitucion">
                <div class="toggle-thumb" />
              </div>
            </label>
          </div>

          <div class="modal-actions">
            <button class="btn-cancel" @click="itemEditando = null">Cancelar</button>
            <button class="btn-gold" @click="guardarItem" :disabled="guardandoItem">
              <div v-if="guardandoItem" class="btn-spinner" />
              {{ guardandoItem ? 'Guardando...' : 'Guardar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- MODAL OPTIMIZADOR -->
    <Teleport to="body">
      <div v-if="mostrarOptimizador" class="modal-overlay" @click.self="mostrarOptimizador = false">
        <div class="modal-card modal-optimizador">
          <div class="modal-header">
            <h3 class="modal-title">🛒 Optimizador de compra</h3>
            <button class="modal-close" @click="mostrarOptimizador = false">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>

          <div v-if="loadingOptimizador" class="state-box-mini">
            <div class="loading-spinner-sm" />
            <span>Analizando precios...</span>
          </div>

          <template v-else-if="optimizacion">
            <!-- Resumen -->
            <div class="opt-resumen">
              <div v-if="optimizacion.mejor_opcion" class="opt-card opt-mejor">
                <span class="opt-label">Mejor opción única</span>
                <span class="opt-proveedor">{{ optimizacion.mejor_opcion.proveedor }}</span>
                <span class="opt-total">${{ formatPrecio(optimizacion.mejor_opcion.total) }}</span>
                <span v-if="optimizacion.mejor_opcion.ahorro_vs_peor > 0" class="opt-ahorro">
                  Ahorrás ${{ formatPrecio(optimizacion.mejor_opcion.ahorro_vs_peor) }} vs el más caro
                </span>
                <span v-if="!optimizacion.mejor_opcion.completo" class="opt-incompleto">
                  ⚠️ No tiene todos los productos
                </span>
              </div>

              <div v-if="optimizacion.division_sugerida" class="opt-card opt-division">
                <span class="opt-label">Dividiendo en {{ optimizacion.division_sugerida.cantidad_proveedores }} comercios</span>
                <span class="opt-total opt-total-division">${{ formatPrecio(optimizacion.division_sugerida.total) }}</span>
                <span v-if="optimizacion.division_sugerida.ahorro_vs_unico > 0" class="opt-ahorro opt-ahorro-division">
                  🔥 Ahorrás ${{ formatPrecio(optimizacion.division_sugerida.ahorro_vs_unico) }} extra
                </span>
              </div>
            </div>

            <!-- Tabla comparativa -->
            <div class="opt-tabla">
              <h4>Comparación por proveedor</h4>
              <div class="opt-tabla-header">
                <span>Proveedor</span>
                <span>Total</span>
                <span>Productos</span>
              </div>
              <div
                v-for="(prov, idx) in optimizacion.proveedores"
                :key="prov.proveedor"
                class="opt-tabla-row"
                :class="{ 'opt-ganador': idx === 0 }"
              >
                <span class="opt-nombre">{{ prov.proveedor }}</span>
                <span class="opt-monto">${{ formatPrecio(prov.total) }}</span>
                <span class="opt-cantidad">{{ prov.items_encontrados }}/{{ optimizacion.items_count }}</span>
              </div>
            </div>

            <!-- Detalle de división -->
            <div v-if="optimizacion.division_sugerida" class="opt-division-detalle">
              <h4>🛍️ Compra dividida sugerida</h4>
              <div v-for="div in optimizacion.division_sugerida.proveedores" :key="div.proveedor" class="opt-division-grupo">
                <div class="opt-division-header">
                  <span>{{ div.proveedor }}</span>
                  <span>${{ formatPrecio(div.subtotal) }}</span>
                </div>
                <div v-for="item in div.items" :key="item.nombre" class="opt-division-item">
                  <span>{{ item.nombre }} x{{ item.cantidad }}</span>
                  <span>${{ formatPrecio(item.precio_unitario) }} c/u</span>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'
import { navigateTo, useRoute } from '#app'

interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  provee_prod: string
  imagen_prod: string | null
  unidad_prod: string
  cantidad_prod: number
}

interface Item {
  id_item: string
  id_lista: string
  id_prod: string | null
  nombre_item: string
  cantidad: number
  unidad: string
  marca: string
  acepta_sustitucion: boolean
  prioridad: string
  estado: string
  notas: string
  precio_referencia: number | null
  producto?: Producto
}

interface Lista {
  id_lista: string
  nombre_lista: string
  fecha_modificacion: string
  items: Item[]
}

const { api } = useApi()
const route = useRoute()
const id = route.params.id as string

const loading = ref(true)
const lista = ref<Lista | null>(null)
const items = ref<Item[]>([])

const filtroActivo = ref('todos')
const filtros = [
  { value: 'todos',     label: 'Todos',    icon: '📋' },
  { value: 'pendiente', label: 'Pendiente',icon: '□'  },
  { value: 'agregado',  label: 'Agregado', icon: '✓'  },
  { value: 'comprado',  label: 'Comprado', icon: '🛒' },
]

const prioridades = [
  { value: 'urgente',    label: '🔴 Urgente'   },
  { value: 'importante', label: '🟡 Importante'},
  { value: 'opcional',   label: '⚪ Opcional'  },
]

// Editar nombre
const editandoNombre = ref(false)
const nombreEditado = ref('')
const inputNombre = ref<HTMLInputElement>()

// Buscador de productos
const mostrarBuscador = ref(false)
const queryProducto = ref('')
const productosBuscados = ref<Producto[]>([])
const loadingProductos = ref(false)
let debounceTimer: ReturnType<typeof setTimeout>

// Item editando
const itemEditando = ref<any>(null)
const guardandoItem = ref(false)

// Optimizador
const mostrarOptimizador = ref(false)
const loadingOptimizador = ref(false)
const optimizacion = ref<any>(null)

// Computed
const itemsFiltrados = computed(() => {
  if (filtroActivo.value === 'todos') return items.value
  return items.value.filter(i => i.estado === filtroActivo.value)
})

const itemsComprados = computed(() => items.value.filter(i => i.estado === 'comprado').length)

const totalLista = computed(() =>
  items.value.reduce((sum, i) => sum + (i.precio_referencia ? Number(i.precio_referencia) * i.cantidad : 0), 0)
)

function contarPorEstado(estado: string) {
  if (estado === 'todos') return items.value.length
  return items.value.filter(i => i.estado === estado).length
}

function formatPrecio(n: number) {
  return n > 0 ? `${n.toLocaleString('es-AR')}` : '—'
}

// Cargar lista
async function cargar() {
  loading.value = true
  try {
    const data = await api<Lista>(`/listas/${id}`)
    lista.value = data
    items.value = data.items || []
    nombreEditado.value = data.nombre_lista
  } catch (err: any) {
    console.error('Error cargando lista:', err)
  } finally {
    loading.value = false
  }
}

// Editar nombre lista
async function guardarNombre() {
  if (!nombreEditado.value.trim() || !lista.value) return
  editandoNombre.value = false
  try {
    await api(`/listas/${id}`, { method: 'PUT', body: { nombre_lista: nombreEditado.value.trim() } })
    lista.value.nombre_lista = nombreEditado.value.trim()
  } catch {}
}

function cancelarNombre() {
  editandoNombre.value = false
  nombreEditado.value = lista.value?.nombre_lista || ''
}

watch(editandoNombre, async (val) => {
  if (val) { await nextTick(); inputNombre.value?.focus() }
})

// Ciclar estado del item
const estadoSig: Record<string, string> = { pendiente: 'agregado', agregado: 'comprado', comprado: 'pendiente' }

async function ciclarEstado(item: Item) {
  const nuevoEstado = estadoSig[item.estado] || 'pendiente'
  item.estado = nuevoEstado
  try {
    await api(`/items/${item.id_item}`, { method: 'PUT', body: { estado: nuevoEstado } })
  } catch {}
}

// Buscar productos
function buscarProductos() {
  clearTimeout(debounceTimer)
  if (queryProducto.value.length < 2) { productosBuscados.value = []; return }
  debounceTimer = setTimeout(async () => {
    loadingProductos.value = true
    try {
      const res = await api<{ results: Producto[] }>(`/products?q=${encodeURIComponent(queryProducto.value)}&limit=20`)
      productosBuscados.value = res.results || []
    } catch {}
    finally { loadingProductos.value = false }
  }, 300)
}

// Seleccionar producto para agregar
function seleccionarProducto(prod: Producto) {
  mostrarBuscador.value = false
  queryProducto.value = ''
  productosBuscados.value = []
  itemEditando.value = {
    id_item: null,
    id_prod: prod.id_prod,
    nombre_item: prod.nombre_prod,
    cantidad: 1,
    unidad: prod.unidad_prod || 'un',
    marca: prod.marca_prod || '',
    acepta_sustitucion: true,
    prioridad: 'importante',
    estado: 'pendiente',
    notas: '',
    precio_referencia: Number(prod.precio_prod) || null,
  }
}

// Abrir editar item existente
function abrirEditarItem(item: Item) {
  itemEditando.value = { ...item }
}

// Guardar item (crear o actualizar)
async function guardarItem() {
  if (!itemEditando.value) return
  guardandoItem.value = true
  try {
    if (!itemEditando.value.id_item) {
      // Crear
      const res = await api<{ data: Item }>(`/listas/${id}/items`, {
        method: 'POST',
        body: itemEditando.value
      })
      items.value.push(res.data)
    } else {
      // Actualizar
      const { id_item, id_lista, id_prod, nombre_item, ...updateData } = itemEditando.value
      await api(`/items/${itemEditando.value.id_item}`, { method: 'PUT', body: updateData })
      const idx = items.value.findIndex(i => i.id_item === itemEditando.value.id_item)
      if (idx !== -1) Object.assign(items.value[idx], itemEditando.value)
    }
    itemEditando.value = null
  } catch (err: any) {
    console.error('Error guardando item:', err)
  } finally {
    guardandoItem.value = false
  }
}

// Eliminar item
async function eliminarItem(itemId: string) {
  try {
    await api(`/items/${itemId}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id_item !== itemId)
  } catch {}
}

// Optimizador
async function cargarOptimizacion() {
  loadingOptimizador.value = true
  try {
    const data = await api(`/listas/${id}/optimize`)
    optimizacion.value = data
  } catch (err) {
    console.error('Error cargando optimización:', err)
  } finally {
    loadingOptimizador.value = false
  }
}

watch(mostrarOptimizador, (val) => {
  if (val && !optimizacion.value) {
    cargarOptimizacion()
  }
})

onMounted(cargar)
</script>

<style scoped>
.lista-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255,255,255,0.03);
  --bg-card-hover: rgba(255,255,255,0.06);
  --border-subtle: rgba(255,255,255,0.08);
  --border-glow: rgba(232,196,160,0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245,240,235,0.6);
  --text-muted: rgba(245,240,235,0.35);
  --accent-gold: #e8c4a0;
  --accent-error: #fb7185;
  --accent-success: #34d399;
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.bg-gradient {
  position: fixed; inset: 0;
  background: radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232,196,160,0.08), transparent),
              linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 100%);
  z-index: 0;
}
.bg-noise {
  position: fixed; inset: 0; opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  z-index: 1; pointer-events: none;
}
.page-content {
  position: relative; z-index: 2;
  padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1rem;
  max-width: 560px; margin: 0 auto;
  padding-bottom: 5rem;
}

.btn-optimizar {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.12), rgba(52, 211, 153, 0.04));
  border: 1px solid rgba(52, 211, 153, 0.25);
  border-radius: var(--radius-md);
  color: #34d399;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s;
}
.btn-optimizar:hover {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.2), rgba(52, 211, 153, 0.08));
  transform: translateY(-1px);
}

.modal-optimizador {
  max-height: 80vh;
  overflow-y: auto;
  border-radius: var(--radius-lg) var(--radius-lg) 0 0;
}
@media (min-width: 640px) {
  .modal-optimizador {
    border-radius: var(--radius-lg);
    max-height: 75vh;
  }
}

.opt-resumen {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.opt-card {
  padding: 1rem;
  border-radius: var(--radius-md);
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.opt-mejor {
  background: rgba(52, 211, 153, 0.08);
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.opt-division {
  background: rgba(232, 196, 160, 0.08);
  border: 1px solid rgba(232, 196, 160, 0.2);
}

.opt-label {
  font-size: 0.72rem;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.opt-proveedor {
  font-size: 0.9rem;
  font-weight: 600;
  color: #34d399;
}

.opt-total {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--text-primary);
}

.opt-total-division {
  color: var(--accent-gold);
}

.opt-ahorro {
  font-size: 0.78rem;
  color: #34d399;
}

.opt-ahorro-division {
  color: var(--accent-gold);
  font-weight: 600;
}

.opt-incompleto {
  font-size: 0.75rem;
  color: #fb7185;
}

.opt-tabla {
  margin-bottom: 1.25rem;
}

.opt-tabla h4, .opt-division-detalle h4 {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.opt-tabla-header, .opt-tabla-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 1rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.8rem;
}

.opt-tabla-header {
  color: var(--text-muted);
  font-weight: 600;
  border-bottom: 1px solid var(--border-subtle);
}

.opt-tabla-row {
  color: var(--text-secondary);
  border-bottom: 1px solid rgba(255,255,255,0.03);
}

.opt-tabla-row.opt-ganador {
  background: rgba(52, 211, 153, 0.06);
  border-radius: var(--radius-sm);
}

.opt-nombre { color: var(--text-primary); font-weight: 500; }
.opt-monto { font-weight: 600; color: var(--accent-gold); }
.opt-cantidad { color: var(--text-muted); }

.opt-division-detalle {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.opt-division-grupo {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.75rem;
}

.opt-division-header {
  display: flex;
  justify-content: space-between;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border-subtle);
}

.opt-division-item {
  display: flex;
  justify-content: space-between;
  font-size: 0.78rem;
  color: var(--text-secondary);
  padding: 0.2rem 0;
}

@media (max-width: 480px) {
  .opt-resumen { grid-template-columns: 1fr; }
}

@keyframes fadeInUp { from { opacity:0; transform:translateY(20px); } to { opacity:1; transform:translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }

/* HEADER */
.page-header { display:flex; align-items:flex-start; gap:0.875rem; padding:0.5rem 0; }
.back-btn {
  width:40px; height:40px; border-radius:50%; flex-shrink:0; margin-top:0.2rem;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.25s;
}
.back-btn:hover { background:rgba(255,255,255,0.08); border-color:var(--border-glow); color:var(--text-primary); }
.header-center { flex:1; min-width:0; }
.page-title {
  font-size:1.4rem; font-weight:700; margin:0; letter-spacing:-0.02em;
  display:flex; align-items:center; gap:0.5rem; cursor:pointer;
}
.edit-icon { color:var(--text-muted); flex-shrink:0; }
.title-input {
  font-size:1.4rem; font-weight:700; letter-spacing:-0.02em;
  background:transparent; border:none; border-bottom:2px solid var(--accent-gold);
  color:var(--text-primary); outline:none; width:100%;
}
.page-subtitle { color:var(--text-secondary); font-size:0.82rem; margin:0.25rem 0 0; }
.page-subtitle strong { color:var(--accent-gold); }

/* PROGRESS */
.progress-bar {
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-md); padding:0.875rem 1rem;
  display:flex; flex-direction:column; gap:0.5rem;
}
.progress-info { display:flex; justify-content:space-between; font-size:0.8rem; color:var(--text-secondary); }
.progress-pct { color:var(--accent-gold); font-weight:600; }
.progress-track { height:4px; background:rgba(255,255,255,0.06); border-radius:999px; overflow:hidden; }
.progress-fill { height:100%; background:var(--accent-gold); border-radius:999px; transition:width 0.4s ease; }

/* FILTROS */
.filter-chips { display:flex; gap:0.5rem; flex-wrap:wrap; }
.filter-chip {
  display:flex; align-items:center; gap:0.375rem;
  padding:0.375rem 0.75rem; border-radius:999px;
  border:1px solid var(--border-subtle);
  background:rgba(255,255,255,0.02);
  color:var(--text-secondary); font-size:0.78rem; font-weight:500;
  cursor:pointer; transition:all 0.2s;
}
.filter-chip.active {
  background:rgba(232,196,160,0.12); border-color:rgba(232,196,160,0.3);
  color:var(--accent-gold);
}
.chip-count {
  background:rgba(255,255,255,0.08); border-radius:999px;
  padding:0.1rem 0.4rem; font-size:0.7rem;
}

/* ITEMS */
.items-lista { display:flex; flex-direction:column; gap:0.5rem; }
.item-card {
  display:flex; align-items:center; gap:0.875rem;
  padding:0.875rem 1rem;
  background:var(--bg-card); border:1px solid var(--border-subtle);
  border-radius:var(--radius-md); transition:all 0.2s;
}
.item-card.comprado { opacity:0.55; }
.item-card.comprado .item-nombre { text-decoration:line-through; }
.item-estado-btn {
  width:32px; height:32px; border-radius:8px; flex-shrink:0;
  background:rgba(255,255,255,0.05); border:1px solid var(--border-subtle);
  color:var(--text-primary); font-size:1rem;
  display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.2s;
}
.item-estado-btn:hover { background:rgba(232,196,160,0.1); border-color:var(--border-glow); }
.item-info { flex:1; min-width:0; }
.item-nombre { color:var(--text-primary); font-size:0.9rem; font-weight:600; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

.item-meta { display:flex; align-items:center; gap:0.5rem; margin-top:0.25rem; flex-wrap:wrap; }
.item-cantidad { color:var(--text-secondary); font-size:0.78rem; }
.item-marca { color:var(--text-muted); font-size:0.78rem; }
.item-prioridad {
  font-size:0.7rem; font-weight:600; text-transform:uppercase; letter-spacing:0.03em;
  padding:0.15rem 0.4rem; border-radius:4px;
}
.item-prioridad.urgente { background:rgba(251,113,133,0.12); color:#fb7185; }
.item-prioridad.importante { background:rgba(232,196,160,0.12); color:var(--accent-gold); }
.item-prioridad.opcional { background:rgba(255,255,255,0.06); color:var(--text-muted); }
.item-notas { color:var(--text-muted); font-size:0.75rem; margin:0.15rem 0 0; }
.item-precio { color:var(--accent-gold); font-size:0.85rem; font-weight:600; margin:0.15rem 0 0; }
.item-actions { display:flex; gap:0.375rem; }
.item-edit-btn, .item-delete-btn {
  width:28px; height:28px; border-radius:6px;
  display:flex; align-items:center; justify-content:center;
  background:transparent; border:1px solid var(--border-subtle);
  color:var(--text-muted); cursor:pointer; transition:all 0.2s;
}
.item-edit-btn:hover { background:rgba(232,196,160,0.1); color:var(--accent-gold); border-color:rgba(232,196,160,0.3); }
.item-delete-btn:hover { background:rgba(251,113,133,0.1); color:var(--accent-error); border-color:rgba(251,113,133,0.3); }

/* STATES */
.state-box {
  display:flex; flex-direction:column; align-items:center; gap:0.75rem;
  padding:2.5rem 1rem; text-align:center;
}
.state-box span { color:var(--text-secondary); font-size:0.9rem; }
.state-box h3 { margin:0; font-size:1.1rem; color:var(--text-primary); }
.state-box p { margin:0; color:var(--text-muted); font-size:0.85rem; }
.empty-icon { font-size:2.5rem; }
.state-box-mini {
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  padding:1.5rem; color:var(--text-muted); font-size:0.85rem;
}

/* LOADING */
.loading-spinner {
  width:28px; height:28px; border-radius:50%;
  border:2px solid rgba(255,255,255,0.08);
  border-top-color:var(--accent-gold);
  animation:spin 0.8s linear infinite;
}
.loading-spinner-sm {
  width:20px; height:20px; border-radius:50%;
  border:2px solid rgba(255,255,255,0.08);
  border-top-color:var(--accent-gold);
  animation:spin 0.8s linear infinite;
}
.btn-spinner {
  width:16px; height:16px; border-radius:50%;
  border:2px solid rgba(255,255,255,0.2);
  border-top-color:#fff;
  animation:spin 0.6s linear infinite;
}

/* BUTTONS */
.btn-agregar {
  display:flex; align-items:center; justify-content:center; gap:0.5rem;
  padding:0.875rem 1rem;
  background:var(--accent-gold); color:#1a1a1a;
  border:none; border-radius:var(--radius-md);
  font-size:0.9rem; font-weight:700;
  cursor:pointer; transition:all 0.25s;
  position:sticky; bottom:1rem;
  box-shadow:0 4px 20px rgba(232,196,160,0.25);
}
.btn-agregar:hover { transform:translateY(-2px); box-shadow:0 6px 24px rgba(232,196,160,0.35); }
.btn-agregar:active { transform:translateY(0); }

/* MODALS */
.modal-overlay {
  position:fixed; inset:0; z-index:100;
  background:rgba(0,0,0,0.7);
  backdrop-filter:blur(8px);
  display:flex; align-items:flex-end; justify-content:center;
  padding:0;
  animation:fadeIn 0.2s ease;
}
.modal-buscador-overlay { align-items:flex-start; padding-top:4rem; }
.modal-config-overlay { align-items:center; padding:1rem; }
@keyframes fadeIn { from { opacity:0; } to { opacity:1; } }

.modal-card {
  background:#12121a;
  border:1px solid var(--border-subtle);
  border-radius:var(--radius-lg) var(--radius-lg) 0 0;
  width:100%; max-width:560px;
  max-height:85vh;
  display:flex; flex-direction:column;
  animation:slideUp 0.3s ease;
}
.modal-buscador-overlay .modal-card { border-radius:var(--radius-lg); max-height:70vh; }
.modal-config-overlay .modal-card { border-radius:var(--radius-lg); max-height:none; }
@keyframes slideUp { from { transform:translateY(100%); } to { transform:translateY(0); } }

.modal-header {
  display:flex; align-items:center; justify-content:space-between;
  padding:1.25rem 1.25rem 0.75rem;
  border-bottom:1px solid var(--border-subtle);
}
.modal-title { margin:0; font-size:1.1rem; font-weight:700; }
.modal-close {
  width:32px; height:32px; border-radius:50%;
  background:rgba(255,255,255,0.04); border:1px solid var(--border-subtle);
  color:var(--text-secondary); display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all 0.2s;
}
.modal-close:hover { background:rgba(255,255,255,0.08); color:var(--text-primary); }

/* SEARCH */
.search-bar {
  display:flex; align-items:center; gap:0.75rem;
  padding:0.875rem 1.25rem;
  border-bottom:1px solid var(--border-subtle);
}
.search-input {
  flex:1; background:transparent; border:none;
  color:var(--text-primary); font-size:0.95rem;
  outline:none;
}
.search-input::placeholder { color:var(--text-muted); }

/* PRODUCTOS LISTA */
.productos-lista {
  overflow-y:auto; flex:1;
  padding:0.5rem 0;
}
.producto-row {
  display:flex; align-items:center; gap:0.875rem;
  padding:0.75rem 1.25rem;
  cursor:pointer; transition:all 0.15s;
}
.producto-row:hover { background:rgba(255,255,255,0.04); }
.prod-img {
  width:44px; height:44px; border-radius:var(--radius-sm);
  object-fit:cover; background:rgba(255,255,255,0.04);
  border:1px solid var(--border-subtle);
}
.prod-info { flex:1; min-width:0; }
.prod-nombre { color:var(--text-primary); font-size:0.9rem; font-weight:600; margin:0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
.prod-meta { color:var(--text-muted); font-size:0.75rem; margin:0.15rem 0 0; }
.prod-precio { color:var(--accent-gold); font-size:0.9rem; font-weight:700; flex-shrink:0; }

/* FORM */
.form-row { display:flex; gap:0.75rem; }
.form-row .field-group { flex:1; }
.field-group {
  display:flex; flex-direction:column; gap:0.375rem;
  padding:0 1.25rem; margin-bottom:0.875rem;
}
.field-label { font-size:0.8rem; font-weight:600; color:var(--text-secondary); }
.field-input {
  background:rgba(255,255,255,0.04);
  border:1px solid var(--border-subtle);
  border-radius:var(--radius-sm);
  padding:0.625rem 0.875rem;
  color:var(--text-primary); font-size:0.9rem;
  outline:none; transition:all 0.2s;
}
.field-input:focus { border-color:var(--border-glow); background:rgba(255,255,255,0.06); }
.field-input::placeholder { color:var(--text-muted); }

/* PRIORITY CHIPS */
.priority-chips { display:flex; gap:0.5rem; flex-wrap:wrap; }
.priority-chip {
  padding:0.4rem 0.75rem; border-radius:999px;
  border:1px solid var(--border-subtle);
  background:rgba(255,255,255,0.03);
  color:var(--text-secondary); font-size:0.8rem; font-weight:500;
  cursor:pointer; transition:all 0.2s;
}
.priority-chip.active { border-color:currentColor; background:rgba(255,255,255,0.08); }
.priority-chip.p-urgente { color:#fb7185; }
.priority-chip.p-urgente.active { background:rgba(251,113,133,0.12); }
.priority-chip.p-importante { color:var(--accent-gold); }
.priority-chip.p-importante.active { background:rgba(232,196,160,0.12); }
.priority-chip.p-opcional { color:var(--text-muted); }
.priority-chip.p-opcional.active { background:rgba(255,255,255,0.08); }

/* TOGGLE */
.toggle-label {
  display:flex; align-items:center; justify-content:space-between;
  padding:0.75rem 1.25rem;
  background:rgba(255,255,255,0.02);
  border:1px solid var(--border-subtle);
  border-radius:var(--radius-sm);
  cursor:pointer;
}
.toggle-desc { font-size:0.75rem; color:var(--text-muted); margin:0.15rem 0 0; }
.toggle-switch {
  width:44px; height:24px; border-radius:999px;
  background:rgba(255,255,255,0.1); border:1px solid var(--border-subtle);
  position:relative; transition:all 0.25s; flex-shrink:0;
}
.toggle-switch.on { background:var(--accent-gold); border-color:var(--accent-gold); }
.toggle-thumb {
  width:20px; height:20px; border-radius:50%;
  background:#fff; position:absolute; top:1px; left:1px;
  transition:all 0.25s; box-shadow:0 2px 4px rgba(0,0,0,0.2);
}
.toggle-switch.on .toggle-thumb { transform:translateX(20px); }

/* MODAL ACTIONS */
.modal-actions {
  display:flex; gap:0.75rem; justify-content:flex-end;
  padding:1rem 1.25rem 1.25rem;
  border-top:1px solid var(--border-subtle);
}
.btn-cancel {
  padding:0.625rem 1.25rem;
  background:transparent; border:1px solid var(--border-subtle);
  border-radius:var(--radius-sm);
  color:var(--text-secondary); font-size:0.85rem; font-weight:600;
  cursor:pointer; transition:all 0.2s;
}
.btn-cancel:hover { background:rgba(255,255,255,0.04); color:var(--text-primary); }
.btn-gold {
  display:flex; align-items:center; gap:0.5rem;
  padding:0.625rem 1.5rem;
  background:var(--accent-gold); border:none;
  border-radius:var(--radius-sm);
  color:#1a1a1a; font-size:0.85rem; font-weight:700;
  cursor:pointer; transition:all 0.2s;
}
.btn-gold:hover { filter:brightness(1.1); }
.btn-gold:disabled { opacity:0.6; cursor:not-allowed; }
</style>
