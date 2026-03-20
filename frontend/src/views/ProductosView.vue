<template>
  <div>
    <div class="toolbar">
      <h2>Productos</h2>
      <div class="filtros">
        <select v-model="filtroCategoria" @change="cargar">
          <option value="">Todas las categorías</option>
          <option v-for="c in categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
        <select v-model="filtroEstado" @change="cargar">
          <option value="">Todos los estados</option>
          <option value="verde">Verde</option>
          <option value="amarillo">Amarillo</option>
          <option value="rojo">Rojo</option>
        </select>
        <RouterLink v-if="auth.esAdmin" to="/productos/nuevo" class="btn-primary">
          + Nuevo producto
        </RouterLink>
      </div>
    </div>

    <div v-if="cargando" class="estado-carga">Cargando...</div>

    <table v-else class="tabla">
      <thead>
        <tr>
          <th v-if="auth.esAdmin" class="col-drag"></th>
          <th>Nombre</th>
          <th>Código</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="p in productos"
          :key="p.id"
          :class="{ 'drag-over': dragOverId === p.id, 'dragging': draggingId === p.id }"
          :draggable="auth.esAdmin"
          @dragstart="onDragStart(p)"
          @dragover.prevent="onDragOver(p)"
          @dragleave="dragOverId = null"
          @drop="onDrop(p)"
          @dragend="onDragEnd"
        >
          <td v-if="auth.esAdmin" class="col-drag" title="Arrastrar para reordenar">⠿</td>
          <td>{{ p.nombre_completo }}</td>
          <td class="codigo">
            <span v-for="c in p.codigos" :key="c.id" class="codigo-tag">
              {{ c.codigo_completo }}
            </span>
          </td>
          <td>
            <div class="estado-selector">
              <button
                v-for="op in estados"
                :key="op.valor"
                :class="['btn-estado', op.valor, { activo: p.estado === op.valor }]"
                :title="op.valor"
                @click="cambiarEstado(p, op.valor)"
              >{{ op.label }}</button>
            </div>
          </td>
          <td>
            <RouterLink :to="`/productos/${p.id}`" class="btn-link">Ver</RouterLink>
            <RouterLink v-if="auth.esAdmin" :to="`/productos/${p.id}/editar`" class="btn-link">Editar</RouterLink>
          </td>
        </tr>
        <tr v-if="!productos.length">
          <td :colspan="auth.esAdmin ? 5 : 4" class="vacio">No hay productos</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

const auth = useAuthStore()
const productos = ref([])
const categorias = ref([])
const filtroCategoria = ref('')
const filtroEstado = ref('')
const cargando = ref(false)

// Drag & drop
const draggingId = ref(null)
const dragOverId = ref(null)
let draggingProducto = null

const estados = [
  { valor: 'verde', label: '●' },
  { valor: 'amarillo', label: '●' },
  { valor: 'rojo', label: '●' },
]

function onDragStart(p) {
  draggingProducto = p
  draggingId.value = p.id
}

function onDragOver(p) {
  if (draggingProducto && draggingProducto.id !== p.id) {
    dragOverId.value = p.id
  }
}

function onDrop(target) {
  if (!draggingProducto || draggingProducto.id === target.id) return

  const lista = productos.value
  const fromIdx = lista.findIndex((p) => p.id === draggingProducto.id)
  const toIdx = lista.findIndex((p) => p.id === target.id)

  // Reordenar localmente
  const item = lista.splice(fromIdx, 1)[0]
  lista.splice(toIdx, 0, item)

  // Persistir en backend
  guardarOrden()
}

function onDragEnd() {
  draggingId.value = null
  dragOverId.value = null
  draggingProducto = null
}

async function guardarOrden() {
  try {
    await client.post('/productos/reordenar/', {
      orden: productos.value.map((p) => p.id),
    })
  } catch (e) {
    console.error('Error al guardar orden:', e)
  }
}

async function cambiarEstado(producto, nuevoEstado) {
  if (producto.estado === nuevoEstado) return
  if (!window.confirm(`¿Cambiar estado de "${producto.codigo_completo}" a "${nuevoEstado}"?`)) return
  try {
    await client.patch(`/productos/${producto.id}/cambiar-estado/`, { estado: nuevoEstado })
    producto.estado = nuevoEstado
  } catch (e) {
    alert(e.response?.data?.detail || 'Error al cambiar estado')
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
  if (categorias.value.length) {
    filtroCategoria.value = categorias.value[0].id
  }
  await cargar()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

h2 { margin: 0; }

.filtros {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

select {
  padding: 0.4rem 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
}

.btn-primary {
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.875rem;
}

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tabla th, .tabla td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.tabla th { background: #f8fafc; font-weight: 600; }

.col-drag {
  width: 32px;
  text-align: center;
  color: #94a3b8;
  cursor: grab;
  font-size: 1.1rem;
  user-select: none;
}

.tabla tr[draggable="true"] { cursor: grab; }
.tabla tr[draggable="true"]:active { cursor: grabbing; }

.dragging { opacity: 0.4; }

.drag-over td {
  border-top: 2px solid #3b82f6;
}

.codigo { font-weight: bold; font-family: monospace; }

.codigo-tag {
  display: inline-block;
  background: #1e293b;
  color: white;
  font-family: monospace;
  font-size: 0.8rem;
  font-weight: bold;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  margin-right: 0.3rem;
}

.estado-selector { display: flex; gap: 0.25rem; }

.btn-estado {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid transparent;
  cursor: pointer;
  font-size: 0.6rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.3;
  transition: opacity 0.15s, border-color 0.15s;
  padding: 0;
}

.btn-estado:hover { opacity: 0.7; }
.btn-estado.activo { opacity: 1; border-color: #1e293b; }
.btn-estado.verde { background: #16a34a; }
.btn-estado.amarillo { background: #ca8a04; }
.btn-estado.rojo { background: #dc2626; }

.btn-link {
  color: #3b82f6;
  text-decoration: none;
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.vacio { text-align: center; color: #94a3b8; padding: 2rem; }
.estado-carga { text-align: center; padding: 2rem; color: #64748b; }
</style>
