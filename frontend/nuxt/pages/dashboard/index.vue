<!-- pages/dashboard/index.vue -->
<template>
  <div class="dashboard" :class="{ 'is-dark': esDark }">

    <!-- Fondo dinámico -->
    <DynamicBackground />

    <!-- Header -->
    <header class="dash-header">
      <div class="dash-header-left">
        <button class="dash-profile-btn" @click="navigateTo('/perfil')" aria-label="Mi perfil">
          <span class="dash-profile-avatar">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </span>
          <span class="dash-profile-info">
            <span class="dash-profile-name">{{ user?.nombre_completo?.split(' ')[0] || 'Mi perfil' }}</span>
            <button class="dash-location-btn" @click.stop="solicitarUbicacion" aria-label="Tu ubicación">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M12 2a7 7 0 0 0-7 7c0 5 7 13 7 13s7-8 7-13a7 7 0 0 0-7-7Z"/>
                <circle cx="12" cy="9" r="2.5"/>
              </svg>
              <span class="dash-location-text">{{ ubicacionTexto }}</span>
            </button>
          </span>
        </button>
      </div>
      <div class="dash-header-right">
        <ToggleTema />
        <button class="dash-notif" aria-label="Notificaciones" @click="navigateTo('/alertas')">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
          </svg>
          <span class="dash-notif-dot" aria-hidden="true" />
        </button>
      </div>
    </header>

    <!-- Contenido -->
    <main class="dash-main">

      <!-- Bienvenida personalizada -->
      <section class="welcome-banner" aria-label="Bienvenida">
        <p class="welcome-title">¡Hola de nuevo, {{ user?.nombre_completo?.split(' ')[0] || 'Usuario' }}! 👋</p>
        <p class="welcome-sub">{{ welcomeMessage }}</p>
      </section>

      <!-- Banner institucional / propuesta de valor -->
      <section class="brand-banner" aria-label="ComparApp">
        <div class="brand-banner-text">
          <p>Compara precios locales, encuentra las mejores ofertas y crea listas de compra inteligentes para ahorrar tiempo y dinero.</p>
        </div>
        <div class="brand-banner-logo">
          <img
            src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/comparAppV2.png"
            alt="ComparApp"
            loading="lazy"
          />
        </div>
      </section>

      <!-- Barra de búsqueda -->
      <section class="search-banner" aria-label="Buscar productos">
        <form class="search-form" @submit.prevent="irABusqueda">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="search-icon">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <input
            v-model="busquedaDash"
            type="text"
            class="search-input"
            placeholder="Buscá productos, marcas y más"
            @focus="irABusqueda"
          />
        </form>
      </section>

      <!-- Banner de alertas activas -->
      <section
        v-if="!loadingAlertas && alertasActivas.length > 0"
        class="alerts-banner"
        aria-label="Alertas de precio activas"
        @click="navigateTo('/alertas')"
      >
        <div class="alerts-banner-icon">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/>
            <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/>
          </svg>
        </div>
        <div class="alerts-banner-text">
          <p class="alerts-banner-title">
            {{ alertasActivas.length }} {{ alertasActivas.length === 1 ? 'alerta activa' : 'alertas activas' }}
          </p>
          <p class="alerts-banner-sub">
            Avisamos cuando baje el precio de {{ alertasActivas[0]?.producto?.nombre_prod || 'tus productos' }}{{ alertasActivas.length > 1 ? ` y ${alertasActivas.length - 1} más` : '' }}
          </p>
        </div>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" class="alerts-banner-arrow">
          <path d="m9 18 6-6-6-6"/>
        </svg>
      </section>

      <!-- 2 cards grandes: Comparador y Productos -->
      <section class="big-cards" aria-label="Accesos principales">
        <button class="big-card big-card--comparador" @click="navigateTo('/comparaciones')">
          <div class="big-card-top">
            <span class="big-card-title">Comparador</span>
            <div class="big-card-icon">
              <img src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/compara23.webp" alt="Comparador" loading="lazy" />
            </div>
          </div>
          <span class="big-card-label">Ahorra en cada compra</span>
          <span class="big-card-sub">Consulta precios actualizados y elige la mejor oferta.</span>
        </button>
        <button class="big-card big-card--productos" @click="navigateTo('/productos')">
          <div class="big-card-top">
            <span class="big-card-title">Productos</span>
            <div class="big-card-icon">
              <img src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/productosProd.webp" alt="Productos" loading="lazy" />
            </div>
          </div>
          <span class="big-card-label">Todo en un solo lugar</span>
          <span class="big-card-sub">Accede a información detallada de cada producto.</span>
        </button>
      </section>

      <!-- 3 mini-cards: Alertas / Favoritos / Historial -->
      <section class="mini-cards" aria-label="Tu actividad">
        <button class="mini-card mini-card--alertas" @click="navigateTo('/alertas')">
          <div class="mini-card-content">
            <span class="mini-card-num">{{ alertasActivas.length }}</span>
            <span class="mini-card-label">{{ alertasActivas.length === 1 ? 'Alerta activa' : 'Alertas activas' }}</span>
          </div>
          <img
            src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/alerta3d.jpg"
            alt="Alertas"
            class="mini-card-img"
            loading="lazy"
          />
        </button>

        <button class="mini-card mini-card--favoritos" @click="navigateTo('/favoritos')">
          <div class="mini-card-content">
            <span class="mini-card-num">{{ favoritos.length }}</span>
            <span class="mini-card-label">{{ favoritos.length === 1 ? 'Favorito' : 'Favoritos' }}</span>
          </div>
          <img
            src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/alertas3d.jpg"
            alt="Favoritos"
            class="mini-card-img"
            loading="lazy"
          />
        </button>

        <button class="mini-card mini-card--historial" @click="navigateTo('/comparaciones/historial')">
          <div class="mini-card-content">
            <span class="mini-card-num">{{ comparacionesGuardadas.length }}</span>
            <span class="mini-card-label">{{ comparacionesGuardadas.length === 1 ? 'Comparación' : 'Comparaciones' }}</span>
          </div>
          <img
            src="https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/lista3d.jpg"
            alt="Historial"
            class="mini-card-img"
            loading="lazy"
          />
        </button>
      </section>

      <!-- Carrusel de categorías -->
      <section class="cat-carousel-section" aria-label="Categorías">
        <h2 class="carousel-title">Categorías</h2>
        <div v-if="loadingCategorias" class="cat-carousel">
          <div class="cat-card-skeleton" v-for="n in 5" :key="n" aria-hidden="true" />
        </div>
        <div v-else ref="catCarouselRef" class="cat-carousel">
          <button
            v-for="cat in categorias"
            :key="cat.id_cate"
            class="cat-card"
            :style="{ background: cat.color + '1a', borderColor: cat.color + '50' }"
            @click="navigateTo(`/productos?categoria=${encodeURIComponent(cat.nombre_cate)}`)"
          >
            <div class="cat-card-icon-wrap">
              <img
                :src="cat.icono_cate"
                :alt="cat.nombre_cate"
                class="cat-card-icon"
                loading="lazy"
              />
            </div>
            <span class="cat-card-label">{{ cat.nombre_cate }}</span>
          </button>
        </div>
      </section>

      <!-- Carrusel de comercios -->
      <section class="com-carousel-section" aria-label="Comercios">
        <h2 class="carousel-title">Comercios</h2>
        <div v-if="loadingComercios" class="com-carousel">
          <div class="com-item-skeleton" v-for="n in 5" :key="n" aria-hidden="true" />
        </div>
        <div v-else-if="comercios.length" ref="comCarouselRef" class="com-carousel">
          <button
            v-for="com in comercios"
            :key="com.id_comer"
            class="com-item"
            @click="navigateTo(`/comercios/${com.id_comer}`)"
          >
            <div class="com-item-avatar">
              <img
                :src="com.logo_comer || `${SUPABASE}/comercios2.jpg`"
                :alt="com.nombre_comer"
                loading="lazy"
                @error="(e) => ((e.target as HTMLImageElement).src = `${SUPABASE}/comercios2.jpg`)"
              />
            </div>
            <span class="com-item-label">{{ com.nombre_comer }}</span>
          </button>
        </div>
      </section>

      <!-- Grid de secciones — fiel al modelo dashV1 -->
      <section class="menu-grid" aria-label="Secciones principales">
        <button
          v-for="(item, index) in menuItems"
          :key="item.title"
          class="menu-pin"
          :class="`stagger-${index}`"
          @click="item.action()"
          :aria-label="`Ir a ${item.title}`"
        >
          <div class="menu-pin-img-wrap">
            <img
              :src="item.imageUrl"
              :alt="item.title"
              class="menu-pin-img"
              loading="lazy"
              @error="(e) => ((e.target as HTMLImageElement).src = '/images/avatar_default.png')"
            />
          </div>
          <span class="menu-pin-label">{{ item.title }}</span>
        </button>
      </section>

      <!-- Productos recientes -->
      <section class="recent-section" aria-label="Productos recientes">
        <div class="recent-header">
          <h2 class="recent-title">Productos recientes</h2>
          <span v-if="products.length" class="recent-badge">{{ products.length }}</span>
        </div>

        <div v-if="loadingProducts" class="recent-skeletons">
          <div class="recent-skeleton" v-for="n in 4" :key="n" aria-hidden="true" />
        </div>

        <div v-else-if="products.length === 0" class="recent-empty">
          <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
          </svg>
          <p>No hay productos cargados aún</p>
        </div>

        <div v-else class="recent-list">
          <article
            v-for="p in products.slice(0, 5)"
            :key="p.id_prod"
            class="recent-item"
            @click="navigateTo(`/productos/lista?q=${encodeURIComponent(p.nombre_prod)}`)"
          >
            <div class="recent-item-img">
              <img
                :src="p.imagen_prod || '/images/avatar_default.png'"
                :alt="p.nombre_prod"
                loading="lazy"
                @error="(e) => ((e.target as HTMLImageElement).src = '/images/avatar_default.png')"
              />
            </div>
            <div class="recent-item-info">
              <p class="recent-item-name">{{ p.nombre_prod }}</p>
              <p class="recent-item-meta">{{ p.comercio_prod }} · {{ p.cate_prod }}</p>
            </div>
            <div class="recent-item-price">
              <span class="price-symbol">$</span>
              <span>{{ Number(p.precio_prod).toLocaleString('es-AR') }}</span>
            </div>
          </article>
        </div>

        <button v-if="products.length > 0" class="ver-mas" @click="navigateTo('/productos')">
          Ver todos los productos
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
          </svg>
        </button>
      </section>

    </main>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

useTema()
useBackground()

const { esDark } = useTema()

interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  describe_prod: string
  comercio_prod: string
  precio_prod: string
  imagen_prod: string | null
  marca_prod: string
  activo_prod: boolean
}

const config = useRuntimeConfig()
const user = ref<any>(null)
const products = ref<Producto[]>([])
const loadingProducts = ref(true)

// Mensajes de bienvenida rotativos
const welcomeMessages = [
  '¿Qué comparamos hoy?',
  'Encontrá el mejor precio en segundos',
  'Ahorrá tiempo y plata comparando',
  'Tu changuito más inteligente',
]
const welcomeMessage = ref(welcomeMessages[Math.floor(Math.random() * welcomeMessages.length)])

// Alertas de precio activas
interface Alerta {
  id: string
  id_prod: string
  precio_objetivo: number
  producto?: {
    nombre_prod: string
    precio_prod: number
    imagen_prod: string | null
    comercio_prod: string
  }
}
const alertasActivas = ref<Alerta[]>([])
const loadingAlertas = ref(true)

// Favoritos — usa el composable global ya sincronizado con Supabase
const { favoritos } = useFavoritos()

// Comparaciones guardadas — tabla historial_comparaciones (aún sin endpoint activo)
const comparacionesGuardadas = ref<any[]>([])

// Categorías
interface Categoria {
  id_cate: string
  nombre_cate: string
  icono_cate: string
  color: string
}
const categorias = ref<Categoria[]>([])
const loadingCategorias = ref(true)

// Comercios
interface Comercio {
  id_comer: string
  nombre_comer: string
  logo_comer: string | null
}
const comercios = ref<Comercio[]>([])
const loadingComercios = ref(true)

const getToken = () => {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? JSON.parse(stored).access_token || '' : ''
  } catch { return '' }
}

const SUPABASE = 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images'

// Drag-to-scroll en desktop para los carruseles horizontales
const catCarouselRef = ref<HTMLElement | null>(null)
const comCarouselRef = ref<HTMLElement | null>(null)
useDragScroll(catCarouselRef)
useDragScroll(comCarouselRef)

// Ubicación del usuario (geolocalización del navegador)
const ubicacionTexto = ref('Detectar ubicación')

async function solicitarUbicacion() {
  if (!navigator.geolocation) {
    ubicacionTexto.value = 'Ubicación no disponible'
    return
  }
  ubicacionTexto.value = 'Buscando...'
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const { latitude, longitude } = pos.coords
        const res = await fetch(
          `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=16&addressdetails=1`
        )
        const data = await res.json()
        const calle = data?.address?.road || data?.address?.suburb || data?.address?.city || 'Tu ubicación'
        const numero = data?.address?.house_number ? ` ${data.address.house_number}` : ''
        ubicacionTexto.value = `${calle}${numero}`
        try { localStorage.setItem('comparapp_ubicacion', ubicacionTexto.value) } catch {}
      } catch {
        ubicacionTexto.value = 'Tu ubicación'
      }
    },
    () => { ubicacionTexto.value = 'Activar ubicación' },
    { enableHighAccuracy: false, timeout: 8000 }
  )
}

// Búsqueda desde el dashboard
const busquedaDash = ref('')
function irABusqueda() {
  const q = busquedaDash.value.trim()
  navigateTo(q ? `/productos/lista?q=${encodeURIComponent(q)}` : '/productos/lista')
}

// Estructura fiel al dashV1: imagen ilustrativa + título debajo
// Distribución masonry: columna izquierda y derecha con tamaños variables
const menuItems = ref([
  { title: 'Admin',       imageUrl: `${SUPABASE}/admin.jpg`,       action: () => navigateTo('/admin') },
])

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch {}
  }

  // Ubicación: usar la guardada o solicitar una nueva
  const ubicacionGuardada = localStorage.getItem('comparapp_ubicacion')
  if (ubicacionGuardada) {
    ubicacionTexto.value = ubicacionGuardada
  } else {
    solicitarUbicacion()
  }

  if (!user.value || user.value.rol !== 'admin') {
    menuItems.value = menuItems.value.filter(p => p.title !== 'Admin')
  }

  try {
    const res = await $fetch<{ count: number; results: Producto[] }>(
      `${config.public.apiBase}/products`
    )
    products.value = res.results || []
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loadingProducts.value = false
  }

  // Cargar alertas activas (solo si hay sesión)
  const token = getToken()
  if (token) {
    try {
      const resAlertas = await $fetch<{ count: number; results: Alerta[] }>(
        `${config.public.apiBase}/alertas`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      alertasActivas.value = resAlertas.results || []
    } catch (err) {
      console.error('Error cargando alertas:', err)
    } finally {
      loadingAlertas.value = false
    }
  } else {
    loadingAlertas.value = false
  }

  // Cargar categorías
  try {
    const resCat = await $fetch<Categoria[]>(`${config.public.apiBase}/categorias`)
    categorias.value = resCat || []
  } catch (err) {
    console.error('Error cargando categorías:', err)
  } finally {
    loadingCategorias.value = false
  }

  // Cargar comercios
  try {
    const resCom = await $fetch<{ count: number; results: Comercio[] }>(`${config.public.apiBase}/comercios`)
    comercios.value = resCom.results || []
  } catch (err) {
    console.error('Error cargando comercios:', err)
  } finally {
    loadingComercios.value = false
  }
})
</script>

<style scoped>
/* ── Base ── */
.dashboard {
  position: relative;
  min-height: 100vh;
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* ── Header ── */
.dash-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-subtle);
}

.dash-header-left {
  display: flex;
  align-items: center;
  gap: 10px;
}

.dash-profile-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 2px 0;
  text-align: left;
}

.dash-profile-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--bg-card-hover);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  transition: border-color 0.2s;
}
.dash-profile-btn:hover .dash-profile-avatar { border-color: var(--border-glow); }

.dash-profile-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
  min-width: 0;
}
.dash-profile-name {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.2;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 160px;
}

.dash-location-btn {
  display: flex; align-items: center; gap: 4px;
  background: none; border: none;
  color: var(--text-secondary);
  font-size: 11px; font-weight: 500;
  cursor: pointer;
  padding: 0;
  max-width: 180px;
}
.dash-location-btn:hover { color: var(--accent-gold); }
.dash-location-text {
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
  max-width: 150px;
}
.dash-header-right { display: flex; align-items: center; gap: 8px; }

.dash-notif {
  position: relative;
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--bg-card-hover);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: border-color 0.2s;
}
.dash-notif:hover { border-color: var(--border-glow); }
.dash-notif-dot {
  position: absolute; top: 7px; right: 7px;
  width: 7px; height: 7px; border-radius: 50%;
  background: var(--accent-rose);
  border: 1.5px solid var(--bg-deep);
}

/* ── Main ── */
.dash-main {
  position: relative;
  z-index: 2;
  padding: 20px 16px 120px;
  display: flex; flex-direction: column; gap: 28px;
  max-width: 600px; margin: 0 auto;
}
.dash-main > * { min-width: 0; }

/* ── Animación de entrada desde la derecha ── */
@keyframes slideInRight {
  from { opacity: 0; transform: translateX(50px); }
  to   { opacity: 1; transform: translateX(0); }
}

@media (prefers-reduced-motion: reduce) {
  @keyframes slideInRight {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
}

/* ── Grid de secciones — modelo dashV1 ── */
/* ── Bienvenida personalizada ── */
.welcome-banner {
  padding: 18px 4px 4px;
}
.welcome-title {
  font-size: 19px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}
.welcome-sub {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

/* ── Banner institucional / propuesta de valor ── */
.brand-banner {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px 18px;
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.16), rgba(74, 222, 128, 0.04));
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(74, 222, 128, 0.3);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
.brand-banner-text {
  flex: 1;
  min-width: 0;
}
.brand-banner-text p {
  font-size: 13px;
  font-weight: 600;
  line-height: 1.45;
  color: var(--text-primary);
  margin: 0;
}
.brand-banner-logo {
  width: 128px; height: 128px;
  flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
}
.brand-banner-logo img {
  width: 100%; height: 100%;
  object-fit: contain;
}

/* ── Barra de búsqueda ── */
.search-banner { padding: 0 4px; }
.search-form {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 12px 16px;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-card);
  transition: border-color 0.2s;
}
.search-form:has(.search-input:focus) { border-color: var(--border-glow); }
.search-icon { color: var(--text-muted); flex-shrink: 0; }
.search-input {
  flex: 1;
  background: none;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}
.search-input::placeholder { color: var(--text-muted); }

/* ── Banner de alertas activas ── */
.alerts-banner {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 14px 16px;
  background: linear-gradient(135deg, var(--accent-gold-dim), var(--bg-card));
  border: 1px solid var(--border-glow);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-card);
}
.alerts-banner:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-modal);
}
.alerts-banner-icon {
  width: 40px; height: 40px;
  border-radius: 50%;
  background: var(--accent-gold);
  color: #1a1a1a;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.alerts-banner-text { flex: 1; min-width: 0; }
.alerts-banner-title {
  font-size: 14px; font-weight: 700;
  color: var(--text-primary); margin: 0 0 2px;
}
.alerts-banner-sub {
  font-size: 12px; color: var(--text-secondary); margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.alerts-banner-arrow { color: var(--text-muted); flex-shrink: 0; }

/* ── 2 cards grandes: Comparador / Productos ── */
.big-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.big-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 8px;
  padding: 16px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  text-align: left;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-card);
  min-height: 150px;
}
.big-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-modal); }
.big-card:active { transform: scale(0.98); }

.big-card--comparador {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.18), var(--bg-card));
  color: var(--text-primary);
}
.big-card--productos {
  background: linear-gradient(135deg, rgba(74, 222, 128, 0.15), var(--bg-card));
  color: var(--text-primary);
}

.big-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
}
.big-card-title {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.big-card-icon {
  width: 64px; height: 64px;
  border-radius: 14px;
  overflow: hidden;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.big-card-icon img {
  width: 100%; height: 100%;
  object-fit: contain;
}

.big-card-label {
  font-size: 15px; font-weight: 700;
  color: var(--text-primary);
}
.big-card-sub {
  font-size: 11.5px;
  font-weight: 400;
  color: var(--text-secondary);
  line-height: 1.35;
}

/* ── 3 mini-cards: Alertas / Favoritos / Historial ── */
.mini-cards {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
}
.mini-card {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: space-between;
  min-height: 100px;
  padding: 12px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  overflow: hidden;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  box-shadow: var(--shadow-card);
}
.mini-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-modal); }
.mini-card:active { transform: scale(0.97); }

.mini-card--alertas {
  background: linear-gradient(135deg, rgba(251, 146, 60, 0.18), var(--bg-card));
}
.mini-card--favoritos {
  background: linear-gradient(135deg, rgba(244, 114, 182, 0.18), var(--bg-card));
}
.mini-card--historial {
  background: linear-gradient(135deg, rgba(96, 165, 250, 0.18), var(--bg-card));
}

.mini-card-content {
  display: flex;
  flex-direction: column;
  gap: 1px;
  z-index: 1;
}
.mini-card-num {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
}
.mini-card-label {
  font-size: 10.5px;
  font-weight: 600;
  color: var(--text-secondary);
  line-height: 1.3;
}

.mini-card-img {
  position: absolute;
  bottom: -6px;
  right: -6px;
  width: 69px;
  height: 69px;
  object-fit: contain;
  opacity: 0.95;
  pointer-events: none;
}

@media (max-width: 380px) {
  .mini-card-num { font-size: 17px; }
  .mini-card-img { width: 57px; height: 57px; }
}

/* ── Título de sección de carrusel ── */
.carousel-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 10px 4px;
}

/* ── Carrusel de categorías (pills horizontales) ── */
.cat-carousel-section { margin-top: 4px; }
.cat-carousel {
  display: flex;
  gap: 10px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
  cursor: grab;
  user-select: none;
}
.cat-carousel::-webkit-scrollbar { display: none; }
.cat-carousel.is-dragging { cursor: grabbing; scroll-behavior: auto; }

.cat-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-shrink: 0;
  width: 84px;
  padding: 14px 8px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-subtle);
  cursor: pointer;
  transition: transform 0.15s ease;
}
.cat-card:hover { transform: translateY(-2px); }
.cat-card:active { transform: scale(0.96); }

.cat-card-icon-wrap {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
}
.cat-card-icon {
  width: 100%; height: 100%;
  object-fit: contain;
  border-radius: 10px;
}
.cat-card-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  text-transform: capitalize;
  text-align: center;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.cat-card-skeleton {
  flex-shrink: 0;
  width: 84px; height: 92px;
  border-radius: var(--radius-lg);
  background: var(--bg-card-hover);
  animation: shimmer 1.4s ease-in-out infinite;
}

/* ── Carrusel de comercios (avatar circular + nombre) ── */
.com-carousel-section { margin-top: 4px; }
.com-carousel {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding: 2px 2px 10px;
  scrollbar-width: none;
  -ms-overflow-style: none;
  cursor: grab;
  user-select: none;
}
.com-carousel::-webkit-scrollbar { display: none; }
.com-carousel.is-dragging { cursor: grabbing; scroll-behavior: auto; }

.com-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
  width: 68px;
  background: none;
  border: none;
  cursor: pointer;
  transition: transform 0.15s ease;
}
.com-item:hover { transform: translateY(-2px); }
.com-item:active { transform: scale(0.96); }

.com-item-avatar {
  width: 56px; height: 56px;
  border-radius: 50%;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
  background: #ffffff;
  display: flex; align-items: center; justify-content: center;
  box-shadow: var(--shadow-card);
  padding: 6px;
}
.com-item-avatar img {
  width: 100%; height: 100%; object-fit: contain;
}

.com-item-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-primary);
  text-align: center;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 68px;
}

.com-item-skeleton {
  flex-shrink: 0;
  width: 56px; height: 56px;
  border-radius: 50%;
  background: var(--bg-card-hover);
  animation: shimmer 1.4s ease-in-out infinite;
}

/* Masonry CSS con column-count, íconos con fondo + título debajo */
.menu-grid {
  columns: 2;
  column-gap: 14px;
}

@media (min-width: 480px) {
  .menu-grid { columns: 3; }
}

/* ── Pin individual — imagen ilustrativa + título debajo ── */
.menu-pin {
  break-inside: avoid;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  padding: 12px 8px 14px;
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  cursor: pointer;
  text-align: center;
  box-shadow: var(--shadow-card);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;

  /* Animación escalonada desde la derecha */
  opacity: 0;
  animation: slideInRight 0.5s cubic-bezier(0.22, 1, 0.36, 1) both;
}

/* Stagger: los índices más altos (derecha en masonry) primero */
.stagger-0 { animation-delay: 520ms; }
.stagger-1 { animation-delay: 455ms; }
.stagger-2 { animation-delay: 390ms; }
.stagger-3 { animation-delay: 325ms; }
.stagger-4 { animation-delay: 260ms; }
.stagger-5 { animation-delay: 195ms; }
.stagger-6 { animation-delay: 130ms; }
.stagger-7 { animation-delay: 65ms;  }
.stagger-8 { animation-delay: 0ms;   }
.stagger-9 { animation-delay: 0ms;   }

.menu-pin:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-modal);
  border-color: var(--border-glow);
}
.menu-pin:active { transform: scale(0.97); }

/* Imagen ilustrativa — sin recorte, se ve completa */
.menu-pin-img-wrap {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.menu-pin-img {
  width: 100%;
  max-height: 100px;
  object-fit: contain;
  display: block;
  border-radius: var(--radius-sm);
}

/* Título siempre visible debajo de la imagen */
.menu-pin-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
  text-align: center;
}

/* ── Sección productos recientes ── */
.recent-section {
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 16px;
  box-shadow: var(--shadow-card);
  display: flex; flex-direction: column; gap: 12px;
}

.recent-header { display: flex; align-items: center; gap: 8px; }
.recent-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin: 0; }
.recent-badge {
  font-size: 11px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
  background: var(--accent-gold-dim);
  color: var(--accent-gold);
  border: 1px solid var(--border-glow);
}

.recent-skeletons { display: flex; flex-direction: column; gap: 8px; }
.recent-skeleton {
  height: 60px; border-radius: var(--radius-sm);
  background: var(--bg-card-hover);
  animation: shimmer 1.4s ease-in-out infinite;
}
@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.45; }
}

.recent-empty {
  display: flex; flex-direction: column; align-items: center;
  gap: 8px; padding: 2rem 0;
  color: var(--text-muted); font-size: 13px;
}

.recent-list { display: flex; flex-direction: column; gap: 6px; }

.recent-item {
  display: flex; align-items: center; gap: 12px;
  padding: 8px 10px;
  background: var(--bg-input);
  border: 1px solid transparent;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background 0.18s, border-color 0.18s;
}
.recent-item:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-subtle);
}

.recent-item-img {
  width: 44px; height: 44px;
  border-radius: var(--radius-xs);
  overflow: hidden; flex-shrink: 0;
  background: var(--bg-card-hover);
}
.recent-item-img img {
  width: 100%; height: 100%; object-fit: cover;
}

.recent-item-info { flex: 1; min-width: 0; }
.recent-item-name {
  font-size: 13px; font-weight: 500;
  color: var(--text-primary); margin: 0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.recent-item-meta {
  font-size: 11px; color: var(--text-muted); margin: 2px 0 0;
}

.recent-item-price {
  display: flex; align-items: baseline; gap: 1px;
  color: var(--accent-emerald);
  font-size: 14px; font-weight: 700;
  white-space: nowrap; flex-shrink: 0;
}
.price-symbol { font-size: 11px; opacity: 0.8; }

.ver-mas {
  display: flex; align-items: center; justify-content: center; gap: 6px;
  width: 100%; padding: 10px;
  background: var(--bg-input);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  font-size: 13px; font-weight: 500; cursor: pointer;
  transition: all 0.2s ease;
}
.ver-mas:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  color: var(--text-primary); gap: 10px;
}
</style>