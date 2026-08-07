<template>
  <section class="importador">
    <header class="imp-header">
      <div class="imp-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        <span>Importar productos desde archivo</span>
      </div>
      <p class="imp-sub">Cargá el CSV exportado del sistema de ventas. Primero vas a ver un resumen; nada se guarda hasta que confirmes.</p>
    </header>

    <!-- PASO 1: elegir archivo -->
    <div v-if="paso === 'idle'" class="imp-drop">
      <label class="imp-file-btn">
        <input type="file" accept=".csv,text/csv" hidden @change="onArchivo" />
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/>
        </svg>
        <span>{{ archivo ? archivo.name : 'Elegir archivo CSV' }}</span>
      </label>
      <p class="imp-hint">
        Usá el export original del sistema (no lo abras ni lo guardes con Excel, rompe los códigos de barras).
      </p>
      <button class="imp-btn primary" :disabled="!archivo" @click="hacerPreview">
        Analizar archivo
      </button>
    </div>

    <!-- Cargando (preview o importación) -->
    <div v-else-if="paso === 'analizando' || paso === 'importando'" class="imp-state">
      <div class="imp-spinner" />
      <span>{{ paso === 'analizando' ? 'Analizando el archivo...' : 'Importando... esto puede tardar unos minutos.' }}</span>
    </div>

    <!-- PASO 2: resumen del preview -->
    <div v-else-if="paso === 'preview' && preview" class="imp-preview">
      <div class="imp-cards">
        <div class="imp-card crear">
          <span class="n">{{ preview.resumen.crear }}</span>
          <span class="l">se crean</span>
        </div>
        <div class="imp-card actualizar">
          <span class="n">{{ preview.resumen.actualizar }}</span>
          <span class="l">se actualizan</span>
        </div>
        <div class="imp-card omitir">
          <span class="n">{{ preview.resumen.omitidos }}</span>
          <span class="l">se omiten</span>
        </div>
      </div>

      <p class="imp-total">
        {{ preview.comercio }} · pasa de <strong>{{ preview.resumen.productos_actuales }}</strong>
        a <strong>{{ preview.resumen.total_despues }}</strong> productos
      </p>

      <div v-if="preview.excede_plan_free" class="imp-warn">
        <template v-if="esAdmin">
          ⚠️ Este comercio quedaría por encima del plan Gratis ({{ preview.limite_plan_free }} productos).
          Como admin no tenés tope, se va a cargar todo igual.
        </template>
        <template v-else>
          ⚠️ Con esta carga se supera el límite del plan Gratis ({{ preview.limite_plan_free }} productos).
          Los productos que excedan el límite se van a omitir automáticamente.
        </template>
      </div>

      <div v-if="preview.muestra_crear?.length" class="imp-muestra">
        <h4>Ejemplos de productos nuevos</h4>
        <ul>
          <li v-for="(it, i) in preview.muestra_crear" :key="'c'+i">
            <span class="m-nombre">{{ it.nombre }}</span>
            <span class="m-precio">{{ fmtPrecio(it.precio) }}</span>
          </li>
        </ul>
      </div>

      <div v-if="preview.omitidos?.length" class="imp-muestra omit">
        <h4>Se omiten ({{ preview.omitidos.length }} mostrados)</h4>
        <ul>
          <li v-for="(it, i) in preview.omitidos" :key="'o'+i">
            <span class="m-nombre">{{ it.nombre }}</span>
            <span class="m-motivo">{{ it.motivo }}</span>
          </li>
        </ul>
      </div>

      <p v-if="errorMsg" class="imp-error">{{ errorMsg }}</p>

      <div class="imp-actions">
        <button class="imp-btn ghost" @click="reset">Cancelar</button>
        <button class="imp-btn primary" @click="confirmarImport">
          Confirmar importación
        </button>
      </div>
    </div>

    <!-- PASO 3: resultado -->
    <div v-else-if="paso === 'resultado' && resultado" class="imp-result">
      <div class="imp-result-head">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <h4>Importación completada</h4>
      </div>

      <div class="imp-result-grid">
        <div><span class="rn">{{ resultado.creados }}</span><span class="rl">creados</span></div>
        <div><span class="rn">{{ resultado.actualizados }}</span><span class="rl">actualizados</span></div>
        <div><span class="rn">{{ resultado.omitidos }}</span><span class="rl">omitidos</span></div>
        <div><span class="rn">{{ resultado.duplicados }}</span><span class="rl">duplicados</span></div>
        <div v-if="resultado.omitidos_por_plan"><span class="rn warn">{{ resultado.omitidos_por_plan }}</span><span class="rl">por plan</span></div>
        <div v-if="resultado.errores"><span class="rn err">{{ resultado.errores }}</span><span class="rl">errores</span></div>
      </div>

      <div v-if="rubrosOrdenados.length" class="imp-rubros">
        <h4>Nuevos por rubro</h4>
        <div class="imp-rubro-chips">
          <span v-for="[rubro, n] in rubrosOrdenados" :key="rubro" class="rubro-chip">
            {{ rubro }} <strong>{{ n }}</strong>
          </span>
        </div>
      </div>

      <div v-if="resultado.detalle_errores?.length" class="imp-muestra omit">
        <h4>Errores</h4>
        <ul>
          <li v-for="(e, i) in resultado.detalle_errores" :key="'e'+i">
            <span class="m-nombre">{{ e.nombre }}</span>
            <span class="m-motivo">{{ e.error }}</span>
          </li>
        </ul>
      </div>

      <div class="imp-actions">
        <button class="imp-btn primary" @click="reset">Importar otro archivo</button>
      </div>
    </div>

    <p v-if="paso === 'idle' && errorMsg" class="imp-error">{{ errorMsg }}</p>
  </section>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRuntimeConfig } from '#app'

const props = defineProps<{
  idComer: string
}>()

const emit = defineEmits<{
  (e: 'importado', resultado: any): void
}>()

const config = useRuntimeConfig()
const API = config.public.apiBase

type Paso = 'idle' | 'analizando' | 'preview' | 'importando' | 'resultado'
const paso = ref<Paso>('idle')
const archivo = ref<File | null>(null)
const preview = ref<any>(null)
const resultado = ref<any>(null)
const errorMsg = ref('')

function getToken(): string {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? (JSON.parse(stored).access_token || '') : ''
  } catch {
    return ''
  }
}

// Rol del usuario actual: admin no tiene tope de plan, comercio sí.
function getRol(): string {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? (JSON.parse(stored).rol || '') : ''
  } catch {
    return ''
  }
}
const esAdmin = ref(false)
onMounted(() => { esAdmin.value = getRol() === 'admin' })

function fmtPrecio(n: any): string {
  const num = Number(n)
  if (isNaN(num)) return '—'
  return num.toLocaleString('es-AR', { style: 'currency', currency: 'ARS', maximumFractionDigits: 0 })
}

const rubrosOrdenados = computed<[string, number][]>(() => {
  const r = resultado.value?.por_rubro || {}
  return Object.entries(r) as [string, number][]
})

function onArchivo(e: Event) {
  const input = e.target as HTMLInputElement
  archivo.value = input.files?.[0] || null
  errorMsg.value = ''
}

async function hacerPreview() {
  if (!archivo.value) return
  paso.value = 'analizando'
  errorMsg.value = ''
  try {
    const fd = new FormData()
    fd.append('file', archivo.value)
    const res = await $fetch<any>(`${API}/comercios/${props.idComer}/productos/preview`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: fd,
    })
    preview.value = res
    paso.value = 'preview'
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo analizar el archivo.'
    paso.value = 'idle'
  }
}

async function confirmarImport() {
  if (!archivo.value) return
  paso.value = 'importando'
  errorMsg.value = ''
  try {
    const fd = new FormData()
    fd.append('file', archivo.value)
    const res = await $fetch<any>(`${API}/comercios/${props.idComer}/productos/importar`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: fd,
    })
    resultado.value = res
    paso.value = 'resultado'
    emit('importado', res)
  } catch (err: any) {
    errorMsg.value = err?.data?.detail || 'No se pudo completar la importación.'
    paso.value = 'preview'
  }
}

function reset() {
  paso.value = 'idle'
  archivo.value = null
  preview.value = null
  resultado.value = null
  errorMsg.value = ''
}
</script>

<style scoped>
.importador {
  background: var(--bg-card, rgba(255, 255, 255, 0.04));
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 16px;
  padding: 1.25rem;
  color: var(--text-primary, #f4f4f5);
}

.imp-header { margin-bottom: 1rem; }
.imp-title {
  display: flex; align-items: center; gap: 0.5rem;
  font-weight: 700; font-size: 1.05rem;
  color: var(--text-primary, #f4f4f5);
}
.imp-title svg { color: var(--accent, #2dd4bf); }
.imp-sub {
  margin: 0.35rem 0 0;
  font-size: 0.85rem;
  color: var(--text-muted, #a1a1aa);
}

/* Paso 1 */
.imp-drop { display: flex; flex-direction: column; gap: 0.75rem; }
.imp-file-btn {
  display: flex; align-items: center; justify-content: center; gap: 0.5rem;
  padding: 1rem; cursor: pointer;
  border: 1.5px dashed var(--border-color, rgba(255, 255, 255, 0.2));
  border-radius: 12px;
  color: var(--text-primary, #f4f4f5);
  transition: border-color 0.15s, background 0.15s;
}
.imp-file-btn:hover { border-color: var(--accent, #2dd4bf); background: rgba(45, 212, 191, 0.05); }
.imp-hint { margin: 0; font-size: 0.78rem; color: var(--text-muted, #a1a1aa); }

/* Estado cargando */
.imp-state {
  display: flex; flex-direction: column; align-items: center; gap: 0.75rem;
  padding: 2rem 1rem; color: var(--text-muted, #a1a1aa);
}
.imp-spinner {
  width: 28px; height: 28px; border-radius: 50%;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: var(--accent, #2dd4bf);
  animation: imp-spin 0.8s linear infinite;
}
@keyframes imp-spin { to { transform: rotate(360deg); } }

/* Preview */
.imp-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.6rem; margin-bottom: 0.9rem; }
.imp-card {
  display: flex; flex-direction: column; align-items: center; gap: 0.15rem;
  padding: 0.85rem 0.5rem; border-radius: 12px;
  background: var(--bg-elevated, rgba(255, 255, 255, 0.05));
}
.imp-card .n { font-size: 1.5rem; font-weight: 800; line-height: 1; }
.imp-card .l { font-size: 0.72rem; color: var(--text-muted, #a1a1aa); }
.imp-card.crear .n { color: #4ade80; }
.imp-card.actualizar .n { color: var(--accent, #2dd4bf); }
.imp-card.omitir .n { color: #a1a1aa; }

.imp-total { font-size: 0.88rem; color: var(--text-muted, #a1a1aa); margin: 0 0 0.75rem; }
.imp-total strong { color: var(--text-primary, #f4f4f5); }

.imp-warn {
  background: rgba(251, 191, 36, 0.12);
  border: 1px solid rgba(251, 191, 36, 0.4);
  color: #fbbf24; border-radius: 10px;
  padding: 0.7rem 0.85rem; font-size: 0.82rem; margin-bottom: 0.9rem;
}

.imp-muestra { margin-bottom: 0.9rem; }
.imp-muestra h4 { font-size: 0.82rem; margin: 0 0 0.4rem; color: var(--text-muted, #a1a1aa); font-weight: 600; }
.imp-muestra ul { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.2rem; max-height: 180px; overflow-y: auto; }
.imp-muestra li {
  display: flex; justify-content: space-between; gap: 0.5rem;
  font-size: 0.82rem; padding: 0.35rem 0.55rem;
  background: var(--bg-elevated, rgba(255, 255, 255, 0.03)); border-radius: 8px;
}
.m-nombre { color: var(--text-primary, #f4f4f5); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.m-precio { color: var(--accent, #2dd4bf); font-weight: 600; flex-shrink: 0; }
.m-motivo { color: #a1a1aa; flex-shrink: 0; font-size: 0.76rem; }

/* Resultado */
.imp-result-head { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem; }
.imp-result-head svg { color: #4ade80; }
.imp-result-head h4 { margin: 0; font-size: 1.05rem; }
.imp-result-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(72px, 1fr)); gap: 0.6rem; margin-bottom: 1rem; }
.imp-result-grid > div {
  display: flex; flex-direction: column; align-items: center; gap: 0.1rem;
  padding: 0.7rem 0.4rem; border-radius: 10px;
  background: var(--bg-elevated, rgba(255, 255, 255, 0.05));
}
.rn { font-size: 1.3rem; font-weight: 800; }
.rn.warn { color: #fbbf24; }
.rn.err { color: #f87171; }
.rl { font-size: 0.7rem; color: var(--text-muted, #a1a1aa); }

.imp-rubros { margin-bottom: 1rem; }
.imp-rubros h4 { font-size: 0.82rem; margin: 0 0 0.4rem; color: var(--text-muted, #a1a1aa); font-weight: 600; }
.imp-rubro-chips { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.rubro-chip {
  font-size: 0.78rem; padding: 0.25rem 0.6rem; border-radius: 999px;
  background: var(--bg-elevated, rgba(255, 255, 255, 0.06));
  color: var(--text-primary, #f4f4f5);
}
.rubro-chip strong { color: var(--accent, #2dd4bf); }

/* Acciones y botones */
.imp-actions { display: flex; justify-content: flex-end; gap: 0.6rem; margin-top: 0.5rem; }
.imp-btn {
  padding: 0.6rem 1.1rem; border-radius: 10px; font-weight: 600; font-size: 0.9rem;
  cursor: pointer; border: none; transition: opacity 0.15s, transform 0.1s;
}
.imp-btn:disabled { opacity: 0.5; cursor: not-allowed; }
.imp-btn.primary { background: var(--accent, #2dd4bf); color: #06201d; }
.imp-btn.primary:hover:not(:disabled) { opacity: 0.9; }
.imp-btn.ghost { background: transparent; color: var(--text-muted, #a1a1aa); border: 1px solid var(--border-color, rgba(255, 255, 255, 0.15)); }

.imp-error { color: #f87171; font-size: 0.85rem; margin-top: 0.6rem; }
</style>