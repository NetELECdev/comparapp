<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRuntimeConfig, useAsyncData, useSeoMeta } from '#imports'

const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase
const idComer = route.params.id

// ── Comercio: se resuelve en el prerender/servidor para que el OG quede
// horneado en el HTML estático (WhatsApp/Facebook lo leen sin ejecutar JS).
// Traemos la lista completa y buscamos por id porque ese endpoint ya
// devuelve lat/lng calculados; el de detalle podría no traerlos.
const { data: comercio } = await useAsyncData(`comercio-${idComer}`, async () => {
  try {
    const res = await $fetch(`${apiBase}/comercios`)
    const lista = res?.results || []
    return lista.find((c) => String(c.id_comer) === String(idComer)) || null
  } catch (e) {
    return null
  }
})

// ── OG dinámico por comercio (se hornea en el build por página)
const nombreC = computed(() => comercio.value?.nombre_comer || 'Comercio')
const descC = computed(() =>
  comercio.value?.direccion_comer
    ? `Mirá los precios de ${nombreC.value} en ${comercio.value.direccion_comer}. Comparados y actualizados en ComparApp.`
    : `Mirá los precios actualizados de ${nombreC.value} en ComparApp.`
)
useSeoMeta({
  title: () => `${nombreC.value} · ComparApp`,
  description: () => descC.value,
  ogTitle: () => `${nombreC.value} en ComparApp`,
  ogDescription: () => descC.value,
  ogType: 'website',
  ogImage: () => comercio.value?.logo_comer || undefined,
  twitterCard: () => (comercio.value?.logo_comer ? 'summary_large_image' : 'summary')
})

// ── Productos: solo en cliente, para que los precios estén siempre frescos.
const productos = ref([])
const cargandoProd = ref(true)
const errorProd = ref(false)

onMounted(async () => {
  if (!comercio.value?.nombre_comer) {
    cargandoProd.value = false
    return
  }
  try {
    const res = await $fetch(`${apiBase}/products`, {
      params: { comercio: comercio.value.nombre_comer, limit: 2000 }
    })
    productos.value = res?.results || []
  } catch (e) {
    errorProd.value = true
  } finally {
    cargandoProd.value = false
  }
  initMapa()
})

// ── Filtros de la grilla
const busqueda = ref('')
const cateActiva = ref('Todos')

const categorias = computed(() => {
  const set = new Set()
  for (const p of productos.value) {
    if (p.cate_prod) set.add(p.cate_prod)
  }
  return ['Todos', ...Array.from(set).sort()]
})

const productosFiltrados = computed(() => {
  const q = busqueda.value.trim().toLowerCase()
  return productos.value.filter((p) => {
    const okCate = cateActiva.value === 'Todos' || p.cate_prod === cateActiva.value
    const okQ =
      !q ||
      (p.nombre_prod || '').toLowerCase().includes(q) ||
      (p.marca_prod || '').toLowerCase().includes(q)
    return okCate && okQ
  })
})

// ── Helpers de formato
function fmtPrecio(n) {
  const num = Number(n)
  if (isNaN(num)) return '—'
  return num.toLocaleString('es-AR', {
    style: 'currency',
    currency: 'ARS',
    maximumFractionDigits: 0
  })
}
function fmtFecha(s) {
  if (!s) return ''
  const d = new Date(s)
  if (isNaN(d)) return ''
  const dd = String(d.getDate()).padStart(2, '0')
  const mm = String(d.getMonth() + 1).padStart(2, '0')
  return `${dd}/${mm}/${d.getFullYear()}`
}
function inicial(nombre) {
  return (nombre || '?').trim().charAt(0).toUpperCase()
}

// ── Compartir (usa ?ref para atribución) + Cómo llegar
const compartidoOk = ref(false)
function linkCompartir() {
  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  return `${origin}/c/${idComer}?ref=comercio_${idComer}`
}
async function compartir() {
  const url = linkCompartir()
  const nombre = comercio.value?.nombre_comer || 'este comercio'
  if (navigator.share) {
    try {
      await navigator.share({ title: nombre, text: `Precios de ${nombre} en ComparApp`, url })
      return
    } catch (e) { /* cancelado */ }
  }
  try {
    await navigator.clipboard.writeText(url)
    compartidoOk.value = true
    setTimeout(() => (compartidoOk.value = false), 2500)
  } catch (e) { /* clipboard bloqueado */ }
}
function linkComoLlegar() {
  const c = comercio.value
  if (c?.lat != null && c?.lng != null) {
    return `https://www.google.com/maps/dir/?api=1&destination=${c.lat},${c.lng}`
  }
  const dir = encodeURIComponent(c?.direccion_comer || '')
  return `https://www.google.com/maps/search/?api=1&query=${dir}`
}
const tieneCoords = computed(() => comercio.value?.lat != null && comercio.value?.lng != null)

// ── Mapa Leaflet (CDN, solo cliente por el SSG)
let mapa = null
async function cargarLeaflet() {
  if (window.L) return window.L
  if (!document.getElementById('leaflet-css')) {
    const link = document.createElement('link')
    link.id = 'leaflet-css'
    link.rel = 'stylesheet'
    link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'
    document.head.appendChild(link)
  }
  await new Promise((resolve, reject) => {
    const s = document.createElement('script')
    s.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js'
    s.onload = resolve
    s.onerror = reject
    document.head.appendChild(s)
  })
  return window.L
}
async function initMapa() {
  if (!tieneCoords.value) return
  try {
    const L = await cargarLeaflet()
    const el = document.getElementById('mapa-comercio')
    if (!el || mapa) return
    const { lat, lng } = comercio.value
    mapa = L.map(el, { scrollWheelZoom: false }).setView([lat, lng], 16)
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; OpenStreetMap &copy; CARTO',
      maxZoom: 19
    }).addTo(mapa)
    const icono = L.divIcon({
      className: 'pin-turq-wrap',
      html: '<div class="pin-turq"></div>',
      iconSize: [26, 26],
      iconAnchor: [13, 26]
    })
    L.marker([lat, lng], { icon: icono }).addTo(mapa)
  } catch (e) { /* si el CDN falla, la dirección igual queda visible */ }
}
</script>

<template>
  <div class="tienda-page">
    <DynamicBackground />

    <main class="page-content">
      <NuxtLink to="/" class="brand">ComparApp</NuxtLink>

      <!-- No encontrado -->
      <div v-if="!comercio" class="state-box">
        <h1>No encontramos este comercio</h1>
        <p>El enlace puede estar desactualizado o el comercio ya no está activo.</p>
        <NuxtLink to="/" class="btn-turq">Ir al inicio</NuxtLink>
      </div>

      <template v-else>
        <!-- Cabecera -->
        <header class="cabecera animate-fade-in-up">
          <div class="logo-wrap">
            <img v-if="comercio.logo_comer" :src="comercio.logo_comer" :alt="comercio.nombre_comer" class="logo" />
            <div v-else class="logo-ph">{{ inicial(comercio.nombre_comer) }}</div>
          </div>
          <div class="cab-info">
            <span v-if="comercio.cate_comer" class="eyebrow">{{ comercio.cate_comer }}</span>
            <h1 class="nombre">{{ comercio.nombre_comer }}</h1>
            <p v-if="comercio.direccion_comer" class="direccion">{{ comercio.direccion_comer }}</p>
            <div class="acciones">
              <button class="btn-turq" @click="compartir">{{ compartidoOk ? '¡Link copiado!' : 'Compartir' }}</button>
              <a class="btn-ghost" :href="linkComoLlegar()" target="_blank" rel="noopener">Cómo llegar</a>
            </div>
          </div>
        </header>

        <!-- Mapa -->
        <section v-if="tieneCoords" class="animate-fade-in-up stagger-1">
          <div id="mapa-comercio" class="mapa"></div>
        </section>
        <p v-else class="sin-mapa">📍 Ubicación no disponible para este comercio todavía.</p>

        <!-- Productos -->
        <section class="productos animate-fade-in-up stagger-2">
          <div class="filtros">
            <input v-model="busqueda" type="search" class="buscador" placeholder="Buscar producto o marca…" />
            <div v-if="categorias.length > 1" class="chips">
              <button v-for="cat in categorias" :key="cat" class="chip" :class="{ on: cateActiva === cat }" @click="cateActiva = cat">
                {{ cat }}
              </button>
            </div>
          </div>

          <div v-if="cargandoProd" class="grilla">
            <div v-for="n in 8" :key="n" class="card sk"></div>
          </div>

          <div v-else-if="productosFiltrados.length" class="grilla">
            <article v-for="p in productosFiltrados" :key="p.id_prod" class="card">
              <div class="card-img">
                <img v-if="p.imagen_prod" :src="p.imagen_prod" :alt="p.nombre_prod" loading="lazy" />
                <div v-else class="img-ph">{{ inicial(p.nombre_prod) }}</div>
              </div>
              <div class="card-body">
                <p class="c-nombre">{{ p.nombre_prod }}</p>
                <p v-if="p.marca_prod && p.marca_prod !== 'sin'" class="c-marca">{{ p.marca_prod }}</p>
                <p class="c-precio">{{ fmtPrecio(p.precio_prod) }}</p>
                <p class="c-meta">
                  <span v-if="p.cantidad_prod && p.unidad_prod">{{ p.cantidad_prod }} {{ p.unidad_prod }}</span>
                  <span v-if="p.fecha_prod" class="c-fecha">{{ fmtFecha(p.fecha_prod) }}</span>
                </p>
              </div>
            </article>
          </div>

          <div v-else class="state-box chico">
            <p v-if="busqueda || cateActiva !== 'Todos'">No hay productos que coincidan con tu búsqueda.</p>
            <p v-else>Este comercio todavía no cargó productos.</p>
          </div>
        </section>
      </template>
    </main>
  </div>
</template>

<style scoped>
.tienda-page {
  /* Acento de la vitrina. Cambiá este hex y se actualiza todo (pin, botones, precios).
     Tu app usa dorado (--accent-gold); acá probamos turquesa. */
  --turq: #2dd4bf;
  --turq-soft: rgba(45, 212, 191, 0.14);
  min-height: 100vh;
  position: relative;
  font-family: 'Inter', -apple-system, sans-serif;
  -webkit-font-smoothing: antialiased;
}
.page-content {
  position: relative;
  z-index: 2;
  max-width: 900px;
  margin: 0 auto;
  padding: 1.25rem 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
@keyframes fadeInUp { from { opacity:0; transform:translateY(20px);} to { opacity:1; transform:translateY(0);} }
@keyframes brillo { 0% { background-position:200% 0;} 100% { background-position:-200% 0;} }
.animate-fade-in-up { opacity:0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.06s; }
.stagger-2 { animation-delay: 0.12s; }

.brand {
  align-self: flex-start;
  color: var(--text-secondary, #9db2c4);
  font-weight: 700;
  font-size: 0.9rem;
  text-decoration: none;
  letter-spacing: -0.01em;
}
.brand:hover { color: var(--turq); }

/* Cabecera */
.cabecera {
  display: flex; gap: 1.1rem; align-items: center;
  padding: 1.25rem;
  background: var(--bg-card, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  border-radius: var(--radius-lg, 20px);
}
.logo-wrap { flex-shrink: 0; }
.logo, .logo-ph {
  width: 82px; height: 82px; border-radius: var(--radius-md, 16px); object-fit: cover;
  background: var(--turq-soft);
}
.logo-ph { display: grid; place-items: center; font-size: 34px; font-weight: 700; color: var(--turq); }
.eyebrow {
  display:block; font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
  color: var(--turq); font-weight: 700; margin-bottom: 4px;
}
.nombre { margin: 0; font-size: clamp(1.4rem, 5vw, 1.9rem); font-weight: 700; line-height: 1.15; color: var(--text-primary, #eaf2f8); }
.direccion { margin: 6px 0 0; color: var(--text-secondary, #9db2c4); font-size: 0.88rem; }
.acciones { display: flex; gap: 0.6rem; margin-top: 0.9rem; flex-wrap: wrap; }
.btn-turq, .btn-ghost {
  padding: 0.55rem 1.1rem; border-radius: 999px; font-size: 0.85rem; font-weight: 600;
  cursor: pointer; text-decoration: none; transition: transform 0.12s ease, background 0.2s ease; border: 1px solid;
}
.btn-turq { background: var(--turq); color: #06231f; border-color: var(--turq); }
.btn-ghost { background: transparent; color: var(--text-primary, #eaf2f8); border-color: var(--border-subtle, rgba(255,255,255,0.14)); }
.btn-turq:hover, .btn-ghost:hover { transform: translateY(-1px); }

/* Mapa */
.mapa {
  height: 240px; border-radius: var(--radius-lg, 20px); overflow: hidden;
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.1)); z-index: 0;
}
.sin-mapa { color: var(--text-muted, #7f93a6); font-size: 0.85rem; margin: 0; }
:global(.pin-turq) {
  width: 22px; height: 22px; border-radius: 50% 50% 50% 0; transform: rotate(-45deg);
  background: #2dd4bf; border: 2px solid #fff; box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

/* Productos */
.filtros { margin-bottom: 1.1rem; }
.buscador {
  width: 100%; padding: 0.8rem 1rem; border-radius: var(--radius-md, 14px);
  background: var(--bg-card, rgba(255,255,255,0.05)); border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  color: var(--text-primary, #eaf2f8); font-size: 0.95rem; font-family: inherit; outline: none;
}
.buscador:focus { border-color: var(--turq); }
.buscador::placeholder { color: var(--text-muted, #7f93a6); }
.chips { display: flex; gap: 0.5rem; margin-top: 0.75rem; overflow-x: auto; padding-bottom: 4px; }
.chip {
  flex-shrink: 0; border: 1px solid var(--border-subtle, rgba(255,255,255,0.1)); background: transparent;
  color: var(--text-secondary, #9db2c4); padding: 0.35rem 0.85rem; border-radius: 999px;
  font-size: 0.8rem; font-weight: 600; cursor: pointer; white-space: nowrap;
}
.chip.on { background: var(--turq-soft); color: var(--turq); border-color: var(--turq); }

.grilla { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.9rem; }
.card {
  border-radius: var(--radius-md, 16px); overflow: hidden;
  background: var(--bg-card, rgba(255,255,255,0.05)); border: 1px solid var(--border-subtle, rgba(255,255,255,0.1));
  transition: transform 0.14s ease, border-color 0.14s ease;
}
.card:hover { transform: translateY(-3px); border-color: var(--turq); }
.card-img { aspect-ratio: 1 / 1; background: rgba(255,255,255,0.03); }
.card-img img { width: 100%; height: 100%; object-fit: cover; }
.img-ph { width: 100%; height: 100%; display: grid; place-items: center; font-size: 38px; font-weight: 700; color: var(--turq); background: var(--turq-soft); }
.card-body { padding: 0.75rem; }
.c-nombre { margin: 0; font-size: 0.88rem; font-weight: 600; line-height: 1.25; color: var(--text-primary, #eaf2f8); }
.c-marca { margin: 3px 0 0; font-size: 0.75rem; color: var(--text-secondary, #9db2c4); }
.c-precio { margin: 0.5rem 0 0; font-size: 1.15rem; font-weight: 700; color: var(--turq); }
.c-meta { margin: 0.4rem 0 0; display: flex; justify-content: space-between; gap: 0.5rem; font-size: 0.68rem; color: var(--text-muted, #7f93a6); }

.sk {
  height: 220px;
  background: linear-gradient(90deg, rgba(255,255,255,0.04) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.04) 75%);
  background-size: 200% 100%; animation: brillo 1.3s infinite;
}

.state-box { text-align: center; padding: 3.5rem 1rem; color: var(--text-secondary, #9db2c4); }
.state-box.chico { padding: 2.5rem 1rem; }
.state-box h1 { color: var(--text-primary, #eaf2f8); margin-bottom: 0.5rem; }
.btn-turq { display: inline-block; margin-top: 1rem; }

@media (prefers-reduced-motion: reduce) {
  .animate-fade-in-up { opacity: 1; animation: none; }
  .sk { animation: none; }
  .card:hover, .btn-turq:hover, .btn-ghost:hover { transform: none; }
}
@media (max-width: 520px) {
  .cabecera { flex-direction: column; text-align: center; align-items: center; }
  .acciones { justify-content: center; }
}
</style>
