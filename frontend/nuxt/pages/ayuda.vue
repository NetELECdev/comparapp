<!-- pages/ayuda.vue -->
<template>
  <div class="ayuda-page">
    <DynamicBackground />

    <div class="ayuda-content">

      <!-- Header -->
      <header class="ayuda-header">
        <button class="back-btn" @click="navigateTo('/perfil')" aria-label="Volver">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m15 18-6-6 6-6"/></svg>
        </button>
        <h1 class="ayuda-title">Ayuda y la empresa</h1>
        <ToggleTema />
      </header>

      <!-- Sobre NetELEC y ComparApp -->
      <section class="ayuda-card">
        <h2 class="ayuda-card-title">Sobre NetELEC y ComparApp</h2>
        <p class="ayuda-text">
          NetELEC es una empresa argentina de base tecnológica dedicada al desarrollo de soluciones
          digitales aplicadas a la optimización del consumo y la transparencia del mercado. Su plataforma
          principal, ComparApp, es un entorno virtual e interactivo diseñado exclusivamente como un
          servicio de intermediación informativa e indexación de datos de precios.
        </p>
        <p class="ayuda-text">
          Nuestra misión es facilitar el acceso a la información pública de mercado para potenciar la
          libre elección de los usuarios, rigiéndonos bajo los más estrictos estándares de la Ley N°
          24.240 de Defensa del Consumidor y la normativa vigente de Lealtad Comercial.
        </p>
      </section>

      <!-- Nuestros principios (acordeón) -->
      <section class="ayuda-card">
        <h2 class="ayuda-card-title">Nuestros principios</h2>
        <div class="acc-list">
          <div v-for="(item, idx) in principios" :key="`pr-${idx}`" class="acc-item">
            <button class="acc-head" @click="toggle('principios', idx)">
              <span>{{ item.titulo }}</span>
              <svg
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
                class="acc-chevron" :class="{ 'is-open': isOpen('principios', idx) }"
              ><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div v-show="isOpen('principios', idx)" class="acc-body">
              <p class="ayuda-text">{{ item.texto }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Guía de comentarios y calificaciones (acordeón) -->
      <section class="ayuda-card">
        <h2 class="ayuda-card-title">Guía de comentarios y calificaciones</h2>
        <p class="ayuda-text ayuda-text--muted">
          Esta guía regirá las opiniones y calificaciones que los usuarios podrán dejar sobre los
          comercios listados en ComparApp cuando esa función esté disponible.
        </p>
        <div class="acc-list">
          <div v-for="(item, idx) in comentariosGuia" :key="`cg-${idx}`" class="acc-item">
            <button class="acc-head" @click="toggle('comentarios', idx)">
              <span>{{ item.titulo }}</span>
              <svg
                width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"
                class="acc-chevron" :class="{ 'is-open': isOpen('comentarios', idx) }"
              ><path d="m6 9 6 6 6-6"/></svg>
            </button>
            <div v-show="isOpen('comentarios', idx)" class="acc-body">
              <p class="ayuda-text">{{ item.texto }}</p>
            </div>
          </div>
        </div>
      </section>

      <!-- Legal -->
      <section class="ayuda-card">
        <h2 class="ayuda-card-title">Legal</h2>
        <div class="legal-list">
          <button class="legal-row" @click="proximamente('Términos y Condiciones')">
            <span>Términos y Condiciones</span>
            <span class="legal-pill">Próximamente</span>
          </button>
          <button class="legal-row" @click="proximamente('Política de Privacidad')">
            <span>Política de Privacidad</span>
            <span class="legal-pill">Próximamente</span>
          </button>
        </div>
      </section>

      <!-- Contacto -->
      <section class="ayuda-card">
        <h2 class="ayuda-card-title">Contacto</h2>
        <a class="contacto-row" href="mailto:netelecinfo@gmail.com">
          <div class="contacto-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          </div>
          <span class="contacto-text">netelecinfo@gmail.com</span>
        </a>
      </section>

      <p class="ayuda-footer">ComparApp es un producto de NetELEC</p>

    </div>

    <!-- Bottom nav — igual que el resto de la app -->
    <nav class="bottom-nav" aria-label="Navegación principal">
      <button class="bnav-btn" @click="navigateTo('/dashboard')" aria-label="Inicio">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Inicio</span>
      </button>
      <button class="bnav-btn" @click="navigateTo('/productos')" aria-label="Productos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
        <span>Productos</span>
      </button>
      <button class="bnav-btn bnav-btn--center" @click="navigateTo('/comparaciones')" aria-label="Comparar">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
      </button>
      <button class="bnav-btn" @click="navigateTo('/favoritos')" aria-label="Favoritos">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
        <span>Favoritos</span>
      </button>
      <button class="bnav-btn" @click="navigateTo('/perfil')" aria-label="Perfil">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Perfil</span>
      </button>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { navigateTo } from '#app'

useTema()
useBackground()

const principios = [
  {
    titulo: 'Relación con los usuarios',
    texto: 'ComparApp es una herramienta de consulta de precios y stock referenciales. NetELEC no vende, no distribuye ni garantiza los productos o servicios exhibidos por los comercios. La relación de consumo se perfecciona exclusivamente entre el usuario y el comercio elegido — NetELEC queda exenta de responsabilidad por vicios redhibitorios, garantías, diferencias de facturación o incumplimientos contractuales de los vendedores.'
  },
  {
    titulo: 'Relación con los comercios',
    texto: 'Los datos replicados en ComparApp provienen de fuentes públicas, canales oficiales de los comercios o información suministrada voluntariamente por ellos, de acuerdo a las pautas de transparencia de precios (Resolución 51-E/2017 o similares). NetELEC no altera ni manipula la información comercial; cualquier desactualización ajena a sus sistemas es responsabilidad del comercio que provee la información primaria.'
  },
  {
    titulo: 'Tratamiento de datos personales',
    texto: 'NetELEC asume el rol de responsable de bases de datos en los términos de la Ley 25.326, garantizando que el tratamiento de la información de usuarios y comercios se realiza bajo estrictos parámetros de seguridad técnica y organizativa, respetando los derechos de acceso, rectificación y supresión de los titulares.'
  }
]

const comentariosGuia = [
  {
    titulo: '1. Relevancia',
    texto: 'Solo pueden calificarse o comentarse comercios con los que el usuario haya tenido una interacción real dentro de ComparApp (consulta de precios, uso en una lista de compra, etc.). No se admiten comentarios sobre comercios sin un vínculo verificable.'
  },
  {
    titulo: '2. Contenido aceptable',
    texto: 'No se admiten comentarios con lenguaje ofensivo, discriminatorio (por motivos de religión, raza, género, origen nacional, edad, estado civil, orientación sexual o discapacidad), amenazas, datos personales de terceros, ni referencias a actividad ilegal.'
  },
  {
    titulo: '3. Motivos de revisión o eliminación',
    texto: 'NetELEC podrá eliminar comentarios que no se relacionen con la experiencia de precio/información del comercio (los reclamos sobre el funcionamiento de la app se canalizan por soporte y no afectan la calificación del comercio), o que contengan información que el usuario no pueda acreditar como una experiencia real. Las calificaciones numéricas sin comentario asociado no se eliminan, salvo pedido expreso de su autor.'
  },
  {
    titulo: '4. Eliminación a pedido del usuario',
    texto: 'Cualquier usuario puede solicitar la baja de su propio comentario o calificación en cualquier momento, escribiendo a netelecinfo@gmail.com.'
  }
]

const openMap = ref<Record<string, boolean>>({})

function toggle(group: string, idx: number) {
  const key = `${group}-${idx}`
  openMap.value[key] = !openMap.value[key]
}
function isOpen(group: string, idx: number) {
  return !!openMap.value[`${group}-${idx}`]
}

function proximamente(nombre: string) {
  alert(`${nombre} — Próximamente`)
}
</script>

<style scoped>
.ayuda-page {
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  -webkit-font-smoothing: antialiased;
}

.ayuda-content {
  position: relative;
  z-index: 2;
  padding: 0 16px 120px;
  max-width: 480px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

/* Header */
.ayuda-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
  background: var(--bg-deep);
  backdrop-filter: blur(16px);
}
.back-btn {
  width: 36px; height: 36px; border-radius: 50%;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  color: var(--text-secondary); display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: all 0.2s;
}
.back-btn:hover { border-color: var(--border-glow); color: var(--text-primary); }
.ayuda-title { font-size: 16px; font-weight: 600; color: var(--text-primary); }

/* Card */
.ayuda-card {
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 18px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ayuda-card-title { font-size: 15px; font-weight: 600; color: var(--text-primary); margin: 0; }

.ayuda-text {
  font-size: 13px; line-height: 1.55;
  color: var(--text-secondary);
  margin: 0;
}
.ayuda-text--muted { color: var(--text-muted); font-size: 12.5px; }

/* Acordeón */
.acc-list { display: flex; flex-direction: column; }
.acc-item { border-bottom: 0.5px solid var(--border-subtle); }
.acc-item:last-child { border-bottom: none; }

.acc-head {
  width: 100%;
  display: flex; align-items: center; justify-content: space-between;
  gap: 10px;
  padding: 12px 2px;
  background: none; border: none;
  color: var(--text-primary);
  font-size: 13.5px; font-weight: 500;
  text-align: left;
  cursor: pointer;
}
.acc-chevron { color: var(--text-muted); flex-shrink: 0; transition: transform 0.2s ease; }
.acc-chevron.is-open { transform: rotate(180deg); color: var(--accent-gold); }

.acc-body { padding: 0 2px 14px; }

/* Legal */
.legal-list { display: flex; flex-direction: column; }
.legal-row {
  display: flex; align-items: center; justify-content: space-between;
  width: 100%;
  padding: 12px 2px;
  background: none; border: none;
  border-bottom: 0.5px solid var(--border-subtle);
  color: var(--text-primary);
  font-size: 13.5px; font-weight: 500;
  cursor: pointer;
}
.legal-row:last-child { border-bottom: none; }
.legal-pill {
  font-size: 10.5px; font-weight: 600;
  padding: 2px 8px; border-radius: 20px;
  background: var(--accent-gold-dim);
  color: var(--accent-gold);
  border: 1px solid var(--border-glow);
}

/* Contacto */
.contacto-row {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 2px;
  text-decoration: none;
  color: var(--text-primary);
}
.contacto-icon {
  width: 34px; height: 34px; border-radius: 50%;
  background: var(--bg-input);
  display: flex; align-items: center; justify-content: center;
  color: var(--accent-gold);
  flex-shrink: 0;
}
.contacto-text { font-size: 13.5px; font-weight: 500; }

.ayuda-footer {
  text-align: center;
  font-size: 11px;
  color: var(--text-muted);
  margin: 4px 0 0;
}

/* Bottom nav — igual que el resto de la app */
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
  color: var(--text-muted); font-size: 10px; font-weight: 500;
  cursor: pointer; padding: 6px 10px; border-radius: var(--radius-sm);
  transition: color 0.2s, background 0.2s;
}
.bnav-btn:hover { color: var(--text-secondary); background: var(--bg-card-hover); }
.bnav-btn--center {
  width: 48px; height: 48px; border-radius: 50%;
  background: var(--accent-gold-dim);
  border: 1px solid var(--border-glow);
  color: var(--accent-gold); padding: 0;
  display: flex; align-items: center; justify-content: center;
  margin-top: -14px;
  box-shadow: 0 4px 16px rgba(232,196,160,0.25);
}
</style>