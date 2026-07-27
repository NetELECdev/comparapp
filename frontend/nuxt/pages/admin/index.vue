<template>
  <div class="admin-page">
    <div class="bg-gradient" />
    <div class="bg-noise" />

    <main class="page-content">
      <!-- HEADER -->
      <header class="page-header animate-fade-in-up">
        <div class="header-left">
          <button class="back-btn" @click="navigateTo('/dashboard')" aria-label="Volver">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m15 18-6-6 6-6"/>
            </svg>
          </button>
          <div>
            <h1 class="page-title">Panel Admin</h1>
            <p class="page-subtitle">Gestión de la plataforma</p>
          </div>
        </div>
        <button class="refresh-btn" @click="loadData" :class="{ spinning: loading }">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 0 0-9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/>
            <path d="M3 3v5h5"/>
            <path d="M3 12a9 9 0 0 0 9 9 9.75 9.75 0 0 0 6.74-2.74L21 16"/>
            <path d="M16 16h5v-5"/>
          </svg>
        </button>
      </header>

      <!-- STATS -->
      <div class="stats-grid animate-fade-in-up stagger-1">
        <div class="stat-card">
          <div class="stat-icon-wrap icon-blue">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="m7.5 4.27 9 5.15"/>
              <path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/>
              <path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ productos.length }}</span>
            <span class="stat-label">Productos</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrap icon-amber">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ comercios.length }}</span>
            <span class="stat-label">Comercios</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrap icon-emerald">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ categoriasUnicas.length }}</span>
            <span class="stat-label">Categorías</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrap icon-fire">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
          <div class="stat-info">
            <span class="stat-value">{{ productosEnOferta.length }}</span>
            <span class="stat-label">En oferta</span>
          </div>
        </div>
      </div>

      <!-- TABS -->
      <div class="tabs-bar animate-fade-in-up stagger-2">
        <button v-for="tab in tabs" :key="tab.id" class="tab-btn" :class="{ active: activeTab === tab.id }" @click="activeTab = tab.id; tab.id === 'comercios-pendientes' && cargarComerciosPendientes(); tab.id === 'usuarios' && cargarUsuarios()">
          <span v-html="tab.icon"></span>
          <span class="tab-label">{{ tab.label }}</span>
          <span v-if="tab.id === 'comercios-pendientes' && comerciosPendientes.length > 0" class="tab-badge">{{ comerciosPendientes.length }}</span>
        </button>
      </div>

      <!-- TAB: PRODUCTOS -->
      <div v-if="activeTab === 'productos'" class="tab-content animate-fade-in-up">
        <div class="section-header">
          <div class="search-box">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input v-model="searchProductos" placeholder="Buscar producto..." />
          </div>
          <button class="btn-primary" @click="openModal('producto')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14"/><path d="M12 5v14"/>
            </svg>
            Nuevo
          </button>
        </div>

        <div v-if="productosFiltrados.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
          </div>
          <h3>No hay productos</h3>
          <p>Cargá el primer producto</p>
        </div>

        <div v-else class="items-list">
          <div v-for="p in productosFiltrados" :key="p.id_prod" class="item-card" :class="{ 'en-oferta': ofertaActivaPorProducto(p.id_prod) }">
            <div class="item-main">
              <img :src="p.imagen_prod || '/images/avatar_default.png'" class="item-thumb" @error="$event.target.src='/images/avatar_default.png'"/>
              <div class="item-info">
                <div class="item-name-row">
                  <span class="item-name">{{ p.nombre_prod }}</span>
                  <span v-if="ofertaActivaPorProducto(p.id_prod)" class="oferta-badge-mini">
                    🔥 -{{ ofertaActivaPorProducto(p.id_prod)?.descuento_pct }}%
                  </span>
                </div>
                <div class="item-meta">
                  <span class="badge">{{ p.cate_prod }}</span>
                  <span class="badge">{{ p.marca_prod }}</span>
                  <span v-if="ofertaActivaPorProducto(p.id_prod)" class="price precio-con-oferta">
                    <span class="precio-tachado">${{ formatPrice(p.precio_prod) }}</span>
                    <span class="precio-nuevo">${{ formatPrice(ofertaActivaPorProducto(p.id_prod)?.precio_oferta) }}</span>
                  </span>
                  <span v-else class="price">${{ formatPrice(p.precio_prod) }}</span>
                </div>
                <span class="item-sub">{{ p.comercio_prod }} • {{ p.cantidad_prod }} {{ p.unidad_prod }}</span>
              </div>
            </div>

            <div class="item-actions">
              <!-- Toggle oferta -->
              <button
                class="action-btn oferta-toggle"
                :class="{ active: ofertaActivaPorProducto(p.id_prod) }"
                @click="toggleOfertaPanel(p)"
                :title="ofertaActivaPorProducto(p.id_prod) ? 'Gestionar oferta' : 'Activar oferta'"
              >
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                </svg>
              </button>
              <button class="action-btn edit" @click="editProducto(p)" title="Editar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/>
                </svg>
              </button>
              <button class="action-btn delete" @click="confirmDelete('producto', p)" title="Eliminar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                </svg>
              </button>
            </div>

            <!-- PANEL OFERTA INLINE -->
            <Transition name="slide-down">
              <div v-if="ofertaPanelProductoId === p.id_prod" class="oferta-panel">
                <div class="oferta-panel-header">
                  <span>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
                    </svg>
                    {{ ofertaActivaPorProducto(p.id_prod) ? 'Oferta activa' : 'Nueva oferta' }}
                  </span>
                  <button class="oferta-panel-close" @click="ofertaPanelProductoId = null">✕</button>
                </div>

                <div class="oferta-panel-body">
                  <div class="oferta-panel-grid">
                    <div class="form-group">
                      <label>Precio normal</label>
                      <input :value="formatPrice(p.precio_prod)" disabled class="input-disabled" />
                    </div>
                    <div class="form-group">
                      <label>Precio oferta *</label>
                      <input
                        v-model.number="formOfertaPanel.precio_oferta"
                        type="number" step="0.01" min="0.01"
                        placeholder="Ej: 1199.00"
                        @input="calcularDescuentoPanel(Number(p.precio_prod))"
                      />
                    </div>
                  </div>

                  <div v-if="descuentoPanel > 0 && !errorPrecioPanel" class="descuento-chip">
                    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
                    -{{ descuentoPanel }}% · Ahorrás ${{ formatPrice(Number(p.precio_prod) - formOfertaPanel.precio_oferta) }}
                  </div>
                  <div v-if="errorPrecioPanel" class="oferta-error">⚠️ El precio de oferta debe ser menor al precio normal</div>

                  <div class="form-group">
                    <label>Vence el *</label>
                    <input v-model="formOfertaPanel.fecha_fin" type="datetime-local" />
                  </div>

                  <div class="oferta-panel-actions">
                    <button
                      v-if="ofertaActivaPorProducto(p.id_prod)"
                      class="btn-desactivar"
                      @click="desactivarOferta(p)"
                      :disabled="savingOferta"
                    >
                      {{ savingOferta ? '...' : 'Desactivar oferta' }}
                    </button>
                    <button
                      class="btn-guardar-oferta"
                      @click="guardarOferta(p)"
                      :disabled="savingOferta || errorPrecioPanel || !formOfertaPanel.precio_oferta || !formOfertaPanel.fecha_fin"
                    >
                      {{ savingOferta ? 'Guardando...' : (ofertaActivaPorProducto(p.id_prod) ? 'Actualizar' : 'Activar oferta') }}
                    </button>
                  </div>
                </div>
              </div>
            </Transition>
          </div>
        </div>
      </div>

      <!-- TAB: PROVEEDORES -->
      <div v-if="activeTab === 'comercios'" class="tab-content animate-fade-in-up">
        <div class="section-header">
          <div class="search-box">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input v-model="searchComercios" placeholder="Buscar comercio..." />
          </div>
          <button class="btn-primary" @click="openModal('comercio')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M5 12h14"/><path d="M12 5v14"/>
            </svg>
            Nuevo
          </button>
        </div>
        <div v-if="geoEstado !== 'ok'" class="geo-bar">
          <span>
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
            </svg>
            <template v-if="geoEstado === 'error'">No se pudo obtener tu ubicación — las distancias no se muestran.</template>
            <template v-else-if="geoEstado === 'pidiendo'">Obteniendo tu ubicación...</template>
            <template v-else>Activá tu ubicación para ver la distancia a cada comercio.</template>
          </span>
          <button class="btn-sm" @click="pedirUbicacionAdmin" :disabled="geoEstado === 'pidiendo'">
            {{ geoEstado === 'pidiendo' ? '...' : 'Activar ubicación' }}
          </button>
        </div>
        <div v-if="comerciosFiltrados.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/>
            </svg>
          </div>
          <h3>No hay comercios</h3>
          <p>Cargá el primer comercio</p>
        </div>
        <div v-else class="cards-grid">
          <div v-for="prov in comerciosFiltrados" :key="prov.id_comer" class="provider-card">
            <div class="provider-header">
              <img :src="prov.logo_comer || '/images/avatar_default.png'" class="provider-logo" @error="$event.target.src='/images/avatar_default.png'"/>
              <div class="provider-status" :class="prov.activo_comer ? 'active' : 'inactive'" />
            </div>
            <h3 class="provider-name">{{ prov.nombre_comer }}</h3>
            <p class="provider-cat">
              {{ prov.cate_comer }}
              <span v-if="prov.plan_comer === 'premium'" class="badge-rol badge-rol--admin" style="margin-left: 0.4rem;">Premium</span>
            </p>
            <div class="provider-meta">
              <span v-if="prov.direccion_comer">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                {{ prov.direccion_comer }}
              </span>
              <span v-if="prov.email_comer">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
                </svg>
                {{ prov.email_comer }}
              </span>
            </div>
            <div class="provider-stats">
              <span class="provider-stat">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/>
                </svg>
                {{ contarProductos(prov) }} {{ contarProductos(prov) === 1 ? 'producto' : 'productos' }}
              </span>
              <span class="provider-stat" v-if="distanciaComercio(prov) !== null">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                {{ distanciaComercio(prov) }} km
              </span>
              <span class="provider-stat provider-stat--muted" v-else-if="prov.lat == null || prov.lng == null" title="Este comercio no tiene ubicación cargada">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                sin ubicación
              </span>
              <span class="provider-stat provider-stat--muted" v-else title="Activá tu ubicación para ver la distancia">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>
                </svg>
                — km
              </span>
            </div>
            <div class="provider-actions">
              <button class="btn-sm" @click="editComercio(prov)">Editar</button>
              <button class="btn-sm danger" @click="confirmDelete('comercio', prov)">Eliminar</button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: CATEGORÍAS -->
      <div v-if="activeTab === 'categorias'" class="tab-content animate-fade-in-up">
        <div class="section-header">
          <h2 class="section-title">Categorías detectadas</h2>
          <span class="section-badge">{{ categoriasUnicas.length }}</span>
        </div>
        <div class="cards-grid categories-grid">
          <div v-for="cat in categoriasConConteo" :key="cat.nombre" class="category-card">
            <div class="cat-icon">{{ getDefaultIcon(cat.nombre) }}</div>
            <h3>{{ cat.nombre }}</h3>
            <p>{{ cat.cantidad }} productos</p>
            <div class="cat-bar">
              <div class="cat-bar-fill" :style="{ width: cat.porcentaje + '%', background: cat.color }" />
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: OFERTAS (vista resumen) -->
      <div v-if="activeTab === 'ofertas'" class="tab-content animate-fade-in-up">
        <div class="section-header">
          <h2 class="section-title">Ofertas vigentes</h2>
          <span class="section-badge">{{ productosEnOferta.length }}</span>
        </div>

        <div v-if="loadingOfertas" class="loading-state">
          <div class="loading-spinner" />
          <p>Cargando ofertas...</p>
        </div>

        <div v-else-if="productosEnOferta.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/>
            </svg>
          </div>
          <h3>Sin ofertas activas</h3>
          <p>Andá a Productos y tocá el ícono 🔥 para activar una oferta</p>
        </div>

        <div v-else class="items-list">
          <div v-for="oferta in productosEnOferta" :key="oferta.id" class="item-card oferta-card">
            <div class="item-main">
              <img :src="oferta.imagen_prod || '/images/avatar_default.png'" class="item-thumb" @error="$event.target.src='/images/avatar_default.png'"/>
              <div class="item-info">
                <div class="item-name-row">
                  <span class="item-name">{{ oferta.nombre_prod }}</span>
                  <span class="oferta-badge-mini">-{{ oferta.descuento_pct }}%</span>
                </div>
                <div class="item-meta">
                  <span class="badge">{{ oferta.cate_prod }}</span>
                  <span class="price precio-con-oferta">
                    <span class="precio-tachado">${{ formatPrice(oferta.precio_normal) }}</span>
                    <span class="precio-nuevo">${{ formatPrice(oferta.precio_oferta) }}</span>
                  </span>
                </div>
                <span class="item-sub oferta-vence">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>
                  </svg>
                  Vence {{ formatFechaOferta(oferta.fecha_fin) }}
                </span>
              </div>
            </div>
            <div class="item-actions">
              <button class="action-btn delete" @click="desactivarOfertaById(oferta)" title="Desactivar">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>
                  <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB: USUARIOS -->
      <div v-if="activeTab === 'usuarios'" class="tab-content animate-fade-in-up">
        <div class="section-header">
          <div class="search-box">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>
            </svg>
            <input v-model="searchUsuarios" placeholder="Buscar por nombre o email..." />
          </div>
        </div>

        <div v-if="loadingUsuarios" class="empty-state">
          <div class="loading-spinner" />
          <p>Cargando usuarios...</p>
        </div>

        <div v-else-if="usuariosFiltrados.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/>
              <path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          </div>
          <h3>Sin usuarios</h3>
          <p>No hay usuarios que coincidan con la búsqueda.</p>
        </div>

        <div v-else class="items-list">
          <article v-for="u in usuariosFiltrados" :key="u.id_user" class="usuario-item">
            <img
              :src="u.avatar_url_user || '/images/avatar_default.png'"
              class="usuario-avatar"
              @error="($event.target as HTMLImageElement).src = '/images/avatar_default.png'"
            />
            <div class="usuario-info">
              <div class="usuario-nombre-row">
                <span class="item-name">{{ u.nombre_completo_user || 'Sin nombre' }}</span>
                <span v-if="u.id_user === miPropioId" class="badge-tu">Tu cuenta</span>
              </div>
              <span class="usuario-email">{{ u.email_user }}</span>
              <div class="usuario-badges">
                <span class="badge-rol" :class="`badge-rol--${u.rol_user}`">{{ rolLabel(u.rol_user) }}</span>
                <span v-if="u.es_comercio_user" class="badge-comercio" :class="{ 'badge-comercio--pendiente': !u.comercio_verificado_user }">
                  🏪 {{ u.comercio_verificado_user ? (u.comercio?.nombre_comer || 'Comercio') : 'Pendiente de aprobación' }}
                </span>
                <span class="badge-estado" :class="u.activo_user ? 'badge-estado--activo' : 'badge-estado--inactivo'">
                  {{ u.activo_user ? 'Activo' : 'Desactivado' }}
                </span>
              </div>
            </div>

            <div v-if="u.id_user !== miPropioId" class="usuario-actions">
              <select
                class="rol-select"
                :value="u.rol_user"
                @change="pedirCambioRol(u, ($event.target as HTMLSelectElement).value as any)"
              >
                <option value="usuario">Usuario</option>
                <option value="comercio">Comercio</option>
                <option value="admin">Admin</option>
              </select>
              <button v-if="u.activo_user" class="btn-sm danger" @click="confirmDelete('usuario', u)">Desactivar</button>
              <button v-else class="btn-sm" @click="reactivarUsuario(u)">Reactivar</button>
            </div>
            <div v-else class="usuario-actions usuario-actions--self">
              <span class="form-hint">No podés modificar tu propia cuenta</span>
            </div>
          </article>
        </div>
      </div>

      <!-- TAB: Solicitudes de comercio pendientes -->
      <div v-if="activeTab === 'comercios-pendientes'" class="tab-content animate-fade-in-up">
        <div v-if="loadingPendientes" class="empty-state">
          <div class="loading-spinner" />
          <p>Cargando solicitudes...</p>
        </div>

        <div v-else-if="comerciosPendientes.length === 0" class="empty-state">
          <div class="empty-icon-wrap">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M9 11l3 3L22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
            </svg>
          </div>
          <h3>Sin solicitudes pendientes</h3>
          <p>Cuando un comercio se registre, va a aparecer acá para tu revisión.</p>
        </div>

        <div v-else class="items-list">
          <article v-for="sol in comerciosPendientes" :key="sol.id_user" class="solicitud-item">
            <div class="solicitud-info">
              <span class="item-name">{{ sol.nombre_completo_user }}</span>
              <span class="solicitud-comercio">{{ sol.comercio?.nombre_comer || 'Sin comercio' }}</span>
              <span class="solicitud-meta">{{ sol.email_user }} · {{ sol.telefono_user || 'Sin teléfono' }}</span>
              <span class="solicitud-direccion" v-if="sol.comercio?.direccion_comer">{{ sol.comercio.direccion_comer }}</span>
            </div>
            <div class="solicitud-actions">
              <button class="btn-rechazar" @click="rechazarSolicitud(sol.id_user)" :disabled="procesandoId === sol.id_user">
                Rechazar
              </button>
              <button class="btn-aprobar" @click="aprobarSolicitud(sol.id_user)" :disabled="procesandoId === sol.id_user">
                {{ procesandoId === sol.id_user ? '...' : 'Aprobar' }}
              </button>
            </div>
          </article>
        </div>
      </div>
    </main>

    <!-- BOTTOM BAR -->
    <div class="bottom-bar">
      <button class="bottom-btn" @click="navigateTo('/dashboard')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
        <span>Inicio</span>
      </button>
      <button class="bottom-btn bottom-btn--accent" @click="navigateTo('/productos')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m16 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="m2 16 3-8 3 8c-.87.65-1.92 1-3 1s-2.13-.35-3-1Z"/><path d="M7 21h10"/><path d="M12 3v18"/><path d="M3 7h2c2 0 5-1 7-2 2 1 5 2 7 2h2"/></svg>
        <span>Comparar</span>
      </button>
      <button class="bottom-btn" @click="navigateTo('/productos')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>
        <span>Productos</span>
      </button>
      <button class="bottom-btn" @click="navigateTo('/perfil')">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        <span>Perfil</span>
      </button>
    </div>

    <!-- MODAL PRODUCTO -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalProductoOpen" class="modal-overlay" @click.self="closeModalProducto">
          <div class="modal-container">
            <div class="modal-header">
              <h3>{{ editingProductoId ? 'Editar Producto' : 'Nuevo Producto' }}</h3>
              <button class="modal-close" @click="closeModalProducto">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
              </button>
            </div>
            <form class="modal-body form-grid" @submit.prevent="saveProducto">
              <div class="form-group full">
                <label>Nombre *</label>
                <input v-model="formProducto.nombre_prod" required placeholder="Ej: Crema de Leche" />
              </div>
              <div class="form-group">
                <label>Categoría *</label>
                <select v-model="formProducto.cate_prod" required>
                  <option value="">Seleccionar...</option>
                  <option v-for="cat in categoriasBD" :key="cat.id" :value="cat.nombre">{{ cat.nombre }}</option>
                </select>
                <input v-if="formProducto.cate_prod === '__nueva__'" v-model="nuevaCategoria" placeholder="Nueva categoría..." class="mt-2" />
              </div>
              <div class="form-group">
                <label>Marca *</label>
                <input v-model="formProducto.marca_prod" required placeholder="Ej: Tonadita" />
              </div>
              <div class="form-group">
                <label>Precio *</label>
                <input v-model="formProducto.precio_prod" type="number" step="0.01" required placeholder="1499.00" />
              </div>
              <div class="form-group">
                <label>Cantidad del envase</label>
                <input v-model="formProducto.cantidad_prod" type="number" placeholder="200" />
                <span class="form-hint">
                  <template v-if="formProducto.unidad_prod === 'Unidad'">
                    Ej: pañales x8 → poner 8
                  </template>
                  <template v-else-if="formProducto.unidad_prod === 'Gramo'">
                    Ej: arroz 500g → poner 500
                  </template>
                  <template v-else-if="formProducto.unidad_prod === 'Mililitro'">
                    Ej: jugo 500ml → poner 500
                  </template>
                  <template v-else-if="formProducto.unidad_prod === 'Kilogramo'">
                    Ej: carne 1kg → poner 1
                  </template>
                  <template v-else-if="formProducto.unidad_prod === 'Litro'">
                    Ej: aceite 1.5L → poner 1.5
                  </template>
                  <template v-else>
                    Cantidad real del envase en la unidad seleccionada
                  </template>
                </span>
              </div>
              <div class="form-group">
                <label>Unidad de medida</label>
                <select v-model="formProducto.unidad_prod">
                  <option v-for="m in medidas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                </select>
                <span class="form-hint">Unidad del envase (no de la unidad mínima)</span>
              </div>
              <div class="form-group full">
                <label>Comercio *</label>
                <select v-model="formProducto.comercio_prod" required>
                  <option value="">Seleccionar...</option>
                  <option v-for="prov in comercios" :key="prov.id_comer" :value="prov.nombre_comer">{{ prov.nombre_comer }}</option>
                </select>
              </div>
              <div class="form-group full">
                <label>Descripción</label>
                <textarea v-model="formProducto.describe_prod" rows="2" placeholder="Descripción..."></textarea>
              </div>
              <div class="form-group full">
                <label>Imagen URL</label>
                <input v-model="formProducto.imagen_prod" placeholder="https://..." />
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input v-model="formProducto.activo_prod" type="checkbox" />
                  <span>Activo</span>
                </label>
              </div>
              <div class="form-actions full">
                <button type="button" class="btn-secondary" @click="closeModalProducto">Cancelar</button>
                <button type="submit" class="btn-primary" :disabled="saving">
                  {{ saving ? 'Guardando...' : (editingProductoId ? 'Actualizar' : 'Crear') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- MODAL PROVEEDOR -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modalComercioOpen" class="modal-overlay" @click.self="closeModalComercio">
          <div class="modal-container">
            <div class="modal-header">
              <h3>{{ editingComercioId ? 'Editar Comercio' : 'Nuevo Comercio' }}</h3>
              <button class="modal-close" @click="closeModalComercio">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
              </button>
            </div>
            <form class="modal-body form-grid" @submit.prevent="saveComercio">
              <div class="form-group full">
                <label>Nombre *</label>
                <input v-model="formComercio.nombre_comer" required placeholder="Ej: Autoservicio Real" />
              </div>
              <div class="form-group">
                <label>Categoría</label>
                <input v-model="formComercio.cate_comer" placeholder="Ej: Comercio" />
              </div>
              <div class="form-group">
                <label>Teléfono</label>
                <input v-model="formComercio.te_comer" placeholder="+54..." />
              </div>
              <div class="form-group full">
                <label>Email</label>
                <input v-model="formComercio.email_comer" type="email" placeholder="email@..." />
              </div>
              <div class="form-group full">
                <label>Dirección</label>
                <input v-model="formComercio.direccion_comer" placeholder="Rio Negro 528..." />
              </div>
              <div class="form-group full">
                <label>Ubicación (pegar de Google Maps)</label>
                <input v-model="coordsPegar" placeholder="-34.6177, -68.3360" @input="parsearCoordenadas" />
                <span class="form-hint">Clic derecho en el local en Google Maps → tocá las coordenadas para copiarlas → pegalas acá. Se completan lat/lng solos.</span>
              </div>
              <div class="form-group">
                <label>Latitud</label>
                <input v-model.number="formComercio.lat" type="number" step="any" placeholder="-34.6177" />
              </div>
              <div class="form-group">
                <label>Longitud</label>
                <input v-model.number="formComercio.lng" type="number" step="any" placeholder="-68.3360" />
              </div>
              <div class="form-group full">
                <label>Representante</label>
                <input v-model="formComercio.representa_comer" placeholder="Nombre contacto" />
              </div>
              <div class="form-group full">
                <label>Logo URL</label>
                <input v-model="formComercio.logo_comer" placeholder="https://..." />
              </div>
              <div class="form-group">
                <label>Plan</label>
                <select v-model="formComercio.plan_comer">
                  <option value="free">Gratis (hasta 10 productos)</option>
                  <option value="premium">Premium (ilimitado)</option>
                </select>
              </div>
              <div class="form-group">
                <label>Vence el (si es premium)</label>
                <input v-model="formComercio.plan_vencimiento_comer" type="date" :disabled="formComercio.plan_comer !== 'premium'" />
              </div>
              <div class="form-group">
                <label class="checkbox-label">
                  <input v-model="formComercio.activo_comer" type="checkbox" />
                  <span>Activo</span>
                </label>
              </div>
              <div class="form-actions full">
                <button type="button" class="btn-secondary" @click="closeModalComercio">Cancelar</button>
                <button type="submit" class="btn-primary" :disabled="saving">
                  {{ saving ? 'Guardando...' : (editingComercioId ? 'Actualizar' : 'Crear') }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- CONFIRM DELETE -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteModalOpen" class="modal-overlay" @click.self="deleteModalOpen = false">
          <div class="modal-container modal-sm">
            <div class="modal-header"><h3>¿Eliminar?</h3></div>
            <div class="modal-body">
              <p class="confirm-text" v-if="deleteType === 'producto'">¿Eliminar {{ deleteItemName }}? No se puede deshacer.</p>
              <p class="confirm-text" v-else-if="deleteType === 'comercio'">¿Desactivar "{{ deleteItemName }}"? Deja de aparecer activo en la plataforma, pero podés reactivarlo después.</p>
              <p class="confirm-text" v-else-if="deleteType === 'usuario'">¿Desactivar a "{{ deleteItemName }}"? No va a poder usar la app hasta que lo reactives.</p>
              <p class="confirm-text" v-else>¿Eliminar {{ deleteItemName }}?</p>
              <div class="form-actions">
                <button class="btn-secondary" @click="deleteModalOpen = false">Cancelar</button>
                <button class="btn-danger" @click="executeDelete" :disabled="deleting">
                  {{ deleting ? 'Eliminando...' : 'Sí, eliminar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- CONFIRM CAMBIO DE ROL -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="roleModalOpen" class="modal-overlay" @click.self="roleModalOpen = false">
          <div class="modal-container modal-sm">
            <div class="modal-header"><h3>¿Cambiar rol?</h3></div>
            <div class="modal-body">
              <p class="confirm-text">
                ¿Cambiar el rol de <strong>{{ roleChangeUsuario?.nombre_completo_user }}</strong>
                de <strong>{{ rolLabel(roleChangeUsuario?.rol_user || '') }}</strong>
                a <strong>{{ rolLabel(roleChangeNuevoRol) }}</strong>?
              </p>
              <p v-if="roleChangeNuevoRol === 'admin'" class="form-hint form-hint--warning">
                ⚠️ Le vas a dar acceso total de administrador a la plataforma.
              </p>
              <div class="form-actions">
                <button class="btn-secondary" @click="roleModalOpen = false">Cancelar</button>
                <button class="btn-primary" @click="confirmarCambioRol" :disabled="cambiandoRol">
                  {{ cambiandoRol ? 'Aplicando...' : 'Confirmar' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- TOAST -->
    <Teleport to="body">
      <Transition name="toast">
        <div v-if="toast.show" class="toast" :class="toast.type">
          <svg v-if="toast.type === 'success'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M20 6 9 17l-5-5"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" x2="12" y1="8" y2="12"/><line x1="12" x2="12.01" y1="16" y2="16"/></svg>
          {{ toast.message }}
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRuntimeConfig, navigateTo } from '#app'

// ─── INTERFACES ───────────────────────────────────────────────

interface Producto {
  id_prod: string
  nombre_prod: string
  cate_prod: string
  describe_prod: string | null
  unidad_prod: string
  cantidad_prod: number
  activo_prod: boolean
  comercio_prod: string
  fecha_prod: string
  marca_prod: string
  imagen_prod: string | null
  precio_prod: string
}

interface Comercio {
  id_comer: string
  nombre_comer: string
  direccion_comer: string | null
  te_comer: string | null
  email_comer: string | null
  representa_comer: string | null
  fechaIngreso_comer: string
  activo_comer: boolean
  cate_comer: string
  logo_comer: string | null
  plan_comer?: string | null
  plan_vencimiento_comer?: string | null
  lat?: number | null
  lng?: number | null
}

interface Oferta {
  id: string
  id_prod: string
  precio_normal: number
  precio_oferta: number
  descuento_pct: number
  fecha_inicio: string
  fecha_fin: string
  activa: boolean
  nombre_prod: string
  marca_prod: string
  cate_prod: string
  imagen_prod: string | null
}

// ─── ESTADO BASE ──────────────────────────────────────────────

const config = useRuntimeConfig()
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const productos = ref<Producto[]>([])
const comercios = ref<Comercio[]>([])
const medidas = ref<{id: number, nombre: string}[]>([])
const categoriasBD = ref<{id: number, nombre: string}[]>([])
const ofertas = ref<Oferta[]>([])
const loadingOfertas = ref(false)

const activeTab = ref('productos')
const searchProductos = ref('')
const searchComercios = ref('')

// ─── Solicitudes de comercio pendientes ──────────────────────
interface Usuario {
  id_user: string
  email_user: string
  nombre_completo_user: string
  rol_user: 'usuario' | 'comercio' | 'admin'
  es_comercio_user: boolean
  comercio_verificado_user: boolean
  activo_user: boolean
  avatar_url_user: string | null
  fecha_registro_user: string | null
  id_comer: string | null
  comercio?: { nombre_comer: string } | null
}

interface SolicitudComercio {
  id_user: string
  email_user: string
  nombre_completo_user: string
  telefono_user: string | null
  fecha_registro_user: string
  id_comer: string
  comercio?: { nombre_comer: string; direccion_comer: string }
}
const comerciosPendientes = ref<SolicitudComercio[]>([])
const loadingPendientes = ref(false)
const procesandoId = ref<string | null>(null)

// ─── Gestión de usuarios ──────────────────────────────────────
const usuarios = ref<Usuario[]>([])
const loadingUsuarios = ref(false)
const searchUsuarios = ref('')
const miPropioId = ref('')

const usuariosFiltrados = computed(() => {
  if (!searchUsuarios.value.trim()) return usuarios.value
  const q = searchUsuarios.value.toLowerCase()
  return usuarios.value.filter(u =>
    u.email_user?.toLowerCase().includes(q) || u.nombre_completo_user?.toLowerCase().includes(q)
  )
})

function rolLabel(rol: string) {
  if (rol === 'admin') return 'Admin'
  if (rol === 'comercio') return 'Comercio'
  return 'Usuario'
}

async function cargarUsuarios() {
  loadingUsuarios.value = true
  try {
    const res = await $fetch<{ count: number; results: Usuario[] }>(
      `${config.public.apiBase}/admin/usuarios`,
      { headers: { Authorization: `Bearer ${getToken()}` } }
    )
    usuarios.value = res.results || []
  } catch (err) {
    console.error('Error cargando usuarios:', err)
    showToast('Error cargando usuarios', 'error')
  } finally {
    loadingUsuarios.value = false
  }
}

// Cambiar rol — pide confirmación siempre, porque tocar el rol (sobre todo
// promover a admin) es una acción sensible que no debería salir de un solo click.
const roleModalOpen = ref(false)
const roleChangeUsuario = ref<Usuario | null>(null)
const roleChangeNuevoRol = ref<'usuario' | 'comercio' | 'admin'>('usuario')
const cambiandoRol = ref(false)

function pedirCambioRol(u: Usuario, nuevoRol: 'usuario' | 'comercio' | 'admin') {
  if (nuevoRol === u.rol_user) return
  roleChangeUsuario.value = u
  roleChangeNuevoRol.value = nuevoRol
  roleModalOpen.value = true
}

async function confirmarCambioRol() {
  if (!roleChangeUsuario.value) return
  cambiandoRol.value = true
  try {
    await $fetch(`${config.public.apiBase}/admin/usuarios/${roleChangeUsuario.value.id_user}/rol`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: { rol: roleChangeNuevoRol.value }
    })
    const idx = usuarios.value.findIndex(u => u.id_user === roleChangeUsuario.value?.id_user)
    if (idx >= 0) usuarios.value[idx].rol_user = roleChangeNuevoRol.value
    showToast(`Rol actualizado a "${rolLabel(roleChangeNuevoRol.value)}"`)
    roleModalOpen.value = false
  } catch (err: any) {
    showToast(err?.data?.detail || 'No se pudo cambiar el rol', 'error')
  } finally {
    cambiandoRol.value = false
  }
}

// Reactivar: acción segura y reversible, sin modal.
// Desactivar: pasa por el mismo modal de confirmación que productos/comercios.
async function reactivarUsuario(u: Usuario) {
  try {
    await $fetch(`${config.public.apiBase}/admin/usuarios/${u.id_user}/estado`, {
      method: 'PUT',
      headers: { Authorization: `Bearer ${getToken()}` },
      body: { activo: true }
    })
    const idx = usuarios.value.findIndex(x => x.id_user === u.id_user)
    if (idx >= 0) usuarios.value[idx].activo_user = true
    showToast('Usuario reactivado')
  } catch (err: any) {
    showToast(err?.data?.detail || 'No se pudo reactivar', 'error')
  }
}

function getToken() {
  try {
    const stored = localStorage.getItem('comparapp_user')
    return stored ? JSON.parse(stored).access_token || '' : ''
  } catch { return '' }
}

async function cargarComerciosPendientes() {
  loadingPendientes.value = true
  try {
    const token = getToken()
    const res = await $fetch<{ count: number; results: SolicitudComercio[] }>(
      `${config.public.apiBase}/admin/comercios-pendientes`,
      { headers: { Authorization: `Bearer ${token}` } }
    )
    comerciosPendientes.value = res.results || []
  } catch (err) {
    console.error('Error cargando solicitudes:', err)
  } finally {
    loadingPendientes.value = false
  }
}

async function aprobarSolicitud(userId: string) {
  procesandoId.value = userId
  try {
    const token = getToken()
    await $fetch(`${config.public.apiBase}/admin/comercios/${userId}/aprobar`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` }
    })
    comerciosPendientes.value = comerciosPendientes.value.filter(s => s.id_user !== userId)
    showToast('Comercio aprobado correctamente')
  } catch (err: any) {
    showToast(err?.data?.detail || 'Error al aprobar', 'error')
  } finally {
    procesandoId.value = null
  }
}

async function rechazarSolicitud(userId: string) {
  const motivo = prompt('Motivo del rechazo (opcional):')
  procesandoId.value = userId
  try {
    const token = getToken()
    await $fetch(`${config.public.apiBase}/admin/comercios/${userId}/rechazar`, {
      method: 'POST',
      headers: { Authorization: `Bearer ${token}` },
      body: { motivo: motivo || null }
    })
    comerciosPendientes.value = comerciosPendientes.value.filter(s => s.id_user !== userId)
    showToast('Solicitud rechazada')
  } catch (err: any) {
    showToast(err?.data?.detail || 'Error al rechazar', 'error')
  } finally {
    procesandoId.value = null
  }
}

const tabs = [
  { id: 'productos',   label: 'Productos',   icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m7.5 4.27 9 5.15"/><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"/><path d="m3.3 7 8.7 5 8.7-5"/><path d="M12 22V12"/></svg>' },
  { id: 'comercios', label: 'Comercios', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 7h-9"/><path d="M14 17H5"/><circle cx="17" cy="17" r="3"/><circle cx="7" cy="7" r="3"/></svg>' },
  { id: 'categorias',  label: 'Categorías',  icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9h18v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9Z"/><path d="m3 9 2.45-4.9A2 2 0 0 1 7.24 3h9.52a2 2 0 0 1 1.8 1.1L21 9"/><path d="M12 3v6"/></svg>' },
  { id: 'ofertas',     label: 'Ofertas',     icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>' },
  { id: 'usuarios',    label: 'Usuarios',    icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>' },
  { id: 'comercios-pendientes', label: 'Solicitudes', icon: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>' },
]

// ─── COMPUTED ─────────────────────────────────────────────────

const productosFiltrados = computed(() => {
  if (!searchProductos.value) return productos.value
  const q = searchProductos.value.toLowerCase()
  return productos.value.filter(p =>
    p.nombre_prod.toLowerCase().includes(q) ||
    p.marca_prod.toLowerCase().includes(q) ||
    p.cate_prod.toLowerCase().includes(q)
  )
})

const comerciosFiltrados = computed(() => {
  if (!searchComercios.value) return comercios.value
  const q = searchComercios.value.toLowerCase()
  return comercios.value.filter(p =>
    p.nombre_comer.toLowerCase().includes(q) ||
    (p.direccion_comer && p.direccion_comer.toLowerCase().includes(q))
  )
})

// ─── Ubicación del admin + distancia a cada comercio ──────────
const adminPos = ref<{ lat: number; lng: number } | null>(null)
const geoEstado = ref<'idle' | 'pidiendo' | 'ok' | 'error'>('idle')

function pedirUbicacionAdmin() {
  if (!('geolocation' in navigator)) { geoEstado.value = 'error'; return }
  geoEstado.value = 'pidiendo'
  navigator.geolocation.getCurrentPosition(
    (pos) => {
      adminPos.value = { lat: pos.coords.latitude, lng: pos.coords.longitude }
      geoEstado.value = 'ok'
    },
    () => { geoEstado.value = 'error' },
    { enableHighAccuracy: false, timeout: 8000, maximumAge: 300000 }
  )
}

function haversine(lat1: number, lng1: number, lat2: number, lng2: number): number {
  const R = 6371
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat / 2) ** 2 +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLng / 2) ** 2
  return Math.round(R * 2 * Math.asin(Math.sqrt(a)) * 10) / 10
}

function distanciaComercio(prov: Comercio): number | null {
  if (!adminPos.value) return null
  if (prov.lat == null || prov.lng == null) return null
  return haversine(adminPos.value.lat, adminPos.value.lng, Number(prov.lat), Number(prov.lng))
}

// ─── Cantidad de productos por comercio ───────────────────────
// Se cuenta desde los productos ya cargados. comercio_prod es texto libre que
// espeja nombre_comer, así que se compara en minúsculas y sin espacios (mismo
// criterio case-insensitive que usa el resto del sistema).
const productosPorComercio = computed(() => {
  const map = new Map<string, number>()
  for (const p of productos.value) {
    const key = (p.comercio_prod || '').trim().toLowerCase()
    if (!key) continue
    map.set(key, (map.get(key) || 0) + 1)
  }
  return map
})

function contarProductos(prov: Comercio): number {
  return productosPorComercio.value.get((prov.nombre_comer || '').trim().toLowerCase()) || 0
}

const categoriasUnicas = computed(() => {
  const set = new Set(productos.value.map(p => p.cate_prod).filter(Boolean))
  return Array.from(set).sort()
})

const categoriasConConteo = computed(() => {
  const total = productos.value.length || 1
  const map = new Map<string, number>()
  productos.value.forEach(p => { map.set(p.cate_prod, (map.get(p.cate_prod) || 0) + 1) })
  return Array.from(map.entries()).map(([nombre, cantidad]) => ({
    nombre, cantidad,
    porcentaje: Math.round((cantidad / total) * 100),
    color: getCategoryColor(nombre)
  })).sort((a, b) => b.cantidad - a.cantidad)
})

// Mapa rápido: id_prod → oferta activa
const ofertasPorProducto = computed(() => {
  const map = new Map<string, Oferta>()
  ofertas.value.forEach(o => map.set(o.id_prod, o))
  return map
})

const productosEnOferta = computed(() => ofertas.value)

function ofertaActivaPorProducto(id_prod: string): Oferta | undefined {
  return ofertasPorProducto.value.get(id_prod)
}

// ─── TOAST ────────────────────────────────────────────────────

const toast = ref({ show: false, message: '', type: 'success' as 'success' | 'error' })
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.value = { show: true, message, type }
  setTimeout(() => toast.value.show = false, 3000)
}

// ─── HELPERS ─────────────────────────────────────────────────

function formatPrice(price: string | number | undefined): string {
  if (price === undefined || price === null) return '0'
  return Number(price)?.toLocaleString('es-AR') || '0'
}

function getCategoryColor(nombre: string): string {
  const colors: Record<string, string> = {
    'Almacen': '#fbbf24', 'Bebidas': '#60a5fa', 'Limpieza': '#34d399',
    'Carnes': '#f87171', 'Frutas': '#4ade80', 'Verduras': '#22c55e',
    'Congelados': '#38bdf8', 'Hogar': '#a78bfa', 'Comercio': '#e8c4a0'
  }
  return colors[nombre] || '#e8c4a0'
}

function getDefaultIcon(nombre: string): string {
  const icons: Record<string, string> = {
    'Almacen': '🥫', 'Bebidas': '🥤', 'Limpieza': '🧼', 'Carnes': '🥩',
    'Frutas': '🍎', 'Verduras': '🥬', 'Congelados': '🧊', 'Hogar': '🏠', 'Ferreteria': '🔧'
  }
  return icons[nombre] || '📦'
}

function formatFechaOferta(fechaStr: string): string {
  if (!fechaStr) return 'sin fecha'
  const fecha = new Date(fechaStr)
  const ahora = new Date()
  const dias = Math.ceil((fecha.getTime() - ahora.getTime()) / (1000 * 60 * 60 * 24))
  if (dias <= 0) return 'hoy'
  if (dias === 1) return 'mañana'
  if (dias <= 7) return `en ${dias} días`
  return fecha.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })
}

function toDatetimeLocalString(isoStr?: string): string {
  if (!isoStr) {
    const d = new Date(); d.setDate(d.getDate() + 7)
    return d.toISOString().slice(0, 16)
  }
  return new Date(isoStr).toISOString().slice(0, 16)
}

// ─── PANEL OFERTA INLINE ──────────────────────────────────────

const ofertaPanelProductoId = ref<string | null>(null)
const savingOferta = ref(false)

const formOfertaPanel = ref({
  precio_oferta: 0,
  fecha_fin: toDatetimeLocalString()
})

const descuentoPanel = ref(0)
const errorPrecioPanel = ref(false)

function calcularDescuentoPanel(precioNormal: number) {
  const oferta = formOfertaPanel.value.precio_oferta
  if (precioNormal > 0 && oferta > 0) {
    errorPrecioPanel.value = oferta >= precioNormal
    descuentoPanel.value = errorPrecioPanel.value ? 0 : Math.round((precioNormal - oferta) / precioNormal * 100)
  } else {
    descuentoPanel.value = 0
    errorPrecioPanel.value = false
  }
}

function toggleOfertaPanel(p: Producto) {
  if (ofertaPanelProductoId.value === p.id_prod) {
    // Cerrar si ya estaba abierto
    ofertaPanelProductoId.value = null
    return
  }
  // Abrir: pre-rellenar si hay oferta activa
  const ofertaActiva = ofertaActivaPorProducto(p.id_prod)
  formOfertaPanel.value = {
    precio_oferta: ofertaActiva?.precio_oferta ?? 0,
    fecha_fin: ofertaActiva ? toDatetimeLocalString(ofertaActiva.fecha_fin) : toDatetimeLocalString()
  }
  descuentoPanel.value = ofertaActiva?.descuento_pct ?? 0
  errorPrecioPanel.value = false
  ofertaPanelProductoId.value = p.id_prod
}

async function guardarOferta(p: Producto) {
  if (errorPrecioPanel.value || !formOfertaPanel.value.precio_oferta || !formOfertaPanel.value.fecha_fin) return
  savingOferta.value = true
  try {
    const ofertaActiva = ofertaActivaPorProducto(p.id_prod)
    const payload = {
      id_prod: p.id_prod,
      precio_normal: Number(p.precio_prod),
      precio_oferta: formOfertaPanel.value.precio_oferta,
      fecha_inicio: new Date().toISOString(),
      fecha_fin: new Date(formOfertaPanel.value.fecha_fin).toISOString()
    }

    if (ofertaActiva) {
      // Actualizar existente
      await $fetch(`${config.public.apiBase}/ofertas/${ofertaActiva.id}`, { method: 'PUT', body: payload })
      showToast('Oferta actualizada')
    } else {
      // Crear nueva
      await $fetch(`${config.public.apiBase}/ofertas`, { method: 'POST', body: payload })
      showToast('🔥 Oferta activada')
    }
    ofertaPanelProductoId.value = null
    await loadOfertas()
  } catch (err: any) {
    showToast(err?.data?.detail || 'Error al guardar oferta', 'error')
  } finally {
    savingOferta.value = false
  }
}

async function desactivarOferta(p: Producto) {
  const ofertaActiva = ofertaActivaPorProducto(p.id_prod)
  if (!ofertaActiva) return
  await desactivarOfertaById(ofertaActiva)
  ofertaPanelProductoId.value = null
}

async function desactivarOfertaById(oferta: Oferta) {
  savingOferta.value = true
  try {
    await $fetch(`${config.public.apiBase}/ofertas/${oferta.id}`, { method: 'DELETE' })
    showToast('Oferta desactivada')
    await loadOfertas()
  } catch (err: any) {
    showToast(err?.data?.detail || 'Error al desactivar', 'error')
  } finally {
    savingOferta.value = false
  }
}

// ─── MODAL PRODUCTO ───────────────────────────────────────────

const modalProductoOpen = ref(false)
const editingProductoId = ref<string | null>(null)
const nuevaCategoria = ref('')
const formProducto = ref<Partial<Producto>>({
  nombre_prod: '', cate_prod: '', marca_prod: '', precio_prod: '',
  cantidad_prod: 1, unidad_prod: 'Unidad', comercio_prod: '',
  describe_prod: '', imagen_prod: '', activo_prod: true
})

function openModal(type: string) {
  if (type === 'producto') {
    editingProductoId.value = null
    formProducto.value = {
      nombre_prod: '', cate_prod: '', marca_prod: '', precio_prod: '',
      cantidad_prod: 1, unidad_prod: 'Unidad', comercio_prod: '',
      describe_prod: '', imagen_prod: '', activo_prod: true
    }
    modalProductoOpen.value = true
  } else if (type === 'comercio') {
    openModalComercio()
  }
}

function closeModalProducto() {
  modalProductoOpen.value = false
  editingProductoId.value = null
  nuevaCategoria.value = ''
}

function editProducto(p: Producto) {
  editingProductoId.value = p.id_prod
  formProducto.value = { ...p }
  modalProductoOpen.value = true
}

async function saveProducto() {
  saving.value = true
  try {
    const payload: Record<string, any> = {
      nombre_prod: formProducto.value.nombre_prod?.trim(),
      cate_prod: formProducto.value.cate_prod?.trim(),
      marca_prod: formProducto.value.marca_prod?.trim(),
      precio_prod: String(formProducto.value.precio_prod || 0),
      cantidad_prod: Number(formProducto.value.cantidad_prod) || 1,
      unidad_prod: formProducto.value.unidad_prod || 'Unidad',
      comercio_prod: formProducto.value.comercio_prod?.trim(),
      describe_prod: formProducto.value.describe_prod?.trim() || null,
      imagen_prod: formProducto.value.imagen_prod?.trim() || null,
      activo_prod: !!formProducto.value.activo_prod,
    }
    if (!payload.nombre_prod || !payload.cate_prod || !payload.marca_prod || !payload.precio_prod || !payload.comercio_prod) {
      showToast('Completá todos los campos requeridos (*)', 'error')
      saving.value = false
      return
    }
    if (editingProductoId.value) {
      await $fetch(`${config.public.apiBase}/products/${editingProductoId.value}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
      const idx = productos.value.findIndex(p => p.id_prod === editingProductoId.value)
      if (idx >= 0) productos.value[idx] = { ...productos.value[idx], ...payload, id_prod: editingProductoId.value } as Producto
      showToast('Producto actualizado')
    } else {
      const res = await $fetch<{ data: Producto }>(`${config.public.apiBase}/products`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
      if (res.data) productos.value.unshift(res.data)
      else await loadData()
      showToast('Producto creado')
    }
    closeModalProducto()
  } catch (err: any) {
    showToast(err?.data?.detail || err?.message || 'Error al guardar producto', 'error')
  } finally {
    saving.value = false
  }
}

// ─── MODAL PROVEEDOR ──────────────────────────────────────────

const modalComercioOpen = ref(false)
const editingComercioId = ref<string | null>(null)
const formComercio = ref<Partial<Comercio>>({
  nombre_comer: '', direccion_comer: '', te_comer: '',
  email_comer: '', representa_comer: '', cate_comer: '', logo_comer: '', activo_comer: true,
  plan_comer: 'free', plan_vencimiento_comer: '',
  lat: null, lng: null
})

// Campo auxiliar: pegar "lat, lng" o un link de Google Maps y auto-completar
const coordsPegar = ref('')

function parsearCoordenadas() {
  const texto = coordsPegar.value.trim()
  if (!texto) return
  const atMatch   = texto.match(/@(-?\d+\.\d+),(-?\d+\.\d+)/)          // .../@lat,lng
  const bangMatch = texto.match(/!3d(-?\d+\.\d+)!4d(-?\d+\.\d+)/)      // .../!3dlat!4dlng
  const pairMatch = texto.match(/^\s*(-?\d+(?:\.\d+)?)\s*[, ]\s*(-?\d+(?:\.\d+)?)\s*$/) // "lat, lng"
  let lat: number | null = null, lng: number | null = null
  if (atMatch)        { lat = parseFloat(atMatch[1]);   lng = parseFloat(atMatch[2]) }
  else if (bangMatch) { lat = parseFloat(bangMatch[1]); lng = parseFloat(bangMatch[2]) }
  else if (pairMatch) { lat = parseFloat(pairMatch[1]); lng = parseFloat(pairMatch[2]) }
  if (lat !== null && lng !== null) {
    formComercio.value.lat = lat
    formComercio.value.lng = lng
  }
}

function openModalComercio() {
  editingComercioId.value = null
  coordsPegar.value = ''
  formComercio.value = {
    nombre_comer: '', direccion_comer: '', te_comer: '',
    email_comer: '', representa_comer: '', cate_comer: '', logo_comer: '', activo_comer: true,
    plan_comer: 'free', plan_vencimiento_comer: '',
    lat: null, lng: null
  }
  modalComercioOpen.value = true
}

function closeModalComercio() { modalComercioOpen.value = false; editingComercioId.value = null }

function editComercio(p: Comercio) {
  editingComercioId.value = p.id_comer
  coordsPegar.value = ''
  formComercio.value = { ...p }
  modalComercioOpen.value = true
}

async function saveComercio() {
  saving.value = true
  try {
    const payload: Record<string, any> = {
      nombre_comer: formComercio.value.nombre_comer?.trim(),
      cate_comer: formComercio.value.cate_comer?.trim() || null,
      direccion_comer: formComercio.value.direccion_comer?.trim() || null,
      te_comer: formComercio.value.te_comer?.trim() || null,
      email_comer: formComercio.value.email_comer?.trim() || null,
      representa_comer: formComercio.value.representa_comer?.trim() || '',
      logo_comer: formComercio.value.logo_comer?.trim() || null,
      activo_comer: !!formComercio.value.activo_comer,
      plan_comer: formComercio.value.plan_comer || 'free',
      plan_vencimiento_comer: formComercio.value.plan_vencimiento_comer || null,
      fechaIngreso_comer: new Date().toISOString().split('T')[0],
      lat: (formComercio.value.lat !== null && formComercio.value.lat !== undefined && String(formComercio.value.lat) !== '') ? Number(formComercio.value.lat) : null,
      lng: (formComercio.value.lng !== null && formComercio.value.lng !== undefined && String(formComercio.value.lng) !== '') ? Number(formComercio.value.lng) : null
    }
    if (!payload.nombre_comer) { showToast('El nombre es requerido', 'error'); saving.value = false; return }
    if (editingComercioId.value) {
      const res = await $fetch<{ data: Comercio }>(`${config.public.apiBase}/comercios/${editingComercioId.value}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
      const idx = comercios.value.findIndex(p => p.id_comer === editingComercioId.value)
      if (idx >= 0) comercios.value[idx] = { ...comercios.value[idx], ...res.data } as Comercio
      showToast('Comercio actualizado')
    } else {
      const res = await $fetch<{ data: Comercio }>(`${config.public.apiBase}/comercios`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${getToken()}` },
        body: payload
      })
      if (res.data) comercios.value.unshift(res.data)
      else await loadData()
      showToast('Comercio creado')
    }
    closeModalComercio()
  } catch (err: any) {
    showToast(err?.data?.detail || 'Error al guardar', 'error')
  } finally {
    saving.value = false
  }
}

// ─── DELETE ───────────────────────────────────────────────────

const deleteModalOpen = ref(false)
const deleteType = ref('')
const deleteItem = ref<any>(null)
const deleteItemName = ref('')

function confirmDelete(type: string, item: any) {
  deleteType.value = type
  deleteItem.value = item
  deleteItemName.value = item.nombre_prod || item.nombre_comer || item.nombre_completo_user || 'elemento'
  deleteModalOpen.value = true
}

async function executeDelete() {
  deleting.value = true
  try {
    const item = deleteItem.value
    if (deleteType.value === 'producto') {
      await $fetch(`${config.public.apiBase}/products/${item.id_prod}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${getToken()}` }
      })
      productos.value = productos.value.filter(p => p.id_prod !== item.id_prod)
      showToast('Producto eliminado')
    } else if (deleteType.value === 'comercio') {
      try {
        await $fetch(`${config.public.apiBase}/comercios/${item.id_comer}`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${getToken()}` },
          body: { activo_comer: false }
        })
        const idx = comercios.value.findIndex(p => p.id_comer === item.id_comer)
        if (idx >= 0) comercios.value[idx].activo_comer = false
        showToast('Comercio desactivado')
      } catch { showToast('No se pudo eliminar el comercio', 'error') }
    } else if (deleteType.value === 'usuario') {
      try {
        await $fetch(`${config.public.apiBase}/admin/usuarios/${item.id_user}/estado`, {
          method: 'PUT',
          headers: { Authorization: `Bearer ${getToken()}` },
          body: { activo: false }
        })
        const idx = usuarios.value.findIndex(u => u.id_user === item.id_user)
        if (idx >= 0) usuarios.value[idx].activo_user = false
        showToast('Usuario desactivado')
      } catch (err: any) {
        showToast(err?.data?.detail || 'No se pudo desactivar el usuario', 'error')
      }
    }
  } catch (err: any) {
    showToast(err?.message || 'Error al eliminar', 'error')
  } finally {
    deleting.value = false
    deleteModalOpen.value = false
  }
}

// ─── DATA LOADING ─────────────────────────────────────────────

async function loadOfertas() {
  loadingOfertas.value = true
  try {
    const res = await $fetch<{ count: number; results: Oferta[] }>(`${config.public.apiBase}/ofertas`)
    ofertas.value = res.results || []
  } catch (err) {
    console.error('Error cargando ofertas:', err)
  } finally {
    loadingOfertas.value = false
  }
}

async function loadData() {
  loading.value = true
  try {
    const [prodRes, provRes, medidasRes, catsRes] = await Promise.all([
      $fetch<{ count: number; results: Producto[] }>(`${config.public.apiBase}/products?limit=1000`).catch(() => ({ results: [] })),
      $fetch<{ count: number; results: Comercio[] }>(`${config.public.apiBase}/comercios`).catch(() => ({ results: [] })),
      $fetch<{id: number, nombre: string}[]>(`${config.public.apiBase}/medidas`).catch(() => []),
      $fetch<{id_cate: string, nombre_cate: string}[]>(`${config.public.apiBase}/categorias`).catch(() => [])
    ])
    productos.value = prodRes.results || []
    comercios.value = provRes.results || []
    medidas.value = medidasRes || []
    categoriasBD.value = (catsRes || []).map((c: any) => ({ id: c.id_cate, nombre: c.nombre_cate }))
    await loadOfertas()
  } catch (err) {
    console.error('Error cargando datos:', err)
    showToast('Error cargando datos', 'error')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
  cargarComerciosPendientes()
  pedirUbicacionAdmin()
  try {
    const stored = localStorage.getItem('comparapp_user')
    if (stored) miPropioId.value = JSON.parse(stored).id || ''
  } catch {}
})
</script>

<style scoped>
.admin-page {
  --bg-deep: #0a0a0f;
  --bg-card: rgba(255, 255, 255, 0.03);
  --bg-card-hover: rgba(255, 255, 255, 0.06);
  --bg-input: rgba(255, 255, 255, 0.04);
  --border-subtle: rgba(255, 255, 255, 0.08);
  --border-glow: rgba(232, 196, 160, 0.25);
  --text-primary: #f5f0eb;
  --text-secondary: rgba(245, 240, 235, 0.6);
  --text-muted: rgba(245, 240, 235, 0.35);
  --accent-gold: #e8c4a0;
  --accent-blue: #60a5fa;
  --accent-amber: #fbbf24;
  --accent-emerald: #34d399;
  --accent-rose: #fb7185;
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
  position: fixed; inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -10%, rgba(232, 196, 160, 0.08), transparent),
    radial-gradient(ellipse 60% 40% at 80% 80%, rgba(167, 139, 250, 0.05), transparent),
    linear-gradient(180deg, #0f0d0a 0%, #0a0a0f 40%, #0a0a0f 100%);
  z-index: 0;
}

.bg-noise {
  position: fixed; inset: 0; opacity: 0.03; z-index: 1; pointer-events: none;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noise'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noise)'/%3E%3C/svg%3E");
}

.page-content {
  position: relative; z-index: 2; padding: 1.5rem;
  display: flex; flex-direction: column; gap: 1.25rem;
  max-width: 600px; margin: 0 auto; padding-bottom: 6rem;
}

@keyframes fadeInUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
@keyframes spin { to { transform: rotate(360deg); } }

.animate-fade-in-up { opacity: 0; animation: fadeInUp 0.5s ease-out forwards; }
.stagger-1 { animation-delay: 0.05s; }
.stagger-2 { animation-delay: 0.1s; }

/* ─── HEADER ─── */
.page-header { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0; }
.header-left { display: flex; align-items: center; gap: 0.875rem; }
.back-btn { width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.25s ease; }
.back-btn:hover { background: rgba(255,255,255,0.08); border-color: var(--border-glow); color: var(--text-primary); transform: scale(1.05); }
.page-title { font-size: 1.5rem; font-weight: 700; margin: 0; letter-spacing: -0.02em; }
.page-subtitle { color: var(--text-secondary); font-size: 0.85rem; margin: 0.15rem 0 0; }
.refresh-btn { width: 40px; height: 40px; border-radius: 50%; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); color: var(--text-secondary); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.25s ease; }
.refresh-btn:hover { background: rgba(255,255,255,0.08); border-color: var(--border-glow); color: var(--text-primary); }
.refresh-btn.spinning svg { animation: spin 1s linear infinite; }

/* ─── STATS ─── */
.stats-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 0.875rem; }
.stat-card { display: flex; align-items: center; gap: 0.875rem; padding: 1.125rem; background: var(--bg-card); backdrop-filter: blur(20px) saturate(180%); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); transition: all 0.3s ease; }
.stat-card:hover { background: var(--bg-card-hover); border-color: var(--border-glow); transform: translateY(-2px); }
.stat-icon-wrap { width: 44px; height: 44px; border-radius: var(--radius-sm); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.icon-blue { background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); color: var(--accent-blue); }
.icon-amber { background: rgba(251,191,36,0.1); border: 1px solid rgba(251,191,36,0.2); color: var(--accent-amber); }
.icon-emerald { background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); color: var(--accent-emerald); }
.icon-fire { background: rgba(232,196,160,0.12); border: 1px solid rgba(232,196,160,0.25); color: var(--accent-gold); }
.stat-info { display: flex; flex-direction: column; gap: 0.2rem; }
.stat-value { font-size: 1.35rem; font-weight: 700; letter-spacing: -0.02em; }
.stat-label { font-size: 0.78rem; color: var(--text-muted); font-weight: 500; }

/* ─── TABS ─── */
.tabs-bar { display: flex; gap: 0.5rem; overflow-x: auto; padding-bottom: 0.25rem; scrollbar-width: none; }
.tabs-bar::-webkit-scrollbar { display: none; }
.tab-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1rem; background: rgba(255,255,255,0.03); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.25s ease; white-space: nowrap; flex-shrink: 0; }
.tab-btn:hover { background: rgba(255,255,255,0.06); border-color: var(--border-glow); color: var(--text-primary); }
.tab-btn.active { background: linear-gradient(135deg, rgba(232,196,160,0.12), rgba(167,139,250,0.08)); border-color: rgba(232,196,160,0.25); color: var(--accent-gold); }
.tab-label { font-size: 0.8rem; }
.tab-badge {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 18px; height: 18px; padding: 0 5px;
  background: #fb7185; color: #1a1a1a;
  border-radius: 999px; font-size: 0.68rem; font-weight: 700;
}

.items-list { display: flex; flex-direction: column; gap: 0.625rem; }
.solicitud-item {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  padding: 0.875rem 1rem; background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle); border-radius: var(--radius-md);
  flex-wrap: wrap;
}
.solicitud-info { display: flex; flex-direction: column; gap: 0.15rem; min-width: 0; flex: 1; }
.solicitud-comercio { font-size: 0.82rem; font-weight: 600; color: var(--accent-gold); }
.solicitud-meta { font-size: 0.74rem; color: var(--text-secondary); }
.solicitud-direccion { font-size: 0.72rem; color: var(--text-muted); }
.solicitud-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }
.btn-aprobar {
  padding: 0.5rem 1rem; border-radius: var(--radius-sm);
  background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.3);
  color: #6ee7b7; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-aprobar:hover:not(:disabled) { background: rgba(52,211,153,0.25); }
.btn-aprobar:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-rechazar {
  padding: 0.5rem 1rem; border-radius: var(--radius-sm);
  background: rgba(251,113,133,0.1); border: 1px solid rgba(251,113,133,0.25);
  color: #fb7185; font-size: 0.8rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-rechazar:hover:not(:disabled) { background: rgba(251,113,133,0.2); }
.btn-rechazar:disabled { opacity: 0.5; cursor: not-allowed; }

/* ─── USUARIOS ─── */
.usuario-item {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.875rem 1rem;
  background: var(--bg-card); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
}
.usuario-avatar {
  width: 44px; height: 44px; border-radius: 50%; flex-shrink: 0;
  object-fit: cover; background: var(--bg-input);
}
.usuario-info { flex: 1; min-width: 0; display: flex; flex-direction: column; gap: 0.2rem; }
.usuario-nombre-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.usuario-email {
  font-size: 0.78rem; color: var(--text-secondary);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.usuario-badges { display: flex; align-items: center; gap: 0.4rem; flex-wrap: wrap; margin-top: 0.2rem; }

.badge-tu {
  font-size: 0.65rem; font-weight: 700; text-transform: uppercase;
  padding: 0.1rem 0.4rem; border-radius: 4px;
  background: rgba(232,196,160,0.15); color: var(--accent-gold);
  border: 1px solid rgba(232,196,160,0.3);
}

.badge-rol {
  font-size: 0.68rem; font-weight: 600;
  padding: 0.15rem 0.5rem; border-radius: 20px;
  border: 1px solid transparent;
}
.badge-rol--usuario { background: rgba(255,255,255,0.06); color: var(--text-secondary); }
.badge-rol--comercio { background: rgba(96,165,250,0.12); color: var(--accent-blue); border-color: rgba(96,165,250,0.25); }
.badge-rol--admin { background: rgba(232,196,160,0.15); color: var(--accent-gold); border-color: rgba(232,196,160,0.3); }

.badge-comercio {
  font-size: 0.68rem; font-weight: 500;
  padding: 0.15rem 0.5rem; border-radius: 20px;
  background: rgba(52,211,153,0.1); color: var(--accent-emerald);
  border: 1px solid rgba(52,211,153,0.25);
}
.badge-comercio--pendiente { background: rgba(251,191,36,0.1); color: var(--accent-amber); border-color: rgba(251,191,36,0.25); }

.badge-estado {
  font-size: 0.68rem; font-weight: 600;
  padding: 0.15rem 0.5rem; border-radius: 20px;
}
.badge-estado--activo { background: rgba(52,211,153,0.1); color: var(--accent-emerald); }
.badge-estado--inactivo { background: rgba(251,113,133,0.12); color: var(--accent-rose); }

.usuario-actions { display: flex; align-items: center; gap: 0.5rem; flex-shrink: 0; }
.usuario-actions--self { color: var(--text-muted); font-size: 0.72rem; font-style: italic; max-width: 110px; text-align: right; }
.rol-select {
  padding: 0.4rem 0.6rem; border-radius: var(--radius-sm);
  background: var(--bg-input); border: 1px solid var(--border-subtle);
  color: var(--text-primary); font-size: 0.78rem; cursor: pointer;
}

.form-hint--warning {
  color: var(--accent-amber); background: rgba(251,191,36,0.08);
  border: 1px solid rgba(251,191,36,0.2); border-radius: var(--radius-sm);
  padding: 0.5rem 0.7rem; font-style: normal; margin: 0.5rem 0;
}


/* ─── SECTION HEADER ─── */
.section-header { display: flex; align-items: center; justify-content: space-between; gap: 1rem; }
.section-title { font-size: 1.1rem; font-weight: 600; margin: 0; }
.section-badge { background: rgba(232,196,160,0.12); color: var(--accent-gold); font-size: 0.75rem; font-weight: 600; padding: 0.25rem 0.625rem; border-radius: 999px; border: 1px solid rgba(232,196,160,0.2); }

/* ─── SEARCH ─── */
.search-box { display: flex; align-items: center; gap: 0.625rem; padding: 0.625rem 1rem; background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); flex: 1; max-width: 300px; transition: all 0.25s ease; }
.search-box:focus-within { border-color: var(--border-glow); box-shadow: 0 0 0 3px rgba(232,196,160,0.06); }
.search-box svg { color: var(--text-muted); flex-shrink: 0; }
.search-box input { flex: 1; background: transparent; border: none; outline: none; color: var(--text-primary); font-size: 0.9rem; font-family: inherit; }
.search-box input::placeholder { color: var(--text-muted); }

/* ─── BUTTONS ─── */
.btn-primary { display: flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.125rem; background: linear-gradient(135deg, rgba(167,139,250,0.2), rgba(167,139,250,0.1)); border: 1px solid rgba(167,139,250,0.3); border-radius: var(--radius-sm); color: #c4b5fd; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.25s ease; white-space: nowrap; }
.btn-primary:hover { background: linear-gradient(135deg, rgba(167,139,250,0.3), rgba(167,139,250,0.2)); border-color: rgba(167,139,250,0.5); color: #ddd6fe; transform: translateY(-1px); }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }
.btn-secondary { padding: 0.625rem 1.125rem; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); color: var(--text-secondary); font-size: 0.85rem; font-weight: 500; cursor: pointer; transition: all 0.25s ease; }
.btn-secondary:hover { background: rgba(255,255,255,0.08); border-color: var(--border-glow); color: var(--text-primary); }
.btn-danger { padding: 0.625rem 1.125rem; background: rgba(248,113,113,0.15); border: 1px solid rgba(248,113,113,0.3); border-radius: var(--radius-sm); color: #fca5a5; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.25s ease; }
.btn-danger:hover { background: rgba(248,113,113,0.25); border-color: rgba(248,113,113,0.5); }
.btn-sm { padding: 0.4rem 0.75rem; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); border-radius: 8px; color: var(--text-secondary); font-size: 0.78rem; font-weight: 500; cursor: pointer; transition: all 0.2s ease; }
.btn-sm:hover { background: rgba(255,255,255,0.08); color: var(--text-primary); }
.btn-sm.danger:hover { background: rgba(248,113,113,0.1); border-color: rgba(248,113,113,0.3); color: var(--accent-rose); }

/* ─── ITEMS LIST ─── */
.items-list { display: flex; flex-direction: column; gap: 0.625rem; }

.item-card {
  display: flex; align-items: center; justify-content: space-between; gap: 0.875rem;
  padding: 0.875rem; background: var(--bg-card); backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid var(--border-subtle); border-radius: var(--radius-lg);
  transition: all 0.25s ease;
  flex-wrap: wrap; /* permite que el panel inline ocupe toda la línea */
}

.item-card:hover { background: var(--bg-card-hover); border-color: var(--border-glow); }
.item-card.en-oferta { border-color: rgba(52, 211, 153, 0.2); }

.item-main { display: flex; align-items: center; gap: 0.875rem; flex: 1; min-width: 0; }
.item-thumb { width: 48px; height: 48px; border-radius: var(--radius-sm); object-fit: cover; background: rgba(255,255,255,0.05); flex-shrink: 0; }
.item-info { display: flex; flex-direction: column; gap: 0.25rem; min-width: 0; }
.item-name-row { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.item-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.item-meta { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.item-sub { font-size: 0.75rem; color: var(--text-muted); }

.badge { display: inline-flex; padding: 0.15rem 0.5rem; background: rgba(255,255,255,0.06); border: 1px solid var(--border-subtle); border-radius: 6px; font-size: 0.7rem; font-weight: 500; color: var(--text-secondary); }
.price { color: #4ade80; font-weight: 600; font-size: 0.85rem; }

.item-actions { display: flex; gap: 0.375rem; flex-shrink: 0; }
.action-btn { width: 32px; height: 32px; border-radius: 8px; background: transparent; border: none; color: var(--text-muted); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; }
.action-btn:hover { background: rgba(255,255,255,0.06); }
.action-btn.edit:hover { color: var(--accent-gold); }
.action-btn.delete:hover { color: var(--accent-rose); }

/* Toggle oferta */
.action-btn.oferta-toggle { color: rgba(232,196,160,0.4); }
.action-btn.oferta-toggle:hover { color: var(--accent-gold); background: rgba(232,196,160,0.08); }
.action-btn.oferta-toggle.active { color: #34d399; background: rgba(52,211,153,0.1); border: 1px solid rgba(52,211,153,0.2); }

/* ─── BADGE MINI OFERTA ─── */
.oferta-badge-mini {
  display: inline-flex; align-items: center; padding: 0.12rem 0.45rem;
  border-radius: 999px; background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.25);
  color: #34d399; font-size: 0.68rem; font-weight: 700; white-space: nowrap;
}

.precio-con-oferta { display: flex !important; align-items: center; gap: 0.375rem; }
.precio-tachado { text-decoration: line-through; color: rgba(245,240,235,0.3) !important; font-size: 0.78rem !important; font-weight: 400 !important; }
.precio-nuevo { color: #34d399 !important; font-weight: 700; }

/* ─── PANEL OFERTA INLINE ─── */
.oferta-panel {
  width: 100%; /* ocupa toda la fila por el flex-wrap del card */
  margin-top: 0.75rem;
  padding: 1rem;
  background: rgba(52,211,153,0.04);
  border: 1px solid rgba(52,211,153,0.15);
  border-radius: var(--radius-md);
}

.oferta-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  font-size: 0.82rem; font-weight: 600; color: #34d399;
  margin-bottom: 0.875rem;
}

.oferta-panel-header span { display: flex; align-items: center; gap: 0.4rem; }

.oferta-panel-close {
  background: none; border: none; color: var(--text-muted);
  font-size: 0.9rem; cursor: pointer; padding: 0.2rem 0.4rem;
  border-radius: 6px; transition: all 0.2s;
}
.oferta-panel-close:hover { color: var(--accent-rose); background: rgba(248,113,113,0.08); }

.oferta-panel-body { display: flex; flex-direction: column; gap: 0.75rem; }

.oferta-panel-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }

.form-group { display: flex; flex-direction: column; gap: 0.3rem; }
.form-hint { display: block; font-size: 0.7rem; color: var(--text-muted); margin-top: 2px; font-style: italic; line-height: 1.4; }
.form-group label { font-size: 0.75rem; font-weight: 600; color: var(--text-secondary); }
.form-group input, .form-group select, .form-group textarea {
  padding: 0.55rem 0.75rem; background: var(--bg-input); border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm); color: #f5f0eb; font-size: 0.88rem; font-family: inherit;
  outline: none; transition: all 0.2s ease; -webkit-text-fill-color: #f5f0eb;
}
.form-group input:focus { border-color: var(--border-glow); box-shadow: 0 0 0 3px rgba(232,196,160,0.06); }
.form-group input::placeholder { color: rgba(245,240,235,0.35); -webkit-text-fill-color: rgba(245,240,235,0.35); }
.input-disabled { opacity: 0.45; cursor: not-allowed; }

.descuento-chip {
  display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.35rem 0.7rem;
  border-radius: 999px; background: rgba(52,211,153,0.12); border: 1px solid rgba(52,211,153,0.25);
  color: #34d399; font-size: 0.8rem; font-weight: 600;
}

.oferta-error {
  padding: 0.45rem 0.7rem; border-radius: 8px;
  background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.2);
  color: #fca5a5; font-size: 0.8rem;
}

.oferta-panel-actions { display: flex; gap: 0.625rem; justify-content: flex-end; padding-top: 0.25rem; }

.btn-guardar-oferta {
  padding: 0.55rem 1rem; background: linear-gradient(135deg, rgba(52,211,153,0.2), rgba(52,211,153,0.1));
  border: 1px solid rgba(52,211,153,0.3); border-radius: var(--radius-sm);
  color: #6ee7b7; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-guardar-oferta:hover { background: linear-gradient(135deg, rgba(52,211,153,0.3), rgba(52,211,153,0.2)); border-color: rgba(52,211,153,0.5); }
.btn-guardar-oferta:disabled { opacity: 0.4; cursor: not-allowed; }

.btn-desactivar {
  padding: 0.55rem 1rem; background: rgba(248,113,113,0.1); border: 1px solid rgba(248,113,113,0.2);
  border-radius: var(--radius-sm); color: #fca5a5; font-size: 0.82rem; font-weight: 600; cursor: pointer; transition: all 0.2s;
}
.btn-desactivar:hover { background: rgba(248,113,113,0.2); border-color: rgba(248,113,113,0.4); }
.btn-desactivar:disabled { opacity: 0.4; cursor: not-allowed; }

/* ─── OFERTA CARD (tab ofertas) ─── */
.oferta-card { border-color: rgba(52,211,153,0.15) !important; }
.oferta-vence { display: flex !important; align-items: center; gap: 0.3rem; }
.oferta-vence svg { color: #fbbf24; }

/* ─── PROVIDERS ─── */
.cards-grid { display: grid; grid-template-columns: 1fr; gap: 0.875rem; }
.provider-card { background: var(--bg-card); backdrop-filter: blur(20px) saturate(180%); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.25rem; transition: all 0.3s ease; }
.provider-card:hover { background: var(--bg-card-hover); border-color: var(--border-glow); transform: translateY(-2px); }
.provider-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem; }
.provider-logo { width: 48px; height: 48px; border-radius: var(--radius-sm); object-fit: cover; background: rgba(255,255,255,0.05); }
.provider-status { width: 10px; height: 10px; border-radius: 50%; }
.provider-status.active { background: var(--accent-emerald); box-shadow: 0 0 8px rgba(52,211,153,0.4); }
.provider-status.inactive { background: var(--accent-rose); }
.provider-name { font-size: 1rem; font-weight: 600; margin: 0 0 0.25rem; }
.provider-cat { font-size: 0.8rem; color: var(--text-muted); margin: 0 0 0.75rem; }
.provider-meta { display: flex; flex-direction: column; gap: 0.375rem; margin-bottom: 0.75rem; }
.provider-meta span { display: flex; align-items: center; gap: 0.375rem; font-size: 0.78rem; color: var(--text-muted); }
.provider-stats { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 1rem; }
.provider-stat { display: inline-flex; align-items: center; gap: 0.35rem; padding: 0.25rem 0.6rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; background: rgba(96,165,250,0.1); border: 1px solid rgba(96,165,250,0.2); color: var(--accent-blue); }
.provider-stat svg { opacity: 0.85; }
.provider-stat--muted { background: rgba(255,255,255,0.04); border-color: var(--border-subtle); color: var(--text-muted); font-weight: 500; }
.geo-bar { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; padding: 0.6rem 0.85rem; margin-bottom: 0.25rem; background: rgba(232,196,160,0.06); border: 1px solid rgba(232,196,160,0.18); border-radius: var(--radius-md); }
.geo-bar span { display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: var(--text-secondary); }
.geo-bar svg { color: var(--accent-gold); flex-shrink: 0; }
.provider-actions { display: flex; gap: 0.5rem; }

/* ─── CATEGORIES ─── */
.categories-grid { grid-template-columns: repeat(2, 1fr); }
.category-card { background: var(--bg-card); backdrop-filter: blur(20px) saturate(180%); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 1.25rem; text-align: center; transition: all 0.3s ease; }
.category-card:hover { background: var(--bg-card-hover); border-color: var(--border-glow); transform: translateY(-2px); }
.cat-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.category-card h3 { font-size: 0.95rem; font-weight: 600; margin: 0 0 0.25rem; }
.category-card p { font-size: 0.78rem; color: var(--text-muted); margin: 0 0 0.75rem; }
.cat-bar { height: 4px; background: rgba(255,255,255,0.06); border-radius: 999px; overflow: hidden; }
.cat-bar-fill { height: 100%; border-radius: 999px; transition: width 0.5s ease; }

/* ─── EMPTY / LOADING ─── */
.empty-state { display: flex; flex-direction: column; align-items: center; gap: 0.75rem; padding: 3rem 1rem; text-align: center; background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); }
.empty-icon-wrap { width: 64px; height: 64px; border-radius: var(--radius-lg); background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); display: flex; align-items: center; justify-content: center; color: var(--text-muted); }
.empty-state h3 { color: var(--text-primary); font-size: 1.1rem; font-weight: 600; margin: 0; }
.empty-state p { color: var(--text-secondary); font-size: 0.85rem; margin: 0; }
.loading-state { display: flex; flex-direction: column; align-items: center; gap: 0.875rem; padding: 3rem 1rem; color: var(--text-muted); font-size: 0.9rem; }
.loading-spinner { width: 32px; height: 32px; border: 2px solid rgba(255,255,255,0.1); border-top-color: var(--accent-gold); border-radius: 50%; animation: spin 0.8s linear infinite; }

/* ─── MODAL ─── */
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal-container { background: linear-gradient(180deg, rgba(20,20,28,0.98), rgba(15,15,22,0.98)); border: 1px solid var(--border-subtle); border-radius: var(--radius-xl); width: 100%; max-width: 520px; max-height: 90vh; overflow-y: auto; box-shadow: 0 24px 64px rgba(0,0,0,0.5); }
.modal-container.modal-sm { max-width: 380px; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 1.25rem; border-bottom: 1px solid var(--border-subtle); }
.modal-header h3 { font-size: 1.1rem; font-weight: 600; margin: 0; }
.modal-close { width: 32px; height: 32px; border-radius: 8px; background: rgba(255,255,255,0.04); border: 1px solid var(--border-subtle); color: var(--text-muted); display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s ease; }
.modal-close:hover { background: rgba(248,113,113,0.1); border-color: rgba(248,113,113,0.3); color: var(--accent-rose); }
.modal-body { padding: 1.25rem; }
.confirm-text { color: var(--text-secondary); font-size: 0.9rem; margin: 0 0 1.25rem; text-align: center; }

/* ─── FORM ─── */
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full { grid-column: 1 / -1; }
.form-group label { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); }
.form-group input, .form-group select, .form-group textarea { padding: 0.625rem 0.875rem; background: var(--bg-input); border: 1px solid var(--border-subtle); border-radius: var(--radius-sm); color: #f5f0eb !important; font-size: 0.9rem; font-family: inherit; outline: none; transition: all 0.25s ease; -webkit-text-fill-color: #f5f0eb !important; }
.form-group input::placeholder, .form-group textarea::placeholder { color: rgba(245,240,235,0.4) !important; -webkit-text-fill-color: rgba(245,240,235,0.4) !important; }
.form-group select option { background: #1a1a24; color: #f5f0eb; }
.form-group input:-webkit-autofill, .form-group select:-webkit-autofill, .form-group textarea:-webkit-autofill { -webkit-text-fill-color: #f5f0eb !important; -webkit-box-shadow: 0 0 0px 1000px #14141c inset !important; }
.form-group input:focus, .form-group select:focus, .form-group textarea:focus { border-color: var(--border-glow); box-shadow: 0 0 0 3px rgba(232,196,160,0.06); }
.checkbox-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.85rem !important; font-weight: 500 !important; }
.checkbox-label input[type="checkbox"] { width: 18px; height: 18px; accent-color: var(--accent-violet); cursor: pointer; }
.form-actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 0.5rem; }
.mt-2 { margin-top: 0.5rem; }

/* ─── TOAST ─── */
.toast { position: fixed; bottom: 5rem; left: 50%; transform: translateX(-50%); z-index: 2000; display: flex; align-items: center; gap: 0.625rem; padding: 0.875rem 1.25rem; border-radius: var(--radius-md); font-size: 0.9rem; font-weight: 500; box-shadow: 0 8px 32px rgba(0,0,0,0.4); backdrop-filter: blur(20px); max-width: 90vw; }
.toast.success { background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.25); color: #6ee7b7; }
.toast.error { background: rgba(248,113,113,0.15); border: 1px solid rgba(248,113,113,0.25); color: #fca5a5; }

/* ─── BOTTOM BAR ─── */
.bottom-bar { position: fixed; bottom: 0; left: 0; right: 0; display: flex; justify-content: space-around; align-items: center; padding: 0.75rem 1rem calc(0.75rem + env(safe-area-inset-bottom)); background: rgba(10,10,15,0.85); backdrop-filter: blur(20px); border-top: 1px solid rgba(255,255,255,0.08); z-index: 100; }
.bottom-btn { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; background: none; border: none; color: rgba(245,240,235,0.45); font-size: 0.65rem; font-weight: 500; cursor: pointer; padding: 0.5rem 1rem; border-radius: 12px; transition: all 0.2s; }
.bottom-btn:hover { color: rgba(245,240,235,0.8); background: rgba(255,255,255,0.05); }
.bottom-btn--accent { color: #e8c4a0; background: rgba(232,196,160,0.1); border: 1px solid rgba(232,196,160,0.2); }
.bottom-btn--accent:hover { background: rgba(232,196,160,0.18); }

/* ─── TRANSITIONS ─── */
.modal-enter-active, .modal-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.modal-enter-from, .modal-leave-to { opacity: 0; }
.modal-enter-from .modal-container, .modal-leave-to .modal-container { transform: scale(0.95) translateY(10px); opacity: 0; }
.toast-enter-active, .toast-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.toast-enter-from, .toast-leave-to { opacity: 0; transform: translateX(-50%) translateY(20px); }

.slide-down-enter-active, .slide-down-leave-active { transition: all 0.25s ease; }
.slide-down-enter-from, .slide-down-leave-to { opacity: 0; transform: translateY(-8px); }

/* ─── RESPONSIVE ─── */
@media (min-width: 640px) {
  .page-content { max-width: 640px; padding: 2rem; gap: 1.5rem; }
  .stats-grid { grid-template-columns: repeat(4, 1fr); }
  .cards-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 480px) {
  .page-content { padding: 1rem; gap: 1rem; }
  .stats-grid { grid-template-columns: repeat(2, 1fr); gap: 0.625rem; }
  .stat-card { padding: 0.875rem; }
  .section-header { flex-direction: column; align-items: stretch; }
  .search-box { max-width: none; }
  .form-grid { grid-template-columns: 1fr; }
  .categories-grid { grid-template-columns: 1fr; }
  .oferta-panel-grid { grid-template-columns: 1fr; }
}
</style>