const FAVORITOS_KEY = 'comparapp_favoritos'

// Estado global (singleton) para que todos los componentes compartan el mismo array
let _favoritos = null

export const useFavoritos = () => {
  // Si ya existe el estado global, usarlo. Si no, crearlo.
  if (!_favoritos) {
    _favoritos = ref([])
    
    // Cargar desde localStorage solo la primera vez
    try {
      const stored = localStorage.getItem(FAVORITOS_KEY)
      if (stored) {
        _favoritos.value = JSON.parse(stored)
        console.log('📦 Favoritos cargados:', _favoritos.value.length)
      }
    } catch (e) {
      console.error('Error cargando favoritos:', e)
    }
  }

  const favoritos = _favoritos

  const guardarFavoritos = () => {
    try {
      localStorage.setItem(FAVORITOS_KEY, JSON.stringify(favoritos.value))
      console.log('💾 Guardados:', favoritos.value.length, 'favoritos')
    } catch (e) {
      console.error('Error guardando favoritos:', e)
    }
  }

  const esFavorito = (id_prod) => {
    if (!id_prod) return false
    return favoritos.value.some(f => f.id_prod === id_prod)
  }

  const toggleFavorito = (producto) => {
    if (!producto || !producto.id_prod) {
      console.error('❌ toggleFavorito: producto sin id_prod', producto)
      alert('Error: Este producto no tiene ID válido')
      return
    }

    const index = favoritos.value.findIndex(f => f.id_prod === producto.id_prod)
    
    if (index >= 0) {
      console.log('❤️ Quitando favorito:', producto.id_prod, producto.nombre_prod)
      favoritos.value.splice(index, 1)
    } else {
      console.log('❤️ Agregando favorito:', producto.id_prod, producto.nombre_prod)
      favoritos.value.push({
        id_prod: producto.id_prod,
        nombre_prod: producto.nombre_prod,
        marca_prod: producto.marca_prod,
        precio_prod: producto.precio_prod,
        cate_prod: producto.cate_prod,
        imagen_prod: producto.imagen_prod,
        provee_prod: producto.provee_prod,
        fecha_agregado: new Date().toISOString()
      })
    }
    
    guardarFavoritos()
    console.log('📦 Total favoritos ahora:', favoritos.value.length)
  }

  const eliminarFavorito = (id_prod) => {
    if (!id_prod) {
      console.error('❌ eliminarFavorito: id_prod vacío')
      return
    }
    favoritos.value = favoritos.value.filter(f => f.id_prod !== id_prod)
    guardarFavoritos()
  }

  return {
    favoritos: readonly(favoritos),
    esFavorito,
    toggleFavorito,
    eliminarFavorito
  }
}