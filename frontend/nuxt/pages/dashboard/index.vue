<template>
  <div class="dashboard">
    <div class="bg-noise" />

    <main class="dashboard-content">
      <header class="header animate-fade-in-up">
        <div class="header-brand">
          <div class="header-logo-wrap">
            <img src="/images/capp3D_elec.png" class="header-logo" alt="ComparApp" />
          </div>
          <div class="header-text">
            <p class="header-greeting">
              Hola, {{ user?.nombre_completo || 'Usuario' }}
              <span class="wave">👋</span>
            </p>
            <p class="header-sub">¿Qué querés comparar hoy?</p>
          </div>
        </div>
        <div class="header-actions">
          <ToggleTema />
          <button class="header-avatar" @click="navigateTo('/perfil')" aria-label="Mi perfil">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </button>
        </div>
      </header>

      <nav class="grid" aria-label="Navegación principal">
        <button
          v-for="(item, index) in menuItems"
          :key="item.title"
          class="card animate-fade-in-up"
          :class="[`stagger-${index + 1}`, item.accent && 'card--accent']"
          @click="item.action"
        >
          <div class="card-icon-wrap" :class="item.iconColor">
            <component :is="item.icon" class="card-icon-svg" />
          </div>
          <div class="card-text">
            <span class="card-title">{{ item.title }}</span>
            <span class="card-desc">{{ item.desc }}</span>
          </div>
          <svg class="card-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="m9 18 6-6-6-6"/>
          </svg>
        </button>
      </nav>

      <section class="section animate-fade-in-up stagger-7">
        <div class="section-header">
          <h3 class="section-title">Productos recientes</h3>
          <span class="section-badge" v-if="products.length > 0">{{ products.length }}</span>
        </div>

        <div v-if="loadingProducts" class="loading-state">
          <div class="loading-spinner" />
          <span>Cargando productos...</span>
        </div>

        <div v-else-if="products.length === 0" class="empty-state">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
          <p>No se encontraron productos</p>
        </div>

        <div v-else class="products-list">
          <article
            v-for="p in products.slice(0, 5)"
            :key="p.id_prod"
            class="product-item"
            @click="navigateTo(`/Productos/lista?q=${encodeURIComponent(p.nombre_prod)}`)"
          >
            <div class="product-img-wrap">
              <img
                :src="p.imagen_prod || '/images/avatar_default.png'"
                :alt="p.nombre_prod"
                class="product-img"
                @error="(e) => (e.target as HTMLImageElement).src = '/images/avatar_default.png'"
              />
            </div>
            <div class="product-info">
              <p class="product-name">{{ p.nombre_prod }}</p>
              <div class="product-meta">
                <span class="product-venue">{{ p.provee_prod }}</span>
                <span class="product-dot">•</span>
                <span class="product-cat">{{ p.cate_prod }}</span>
              </div>
            </div>
            <div class="product-price">
              <span class="price-currency">$</span>
              <span class="price-value">{{ Number(p.precio_prod).toLocaleString('es-AR') }}</span>
            </div>
          </article>
        </div>

        <button v-if="products.length > 0" class="ver-mas" @click="navigateTo('/Productos')">
          <span>Ver todos los productos</span>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M5 12h14"/>
            <path d="m12 5 7 7-7 7"/>
          </svg>
        </button>
      </section>

      <footer class="footer animate-fade-in-up stagger-8">
        <p>ComparApp <span class="footer-year">© 2025</span></p>
      </footer>
    </main>

    <div class="bottom-bar">
      <button class="bottom-btn" @click="navigateTo('/dashboard')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Inicio</span>
      </button>
      <button class="bottom-btn bottom-btn--accent" @click="navigateTo('/Productos')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
        <span>Comparar</span>
      </button>
      <button class="bottom-btn" @click="navigateTo('/Productos/lista')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
        <span>Productos</span>
      </button>
      <button class="bottom-btn" @click="navigateTo('/perfil')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Perfil</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, h } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

// ── Composables globales ──────────────────────────────────────
useTema()        // inicializa tema (dark/light) desde localStorage
useBackground()  // inicia el ciclo de fondos

// ── Interfaces ────────────────────────────────────────────────
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

// ── Íconos ────────────────────────────────────────────────────
const IconPackage = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'm7.5 4.27 9 5.15' }),
  h('path', { d: 'M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z' }),
  h('path', { d: 'm3.3 7 8.7 5 8.7-5' }),
  h('path', { d: 'M12 22V12' })
])
const IconStore = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z' }),
  h('path', { d: 'm3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9' }),
  h('path', { d: 'M12 3v6' })
])
const IconScale = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'm16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z' }),
  h('path', { d: 'm2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z' }),
  h('path', { d: 'M7 21h10' }), h('path', { d: 'M12 3v18' }),
  h('path', { d: 'M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2' })
])
const IconHistory = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8' }),
  h('path', { d: 'M3 3v5h5' }), h('path', { d: 'M12 7v5l4 2' })
])
const IconStar = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('polygon', { points: '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2' })
])
const IconBell = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9' }),
  h('path', { d: 'M10.3 21a1.94 1.94 0 0 0 3.4 0' })
])
const IconFlame = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z' })
])
const IconUser = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
  h('circle', { cx: '12', cy: '7', r: '4' })
])
const IconLista = () => h('svg', { width: 22, height: 22, viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 2, 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
  h('line', { x1: '8', y1: '6', x2: '21', y2: '6' }),
  h('line', { x1: '8', y1: '12', x2: '21', y2: '12' }),
  h('line', { x1: '8', y1: '18', x2: '21', y2: '18' }),
  h('line', { x1: '3', y1: '6', x2: '3.01', y2: '6' }),
  h('line', { x1: '3', y1: '12', x2: '3.01', y2: '12' }),
  h('line', { x1: '3', y1: '18', x2: '3.01', y2: '18' }),
])

// ── Estado ────────────────────────────────────────────────────
const config = useRuntimeConfig()
const user = ref<any>(null)
const products = ref<Producto[]>([])
const loadingProducts = ref(true)

const menuItems = ref([
  { title: 'Productos',   desc: 'Buscá y compará precios',      icon: IconPackage, iconColor: 'icon-blue',   action: () => navigateTo('/Productos') },
  { title: 'Proveedores', desc: 'Comercios y supermercados',     icon: IconStore,   iconColor: 'icon-amber',  action: () => navigateTo('/proveedores') },
  { title: 'Comparador',  desc: 'Compará entre comercios',       icon: IconScale,   iconColor: 'icon-emerald',action: () => navigateTo('/comparaciones') },
  { title: 'Mis Listas',  desc: 'Organizá tu compra',            icon: IconLista,   iconColor: 'icon-teal',   action: () => navigateTo('/listas') },
  { title: 'Historial',   desc: 'Tus búsquedas anteriores',      icon: IconHistory, iconColor: 'icon-violet', action: () => navigateTo('/comparaciones/historial') },
  { title: 'Favoritos',   desc: 'Productos que seguís',          icon: IconStar,    iconColor: 'icon-rose',   action: () => navigateTo('/favoritos') },
  { title: 'Alertas',     desc: 'Avisame cuando baje',           icon: IconBell,    iconColor: 'icon-orange', action: () => showComingSoon('Alertas') },
  { title: 'Ofertas',     desc: 'Las mejores promo de hoy',      icon: IconFlame,   iconColor: 'icon-fire',   accent: true, action: () => navigateTo('/ofertas') },
  { title: 'Mi Perfil',   desc: 'Configurá tu cuenta',           icon: IconUser,    iconColor: 'icon-slate',  action: () => navigateTo('/perfil') },
  { title: 'Admin',       desc: 'Panel de administración',       icon: IconUser,    iconColor: 'icon-slate',  action: () => user.value?.rol === 'admin' ? navigateTo('/admin') : null },
])

onMounted(async () => {
  const stored = localStorage.getItem('comparapp_user')
  if (stored) {
    try { user.value = JSON.parse(stored) } catch {}
  }
  try {
    const res = await $fetch<{ count: number; results: Producto[] }>(`${config.public.apiBase}/products`)
    products.value = res.results || []
  } catch (err) {
    console.error('Error cargando productos:', err)
  } finally {
    loadingProducts.value = false
  }
})

const showComingSoon = (name: string) => alert(`${name} — Próximamente disponible`)
</script>

<style scoped>
/* ─────────────────────────────────────────────────────────────
   DASHBOARD — usa las variables globales de tokens.css
   NO redefinir variables de color aquí: rompe el tema
───────────────────────────────────────────────────────────── */

.dashboard {
  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.bg-noise {
  position: fixed; inset: 0; opacity: 0.03; z-index: 1; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

.dashboard-content {
  position: relative; z-index: 2;
  padding: 1.5rem; padding-bottom: 5rem;
  display: flex; flex-direction: column; gap: 1.5rem;
  max-width: 480px; margin: 0 auto;
}

/* ─── ANIMACIONES ─── */
@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }
@keyframes wave { 0%, 100% { transform: rotate(0deg); } 25% { transform: rotate(20deg); } 75% { transform: rotate(-10deg); } }

.animate-fade-in-up { opacity: 0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1  { animation-delay: 0.05s; }
.stagger-2  { animation-delay: 0.1s; }
.stagger-3  { animation-delay: 0.15s; }
.stagger-4  { animation-delay: 0.2s; }
.stagger-5  { animation-delay: 0.25s; }
.stagger-6  { animation-delay: 0.3s; }
.stagger-7  { animation-delay: 0.35s; }
.stagger-8  { animation-delay: 0.4s; }
.wave { display: inline-block; animation: wave 2s ease-in-out infinite; transform-origin: 70% 70%; }

/* ─── HEADER ─── */
.header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1rem 1.25rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
}
.header-brand { display: flex; align-items: center; gap: 0.875rem; }
.header-logo-wrap {
  width: 84px; height: 55px; border-radius: var(--radius-sm);
  background: rgba(22, 22, 22, 0.05);
  display: flex; align-items: center; justify-content: center;
  border: 1px solid rgba(232, 196, 160, 0.15);
}
.header-logo { width: 72px; height: 72px; object-fit: contain; }
.header-text { display: flex; flex-direction: column; gap: 0.15rem; }
.header-greeting { color: var(--text-primary); font-size: 0.95rem; font-weight: 600; margin: 0; }
.header-sub { color: var(--text-secondary); font-size: 0.78rem; margin: 0; }
.header-actions { display: flex; align-items: center; gap: 0.5rem; }
.header-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.25s ease;
}
.header-avatar:hover { background: var(--bg-card-hover); border-color: var(--border-glow); color: var(--text-primary); }

/* ─── GRID ─── */
.grid {
  display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.75rem;
}

/* ─── CARDS ─── */
.card {
  position: relative; display: flex; flex-direction: column; gap: 0.625rem;
  padding: 1.125rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  text-align: left; cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}
.card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}
.card--accent {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.08), rgba(167, 139, 250, 0.05));
  border-color: rgba(232, 196, 160, 0.2);
}
.card--accent:hover { border-color: rgba(232, 196, 160, 0.35); }

.card-icon-wrap {
  width: 42px; height: 42px; border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}

/* Colores de íconos */
.icon-blue    { background: rgba(96,165,250,0.12);  border: 1px solid rgba(96,165,250,0.2);  color: #60a5fa; }
.icon-amber   { background: rgba(251,191,36,0.12);  border: 1px solid rgba(251,191,36,0.2);  color: #fbbf24; }
.icon-emerald { background: rgba(52,211,153,0.12);  border: 1px solid rgba(52,211,153,0.2);  color: #34d399; }
.icon-teal    { background: rgba(45,212,191,0.12);  border: 1px solid rgba(45,212,191,0.2);  color: #2dd4bf; }
.icon-violet  { background: rgba(167,139,250,0.12); border: 1px solid rgba(167,139,250,0.2); color: #a78bfa; }
.icon-rose    { background: rgba(251,113,133,0.12); border: 1px solid rgba(251,113,133,0.2); color: #fb7185; }
.icon-orange  { background: rgba(251,146,60,0.12);  border: 1px solid rgba(251,146,60,0.2);  color: #fb923c; }
.icon-fire    { background: rgba(232,196,160,0.12); border: 1px solid rgba(232,196,160,0.2); color: #e8c4a0; }
.icon-slate   { background: rgba(148,163,184,0.12); border: 1px solid rgba(148,163,184,0.2); color: #94a3b8; }

.card-text { display: flex; flex-direction: column; gap: 0.2rem; }
.card-title { color: var(--text-primary); font-size: 0.88rem; font-weight: 600; }
.card-desc  { color: var(--text-secondary); font-size: 0.72rem; line-height: 1.35; }
.card-arrow {
  position: absolute; top: 1rem; right: 1rem;
  color: var(--text-muted); opacity: 0;
  transform: translateX(-4px); transition: all 0.25s ease;
}
.card:hover .card-arrow { opacity: 1; transform: translateX(0); color: var(--text-secondary); }

/* ─── SECCIÓN PRODUCTOS ─── */
.section {
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-card);
}
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1rem; }
.section-title { color: var(--text-primary); font-size: 1rem; font-weight: 600; margin: 0; }
.section-badge {
  background: rgba(232, 196, 160, 0.12); color: var(--accent-gold);
  font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.625rem;
  border-radius: 999px; border: 1px solid rgba(232, 196, 160, 0.2);
}

.loading-state, .empty-state {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 2rem 0;
  color: var(--text-muted); font-size: 0.9rem;
}
.loading-spinner {
  width: 24px; height: 24px;
  border: 2px solid var(--border-subtle);
  border-top-color: var(--accent-gold);
  border-radius: 50%; animation: spin 0.8s linear infinite;
}
.empty-state svg { color: var(--text-muted); opacity: 0.5; }

.products-list { display: flex; flex-direction: column; gap: 0.5rem; }
.product-item {
  display: flex; align-items: center; gap: 0.875rem; padding: 0.625rem;
  background: var(--bg-input);
  border-radius: var(--radius-md); border: 1px solid transparent;
  cursor: pointer; transition: all 0.2s ease;
}
.product-item:hover { background: var(--bg-card-hover); border-color: var(--border-subtle); }
.product-img-wrap {
  width: 44px; height: 44px; border-radius: var(--radius-sm);
  overflow: hidden; flex-shrink: 0; background: var(--bg-card);
}
.product-img { width: 100%; height: 100%; object-fit: cover; }
.product-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.2rem; }
.product-name { color: var(--text-primary); font-size: 0.85rem; font-weight: 500; margin: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.product-meta { display: flex; align-items: center; gap: 0.35rem; font-size: 0.72rem; }
.product-venue { color: var(--text-secondary); }
.product-dot   { color: var(--text-muted); }
.product-cat   { color: var(--text-muted); }
.product-price {
  display: flex; align-items: baseline; gap: 0.1rem;
  color: var(--accent-emerald);
  font-weight: 700; font-size: 0.9rem; white-space: nowrap; flex-shrink: 0;
}
.price-currency { font-size: 0.75rem; opacity: 0.8; }

.ver-mas {
  width: 100%; margin-top: 0.875rem; padding: 0.75rem;
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md); color: var(--text-secondary);
  font-size: 0.85rem; font-weight: 500; cursor: pointer;
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  transition: all 0.25s ease;
}
.ver-mas:hover { background: var(--bg-card-hover); border-color: var(--border-glow); color: var(--text-primary); gap: 0.75rem; }

/* ─── FOOTER ─── */
.footer { text-align: center; padding-top: 0.5rem; }
.footer p { color: var(--text-muted); font-size: 0.75rem; margin: 0; }
.footer-year { opacity: 0.6; }

/* ─── BOTTOM BAR ─── */
.bottom-bar {
  position: fixed; bottom: 0; left: 0; right: 0;
  display: flex; justify-content: space-around; align-items: center;
  padding: 0.75rem 1rem calc(0.75rem + env(safe-area-inset-bottom));
  background: var(--bg-overlay);
  backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px);
  border-top: 1px solid var(--border-subtle); z-index: 100;
}
.bottom-btn {
  display: flex; flex-direction: column; align-items: center; gap: 0.25rem;
  background: none; border: none; color: var(--text-muted);
  font-size: 0.65rem; font-weight: 500; cursor: pointer;
  padding: 0.5rem 1rem; border-radius: 12px; transition: all 0.2s;
}
.bottom-btn:hover { color: var(--text-secondary); background: var(--bg-card); }
.bottom-btn--accent {
  color: var(--accent-gold);
  background: var(--accent-gold-dim);
  border: 1px solid var(--border-glow);
}
.bottom-btn--accent:hover { background: rgba(232,196,160,0.18); }

/* ─── RESPONSIVE ─── */
@media (max-width: 360px) { .grid { grid-template-columns: 1fr; } .dashboard-content { padding: 1rem; } }
@media (min-width: 640px) { .dashboard-content { max-width: 520px; padding: 2rem; gap: 1.75rem; } }
</style>