<!-- pages/dashboard/index.vue -->
<template>
  <div class="dashboard" :class="{ 'is-dark': esDark }">

    <!-- Fondo dinámico -->
    <DynamicBackground />

    <!-- Header -->
    <header class="dash-header">
      <div class="dash-header-left">
        <button class="dash-avatar" @click="navigateTo('/perfil')" aria-label="Mi perfil">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
            <circle cx="12" cy="7" r="4"/>
          </svg>
        </button>
        <div>
          <p class="dash-greeting">Hola, {{ user?.nombre_completo?.split(' ')[0] || 'Usuario' }} 👋</p>
          <p class="dash-sub">¿Qué comparamos hoy?</p>
        </div>
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
              <p class="recent-item-meta">{{ p.provee_prod }} · {{ p.cate_prod }}</p>
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

    <!-- Bottom nav flotante glassmorphism -->
    <nav class="bottom-nav" aria-label="Navegación principal">
      <button class="bnav-btn bnav-btn--active" @click="navigateTo('/dashboard')" aria-label="Inicio" aria-current="page">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
          <polyline points="9 22 9 12 15 12 15 22"/>
        </svg>
        <span>Inicio</span>
      </button>
      <button class="bnav-btn" @click="navigateTo('/productos')" aria-label="Productos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="m7.5 4.27 9 5.15"/>
          <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
          <path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
        </svg>
        <span>Productos</span>
      </button>
      <button class="bnav-btn bnav-btn--center" @click="navigateTo('/comparaciones')" aria-label="Comparar">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
          <path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/>
          <path d="M7 21h10"/><path d="M12 3v18"/>
          <path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/>
        </svg>
      </button>
      <button class="bnav-btn" @click="navigateTo('/favoritos')" aria-label="Favoritos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
        <span>Favoritos</span>
      </button>
      <button class="bnav-btn" @click="navigateTo('/perfil')" aria-label="Perfil">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
        <span>Perfil</span>
      </button>
    </nav>

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
  provee_prod: string
  precio_prod: string
  imagen_prod: string | null
  marca_prod: string
  activo_prod: boolean
}

const config = useRuntimeConfig()
const user = ref<any>(null)
const products = ref<Producto[]>([])
const loadingProducts = ref(true)

const SUPABASE = 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images'

// Estructura fiel al dashV1: imagen ilustrativa + título debajo
// Distribución masonry: columna izquierda y derecha con tamaños variables
const menuItems = ref([
  { title: 'Alertas',     imageUrl: `${SUPABASE}/alerta.jpg`,      action: () => navigateTo('/alertas') },
  { title: 'Comparador',  imageUrl: `${SUPABASE}/comparador.jpg`,  action: () => navigateTo('/comparaciones') },
  { title: 'Favoritos',   imageUrl: `${SUPABASE}/favoritos.jpg`,   action: () => navigateTo('/favoritos') },
  { title: 'Historial',   imageUrl: `${SUPABASE}/historial.jpg`,   action: () => navigateTo('/comparaciones/historial') },
  { title: 'Listas',      imageUrl: `${SUPABASE}/lista.jpg`,       action: () => navigateTo('/listas') },
  { title: 'Productos',   imageUrl: `${SUPABASE}/productos.jpg`,   action: () => navigateTo('/productos') },
  { title: 'Proveedores', imageUrl: `${SUPABASE}/proveedores.jpg`, action: () => navigateTo('/proveedores') },
  { title: 'Ofertas',     imageUrl: `${SUPABASE}/ofertas.jpg`,     action: () => navigateTo('/ofertas') },
  { title: 'Perfil',      imageUrl: `${SUPABASE}/admin.jpg`,       action: () => navigateTo('/perfil') },
  { title: 'Admin',       imageUrl: `${SUPABASE}/admin.jpg`,       action: () => navigateTo('/admin') },
])

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch {}
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

.dash-avatar {
  width: 36px; height: 36px;
  border-radius: 50%;
  background: var(--bg-card-hover);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; flex-shrink: 0;
  transition: border-color 0.2s;
}
.dash-avatar:hover { border-color: var(--border-glow); }

.dash-greeting {
  font-size: 14px; font-weight: 600;
  color: var(--text-primary); margin: 0; line-height: 1.2;
}
.dash-sub {
  font-size: 11px; color: var(--text-secondary); margin: 0;
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

/* ── Bottom nav flotante glassmorphism ── */
.bottom-nav {
  position: fixed;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  width: calc(100% - 32px);
  max-width: 480px;
  display: flex; align-items: center; justify-content: space-around;
  padding: 10px 12px;
  background: var(--bg-overlay);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  z-index: 100;
}

.bnav-btn {
  display: flex; flex-direction: column; align-items: center; gap: 3px;
  background: none; border: none;
  color: var(--text-muted);
  font-size: 10px; font-weight: 500;
  cursor: pointer;
  padding: 6px 10px; border-radius: var(--radius-sm);
  transition: color 0.2s, background 0.2s;
}
.bnav-btn:hover { color: var(--text-secondary); background: var(--bg-card-hover); }
.bnav-btn--active { color: var(--accent-gold); }

.bnav-btn--center {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--accent-gold-dim);
  border: 1px solid var(--border-glow);
  color: var(--accent-gold);
  padding: 0;
  display: flex; align-items: center; justify-content: center;
  margin-top: -14px;
  box-shadow: 0 4px 16px rgba(232, 196, 160, 0.25);
}
.bnav-btn--center:hover { background: rgba(232, 196, 160, 0.2); }

@media (min-width: 480px) {
  .bottom-nav { max-width: 520px; }
}
</style>
