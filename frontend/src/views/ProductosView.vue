<template>
  <div class="productos-page">
    <!-- Header -->
    <div class="page-header">
      <div class="page-title">
        <h1>Productos</h1>
        <span v-if="!cargando" class="count-badge">{{ productos.length }}</span>
      </div>
      <div class="page-actions">
        <div class="filtros">
          <div class="select-wrap">
            <select v-model="filtroCategoria" @change="cargar">
              <option value="">Todas las categorías</option>
              <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
            </select>
          </div>
          <div class="estado-filtros">
            <button
              v-for="op in estadoOpciones"
              :key="op.valor"
              :class="['filtro-estado', op.valor, { activo: filtroEstado === op.valor }]"
              @click="toggleFiltroEstado(op.valor)"
              :title="filtroEstado === op.valor ? 'Quitar filtro' : op.label"
            >
              <span class="dot"></span>
              {{ op.label }}
              <svg v-if="filtroEstado === op.valor" class="filtro-x" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>
        </div>
        <RouterLink v-if="auth.esAdmin" to="/productos/nuevo" class="btn-primary">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          Nuevo producto
        </RouterLink>
      </div>
    </div>

    <p v-if="errorEstado" class="error-msg">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      {{ errorEstado }}
    </p>

    <!-- Loading -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-dots">
        <span></span><span></span><span></span>
      </div>
    </div>

    <!-- Table (tablet+) -->
    <div v-else class="table-wrap table-desktop">
      <table class="tabla">
        <thead>
          <tr>
            <th v-if="auth.esAdmin" class="col-drag"></th>
            <th>Nombre</th>
            <th>Código</th>
            <th>Estado</th>
            <th class="col-actions">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="p in productos"
            :key="p.id"
            :class="{
              'drag-over': dragOverId === p.id,
              'dragging': draggingId === p.id
            }"
            :draggable="auth.esAdmin"
            @dragstart="onDragStart(p)"
            @dragover.prevent="onDragOver(p)"
            @dragleave="dragOverId = null"
            @drop="onDrop(p)"
            @dragend="onDragEnd"
          >
            <td v-if="auth.esAdmin" class="col-drag">
              <span class="drag-handle" title="Arrastrar para reordenar">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><circle cx="9" cy="5" r="1.5"/><circle cx="15" cy="5" r="1.5"/><circle cx="9" cy="12" r="1.5"/><circle cx="15" cy="12" r="1.5"/><circle cx="9" cy="19" r="1.5"/><circle cx="15" cy="19" r="1.5"/></svg>
              </span>
            </td>
            <td class="col-nombre">{{ p.nombre_completo }}</td>
            <td class="col-codigo">
              <span v-for="c in p.codigos" :key="c.id" class="codigo-tag">
                {{ c.codigo_completo }}
              </span>
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
                <RouterLink v-if="auth.esAdmin" :to="`/productos/${p.id}/editar`" class="btn-row">Editar</RouterLink>
              </div>
            </td>
          </tr>
          <tr v-if="!productos.length">
            <td :colspan="auth.esAdmin ? 5 : 4" class="empty-state">
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
              <span>No hay productos</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Cards (mobile) -->
    <div v-if="!cargando" class="cards-mobile">
      <div v-if="!productos.length" class="empty-mobile">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
        <span>No hay productos</span>
      </div>
      <div v-for="p in productos" :key="p.id" class="product-card">
        <div class="card-top">
          <div class="card-codes">
            <span v-for="c in p.codigos" :key="c.id" class="codigo-tag">{{ c.codigo_completo }}</span>
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
        <p class="card-nombre">{{ p.nombre_completo }}</p>
        <div class="card-actions">
          <RouterLink :to="`/productos/${p.id}`" class="btn-row">Ver detalle</RouterLink>
          <RouterLink v-if="auth.esAdmin" :to="`/productos/${p.id}/editar`" class="btn-row">Editar</RouterLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import client from '@/api/client'

const auth = useAuthStore()
const { showConfirm } = useConfirm()
const productos = ref([])
const categorias = ref([])
const filtroCategoria = ref('')
const filtroEstado = ref('')
const cargando = ref(false)

const draggingId = ref(null)
const dragOverId = ref(null)
const errorEstado = ref('')
let draggingProducto = null

const estadoOpciones = [
  { valor: 'verde', label: 'Verde' },
  { valor: 'amarillo', label: 'Amarillo' },
  { valor: 'rojo', label: 'Rojo' },
]

function toggleFiltroEstado(valor) {
  filtroEstado.value = filtroEstado.value === valor ? '' : valor
  cargar()
}

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
  guardarOrden()
}

async function guardarOrden() {
  try {
    await client.post('/productos/reordenar/', { orden: productos.value.map(p => p.id) })
  } catch (e) { console.error('Error al guardar orden:', e) }
}

async function cambiarEstado(producto, nuevoEstado) {
  if (producto.estado === nuevoEstado) return
  if (!await showConfirm(`¿Cambiar estado de "${producto.nombre_completo}" a "${nuevoEstado}"?`, 'Cambiar estado')) return
  try {
    await client.patch(`/productos/${producto.id}/cambiar-estado/`, { estado: nuevoEstado })
    producto.estado = nuevoEstado
  } catch (e) {
    errorEstado.value = e.response?.data?.detail || 'Error al cambiar estado'
  }
}

async function cargar() {
  cargando.value = true
  try {
    const params = {}
    if (filtroCategoria.value) params.categoria_id = filtroCategoria.value
    if (filtroEstado.value) params.estado = filtroEstado.value
    const { data } = await client.get('/productos/', { params })
    productos.value = data.results ?? data
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  const { data } = await client.get('/categorias/')
  categorias.value = data.results ?? data
  if (categorias.value.length) filtroCategoria.value = categorias.value[0].id
  await cargar()
})
</script>

<style scoped>
.productos-page { display: flex; flex-direction: column; gap: 1.5rem; }

.error-msg {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--rojo);
  background: var(--rojo-bg); border: 1px solid var(--rojo-bd);
  padding: 0.5rem 0.75rem; border-radius: var(--r-md);
}

/* ── Header ── */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  display: flex;
  align-items: baseline;
  gap: 0.625rem;
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--ink);
}

.count-badge {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-3);
  background: var(--bg);
  border: 1px solid var(--border);
  padding: 0.125rem 0.5rem;
  border-radius: 99px;
}

.page-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filtros {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Select */
.select-wrap {
  position: relative;
}

.select-wrap::after {
  content: '';
  position: absolute;
  right: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0;
  height: 0;
  border-left: 4px solid transparent;
  border-right: 4px solid transparent;
  border-top: 5px solid var(--ink-3);
  pointer-events: none;
}

select {
  appearance: none;
  padding: 0.4375rem 2rem 0.4375rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-size: 0.8125rem;
  color: var(--ink-2);
  background: var(--surface);
  cursor: pointer;
  transition: border-color var(--t);
  outline: none;
}

select:focus { border-color: var(--ink); }

/* Estado filtros */
.estado-filtros {
  display: flex;
  gap: 0.25rem;
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 0.1875rem;
}

.filtro-estado {
  display: flex;
  align-items: center;
  gap: 0.3125rem;
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-3);
  background: none;
  border: none;
  border-radius: 5px;
  transition: color var(--t), background var(--t);
}

.filtro-estado .dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}

.filtro-estado.verde .dot { background: var(--verde); }
.filtro-estado.amarillo .dot { background: var(--amarillo); }
.filtro-estado.rojo .dot { background: var(--rojo); }

.filtro-estado:hover { color: var(--ink); background: var(--surface); }
.filtro-estado.activo { color: var(--ink); background: var(--surface); font-weight: 600; }

.filtro-x { flex-shrink: 0; opacity: 0.5; margin-left: 0.125rem; }

/* Btn primary */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4375rem 0.875rem;
  background: var(--ink);
  color: var(--accent-fg);
  border: none;
  border-radius: var(--r-md);
  font-size: 0.8125rem;
  font-weight: 500;
  text-decoration: none;
  transition: opacity var(--t);
  white-space: nowrap;
}

.btn-primary:hover { opacity: 0.82; }

/* ── Loading ── */
.loading-state {
  display: flex;
  justify-content: center;
  padding: 4rem 0;
}

.loading-dots {
  display: flex;
  gap: 0.375rem;
  align-items: center;
}

.loading-dots span {
  width: 6px;
  height: 6px;
  background: var(--ink-4);
  border-radius: 50%;
  animation: pulse 1.2s ease-in-out infinite;
}

.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }

@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

/* ── Table ── */
.table-wrap {
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  overflow: hidden;
  background: var(--surface);
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tabla thead tr {
  border-bottom: 1px solid var(--border);
}

.tabla th {
  padding: 0.625rem 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-3);
  text-align: left;
  background: var(--bg);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.tabla td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--border);
  color: var(--ink-2);
  vertical-align: middle;
}

.tabla tbody tr:last-child td { border-bottom: none; }

.tabla tbody tr {
  transition: background var(--t);
}

.tabla tbody tr:hover { background: var(--bg); }
.tabla tbody tr.dragging { opacity: 0.35; }
.tabla tbody tr.drag-over td:first-child {
  box-shadow: inset 3px 0 0 var(--ink);
}

/* Columns */
.col-drag {
  width: 40px;
  text-align: center;
}

.drag-handle {
  color: var(--ink-4);
  cursor: grab;
  display: inline-flex;
  padding: 0.25rem;
  border-radius: var(--r-sm);
  transition: color var(--t);
}

.drag-handle:hover { color: var(--ink-2); }

.col-nombre { color: var(--ink); font-weight: 400; }

.col-codigo { width: 140px; }

.codigo-tag {
  display: inline-block;
  font-family: var(--font-mono);
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--ink);
  color: var(--accent-fg);
  padding: 0.1875rem 0.5rem;
  border-radius: var(--r-sm);
  margin-right: 0.25rem;
  letter-spacing: 0.04em;
}

/* Estado selector */
.col-estado { width: 100px; }

.estado-selector {
  display: flex;
  gap: 0.3125rem;
  align-items: center;
}

.btn-estado {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  opacity: 0.25;
  transition: opacity var(--t), border-color var(--t), transform var(--t);
  padding: 0;
  flex-shrink: 0;
}

.btn-estado:hover { opacity: 0.65; transform: scale(1.1); }
.btn-estado.activo { opacity: 1; transform: scale(1.1); }

.btn-estado.verde { background: var(--verde); }
.btn-estado.verde.activo { border-color: var(--verde); }
.btn-estado.amarillo { background: var(--amarillo); }
.btn-estado.amarillo.activo { border-color: var(--amarillo); }
.btn-estado.rojo { background: var(--rojo); }
.btn-estado.rojo.activo { border-color: var(--rojo); }

/* Row actions */
.col-actions { width: 120px; }

.row-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity var(--t);
}

.tabla tbody tr:hover .row-actions { opacity: 1; }

.btn-row {
  padding: 0.25rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-2);
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: var(--r-sm);
  text-decoration: none;
  transition: color var(--t), border-color var(--t), background var(--t);
}

.btn-row:hover {
  color: var(--ink);
  border-color: var(--ink);
  background: var(--surface);
}

/* Empty */
.empty-state {
  text-align: center;
  padding: 4rem 1rem;
  color: var(--ink-4);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
}

.empty-state svg { opacity: 0.4; }
.empty-state span { font-size: 0.875rem; }

/* ── Mobile cards ── */
.cards-mobile { display: none; }

.product-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.625rem;
}

.card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.card-codes { display: flex; flex-wrap: wrap; gap: 0.25rem; }

.card-nombre {
  font-size: 0.9375rem;
  color: var(--ink);
  line-height: 1.4;
}

.card-actions {
  display: flex;
  gap: 0.375rem;
  padding-top: 0.25rem;
  border-top: 1px solid var(--border);
}

.empty-mobile {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--ink-4);
  font-size: 0.875rem;
}
.empty-mobile svg { opacity: 0.4; }

/* ── Responsive ── */
@media (max-width: 768px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .page-actions { width: 100%; }
  .filtros { width: 100%; }
  .select-wrap { flex: 1; }
  select { width: 100%; }
  .btn-primary { margin-left: auto; }

  /* Ocultar tabla, mostrar cards */
  .table-desktop { display: none; }
  .cards-mobile {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
}

@media (max-width: 480px) {
  .estado-filtros { flex: 1; justify-content: space-between; }
  .filtro-estado { flex: 1; justify-content: center; }
}
</style>
