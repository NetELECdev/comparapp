<template>
  <div
    class="splash"
    data-tema="dark"
    :class="{ 'splash--saliendo': saliendo }"
    role="status"
    aria-live="polite"
    @click="entrar"
  >
    <div class="splash-centro">
      <img src="/images/logo-comparapp-oscuro.svg" alt="" class="splash-logo" />
      <h1 class="splash-marca">Compar<span>App</span></h1>
      <p class="splash-lema">Compará y ahorrá en tu barrio</p>
    </div>

    <div class="splash-pie">
      <div class="splash-barra">
        <div class="splash-barra-relleno" :class="{ lleno: listo }" />
      </div>
      <p class="splash-texto" :class="{ 'splash-texto--listo': listo }">
        {{ listo ? 'Ahí vamos... ✓' : 'Buscando los mejores precios...' }}
      </p>
    </div>
  </div>
</template>

<script setup>
// 26/11/2026: se quitó el video. Presentación corta (~2 s) con logo
// y "Ahí vamos...", después /dashboard. Tocar la pantalla la saltea.
const route = useRoute()
const listo = ref(false)
const saliendo = ref(false)
const timers = []

function entrar() {
  if (saliendo.value) return
  timers.forEach(clearTimeout)
  saliendo.value = true
  setTimeout(() => navigateTo('/dashboard', { replace: true }), 250)
}

onMounted(() => {
  // Error de Google OAuth: a /login con el query para que se muestre ahí
  if (route.query.error || route.query.error_description || route.query.error_code) {
    return navigateTo({ path: '/login', query: route.query }, { replace: true })
  }

  const reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  timers.push(setTimeout(() => { listo.value = true }, reducido ? 200 : 1400))
  timers.push(setTimeout(entrar, reducido ? 700 : 2000))
})

onUnmounted(() => timers.forEach(clearTimeout))
</script>

<style scoped>
.splash {
  position: fixed;
  inset: 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: radial-gradient(ellipse 70% 45% at 50% 40%, rgba(68, 64, 181, 0.22), transparent 70%), #0D0E12;
  color: #F4F4F7;
  cursor: pointer;
  user-select: none;
  transition: opacity 0.25s ease;
}
.splash--saliendo { opacity: 0; }

.splash-centro {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.splash-logo {
  width: 112px;
  height: 112px;
  animation: logoEntra 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) both;
}

.splash-marca {
  margin: 0.25rem 0 0;
  font-size: 2.1rem;
  font-weight: 800;
  letter-spacing: -0.03em;
  animation: subir 0.5s ease-out 0.25s both;
}
.splash-marca span { color: #BDE84A; }

.splash-lema {
  margin: 0;
  font-size: 0.95rem;
  color: rgba(244, 244, 247, 0.65);
  animation: subir 0.5s ease-out 0.4s both;
}

.splash-pie {
  position: absolute;
  bottom: calc(14vh + env(safe-area-inset-bottom));
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  animation: subir 0.5s ease-out 0.5s both;
}

.splash-barra {
  width: 180px;
  height: 4px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
  overflow: hidden;
}
.splash-barra-relleno {
  height: 100%;
  width: 0;
  border-radius: inherit;
  background: linear-gradient(90deg, #4440B5, #BDE84A);
  animation: llenar 1.4s ease-in-out 0.1s forwards;
}
.splash-barra-relleno.lleno { width: 100%; animation: none; }

.splash-texto {
  margin: 0;
  font-size: 0.85rem;
  color: rgba(244, 244, 247, 0.6);
  transition: color 0.2s ease;
}
.splash-texto--listo { color: #BDE84A; font-weight: 600; }

@keyframes logoEntra {
  from { opacity: 0; transform: scale(0.6) rotate(-8deg); }
  to   { opacity: 1; transform: scale(1) rotate(0); }
}
@keyframes subir {
  from { opacity: 0; transform: translateY(12px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes llenar {
  from { width: 0; }
  to   { width: 100%; }
}

@media (prefers-reduced-motion: reduce) {
  .splash-logo, .splash-marca, .splash-lema, .splash-pie, .splash-barra-relleno { animation: none; }
  .splash-barra-relleno { width: 100%; }
}
</style>
