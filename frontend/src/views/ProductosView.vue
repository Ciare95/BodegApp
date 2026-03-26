<template>
  <div class="productos-page">

    <!-- Hero buscador -->
    <div class="hero">
      <p class="hero-hint">Escribe el nombre o código del producto</p>
      <div class="hero-search">
        <svg class="hero-icon" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input
          ref="heroInput"
          v-model="queryHero"
          type="search"
          placeholder="Ej: ARANDELA 3/16 o EB-40"
          @input="buscarHero"
          @keydown.down.prevent="moverSeleccion(1)"
          @keydown.up.prevent="moverSeleccion(-1)"
          @keydown.enter.prevent="confirmarSeleccion"
          @keydown.escape="resultadosHero = []"
        />
      </div>
      <Transition name="dropdown">
        <ul v-if="resultadosHero.length" class="hero-resultados">
          <li
            v-for="(p, i) in resultadosHero"
            :key="p.id"
            :class="{ activo: i === indiceActivo }"
            @click="irAProducto(p)"
            @mouseenter="indiceActivo = i"
          >
            <span class="res-codigo">{{ p.codigo_completo ?? '—' }}</span>
            <span class="res-nombre">{{ p.nombre_completo }}</span>
            <span :class="['res-estado', p.estado]"><span class="dot"></span></span>
          </li>
        </ul>
        <div v-else-if="queryHero && !cargandoHero && buscado" class="hero-sin-resultados">
          Sin resultados para "{{ queryHero }}"
        </div>
      </Transition>
    </div>

    <!-- Breadcrumb + acción -->
    <div class="toolbar">
      <nav class="breadcrumb">
        <button class="crumb" :class="{ activo: !categoriaActiva }" @click="resetear">Productos</button>
        <template v-if="categoriaActiva">
          <span class="sep">›</span>
          <button class="crumb" :class="{ activo: !subcategoriaActiva }" @click="seleccionarCategoria(categoriaActiva)">
            {{ categoriaActiva.nombre }}
          </button>
        </template>
        <template v-if="subcategoriaActiva">
          <span class="sep">›</span>
          <span class="crumb activo">{{ subcategoriaActiva.nombre }}</span>
        </template>
      </nav>
      <RouterLink
          v-if="auth.esAdmin"
          :to="{ name: 'producto-nuevo', query: { categoria_id: categoriaActiva?.id, subcategoria_id: subcategoriaActiva?.id } }"
          class="btn-primary"
        >
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nuevo
      </RouterLink>
    </div>

    <!-- Loading -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-dots"><span></span><span></span><span></span></div>
    </div>

    <!-- Cards de categorías -->
    <div v-else-if="!categoriaActiva" class="cards-grid">
      <button
        v-for="cat in categorias"
        :key="cat.id"
        class="cat-card"
        @click="seleccionarCategoria(cat)"
      >
        <span class="cat-nombre">{{ cat.nombre }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
      <div v-if="!categorias.length" class="empty-hint">No hay categorías</div>
    </div>

    <!-- Cards de subcategorías -->
    <div v-else-if="!subcategoriaActiva" class="cards-grid">
      <button
        v-for="sub in subcategorias"
        :key="sub.id"
        class="cat-card"
        @click="seleccionarSubcategoria(sub)"
      >
        <span class="cat-nombre">{{ sub.nombre }}</span>
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
      </button>
      <div v-if="!subcategorias.length" class="empty-hint">No hay subcategorías</div>
    </div>

    <!-- Tabla de productos -->
    <template v-else>
      <p v-if="errorEstado" class="error-msg">{{ errorEstado }}</p>

      <!-- Filtro estado -->
      <div class="tabla-toolbar">
        <div class="estado-filtros">
          <button
            v-for="op in estadoOpciones"
            :key="op.valor"
            :class="['filtro-estado', op.valor, { activo: filtroEstado === op.valor }]"
            @click="toggleFiltroEstado(op.valor)"
          >
            <span class="dot"></span>{{ op.label }}
            <svg v-if="filtroEstado === op.valor" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <span class="count-badge">{{ productos.length }}</span>
      </div>

      <div class="table-wrap table-desktop">
        <table class="tabla">
          <thead>
            <tr>
              <th v-if="auth.esAdmin" class="col-drag"></th>
              <th>Nombre</th>
              <th>Código</th>
              <th>Estado</th>
              <th class="col-actions"></th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in productos"
              :key="p.id"
              :class="{ 'drag-over': dragOverId === p.id, 'dragging': draggingId === p.id }"
              @dragover.prevent="onDragOver(p)"
              @dragleave="dragOverId = null"
              @drop="onDrop(p)"
              @dragend="onDragEnd"
            >
              <td v-if="auth.esAdmin" class="col-drag">
                <span class="drag-handle" draggable="true" @dragstart.stop="onDragStart(p)">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/></svg>
                </span>
              </td>
              <td class="col-nombre">
                <RouterLink :to="`/productos/${p.id}`" class="nombre-link">{{ p.nombre_completo }}</RouterLink>
              </td>
              <td class="col-codigo">
                <span v-if="p.codigo_completo && p.codigo_completo !== '—'" class="codigo-tag">{{ p.codigo_completo }}</span>
                <span v-else class="sin-codigo">—</span>
              </td>
              <td class="col-estado">
                <div class="estado-selector">
                  <button
                    v-for="op in estadoOpciones"
                    :key="op.valor"
                    :class="['btn-estado', op.valor, { activo: p.estado === op.valor }]"
                    :title="op.label"
                    @click="cambiarEstado(p, op.valor)"
                  ></button>
                </div>
              </td>
              <td class="col-actions">
                <div class="row-actions">
                  <RouterLink :to="`/productos/${p.id}`" class="btn-row">Ver</RouterLink>
                  <RouterLink v-if="auth.esAdmin" :to="{ name: 'producto-editar', params: { id: p.id }, query: { categoria_id: categoriaActiva?.id, subcategoria_id: subcategoriaActiva?.id } }" class="btn-row">Editar</RouterLink>
                </div>
              </td>
            </tr>
            <tr v-if="!productos.length">
              <td :colspan="auth.esAdmin ? 5 : 4" class="empty-cell">Sin productos en esta subcategoría</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Mobile cards -->
      <div class="cards-mobile">
        <div v-if="!productos.length" class="empty-hint">Sin productos</div>
        <div v-for="p in productos" :key="p.id" class="product-card">
          <div class="card-top">
            <div class="card-codes">
              <span v-if="p.codigo_completo && p.codigo_completo !== '—'" class="codigo-tag">{{ p.codigo_completo }}</span>
              <span v-else class="sin-codigo">—</span>
            </div>
            <div class="estado-selector">
              <button
                v-for="op in estadoOpciones"
                :key="op.valor"
                :class="['btn-estado', op.valor, { activo: p.estado === op.valor }]"
                :title="op.label"
                @click="cambiarEstado(p, op.valor)"
              ></button>
            </div>
          </div>
          <RouterLink :to="`/productos/${p.id}`" class="card-nombre">{{ p.nombre_completo }}</RouterLink>
          <div class="card-actions">
            <RouterLink :to="`/productos/${p.id}`" class="btn-row">Ver detalle</RouterLink>
            <RouterLink v-if="auth.esAdmin" :to="{ name: 'producto-editar', params: { id: p.id }, query: { categoria_id: categoriaActiva?.id, subcategoria_id: subcategoriaActiva?.id } }" class="btn-row">Editar</RouterLink>
          </div>
        </div>
      </div>
    </template>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import client from '@/api/client'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const { showConfirm } = useConfirm()

// ── Navegación por niveles ──
const categorias = ref([])
const subcategorias = ref([])
const productos = ref([])
const categoriaActiva = ref(null)
const subcategoriaActiva = ref(null)
const cargando = ref(false)
const filtroEstado = ref('')
const errorEstado = ref('')

// ── Hero buscador ──
const heroInput = ref(null)
const queryHero = ref('')
const resultadosHero = ref([])
const cargandoHero = ref(false)
const buscado = ref(false)
const indiceActivo = ref(-1)
let timerHero = null

// ── Drag & drop ──
const draggingId = ref(null)
const dragOverId = ref(null)
let draggingProducto = null

const estadoOpciones = [
  { valor: 'verde', label: 'Disponible' },
  { valor: 'amarillo', label: 'Queda poco' },
  { valor: 'rojo', label: 'Sin stock' },
]

// ── Hero search ──
function buscarHero() {
  clearTimeout(timerHero)
  indiceActivo.value = -1
  buscado.value = false
  if (!queryHero.value.trim()) { resultadosHero.value = []; return }
  timerHero = setTimeout(async () => {
    cargandoHero.value = true
    try {
      const { data } = await client.get('/productos/', { params: { q: queryHero.value } })
      resultadosHero.value = (data.results ?? data).slice(0, 8)
      buscado.value = true
    } finally {
      cargandoHero.value = false
    }
  }, 300)
}

function moverSeleccion(dir) {
  if (!resultadosHero.value.length) return
  const total = resultadosHero.value.length
  indiceActivo.value = (indiceActivo.value + dir + total) % total
}

function confirmarSeleccion() {
  if (indiceActivo.value >= 0 && resultadosHero.value[indiceActivo.value]) {
    irAProducto(resultadosHero.value[indiceActivo.value])
  } else if (resultadosHero.value.length === 1) {
    irAProducto(resultadosHero.value[0])
  }
}

function irAProducto(p) {
  resultadosHero.value = []
  queryHero.value = ''
  router.push(`/productos/${p.id}`)
}

// ── Navegación ──
function resetear() {
  categoriaActiva.value = null
  subcategoriaActiva.value = null
  productos.value = []
  filtroEstado.value = ''
}

async function seleccionarCategoria(cat) {
  categoriaActiva.value = cat
  subcategoriaActiva.value = null
  productos.value = []
  cargando.value = true
  try {
    const { data } = await client.get('/subcategorias/', { params: { categoria_id: cat.id } })
    subcategorias.value = data.results ?? data
  } finally {
    cargando.value = false
  }
}

async function seleccionarSubcategoria(sub) {
  subcategoriaActiva.value = sub
  await cargarProductos()
}

async function cargarProductos() {
  cargando.value = true
  try {
    const params = { subcategoria_id: subcategoriaActiva.value.id }
    if (filtroEstado.value) params.estado = filtroEstado.value
    const { data } = await client.get('/productos/', { params })
    productos.value = data.results ?? data
  } finally {
    cargando.value = false
  }
}

function toggleFiltroEstado(valor) {
  filtroEstado.value = filtroEstado.value === valor ? '' : valor
  cargarProductos()
}

// ── Estado ──
async function cambiarEstado(producto, nuevoEstado) {
  if (producto.estado === nuevoEstado) return
  const label = estadoOpciones.find(o => o.valor === nuevoEstado)?.label
  if (!await showConfirm(`¿Cambiar estado de "${producto.nombre_completo}" a "${label}"?`, 'Cambiar estado')) return
  try {
    await client.patch(`/productos/${producto.id}/cambiar-estado/`, { estado: nuevoEstado })
    producto.estado = nuevoEstado
  } catch (e) {
    errorEstado.value = e.response?.data?.detail || 'Error al cambiar estado'
  }
}

// ── Drag & drop ──
function onDragStart(p) { draggingProducto = p; draggingId.value = p.id }
function onDragOver(p) { if (draggingProducto?.id !== p.id) dragOverId.value = p.id }
function onDragEnd() { draggingId.value = null; dragOverId.value = null; draggingProducto = null }
function onDrop(target) {
  if (!draggingProducto || draggingProducto.id === target.id) return
  const lista = productos.value
  const fromIdx = lista.findIndex(p => p.id === draggingProducto.id)
  const toIdx = lista.findIndex(p => p.id === target.id)
  const item = lista.splice(fromIdx, 1)[0]
  lista.splice(toIdx, 0, item)
  client.post('/productos/reordenar/', { orden: lista.map(p => p.id) }).catch(console.error)
}

onMounted(async () => {
  const { data } = await client.get('/categorias/')
  categorias.value = data.results ?? data

  // Restaurar estado si venimos del form con query params
  const qCatId = Number(route.query.categoria_id)
  const qSubId = Number(route.query.subcategoria_id)
  if (qCatId && qSubId) {
    const cat = (data.results ?? data).find(c => c.id === qCatId)
    if (cat) {
      await seleccionarCategoria(cat)
      const sub = subcategorias.value.find(s => s.id === qSubId)
      if (sub) await seleccionarSubcategoria(sub)
    }
  } else {
    heroInput.value?.focus()
  }
})
</script>

<style scoped>
.productos-page { display: flex; flex-direction: column; gap: 1.5rem; }

/* ── Hero ── */
.hero {
  position: relative;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1.75rem 2rem;
  display: flex;
  flex-direction: column;
  gap: 0.875rem;
}

.hero-hint {
  font-size: 0.8125rem;
  color: var(--ink-3);
  font-weight: 500;
  letter-spacing: 0.01em;
}

.hero-search {
  position: relative;
  display: flex;
  align-items: center;
}

.hero-icon {
  position: absolute;
  left: 0.875rem;
  color: var(--ink-3);
  pointer-events: none;
  flex-shrink: 0;
}

.hero-search input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  font-size: 1rem;
  border: 1.5px solid var(--border-md);
  border-radius: var(--r-md);
  background: var(--bg);
  color: var(--ink);
  outline: none;
  transition: border-color var(--t), box-shadow var(--t);
}

.hero-search input::placeholder { color: var(--ink-4); }
.hero-search input:focus {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px rgba(17,17,17,0.07);
  background: var(--surface);
}

.hero-resultados {
  position: absolute;
  top: calc(100% + 4px);
  left: 0; right: 0;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  list-style: none;
  z-index: 100;
  max-height: 320px;
  overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.hero-resultados li {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem 1rem; cursor: pointer;
  border-bottom: 1px solid var(--border);
  transition: background var(--t);
}
.hero-resultados li:last-child { border-bottom: none; }
.hero-resultados li:hover, .hero-resultados li.activo { background: var(--border); }

.res-codigo {
  font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  padding: 0.125rem 0.5rem; border-radius: var(--r-sm);
  letter-spacing: 0.04em; flex-shrink: 0;
}
.res-nombre { flex: 1; font-size: 0.875rem; color: var(--ink-2); }
.res-estado .dot { width: 7px; height: 7px; border-radius: 50%; display: block; }
.res-estado.verde .dot { background: var(--verde); }
.res-estado.amarillo .dot { background: var(--amarillo); }
.res-estado.rojo .dot { background: var(--rojo); }

.hero-sin-resultados {
  position: absolute;
  top: calc(100% + 4px); left: 0; right: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 1rem;
  color: var(--ink-3); font-size: 0.8125rem; text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* ── Toolbar ── */
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.crumb {
  font-size: 0.875rem;
  color: var(--ink-3);
  background: none;
  border: none;
  padding: 0.25rem 0.375rem;
  border-radius: var(--r-sm);
  cursor: pointer;
  transition: color var(--t), background var(--t);
}
.crumb:hover { color: var(--ink); background: var(--bg); }
.crumb.activo { color: var(--ink); font-weight: 500; cursor: default; }
.crumb.activo:hover { background: none; }

.sep { color: var(--ink-4); font-size: 0.875rem; }

.btn-primary {
  display: flex; align-items: center; gap: 0.375rem;
  padding: 0.4375rem 0.875rem;
  background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md);
  font-size: 0.8125rem; font-weight: 500;
  text-decoration: none; transition: opacity var(--t);
  white-space: nowrap; flex-shrink: 0;
}
.btn-primary:hover { opacity: 0.82; }

/* ── Cards grid (categorías / subcategorías) ── */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 0.75rem;
}

.cat-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 1rem 1.125rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  cursor: pointer;
  text-align: left;
  transition: border-color var(--t), box-shadow var(--t), background var(--t);
}
.cat-card:hover {
  border-color: var(--ink);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.cat-card svg { color: var(--ink-4); flex-shrink: 0; }
.cat-nombre {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--ink);
  line-height: 1.3;
}

.empty-hint {
  color: var(--ink-4);
  font-size: 0.875rem;
  padding: 2rem 0;
  grid-column: 1 / -1;
  text-align: center;
}

/* ── Tabla toolbar ── */
.tabla-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.estado-filtros {
  display: flex; gap: 0.25rem;
  background: var(--bg); border: 1px solid var(--border);
  border-radius: var(--r-md); padding: 0.1875rem;
}

.filtro-estado {
  display: flex; align-items: center; gap: 0.3125rem;
  padding: 0.25rem 0.625rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-3); background: none; border: none;
  border-radius: 5px; transition: color var(--t), background var(--t);
}
.filtro-estado .dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.filtro-estado.verde .dot { background: var(--verde); }
.filtro-estado.amarillo .dot { background: var(--amarillo); }
.filtro-estado.rojo .dot { background: var(--rojo); }
.filtro-estado:hover { color: var(--ink); background: var(--surface); }
.filtro-estado.activo { color: var(--ink); background: var(--surface); font-weight: 600; }

.count-badge {
  font-size: 0.75rem; font-weight: 500; color: var(--ink-3);
  background: var(--bg); border: 1px solid var(--border);
  padding: 0.125rem 0.5rem; border-radius: 99px;
}

/* ── Tabla ── */
.table-wrap {
  border: 1px solid var(--border); border-radius: var(--r-lg);
  overflow: hidden; background: var(--surface);
}
.tabla { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.tabla thead tr { border-bottom: 1px solid var(--border); }
.tabla th {
  padding: 0.625rem 1rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-3); text-align: left; background: var(--bg);
  letter-spacing: 0.02em; text-transform: uppercase;
}
.tabla td {
  padding: 0.75rem 1rem; border-bottom: 1px solid var(--border);
  color: var(--ink-2); vertical-align: middle;
}
.tabla tbody tr:last-child td { border-bottom: none; }
.tabla tbody tr { transition: background var(--t); }
.tabla tbody tr:hover { background: var(--bg); }
.tabla tbody tr.dragging { opacity: 0.35; }
.tabla tbody tr.drag-over td:first-child { box-shadow: inset 3px 0 0 var(--ink); }

.col-drag { width: 40px; text-align: center; }
.drag-handle {
  color: var(--ink-4); cursor: grab;
  display: inline-flex; padding: 0.25rem;
  border-radius: var(--r-sm); transition: color var(--t);
}
.drag-handle:hover { color: var(--ink-2); }

.col-nombre { color: var(--ink); }
.nombre-link { color: var(--ink); text-decoration: none; transition: color var(--t); }
.nombre-link:hover { color: var(--ink-2); text-decoration: underline; }

.col-codigo { width: 140px; }
.codigo-tag {
  display: inline-block; font-family: var(--font-mono);
  font-size: 0.75rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  padding: 0.1875rem 0.5rem; border-radius: var(--r-sm);
  margin-right: 0.25rem; letter-spacing: 0.04em;
}

.col-estado { width: 100px; }
.estado-selector { display: flex; gap: 0.3125rem; align-items: center; }
.btn-estado {
  width: 20px; height: 20px; border-radius: 50%;
  border: 2px solid transparent; cursor: pointer;
  opacity: 0.25; padding: 0; flex-shrink: 0;
  transition: opacity var(--t), border-color var(--t), transform var(--t);
}
.btn-estado:hover { opacity: 0.65; transform: scale(1.1); }
.btn-estado.activo { opacity: 1; transform: scale(1.1); }
.btn-estado.verde { background: var(--verde); }
.btn-estado.verde.activo { border-color: var(--verde); }
.btn-estado.amarillo { background: var(--amarillo); }
.btn-estado.amarillo.activo { border-color: var(--amarillo); }
.btn-estado.rojo { background: var(--rojo); }
.btn-estado.rojo.activo { border-color: var(--rojo); }

.col-actions { width: 120px; }
.row-actions { display: flex; gap: 0.25rem; opacity: 0; transition: opacity var(--t); }
.tabla tbody tr:hover .row-actions { opacity: 1; }

.btn-row {
  padding: 0.25rem 0.625rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-2); background: var(--bg);
  border: 1px solid var(--border); border-radius: var(--r-sm);
  text-decoration: none; transition: color var(--t), border-color var(--t), background var(--t);
}
.btn-row:hover { color: var(--ink); border-color: var(--ink); background: var(--surface); }

.empty-cell {
  text-align: center; padding: 3rem 1rem;
  color: var(--ink-4); font-size: 0.875rem;
}

.error-msg {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--rojo);
  background: var(--rojo-bg); border: 1px solid var(--rojo-bd);
  padding: 0.5rem 0.75rem; border-radius: var(--r-md);
}

/* ── Loading ── */
.loading-state { display: flex; justify-content: center; padding: 4rem 0; }
.loading-dots { display: flex; gap: 0.375rem; align-items: center; }
.loading-dots span {
  width: 6px; height: 6px; background: var(--ink-4);
  border-radius: 50%; animation: pulse 1.2s ease-in-out infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ── Mobile cards ── */
.cards-mobile { display: none; }
.product-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 1rem;
  display: flex; flex-direction: column; gap: 0.625rem;
}
.card-top { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.card-codes { display: flex; flex-wrap: wrap; gap: 0.25rem; }
.card-nombre { font-size: 0.9375rem; color: var(--ink); line-height: 1.4; text-decoration: none; }
.card-actions { display: flex; gap: 0.375rem; padding-top: 0.25rem; border-top: 1px solid var(--border); }

/* ── Dropdown transition ── */
.dropdown-enter-active, .dropdown-leave-active { transition: opacity 0.12s ease, transform 0.12s ease; }
.dropdown-enter-from, .dropdown-leave-to { opacity: 0; transform: translateY(-4px); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .hero { padding: 1.25rem 1rem; }
  .cards-grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); }
  .table-desktop { display: none; }
  .cards-mobile { display: flex; flex-direction: column; gap: 0.75rem; }
  .toolbar { flex-wrap: wrap; }
}
</style>
