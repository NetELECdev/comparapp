<!-- pages/productos/[id].vue -->
<template>
  <div class="producto-detalle-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/Productos/lista')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Detalle</h1>
            <p class="page-subtitle">{{ producto?.nombre_prod || 'Producto' }}</p>
          </div>
        </div>
      </header>

      <!-- LOADING -->
      <div v-if="loading" class="loading-state animate-fade-in-up">
        <div class="loading-spinner" />
        <p>Cargando producto...</p>
      </div>

      <!-- DETALLE DEL PRODUCTO -->
      <div v-else-if="producto" class="detalle-card animate-fade-in-up stagger-1">
        <!-- Imagen -->
        <div class="detalle-img">
          <img 
            :src="producto.imagen_prod || '/images/avatar_default.png'" 
            :alt="producto.nombre_prod"
            @error="onImageError"
          />
        </div>

        <!-- Info principal -->
        <div class="detalle-info">
          <span class="detalle-categoria">{{ producto.cate_prod }}</span>
          <h2 class="detalle-nombre">{{ producto.nombre_prod }}</h2>
          <p class="detalle-marca">{{ producto.marca_prod }}</p>
          
          <div class="detalle-precio-wrap">
            <span class="detalle-precio">${{ formatPrice(producto.precio_prod) }}</span>
            <span class="detalle-unidad">{{ producto.cantidad_prod }} {{ producto.unidad_prod }}</span>
          </div>

          <p class="detalle-proveedor">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 7h-9"/>
              <path d="M14 17H5"/>
              <circle cx="17" cy="17" r="3"/>
              <circle cx="7" cy="7" r="3"/>
            </svg>
            {{ producto.provee_prod }}
          </p>

          <p v-if="producto.describe_prod" class="detalle-descripcion">
            {{ producto.describe_prod }}
          </p>
        </div>

        <!-- Acciones -->
        <div class="detalle-acciones">
          <!-- Selector de cantidad -->
          <div class="quantity-selector">
            <button class="qty-btn qty-minus" :disabled="cantidad <= 1" @click="cantidad--">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12h14"/>
              </svg>
            </button>
            <span class="qty-value">{{ cantidad }}</span>
            <button class="qty-btn qty-plus" @click="cantidad++">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M5 12h14"/>
                <path d="M12 5v14"/>
              </svg>
            </button>
          </div>

          <!-- Botón comparar -->
          <button 
            class="compare-btn-detalle" 
            :class="{ added: wasAdded }"
            @click="agregarAComparacion"
            :disabled="wasAdded"
          >
            <span v-if="wasAdded">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M20 6 9 17l-5-5"/>
              </svg>
              Agregado
            </span>
            <span v-else>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M3 6h18"/>
                <path d="M7 12h10"/>
                <path d="M10 18h4"/>
              </svg>
              Comparar
            </span>
          </button>
        </div>
      </div>

      <!-- ERROR: Producto no encontrado -->
      <div v-else class="empty-state animate-fade-in-up">
        <div class="empty-icon-wrap">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.3-4.3"/>
          </svg>
        </div>
        <h3>Producto no encontrado</h3>
        <p>El producto que buscás no existe o fue eliminado</p>
        <button class="back-btn-text" @click="navigateTo('/Productos/lista')">
          Volver al listado
        </button>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRuntimeConfig, navigateTo } from '#app'

// ─── Interface ───
interface Producto {
  id_prod: string
  nombre_prod: string
  marca_prod: string
  precio_prod: string
  cate_prod: string
  imagen_prod: string | null
  provee_prod: string
  fecha_prod?: string
  activo_prod: boolean
  describe_prod?: string
  cantidad_prod?: number
  unidad_prod?: string
}

// ─── Estado ───
const route = useRoute()
const config = useRuntimeConfig()
const loading = ref(true)
const producto = ref<Producto | null>(null)
const cantidad = ref(1)
const wasAdded = ref(false)

// ─── Métodos ───
function formatPrice(price: string | number): string {
  return Number(price)?.toLocaleString('es-AR') || '0'
}

function onImageError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = '/images/avatar_default.png'
}

function agregarAComparacion() {
  if (!producto.value) return
  
  const item = { ...producto.value, cantidad: cantidad.value }
  const stored = localStorage.getItem('comparapp_comparacion')
  let comparacion: any[] = []
  
  try {
    comparacion = stored ? JSON.parse(stored) : []
  } catch {}
  
  const existente = comparacion.find((p: any) => p.id_prod === item.id_prod)
  if (existente) {
    existente.cantidad = item.cantidad
  } else {
    comparacion.push(item)
  }
  
  localStorage.setItem('comparapp_comparacion', JSON.stringify(comparacion))
  wasAdded.value = true
  
  setTimeout(() => {
    wasAdded.value = false
    cantidad.value = 1
  }, 2000)
}

// ─── Cargar producto ───
onMounted(async () => {
  const id = route.params.id as string
  
  // Validar UUID
  const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
  if (!uuidRegex.test(id)) {
    loading.value = false
    return
  }

  try {
    // Usar el endpoint específico por ID (más rápido)
    producto.value = await $fetch<Producto>(
      `${config.public.apiBase}/products/${id}`
    )
  } catch (err) {
    console.error('Error cargando producto:', err)
    producto.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.producto-detalle-page {
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
  max-width: 600px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
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

.stagger-1 { animation-delay: 0.1s; }

/* ─── HEADER ─── */
.page-header {
  display: flex;
  align-items: center;
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
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 250px;
}

/* ─── LOADING ─── */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.875rem;
  padding: 4rem 1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}

.loading-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid rgba(255, 255, 255, 0.1);
  border-top-color: var(--accent-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ─── DETALLE CARD ─── */
.detalle-card {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  background: var(--bg-card);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-xl);
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

.detalle-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
}

.detalle-img {
  width: 100%;
  aspect-ratio: 1;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}

.detalle-img img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  padding: 1rem;
}

/* ─── INFO ─── */
.detalle-info {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.detalle-categoria {
  display: inline-flex;
  align-self: flex-start;
  padding: 0.25rem 0.75rem;
  background: rgba(232, 196, 160, 0.1);
  border: 1px solid rgba(232, 196, 160, 0.2);
  border-radius: 999px;
  color: var(--accent-gold);
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.detalle-nombre {
  font-size: 1.35rem;
  font-weight: 700;
  margin: 0.25rem 0 0;
  line-height: 1.2;
  letter-spacing: -0.01em;
}

.detalle-marca {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

.detalle-precio-wrap {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.detalle-precio {
  color: #4ade80;
  font-size: 1.85rem;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.detalle-unidad {
  color: var(--text-muted);
  font-size: 0.8rem;
}

.detalle-proveedor {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.5rem 0 0;
}

.detalle-proveedor svg {
  color: var(--accent-violet);
}

.detalle-descripcion {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0.75rem 0 0;
  padding-top: 0.75rem;
  border-top: 1px solid var(--border-subtle);
}

/* ─── ACCIONES ─── */
.detalle-acciones {
  display: flex;
  align-items: center;
  gap: 0.875rem;
  margin-top: 0.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-subtle);
}

.quantity-selector {
  display: flex;
  align-items: center;
  gap: 0;
  background: rgba(255, 255, 255, 0.04);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  overflow: hidden;
}

.qty-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: rgba(245, 240, 235, 0.6);
  cursor: pointer;
  transition: all 0.2s ease;
}

.qty-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.08);
  color: #f5f0eb;
}

.qty-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.qty-minus { border-right: 1px solid rgba(255, 255, 255, 0.06); }
.qty-plus { border-left: 1px solid rgba(255, 255, 255, 0.06); }

.qty-value {
  min-width: 36px;
  text-align: center;
  color: #f5f0eb;
  font-size: 0.95rem;
  font-weight: 600;
  padding: 0 0.25rem;
}

.compare-btn-detalle {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.2), rgba(167, 139, 250, 0.1));
  border: 1px solid rgba(167, 139, 250, 0.3);
  border-radius: var(--radius-md);
  color: #c4b5fd;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
}

.compare-btn-detalle:hover:not(:disabled) {
  background: linear-gradient(135deg, rgba(167, 139, 250, 0.3), rgba(167, 139, 250, 0.2));
  border-color: rgba(167, 139, 250, 0.5);
  color: #ddd6fe;
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(167, 139, 250, 0.15);
}

.compare-btn-detalle.added {
  background: linear-gradient(135deg, rgba(52, 211, 153, 0.15), rgba(52, 211, 153, 0.1));
  border-color: rgba(52, 211, 153, 0.3);
  color: #6ee7b7;
}

.compare-btn-detalle:disabled {
  cursor: default;
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
  color: var(--text-muted);
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
  margin-top: 0.75rem;
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
  .detalle-card { padding: 1.25rem; }
  .detalle-precio { font-size: 1.6rem; }
  .page-subtitle { max-width: 200px; }
}
</style>