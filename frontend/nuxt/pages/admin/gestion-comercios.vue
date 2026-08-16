<template>
  <div class="gestion-page">
    <DynamicBackground />

    <main class="page-content">
      <!-- Encabezado -->
      <div class="gc-head">
        <button class="gc-back" @click="navigateTo('/dashboard')" aria-label="Volver">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <div>
          <h1 class="gc-title">Gestión de comercios</h1>
          <p class="gc-sub">Cargá fotos y códigos de cualquier comercio</p>
        </div>
      </div>

      <!-- No admin -->
      <div v-if="!isAdmin" class="gc-box">
        <p>Esta sección es solo para administradores.</p>
      </div>

      <!-- Cargando comercios -->
      <div v-else-if="cargandoComercios" class="gc-box">
        <div class="gc-spinner" />
        <span>Cargando comercios...</span>
      </div>

      <!-- Selector de comercio -->
      <template v-else>
        <div class="gc-selector">
          <label>Comercio</label>
          <select v-model="comercioSel" @change="onCambioComercio">
            <option :value="null" disabled>Elegí un comercio…</option>
            <option v-for="c in comercios" :key="c.id_comer" :value="c">
              {{ c.nombre_comer }}
            </option>
          </select>
        </div>

        <!-- Sin comercio elegido -->
        <div v-if="!comercioSel" class="gc-box gc-empty">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>
          <p>Elegí un comercio arriba para ver y gestionar sus productos.</p>
        </div>

        <!-- Cargando productos del comercio -->
        <div v-else-if="cargandoProductos" class="gc-box">
          <div class="gc-spinner" />
          <span>Cargando productos de {{ comercioSel.nombre_comer }}...</span>
        </div>

        <!-- Herramientas de gestión del comercio elegido -->
        <template v-else>
          <div class="gc-resumen">
            <div class="gc-stat"><span class="n">{{ productos.length }}</span><span class="l">productos</span></div>
            <div class="gc-stat"><span class="n verde">{{ conFoto }}</span><span class="l">con foto</span></div>
            <div class="gc-stat"><span class="n gold">{{ sinFoto }}</span><span class="l">sin foto</span></div>
            <div class="gc-stat"><span class="n azul">{{ sinEan }}</span><span class="l">sin código</span></div>
          </div>

          <div class="gc-tools">
            <div class="gc-search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21 21-4.34-4.34"/><circle cx="11" cy="11" r="8"/></svg>
              <input
                v-model="busqueda"
                type="text"
                placeholder="Buscar producto por nombre..."
              />
              <button v-if="busqueda" class="gc-search-clear" @click="busqueda = ''" aria-label="Limpiar búsqueda">✕</button>
            </div>
            <select v-model="ordenPor" class="gc-orden">
              <option value="nombre-asc">Nombre (A-Z)</option>
              <option value="nombre-desc">Nombre (Z-A)</option>
              <option value="fecha-desc">Fecha (más reciente)</option>
              <option value="fecha-asc">Fecha (más antigua)</option>
            </select>
          </div>

          <p v-if="busqueda && !productosFiltrados.length" class="gc-sin-resultados">
            No se encontraron productos que coincidan con "{{ busqueda }}".
          </p>

          <ImagenesPendientes
            :productos="productosFiltrados"
            :imagen-por-categoria="imagenPorCategoria"
            @actualizado="cargarProductos"
          />

          <CodigosPendientes
            :productos="productosFiltrados"
            :imagen-por-categoria="imagenPorCategoria"
            @actualizado="cargarProductos"
          />
        </template>
      </template>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { navigateTo } from '#app'

interface Comercio {
  id_comer: string
  nombre_comer: string
  [key: string]: any
}
interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  imagen_prod: string | null
  ean_prod?: string | null
  fecha_prod?: string | null
  [key: string]: any
}

const { api } = useApi()

// Admin (mismo patrón que /comercios)
const user = ref<any>(null)
const isAdmin = computed(() => user.value?.rol === 'admin')

const comercios = ref<Comercio[]>([])
const comercioSel = ref<Comercio | null>(null)
const productos = ref<Producto[]>([])
const categorias = ref<{ nombre: string; icono?: string }[]>([])

const cargandoComercios = ref(true)
const cargandoProductos = ref(false)

// Búsqueda y orden (solo dentro del comercio seleccionado)
const busqueda = ref('')
const ordenPor = ref<'nombre-asc' | 'nombre-desc' | 'fecha-desc' | 'fecha-asc'>('nombre-asc')

const productosFiltrados = computed(() => {
  let lista = productos.value

  if (busqueda.value.trim()) {
    const q = busqueda.value.trim().toLowerCase()
    lista = lista.filter(p => (p.nombre_prod || '').toLowerCase().includes(q))
  }

  return [...lista].sort((a, b) => {
    switch (ordenPor.value) {
      case 'nombre-asc':
        return (a.nombre_prod || '').localeCompare(b.nombre_prod || '')
      case 'nombre-desc':
        return (b.nombre_prod || '').localeCompare(a.nombre_prod || '')
      case 'fecha-desc':
        return new Date(b.fecha_prod || 0).getTime() - new Date(a.fecha_prod || 0).getTime()
      case 'fecha-asc':
        return new Date(a.fecha_prod || 0).getTime() - new Date(b.fecha_prod || 0).getTime()
      default:
        return 0
    }
  })
})

// Resumen (siempre sobre el total del comercio, no sobre la búsqueda)
const conFoto = computed(() => productos.value.filter(p => p.imagen_prod).length)
const sinFoto = computed(() => productos.value.filter(p => !p.imagen_prod).length)
const sinEan = computed(() => productos.value.filter(p => !p.ean_prod).length)

const imagenPorCategoria = computed(() => {
  const map: Record<string, string> = {}
  for (const c of categorias.value) {
    if (c.nombre && c.icono) map[c.nombre.toLowerCase().trim()] = c.icono
  }
  return map
})

async function cargarComercios() {
  cargandoComercios.value = true
  try {
    const res = await api<{ count: number; results: Comercio[] }>('/comercios')
    comercios.value = res.results || []
  } catch (e) {
    console.error('Error cargando comercios:', e)
  } finally {
    cargandoComercios.value = false
  }
}

async function cargarCategorias() {
  try {
    const cats = await api<any[]>('/categorias')
    categorias.value = (cats || []).map((c: any) => ({ nombre: c.nombre_cate, icono: c.icono_cate }))
  } catch (e) {
    console.error('Error cargando categorías:', e)
  }
}

async function cargarProductos() {
  if (!comercioSel.value) return
  cargandoProductos.value = true
  try {
    const res = await api<{ count: number; results: Producto[] }>(
      `/products?comercio=${encodeURIComponent(comercioSel.value.nombre_comer)}&limit=5000`
    )
    productos.value = res.results || []
  } catch (e) {
    console.error('Error cargando productos:', e)
  } finally {
    cargandoProductos.value = false
  }
}

function onCambioComercio() {
  productos.value = []
  busqueda.value = ''
  cargarProductos()
}

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch { /* ignore */ }
  }
  if (!isAdmin.value) return
  await Promise.all([cargarComercios(), cargarCategorias()])
})
</script>

<style scoped>
.gestion-page { min-height: 100vh; position: relative; }
.page-content { max-width: 560px; margin: 0 auto; padding: 1.25rem; position: relative; z-index: 1; }

.gc-head { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }
.gc-back {
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px; border-radius: 10px; flex-shrink: 0;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  color: var(--text-primary, #f4f4f5); cursor: pointer;
}
.gc-title { margin: 0; font-size: 1.35rem; font-weight: 800; color: var(--text-primary, #f4f4f5); }
.gc-sub { margin: 0.1rem 0 0; font-size: 0.85rem; color: var(--text-secondary, #a1a1aa); }

.gc-selector { margin-bottom: 1rem; }
.gc-selector label { display: block; font-size: 0.8rem; color: var(--text-secondary, #a1a1aa); margin-bottom: 0.35rem; }
.gc-selector select {
  width: 100%; padding: 0.7rem 0.85rem; border-radius: 12px;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-primary, #f4f4f5); font-size: 0.95rem;
}

.gc-box {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 2rem 1rem; text-align: center;
  color: var(--text-secondary, #a1a1aa);
  background: var(--bg-card, rgba(255,255,255,0.04));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  border-radius: 16px;
}
.gc-empty svg { color: var(--text-muted, #71717a); }

.gc-spinner {
  width: 26px; height: 26px; border-radius: 50%;
  border: 3px solid rgba(255,255,255,0.15); border-top-color: var(--accent-gold, #e8c4a0);
  animation: gc-spin 0.8s linear infinite;
}
@keyframes gc-spin { to { transform: rotate(360deg); } }

.gc-tools {
  display: flex; gap: 0.5rem; margin-bottom: 1rem;
}
.gc-search {
  flex: 1; display: flex; align-items: center; gap: 0.5rem;
  padding: 0 0.75rem; border-radius: 12px; min-width: 0;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-secondary, #a1a1aa);
}
.gc-search svg { flex-shrink: 0; }
.gc-search input {
  flex: 1; min-width: 0; padding: 0.65rem 0; border: none; background: transparent;
  color: var(--text-primary, #f4f4f5); font-size: 0.9rem; outline: none;
}
.gc-search-clear {
  flex-shrink: 0; background: none; border: none; cursor: pointer;
  color: var(--text-muted, #71717a); font-size: 0.85rem; padding: 0.2rem;
}
.gc-orden {
  padding: 0 0.6rem; border-radius: 12px; flex-shrink: 0;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-primary, #f4f4f5); font-size: 0.85rem;
}
.gc-sin-resultados {
  text-align: center; color: var(--text-secondary, #a1a1aa);
  font-size: 0.85rem; padding: 1rem 0;
}

.gc-resumen {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.5rem; margin-bottom: 1rem;
}
.gc-stat {
  display: flex; flex-direction: column; align-items: center; gap: 0.1rem;
  padding: 0.75rem 0.4rem; border-radius: 12px;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.08));
}
.gc-stat .n { font-size: 1.3rem; font-weight: 800; color: var(--text-primary, #f4f4f5); }
.gc-stat .n.verde { color: #4ade80; }
.gc-stat .n.gold { color: #e8c4a0; }
.gc-stat .n.azul { color: #60a5fa; }
.gc-stat .l { font-size: 0.68rem; color: var(--text-muted, #71717a); }

.gestion-page > .page-content > * + * { margin-top: 0; }
.gestion-page :deep(.img-pend),
.gestion-page :deep(.cod-pend) { margin-bottom: 1rem; }
</style>