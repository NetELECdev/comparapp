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
          <article v-for="p in productosFiltrados" :key="p.id_prod" class="producto-item">
            <img :src="p.imagen_prod || '/images/avatar_default.png'" class="item-thumb" @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'" />
            <div class="item-info">
              <span class="item-name">{{ p.nombre_prod }}</span>
              <span class="item-meta">{{ p.marca_prod }} · {{ p.cate_prod }}</span>
              <span class="item-price">${{ formatPrice(p.precio_prod) }}</span>
            </div>
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
}

const config = useRuntimeConfig()

const estadoCargado = ref(false)
const estaVerificado = ref(false)
const motivoRechazo = ref('')
const miComercio = ref<{ id_comer: string; nombre_comer: string } | null>(null)

const productos = ref<Producto[]>([])
const loadingProductos = ref(true)
const searchQuery = ref('')
const categorias = ref<{ id: number; nombre: string }[]>([])
const medidas = ref<{ id: number; nombre: string }[]>([])

const modalOpen = ref(false)
const editandoId = ref<string | null>(null)
const guardando = ref(false)
const subiendoImagen = ref(false)
const errorMsg = ref('')

const form = ref<Partial<Producto>>({
  nombre_prod: '', cate_prod: '', marca_prod: '', precio_prod: '',
  cantidad_prod: 1, unidad_prod: 'Unidad', describe_prod: '', imagen_prod: '', activo_prod: true
})

function getToken() {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? JSON.parse(stored).access_token || '' : ''
  } catch { return '' }
}

function formatPrice(p: string | number) {
  return Number(p).toLocaleString('es-AR')
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
      { params: { q: miComercio.value.nombre_comer, limit: 200 } }
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
    cantidad_prod: 1, unidad_prod: 'Unidad', describe_prod: '', imagen_prod: '', activo_prod: true
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
    await Promise.all([cargarProductos(), cargarCategoriasYMedidas()])
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
}
.item-thumb { width: 48px; height: 48px; border-radius: var(--radius-sm); object-fit: cover; background: var(--bg-card-hover); flex-shrink: 0; }
.item-info { flex: 1; display: flex; flex-direction: column; gap: 0.125rem; min-width: 0; }
.item-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.item-meta { font-size: 0.75rem; color: var(--text-secondary); }
.item-price { font-size: 0.85rem; font-weight: 700; color: var(--accent-gold); }
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
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--border-glow); }
.form-group textarea { resize: vertical; font-family: inherit; }
.input-disabled { opacity: 0.6; cursor: not-allowed; }
.form-hint { font-size: 0.72rem; color: var(--text-muted); margin: 0; }
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

.form-actions { display: flex; gap: 0.75rem; margin-top: 0.5rem; }
.form-actions .btn-secondary, .form-actions .btn-primary { flex: 1; justify-content: center; }
</style>