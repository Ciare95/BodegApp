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
          <th>Nombre</th>
          <th>Código</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="p in productos" :key="p.id">
          <td>{{ p.nombre_completo }}</td>
          <td class="codigo">{{ p.codigo_completo }}</td>
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
          <td colspan="4" class="vacio">No hay productos</td>
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

const estados = [
  { valor: 'verde', label: '●' },
  { valor: 'amarillo', label: '●' },
  { valor: 'rojo', label: '●' },
]

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

.codigo { font-weight: bold; font-family: monospace; }

.estado-selector {
  display: flex;
  gap: 0.25rem;
}

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

.btn-estado.verde { background: #16a34a; color: #16a34a; }
.btn-estado.amarillo { background: #ca8a04; color: #ca8a04; }
.btn-estado.rojo { background: #dc2626; color: #dc2626; }

.badge {
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  text-transform: capitalize;
}

.badge.verde { background: #dcfce7; color: #166534; }
.badge.amarillo { background: #fef9c3; color: #854d0e; }
.badge.rojo { background: #fee2e2; color: #991b1b; }

.btn-link {
  color: #3b82f6;
  text-decoration: none;
  margin-right: 0.5rem;
  font-size: 0.875rem;
}

.vacio { text-align: center; color: #94a3b8; padding: 2rem; }
.estado-carga { text-align: center; padding: 2rem; color: #64748b; }
</style>
