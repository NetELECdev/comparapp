<template>
  <div class="favoritos-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Mis Favoritos</h1>
            <p class="page-subtitle">{{ favoritos.length }} producto{{ favoritos.length !== 1 ? 's' : '' }} guardado{{ favoritos.length !== 1 ? 's' : '' }}</p>
          </div>
        </div>
      </header>

      <!-- LISTA DE FAVORITOS -->
      <div v-if="favoritos.length > 0" class="favoritos-lista animate-fade-in-up stagger-1">
        <div
          v-for="(item, index) in favoritosOrdenados"
          :key="item.id_prod"
          class="favorito-card"
          :class="'stagger-' + Math.min(index + 2, 8)"
        >
          <NuxtLink :to="`/productos/${item.id_prod}`" class="fav-link">
            <div class="fav-img">
              <img :src="item.imagen_prod || '/images/avatar_default.png'" :alt="item.nombre_prod" />
            </div>
            <div class="fav-info">
              <span class="fav-categoria">{{ item.cate_prod }}</span>
              <h3 class="fav-nombre">{{ item.nombre_prod }}</h3>
              <p class="fav-marca">{{ item.marca_prod }}</p>
              <p class="fav-comercio">{{ item.comercio_prod }}</p>
              <span class="fav-precio">${{ formatPrice(item.precio_prod) }}</span>
            </div>
          </NuxtLink>
          
          <div class="fav-actions">
            <button 
              class="fav-remove-btn" 
              @click="eliminarFavorito(item.id_prod)"
              aria-label="Eliminar de favoritos"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 6 6 18"/>
                <path d="m6 6 12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- EMPTY STATE -->
      <div v-else class="empty-state animate-fade-in-up stagger-1">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"/>
          </svg>
        </div>
        <h3>No tenés favoritos</h3>
        <p>Agregá productos a favoritos tocando el corazón ❤️</p>
        <button class="back-btn-text" @click="navigateTo('/productos/lista')">
          Explorar productos
        </button>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { navigateTo } from '#app'

const { favoritos, eliminarFavorito } = useFavoritos()

const favoritosOrdenados = computed(() => {
  return [...favoritos.value].sort((a, b) => 
    new Date(b.fecha_agregado).getTime() - new Date(a.fecha_agregado).getTime()
  )
})

function formatPrice(price) {
  return Number(price)?.toLocaleString('es-AR') || '0'
}
</script>

<style scoped>
.favoritos-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-card-hover: rgba(255, 255, 255, 0.06);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-glow: rgba(232, 196, 160, 0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245, 240, 235, 0.6);
  --text-muted: rgba(245, 240, 235, 0.35);
  --accent-gold: #e8c4a0;
  --accent-violet: #a78bfa;
  --radius-sm: 12px;
  --radius-md: 16px;
  --radius-lg: 20px;
  --radius-xl: 24px;

  position: relative;
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

.bg-gradient {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232, 196, 160, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167, 139, 250, 0.05), transparent),
    linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 40%, #0a0a0f 100%);
  z-index: 0;
}

.bg-noise {
  position: fixed;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
  z-index: 1;
  pointer-events: none;
}

.page-content {
  position: relative;
  z-index: 2;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  max-width: 600px;
  margin: 0 auto;
  padding-bottom: 2.5rem;
}

@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.animate-fade-in-up {
  opacity: 0;
  animation: fadeInUp 0.5s ease-out forwards;
}

.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }
.stagger-3 { animation-delay: 0.15s; }
.stagger-4 { animation-delay: 0.2s; }
.stagger-5 { animation-delay: 0.25s; }
.stagger-6 { animation-delay: 0.3s; }
.stagger-7 { animation-delay: 0.35s; }
.stagger-8 { animation-delay: 0.4s; }

/* ─── HEADER ─── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.875rem;
}

.back-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
  flex-shrink: 0;
}

.back-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-glow);
  color: var(--text-primary);
  transform: scale(1.05);
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.page-subtitle {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.15rem 0 0;
}

/* ─── FAVORITOS LISTA ─── */
.favoritos-lista {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.favorito-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.favorito-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.favorito-card:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-glow);
  transform: translateY(-2px);
}

.fav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  text-decoration: none;
  color: inherit;
  min-width: 0;
}

.fav-img {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  flex-shrink: 0;
}

.fav-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fav-info {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
  flex: 1;
}

.fav-categoria {
  display: inline-flex;
  align-self: flex-start;
  padding: 0.15rem 0.5rem;
  background: rgba(232, 196, 160, 0.1);
  border: 1px solid rgba(232, 196, 160, 0.2);
  border-radius: 999px;
  color: var(--accent-gold);
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.fav-nombre {
  font-size: 0.95rem;
  font-weight: 600;
  margin: 0;
  line-height: 1.2;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fav-marca {
  color: var(--text-secondary);
  font-size: 0.8rem;
  margin: 0;
}

.fav-comercio {
  color: var(--text-muted);
  font-size: 0.75rem;
  margin: 0;
}

.fav-precio {
  color: #4ade80;
  font-size: 1.1rem;
  font-weight: 700;
  margin-top: 0.25rem;
}

.fav-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  flex-shrink: 0;
}

.fav-remove-btn {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.25s ease;
}

.fav-remove-btn:hover {
  background: rgba(251, 113, 133, 0.15);
  border-color: rgba(251, 113, 133, 0.3);
  color: #fb7185;
  transform: scale(1.1);
}

/* ─── EMPTY STATE ─── */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 4rem 1rem;
  text-align: center;
}

.empty-icon-wrap {
  width: 64px;
  height: 64px;
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fb7185;
}

.empty-state h3 {
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.empty-state p {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0;
}

.back-btn-text {
  margin-top: 0.5rem;
  padding: 0.625rem 1.25rem;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.85rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
}

.back-btn-text:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: var(--border-glow);
  color: var(--text-primary);
}

@media (max-width: 480px) {
  .page-content { padding: 1rem; }
  .page-title { font-size: 1.25rem; }
  .fav-img { width: 56px; height: 56px; }
}

@media (min-width: 640px) {
  .page-content {
    max-width: 640px;
    padding: 2rem;
  }
}
</style>