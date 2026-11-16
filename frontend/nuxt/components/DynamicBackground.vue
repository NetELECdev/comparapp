<template>
  <div class="dynamic-bg" :class="{ visible: MODO_FONDO !== 'rotativo' || isVisible }">
    <!-- Modo liso: solo color del tema, sin imagenes -->
    <div v-if="MODO_FONDO === 'liso'" class="dynamic-bg-liso" />

    <!-- Modo atenuado / rotativo: imagen + velo -->
    <template v-else>
      <div
        class="dynamic-bg-img"
        :class="{ 'is-atenuado': MODO_FONDO === 'atenuado' }"
        :style="{ backgroundImage: `url('${urlImagen}')` }"
      />
      <div class="dynamic-bg-overlay" :style="overlayStyle" />
    </template>
  </div>
</template>

<script setup lang="ts">
// ── ELEGIR MODO DE FONDO ──────────────────────────────
// 'liso'     -> color del tema, sin imagenes (opcion A)
// 'atenuado' -> foto fija, blur + velo 85% (opcion B)
// 'rotativo' -> comportamiento anterior (fotos cada 5 min)
const MODO_FONDO = 'liso' as 'liso' | 'atenuado' | 'rotativo'

const { fondoActual, fondos, isVisible, overlayClass } = useBackground()
const { esDark } = useTema()



const urlImagen = computed(() =>
  MODO_FONDO === 'atenuado' ? fondos.value[0].valor : fondoActual.value.valor
)

const overlayStyle = computed(() => {
  if (MODO_FONDO === 'atenuado') {
    return { background: esDark.value ? 'rgba(15,29,17,0.85)' : 'rgba(244,246,241,0.85)' }
  }
  if (overlayClass.value.includes('black/40')) return { background: 'rgba(0,0,0,0.40)' }
  if (overlayClass.value.includes('black/60')) return { background: 'rgba(0,0,0,0.60)' }
  if (overlayClass.value.includes('black/70')) return { background: 'rgba(0,0,0,0.70)' }
  if (overlayClass.value.includes('black/80')) return { background: 'rgba(0,0,0,0.80)' }
  if (overlayClass.value.includes('white/25')) return { background: 'rgba(255,255,255,0.25)' }
  if (overlayClass.value.includes('white/60')) return { background: 'rgba(255,255,255,0.60)' }
  return { background: 'rgba(0,0,0,0.40)' }
})
</script>

<style scoped>
.dynamic-bg {
  position: fixed;
  inset: 0;
  z-index: -10;
  opacity: 0;
  transition: opacity 0.7s ease-in-out;
  pointer-events: none;
}
.dynamic-bg.visible { opacity: 1; }
.dynamic-bg-liso {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, #182E1B 0%, #0F1D11 100%);
}
/* Tema resuelto por CSS (atributo data-tema en <html>), no por JS: evita el desfasaje de hidratacion SSG */
[data-tema="light"] .dynamic-bg-liso {
  background: #E8ECE4;
}
.dynamic-bg-img {
  position: absolute;
  inset: 0;
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
}
.dynamic-bg-img.is-atenuado {
  filter: blur(8px);
  transform: scale(1.05); /* evita bordes claros por el blur */
}
.dynamic-bg-overlay {
  position: absolute;
  inset: 0;
  transition: background 0.5s;
}
</style>