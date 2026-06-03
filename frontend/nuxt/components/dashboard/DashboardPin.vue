<!-- components/dashboard/DashboardPin.vue -->
<template>
  <article
    class="pin"
    :class="[`pin--${size}`, { 'pin--best': isBestPrice }]"
    :style="{ '--delay': delay + 'ms' }"
    @click="$emit('click')"
    role="button"
    :aria-label="`Ir a ${title}`"
    tabindex="0"
    @keydown.enter="$emit('click')"
  >
    <!-- Badge mejor precio -->
    <div v-if="isBestPrice" class="pin-badge" aria-label="Mejor precio">
      <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
      Mejor precio
    </div>

    <!-- Imagen con skeleton -->
    <div class="pin-img-wrap">
      <div v-if="imgLoading" class="pin-skeleton" aria-hidden="true" />
      <img
        v-show="!imgLoading && !imgError"
        :src="imageUrl"
        :alt="title"
        class="pin-img"
        loading="lazy"
        @load="imgLoading = false"
        @error="onImgError"
      />
      <!-- Fallback error -->
      <div v-if="imgError" class="pin-fallback" aria-hidden="true">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="m7.5 4.27 9 5.15"/>
          <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
          <path d="m3.3 7 8.7 5 8.7-5"/>
          <path d="M12 22V12"/>
        </svg>
        <span>{{ title }}</span>
      </div>
    </div>

    <!-- Overlay con info -->
    <div class="pin-overlay" aria-hidden="true">
      <!-- Acciones top-right -->
      <div class="pin-actions">
        <button
          class="pin-action-btn"
          :class="{ 'pin-action-btn--active': isFavorited }"
          @click.stop="toggleFav"
          :aria-label="isFavorited ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" :fill="isFavorited ? 'currentColor' : 'none'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
          </svg>
        </button>
        <button
          class="pin-action-btn"
          @click.stop="share"
          aria-label="Compartir"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
            <polyline points="16 6 12 2 8 6"/>
            <line x1="12" y1="2" x2="12" y2="15"/>
          </svg>
        </button>
      </div>

      <!-- Info bottom -->
      <div class="pin-info">
        <p class="pin-title">{{ title }}</p>
        <div v-if="price || provider" class="pin-meta">
          <span v-if="price" class="pin-price">${{ price }}</span>
          <span v-if="price && provider" class="pin-sep">·</span>
          <span v-if="provider" class="pin-provider">{{ provider }}</span>
        </div>
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string
  imageUrl: string
  size?: 'small' | 'medium' | 'large'
  price?: string
  provider?: string
  isBestPrice?: boolean
  isFavorite?: boolean
  delay?: number
}>()

const emit = defineEmits<{
  click: []
  favorite: [value: boolean]
}>()

const imgLoading = ref(true)
const imgError = ref(false)
const isFavorited = ref(props.isFavorite ?? false)

function onImgError() {
  imgLoading.value = false
  imgError.value = true
}

function toggleFav() {
  isFavorited.value = !isFavorited.value
  emit('favorite', isFavorited.value)
}

async function share() {
  const url = window.location.href
  if (navigator.share) {
    await navigator.share({ title: props.title, url })
  } else {
    await navigator.clipboard.writeText(url)
  }
}
</script>

<style scoped>
/* ── Alturas modulares (módulo base: 72px móvil, 80px desktop) ── */
.pin { --h-small: 200px; --h-medium: 320px; --h-large: 440px; }
@media (min-width: 640px) {
  .pin { --h-small: 240px; --h-medium: 400px; --h-large: 560px; }
}

.pin {
  position: relative;
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  background: var(--bg-card);
  border: 1px solid var(--border-subtle);
  box-shadow: var(--shadow-card);

  /* Animación de entrada desde derecha */
  opacity: 0;
  transform: translateX(60px);
  animation: pinSlideIn 0.6s cubic-bezier(0.22, 1, 0.36, 1) var(--delay, 0ms) both;

  transition:
    transform 0.2s ease-out,
    box-shadow 0.2s ease-out,
    border-color 0.2s ease-out;
}

@keyframes pinSlideIn {
  from { opacity: 0; transform: translateX(60px); }
  to   { opacity: 1; transform: translateX(0); }
}

@media (prefers-reduced-motion: reduce) {
  .pin {
    animation: pinFadeIn 0.3s ease both;
    transform: none;
  }
  @keyframes pinFadeIn {
    from { opacity: 0; }
    to   { opacity: 1; }
  }
}

.pin--small  { height: var(--h-small); }
.pin--medium { height: var(--h-medium); }
.pin--large  { height: var(--h-large); }

.pin:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-modal);
  border-color: var(--border-glow);
}

.pin:focus-visible {
  outline: 2px solid var(--accent-gold);
  outline-offset: 2px;
}

/* ── Badge ── */
.pin-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  border-radius: 20px;
  font-size: 10px;
  font-weight: 600;
  color: #7A4A00;
  background: linear-gradient(135deg, #FFD700, #FFA500);
  border: 1px solid rgba(255, 255, 255, 0.3);
}

/* ── Imagen ── */
.pin-img-wrap {
  position: absolute;
  inset: 0;
}

.pin-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.pin-skeleton {
  width: 100%;
  height: 100%;
  background: var(--bg-card-hover);
  animation: shimmer 1.4s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.5; }
}

.pin-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  background: var(--bg-card-hover);
  color: var(--text-muted);
  font-size: 11px;
  text-align: center;
  padding: 1rem;
}

/* ── Overlay ── */
.pin-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px;
  /* Gradiente siempre visible para el título */
  background: linear-gradient(
    to top,
    rgba(0, 0, 0, 0.75) 0%,
    rgba(0, 0, 0, 0.2) 40%,
    transparent 100%
  );
}

/* Acciones top: ocultas en reposo, visibles en hover */
.pin-overlay .pin-actions {
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.pin:hover .pin-overlay .pin-actions {
  opacity: 1;
  transform: translateY(0);
}

/* ── Acciones ── */
.pin-actions {
  display: flex;
  justify-content: flex-end;
  gap: 6px;
}

.pin-action-btn {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #1a1a1a;
  transition: transform 0.15s ease, background 0.15s ease;
}

.pin-action-btn:hover { transform: scale(1.1); background: #fff; }
.pin-action-btn:active { transform: scale(0.93); }

.pin-action-btn--active {
  color: #e11d48;
  background: #fff;
  animation: heartPop 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes heartPop {
  0%   { transform: scale(1); }
  50%  { transform: scale(1.35); }
  100% { transform: scale(1); }
}

/* ── Info ── */
.pin-info { display: flex; flex-direction: column; gap: 3px; }

.pin-title {
  color: #fff;
  font-size: 13px;
  font-weight: 600;
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 1px 4px rgba(0,0,0,0.4);
}

.pin-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
}

.pin-price {
  color: #fff;
  font-weight: 700;
}

.pin-sep { color: rgba(255,255,255,0.5); }

.pin-provider {
  color: rgba(255,255,255,0.75);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100px;
}
</style>