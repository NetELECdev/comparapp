// composables/useOfertas.ts
// Ofertas vigentes (tabla ofertas) cacheadas en memoria y compartidas entre componentes.
export interface OfertaVigente {
  id: string
  id_prod: string
  precio_normal: number
  precio_oferta: number
  descuento_pct: number | null
  fecha_inicio: string | null
  fecha_fin: string
  condicion_oferta: string | null
}

let pendiente: Promise<void> | null = null
const TTL_MS = 5 * 60 * 1000

export function useOfertas() {
  const config = useRuntimeConfig()
  const lista = useState<OfertaVigente[]>('ofertas_vigentes', () => [])
  const cargadoEn = useState<number>('ofertas_cargado_en', () => 0)

  async function cargarOfertas(forzar = false) {
    if (import.meta.server) return
    if (!forzar && Date.now() - cargadoEn.value < TTL_MS) return
    if (pendiente) return pendiente
    pendiente = (async () => {
      try {
        const res = await $fetch<{ results: OfertaVigente[] }>(`${config.public.apiBase}/ofertas`, { query: { limit: 500 } })
        const ahora = Date.now()
        lista.value = (res?.results || []).filter(o =>
          (!o.fecha_inicio || new Date(o.fecha_inicio).getTime() <= ahora) &&
          new Date(o.fecha_fin).getTime() > ahora
        )
        cargadoEn.value = ahora
      } catch (e) {
        console.error('No se pudieron cargar las ofertas:', e)
      } finally {
        pendiente = null
      }
    })()
    return pendiente
  }

  // Si un producto tiene varias ofertas vigentes, se queda con la mas barata
  const porProducto = computed(() => {
    const m = new Map<string, OfertaVigente>()
    for (const o of lista.value) {
      const prev = m.get(o.id_prod)
      if (!prev || Number(o.precio_oferta) < Number(prev.precio_oferta)) m.set(o.id_prod, o)
    }
    return m
  })

  // Oferta aplicable: solo si es mas barata que el precio actual del producto
  function ofertaDe(p: { id_prod?: string; precio_prod?: number | string } | null | undefined): OfertaVigente | null {
    if (!p?.id_prod) return null
    const o = porProducto.value.get(p.id_prod)
    return o && Number(o.precio_oferta) < Number(p.precio_prod) ? o : null
  }

  function precioEfectivo(p: { id_prod?: string; precio_prod?: number | string } | null | undefined): number {
    const o = ofertaDe(p)
    return o ? Number(o.precio_oferta) : Number(p?.precio_prod)
  }

  function pctOferta(p: { id_prod?: string; precio_prod?: number | string } | null | undefined): number {
    const o = ofertaDe(p)
    const normal = Number(p?.precio_prod)
    return o && normal > 0 ? Math.round((1 - Number(o.precio_oferta) / normal) * 100) : 0
  }

  function finOferta(o: OfertaVigente | null): string {
    return o ? new Date(o.fecha_fin).toLocaleDateString('es-AR', { day: '2-digit', month: '2-digit' }) : ''
  }

  return { ofertas: lista, cargarOfertas, ofertaDe, precioEfectivo, pctOferta, finOferta }
}
