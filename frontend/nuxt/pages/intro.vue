<template>
  <div class="intro-page">
    <div class="bg-gradient" />

    <!-- PASO 1: Logo (obligatorio, mínimo 2 segundos) -->
    <div v-if="step === 1" class="intro-overlay animate-fade-in">
      <div class="logo-wrap" :class="{ 'logo-ready': logoVerified }">
        <img
          :src="logoSrc"
          alt="ComparApp"
          class="logo-img"
        />
      </div>
      <p class="step-text">{{ step1Text }}</p>
      <div class="step-indicator">
        <span class="dot active" />
        <span class="dot" :class="{ active: step >= 2 }" />
        <span class="dot" :class="{ active: step >= 3 }" />
      </div>
    </div>

    <!-- PASO 2: Video cargando (verificación previa) -->
    <div v-else-if="step === 2" class="intro-overlay animate-fade-in">
      <div class="logo-wrap logo-pulse">
        <img :src="logoSrc" alt="ComparApp" class="logo-img" />
      </div>
      <p class="step-text">{{ step2Text }}</p>
      <div class="progress-bar-mini">
        <div class="progress-fill-mini" :style="{ width: preloadProgress + '%' }" />
      </div>
      <div class="step-indicator">
        <span class="dot active" />
        <span class="dot active" />
        <span class="dot" :class="{ active: step >= 3 }" />
      </div>
    </div>

    <!-- PASO 3: Video reproduciéndose -->
    <div v-else-if="step === 3" class="video-stage animate-fade-in">
      <video
        ref="videoRef"
        class="intro-video"
        autoplay
        muted
        playsinline
        preload="auto"
        @ended="onVideoEnd"
        @error="onVideoError"
        @timeupdate="onTimeUpdate"
      >
        <source :src="videoSrc" type="video/mp4" />
      </video>

      <button class="skip-btn" @click="entrar">
        Saltar
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14"/>
          <path d="m12 5 7 7-7 7"/>
        </svg>
      </button>

      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: videoProgress + '%' }" />
      </div>

      <div class="step-indicator step-indicator--video">
        <span class="dot active" />
        <span class="dot active" />
        <span class="dot active" />
      </div>
    </div>

    <!-- PASO 4: Fallback (si algo falla) -->
    <div v-else-if="step === 4" class="intro-overlay animate-fade-in">
      <div class="logo-wrap logo-pulse">
        <img :src="logoSrc" alt="ComparApp" class="logo-img" />
      </div>
      <h2 class="fallback-title">ComparApp</h2>
      <p class="fallback-subtitle">Tu plataforma de ahorro inteligente</p>
      <button class="btn-start" @click="entrar">
        Ingresar
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M5 12h14"/>
          <path d="m12 5 7 7-7 7"/>
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { navigateTo, useRoute } from '#app'

// ============================================
// ASSETS: strings dinámicos → Vite no los
// resuelve como módulos en build time
// ============================================
const logoSrc = '/images/favicon.ico'
const videoSrc = 'https://fbsugjqjbltvvyywfsal.supabase.co/storage/v1/object/public/product-images/Intro2.mp4'

// PASOS: 1=Logo | 2=Video cargando | 3=Video reproduciendo | 4=Fallback
const step = ref(1)
const videoRef = ref<HTMLVideoElement>()
const logoVerified = ref(false)
const step1Text = ref('Cargando logo...')
const step2Text = ref('Preparando video...')
const preloadProgress = ref(0)
const videoProgress = ref(0)

let step1Timer: ReturnType<typeof setTimeout> | null = null
let step2Timer: ReturnType<typeof setTimeout> | null = null
let safetyTimer: ReturnType<typeof setTimeout> | null = null
let preloadInterval: ReturnType<typeof setInterval> | null = null

// ============================================
// PASO 1: Logo verificado via JS (no @load del template)
// El evento @load en v-if puede perderse si la imagen
// ya estaba cacheada cuando Vue monta el elemento.
// Usamos un Image() programático que siempre dispara.
// ============================================
function verifyLogo() {
  const img = new Image()

  img.onload = () => {
    console.log('✅ Paso 1: Logo cargado')
    logoVerified.value = true
    step1Text.value = 'Iniciando ✓'

    // Mínimo 2 segundos en el paso 1
    step1Timer = setTimeout(() => {
      goToStep2()
    }, 2000)
  }

  img.onerror = () => {
    console.error('❌ Error cargando logo, avanzando igual...')
    step1Text.value = 'Cargando...'
    step1Timer = setTimeout(() => {
      goToStep2()
    }, 2000)
  }

  // Asignar src DESPUÉS de los handlers para garantizar que disparen
  img.src = logoSrc
}

// ============================================
// PASO 2: Precargar video (verificación completa)
// ============================================
function goToStep2() {
  step.value = 2
  step2Text.value = 'Verificando video...'
  console.log('⏳ Paso 2: Verificando video...')

  preloadInterval = setInterval(() => {
    if (preloadProgress.value < 90) {
      preloadProgress.value += Math.random() * 15
      if (preloadProgress.value > 90) preloadProgress.value = 90
    }
  }, 200)

  const tempVideo = document.createElement('video')
  tempVideo.preload = 'auto'
  tempVideo.src = videoSrc

  tempVideo.addEventListener('canplaythrough', () => {
    console.log('✅ Paso 2: Video precargado')
    if (preloadInterval) clearInterval(preloadInterval)
    preloadProgress.value = 100
    step2Text.value = 'Ahí Vamos... ✓'

    step2Timer = setTimeout(() => {
      goToStep3()
    }, 500)
  })

  tempVideo.addEventListener('error', () => {
    console.error('❌ Error precargando video')
    if (preloadInterval) clearInterval(preloadInterval)
    goToStep4()
  })

  tempVideo.load()

  // Timeout de seguridad: máximo 5 segundos en paso 2
  setTimeout(() => {
    if (step.value === 2) {
      console.log('⏱️ Timeout paso 2, intentando reproducir igual...')
      goToStep3()
    }
  }, 5000)
}

// ============================================
// PASO 3: Reproducir video
// ============================================
function goToStep3() {
  step.value = 3
  console.log('▶️ Paso 3: Reproduciendo video...')

  requestAnimationFrame(() => {
    setTimeout(() => {
      const v = videoRef.value
      if (!v) {
        console.error('❌ No se encontró elemento video')
        goToStep4()
        return
      }

      v.play().then(() => {
        console.log('✅ Video reproduciéndose')
      }).catch((err) => {
        console.error('❌ Error reproduciendo:', err)
        goToStep4()
      })
    }, 200)
  })

  // Safety: máximo 10 segundos reproduciendo
  safetyTimer = setTimeout(() => {
    if (step.value === 3) {
      console.log('⏱️ Safety timeout: video tomó demasiado')
      entrar()
    }
  }, 10000)
}

function onTimeUpdate() {
  const v = videoRef.value
  if (v && v.duration > 0) {
    videoProgress.value = (v.currentTime / v.duration) * 100
  }
}

function onVideoEnd() {
  console.log('✅ Paso 3: Video terminado')
  videoProgress.value = 100
  if (safetyTimer) clearTimeout(safetyTimer)
  setTimeout(entrar, 300)
}

function onVideoError(e: Event) {
  console.error('❌ Error en video:', e)
  goToStep4()
}

// ============================================
// PASO 4: Fallback
// ============================================
function goToStep4() {
  console.log('⚠️ Paso 4: Fallback')
  step.value = 4
  if (preloadInterval) clearInterval(preloadInterval)
  if (safetyTimer) clearTimeout(safetyTimer)
}

// ============================================
// NAVEGACIÓN
// ============================================
function entrar() {
  if (step1Timer) clearTimeout(step1Timer)
  if (step2Timer) clearTimeout(step2Timer)
  if (preloadInterval) clearInterval(preloadInterval)
  if (safetyTimer) clearTimeout(safetyTimer)
  navigateTo('/dashboard')
}

// ============================================
// LIFECYCLE
// ============================================
onMounted(() => {
  // Si Google OAuth falló y nos redirigió de vuelta acá con un ?error=...
  // en la URL, no tiene sentido mostrarle al usuario la animación de
  // bienvenida — lo mandamos directo a /login, preservando el error para
  // que se muestre ahí (ver pages/login.vue).
  const route = useRoute()
  if (route.query.error) {
    return navigateTo({ path: '/login', query: route.query }, { replace: true })
  }

  console.log('🎬 Intro iniciada - Paso 1: Logo')
  verifyLogo()  // ← verificación programática, nunca pierde el evento
})

onUnmounted(() => {
  if (step1Timer) clearTimeout(step1Timer)
  if (step2Timer) clearTimeout(step2Timer)
  if (preloadInterval) clearInterval(preloadInterval)
  if (safetyTimer) clearTimeout(safetyTimer)
})
</script>

<style scoped>
/* ============================================
   BASE: ocupa todo el viewport siempre
   ============================================ */
.intro-page {
  position: fixed;
  inset: 0;
  width: 100dvw;
  height: 100dvh;
  background: #0a0a0f;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  z-index: 9999;
}

.bg-gradient {
  position: fixed;
  inset: 0;
  background:
    radial-gradient(ellipse 60% 40% at 50% 50%, rgba(232, 196, 160, 0.05), transparent),
    linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 50%, #0a0a0f 100%);
  z-index: 0;
  pointer-events: none;
}

/* ============================================
   PASOS 1, 2 y 4: overlay centrado
   ============================================ */
.intro-overlay {
  position: relative;
  z-index: 5;
  width: 100%;
  max-width: 420px;
  padding: clamp(1.5rem, 5vw, 2.5rem);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: clamp(1rem, 3vw, 1.5rem);
}

/* ============================================
   LOGO
   ============================================ */
.logo-wrap {
  width: clamp(80px, 20vw, 120px);
  height: clamp(80px, 20vw, 120px);
  border-radius: clamp(16px, 4vw, 28px);
  background: rgba(232, 196, 160, 0.1);
  border: 1px solid rgba(232, 196, 160, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
  transition: all 0.5s ease;
  flex-shrink: 0;
}

.logo-ready {
  background: rgba(232, 196, 160, 0.15);
  border-color: rgba(232, 196, 160, 0.4);
  box-shadow: 0 8px 32px rgba(232, 196, 160, 0.1);
}

.logo-pulse {
  animation: pulse 2s ease-in-out infinite;
}

.logo-img {
  width: 65%;
  height: 65%;
  object-fit: contain;
  filter: drop-shadow(0 4px 8px rgba(0,0,0,0.4));
}

/* ============================================
   TEXTOS
   ============================================ */
.step-text {
  color: rgba(245, 240, 235, 0.6);
  font-size: clamp(0.8rem, 2.5vw, 0.95rem);
  margin: 0;
  min-height: 1.5rem;
  font-weight: 500;
  text-align: center;
}

.fallback-title {
  color: #f5f0eb;
  font-size: clamp(1.3rem, 5vw, 1.75rem);
  font-weight: 700;
  margin: 0;
  letter-spacing: -0.02em;
  text-align: center;
}

.fallback-subtitle {
  color: rgba(245, 240, 235, 0.5);
  font-size: clamp(0.8rem, 2.5vw, 0.95rem);
  margin: -0.25rem 0 0.25rem;
  text-align: center;
}

/* ============================================
   DOTS
   ============================================ */
.step-indicator {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.step-indicator--video {
  position: absolute;
  bottom: clamp(1rem, 3vh, 1.5rem);
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.15);
  transition: all 0.3s ease;
}

.dot.active {
  background: #e8c4a0;
  box-shadow: 0 0 8px rgba(232, 196, 160, 0.4);
}

/* ============================================
   PROGRESS BAR MINI (paso 2)
   ============================================ */
.progress-bar-mini {
  width: clamp(120px, 40vw, 180px);
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill-mini {
  height: 100%;
  background: linear-gradient(90deg, #e8c4a0, #f5d0a9);
  border-radius: 9999px;
  transition: width 0.2s ease;
}

/* ============================================
   PASO 3: VIDEO — se dimensiona desde la altura
   height: 100dvh → ocupa toda la altura
   width: auto    → el ancho sale del ratio natural del video
   max-width: 100dvw → nunca desborda si el video es muy ancho
   ============================================ */
.video-stage {
  position: absolute;
  inset: 0;
  z-index: 5;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #0a0a0f;
}

.intro-video {
  height: 100dvh;
  width: auto;
  max-width: 100dvw;
  display: block;
}

/* ============================================
   SKIP BUTTON
   ============================================ */
.skip-btn {
  position: absolute;
  top: clamp(1.75rem, 4.5vh, 2.5rem);
  right: clamp(0.75rem, 2.5vw, 1.5rem);
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: clamp(0.4rem, 1.5vh, 0.6rem) clamp(0.75rem, 2.5vw, 1.25rem);
  background: rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 9999px;
  color: rgba(245, 240, 235, 0.7);
  font-size: clamp(0.75rem, 2vw, 0.85rem);
  font-weight: 500;
  cursor: pointer;
  transition: all 0.25s ease;
  z-index: 10;
  white-space: nowrap;
}

.skip-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  border-color: rgba(232, 196, 160, 0.3);
  color: #f5f0eb;
}

/* ============================================
   PROGRESS BAR (paso 3)
   ============================================ */
.progress-bar {
  position: absolute;
  bottom: clamp(1.5rem, 4vh, 3rem);
  left: 50%;
  transform: translateX(-50%);
  width: clamp(120px, 40vw, 220px);
  height: 3px;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  overflow: hidden;
  z-index: 10;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #e8c4a0, #f5d0a9);
  border-radius: 9999px;
  transition: width 0.1s linear;
}

/* ============================================
   BTN FALLBACK
   ============================================ */
.btn-start {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: clamp(0.7rem, 2.5vh, 0.875rem) clamp(1.25rem, 5vw, 2rem);
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.2), rgba(232, 196, 160, 0.1));
  border: 1px solid rgba(232, 196, 160, 0.3);
  border-radius: 9999px;
  color: #e8c4a0;
  font-size: clamp(0.875rem, 2.5vw, 1rem);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-start:hover {
  background: linear-gradient(135deg, rgba(232, 196, 160, 0.3), rgba(232, 196, 160, 0.2));
  border-color: rgba(232, 196, 160, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(232, 196, 160, 0.15);
}

/* ============================================
   ANIMACIONES
   ============================================ */
@keyframes fadeIn {
  from { opacity: 0; transform: scale(0.97); }
  to   { opacity: 1; transform: scale(1); }
}

.animate-fade-in {
  animation: fadeIn 0.4s ease-out both;
}

@keyframes pulse {
  0%, 100% { transform: scale(1);    opacity: 1; }
  50%       { transform: scale(1.03); opacity: 0.9; }
}

/* ============================================
   RESPONSIVE — ajustes específicos por breakpoint
   ============================================ */

/* Landscape móvil: el video ya cubre todo, solo ajustamos UI */
@media (max-width: 640px) and (orientation: landscape) {
  .skip-btn {
    top: 0.5rem;
    right: 0.5rem;
  }
  .progress-bar {
    bottom: 0.75rem;
  }
}

/* Tablets en portrait */
@media (min-width: 641px) and (max-width: 1024px) {
  .intro-overlay {
    max-width: 480px;
  }
}
</style>