<template>
  <section class="img-pend">
    <header class="ip-header">
      <div class="ip-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="9" cy="9" r="2"/><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"/>
        </svg>
        <span>Fotos pendientes</span>
        <span v-if="pendientes.length" class="ip-count">{{ pendientes.length }}</span>
      </div>
      <p class="ip-sub">
        Estos productos todavía no tienen foto propia (se muestran con la imagen de su categoría).
        Subí la foto real de cada uno; se aplica también al mismo producto en otros comercios.
      </p>
    </header>

      <div class="ip-progreso">
        <div class="ip-progreso-texto">
          <span><strong>{{ totalConImagen }}</strong> de <strong>{{ totalProductos }}</strong> con foto</span>
          <span>faltan <strong>{{ pendientes.length }}</strong></span>
        </div>
        <div class="ip-progreso-barra">
          <div class="ip-progreso-relleno" :style="{ width: porcentaje + '%' }"></div>
        </div>
      </div>


    <!-- Nada pendiente -->
    <div v-if="!pendientes.length" class="ip-empty">
      <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
      </svg>
      <p>¡Todos tus productos tienen foto! No queda nada pendiente.</p>
    </div>

    <!-- Grilla de pendientes -->
    <div v-else class="ip-grid">
      <article v-for="p in pendientesVisibles" :key="p.id_prod" class="ip-card">
        <div class="ip-thumb">
          <img :src="thumb(p)" :alt="p.nombre_prod" />
          <div v-if="subiendoId === p.id_prod" class="ip-thumb-overlay">
            <span class="ip-spinner" />
          </div>
        </div>
        <div class="ip-info">
          <span class="ip-name">{{ p.nombre_prod }}</span>
          <span class="ip-cat">{{ p.cate_prod }}</span>
        </div>
        <label class="ip-upload" :class="{ disabled: subiendoId === p.id_prod }">
          <input
            type="file"
            accept="image/jpeg,image/png,image/webp"
            hidden
            :disabled="subiendoId !== null"
            @change="(e) => onArchivo(e, p)"
          />
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          {{ subiendoId === p.id_prod ? 'Subiendo...' : 'Subir foto' }}
        </label>
      </article>
    </div>

    <button
      v-if="pendientes.length > visibles"
      class="ip-mostrar-mas"
      @click="mostrarMas"
    >
      Mostrar más ({{ pendientes.length - visibles }} restantes)
    </button>

    <p v-if="errorMsg" class="ip-error">{{ errorMsg }}</p>
    <p v-if="okMsg" class="ip-ok">{{ okMsg }}</p>
  </section>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRuntimeConfig } from '#app'

interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  imagen_prod: string | null
  [key: string]: any
}

const props = defineProps<{
  productos: Producto[]
  imagenPorCategoria?: Record<string, string>
}>()

const emit = defineEmits<{
  (e: 'actualizado'): void
}>()

const config = useRuntimeConfig()
const API = config.public.apiBase

const subiendoId = ref<string | null>(null)
const errorMsg = ref('')
const okMsg = ref('')

const totalConImagen = computed(() =>
  (props.productos || []).filter(p => p.imagen_prod).length
)
const totalProductos = computed(() => (props.productos || []).length)
const porcentaje = computed(() =>
  totalProductos.value ? Math.round(totalConImagen.value * 100 / totalProductos.value) : 0
)

// Solo los productos SIN foto propia
const pendientes = computed(() =>
  (props.productos || []).filter(p => !p.imagen_prod)
)

// Paginación: mostrar de a 24
const visibles = ref(24)
const pendientesVisibles = computed(() => pendientes.value.slice(0, visibles.value))
function mostrarMas() { visibles.value += 24 }

function getToken(): string {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? (JSON.parse(stored).access_token || '') : ''
  } catch {
    return ''
  }
}

// Placeholder de categoría mientras no tiene foto (mismo criterio que la grilla)
function thumb(p: Producto): string {
  const map = props.imagenPorCategoria || {}
  return map[(p.cate_prod || '').toLowerCase().trim()] || '/images/avatar_default.png'
}

async function onArchivo(e: Event, p: Producto) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  subiendoId.value = p.id_prod
  errorMsg.value = ''
  okMsg.value = ''
  try {
    const token = getToken()

    // 1) Subir la imagen al bucket
    const fd = new FormData()
    fd.append('file', file)
    const up = await $fetch<{ url: string }>(`${API}/upload-imagen-producto`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: fd,
    })

    // 2) Persistir en el producto
    await $fetch(`${API}/products/${p.id_prod}`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${token}` },
      body: { imagen_prod: up.url },
    })

    // 3) Propagar al mismo producto en otros comercios (foto compartida)
    try {
      await $fetch(`${API}/products/${p.id_prod}/imagen`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
        body: { imagen_prod: up.url },
      })
    } catch (e) {
      // Si la propagación falla, la foto igual quedó guardada en este producto.
      console.error('No se pudo propagar la imagen a otros comercios:', e)
    }

    okMsg.value = `Foto agregada a "${p.nombre_prod}"`
    setTimeout(() => (okMsg.value = ''), 2500)
    emit('actualizado')
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo subir la imagen. Probá de nuevo.'
  } finally {
    subiendoId.value = null
    input.value = ''
  }
}
</script>

<style scoped>
.img-pend {
  background: var(--bg-card, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  padding: 1.25rem;
  color: var(--text-primary, #f4f4f5);
}
.ip-progreso { margin: 0 0 1rem; }
.ip-progreso-texto {
  display: flex; justify-content: space-between;
  font-size: 0.82rem; color: var(--text-secondary, #a1a1aa); margin-bottom: 0.4rem;
}
.ip-progreso-texto strong { color: var(--text-primary, #f4f4f5); }
.ip-progreso-barra {
  height: 8px; border-radius: 999px;
  background: var(--bg-input, rgba(255,255,255,0.08)); overflow: hidden;
}
.ip-progreso-relleno {
  height: 100%; border-radius: 999px;
  background: var(--accent-gold, #e8c4a0); transition: width 0.4s ease;
}
.ip-header { margin-bottom: 1rem; }
.ip-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-weight: 700; font-size: 1.05rem;
}
.ip-title svg { color: var(--accent-gold, #e8c4a0); }
.ip-count {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 22px; height: 22px; padding: 0 7px;
  background: rgba(251, 191, 36, 0.15); border: 1px solid rgba(251, 191, 36, 0.3);
  color: #fbbf24; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
}
.ip-sub {
  margin: 0.35rem 0 0;
  font-size: 0.82rem;
  color: var(--text-secondary, #a1a1aa);
  line-height: 1.45;
}

.ip-empty {
  display: flex; flex-direction: column; align-items: center; gap: 0.6rem;
  padding: 2rem 1rem; text-align: center;
  color: var(--text-secondary, #a1a1aa);
}
.ip-empty svg { color: #4ade80; }

.ip-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 0.75rem;
}
.ip-card {
  display: flex; flex-direction: column;
  background: var(--bg-input, rgba(255, 255, 255, 0.03));
  border: 1px solid var(--border-subtle, rgba(255, 255, 255, 0.08));
  border-radius: 12px;
  overflow: hidden;
}
.ip-thumb {
  position: relative;
  aspect-ratio: 1 / 1;
  background: rgba(255, 255, 255, 0.03);
}
.ip-thumb img { width: 100%; height: 100%; object-fit: cover; opacity: 0.85; }
.ip-thumb-overlay {
  position: absolute; inset: 0;
  display: flex; align-items: center; justify-content: center;
  background: rgba(0, 0, 0, 0.5);
}
.ip-spinner {
  width: 24px; height: 24px; border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.25);
  border-top-color: var(--accent-gold, #e8c4a0);
  animation: ip-spin 0.8s linear infinite;
}
@keyframes ip-spin { to { transform: rotate(360deg); } }

.ip-info { padding: 0.6rem 0.7rem 0.4rem; display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; }
.ip-name {
  font-size: 0.85rem; font-weight: 600; line-height: 1.25;
  color: var(--text-primary, #f4f4f5);
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}
.ip-cat { font-size: 0.72rem; color: var(--text-muted, #71717a); }

.ip-upload {
  display: flex; align-items: center; justify-content: center; gap: 0.4rem;
  margin: 0.5rem 0.7rem 0.7rem;
  padding: 0.5rem; border-radius: 8px;
  background: rgba(232, 196, 160, 0.1);
  border: 1px solid rgba(232, 196, 160, 0.3);
  color: var(--accent-gold, #e8c4a0);
  font-size: 0.8rem; font-weight: 600; cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}
.ip-upload:hover:not(.disabled) { background: rgba(232, 196, 160, 0.18); }
.ip-upload.disabled { opacity: 0.6; cursor: wait; }

.ip-error { color: #fb7185; font-size: 0.85rem; margin: 0.75rem 0 0; }
.ip-ok { color: #4ade80; font-size: 0.85rem; margin: 0.75rem 0 0; }

.ip-mostrar-mas {
  display: block; width: 100%; margin-top: 1rem; padding: 0.7rem;
  border-radius: 10px; cursor: pointer;
  background: var(--bg-input, rgba(255,255,255,0.05));
  border: 1px solid var(--border-subtle, rgba(255,255,255,0.15));
  color: var(--text-primary, #f4f4f5); font-size: 0.88rem; font-weight: 600;
}
.ip-mostrar-mas:hover { background: rgba(255,255,255,0.1); }
</style>