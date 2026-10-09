<template>
  <div class="detalle-page">
    <div class="page-header">
      <button class="btn-volver" @click="router.push({ name: 'revision' })">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6"/>
        </svg>
        Revisión
      </button>
      <h1>Prefijo {{ prefijo }}</h1>
      <span v-if="!cargando && !error" class="conteo-badge">{{ productos.length }} producto{{ productos.length === 1 ? '' : 's' }}</span>
    </div>

    <div v-if="cargando" class="estado-msg">Cargando…</div>
    <div v-else-if="error" class="estado-msg error">{{ error }}</div>
    <div v-else-if="productos.length === 0" class="estado-msg">Sin productos para este prefijo.</div>

    <div v-else class="tabla-wrap">
      <table class="tabla-productos">
        <thead>
          <tr>
            <th class="col-codigo">Código</th>
            <th class="col-nombre">Producto</th>
            <th class="col-estado">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="prod in productos" :key="prod.id">
            <td class="col-codigo codigo-text">{{ codigoPrincipal(prod) }}</td>
            <td class="col-nombre">{{ prod.nombre_completo }}</td>
            <td class="col-estado">
              <div class="estado-wrap">
                <span class="estado-dot" :class="estadoActual(prod)"></span>
                <select
                  :value="estadoActual(prod)"
                  class="estado-select"
                  :class="estadoActual(prod)"
                  @change="cambiarEstado(prod, $event.target.value)"
                >
                  <option value="verde">Verde</option>
                  <option value="amarillo">Amarillo</option>
                  <option value="rojo">Rojo</option>
                </select>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'

const route = useRoute()
const router = useRouter()
const prefijo = route.params.prefijo

const productos = ref([])
const cargando = ref(true)
const error = ref(null)

function sortKey(valor) {
  return /^\d+$/.test(valor)
    ? [1, parseInt(valor, 10), '']
    : [0, 0, valor.toUpperCase()]
}

function ordenarPorSufijo(lista) {
  return [...lista].sort((a, b) => {
    const sufA = codigoDosValor(a)
    const sufB = codigoDosValor(b)
    const ka = sortKey(sufA)
    const kb = sortKey(sufB)
    if (ka[0] !== kb[0]) return ka[0] - kb[0]
    return ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
  })
}

function codigoDosValor(prod) {
  const codigo = prod.codigos?.find(c => c.codigo_uno_valor?.toUpperCase() === prefijo.toUpperCase())
  return codigo?.codigo_dos_valor ?? ''
}

function codigoPrincipal(prod) {
  const codigo = prod.codigos?.find(c => c.codigo_uno_valor?.toUpperCase() === prefijo.toUpperCase())
  return codigo?.codigo_completo ?? prod.codigo_completo
}

function estadoActual(prod) {
  return prod.estado
}

onMounted(async () => {
  try {
    // Obtener el id del prefijo a partir del valor en la URL
    const { data: prefijosData } = await client.get('/codigos-uno/', { params: { con_conteo: 'true' } })
    const lista = prefijosData.results ?? prefijosData
    const encontrado = lista.find(p => p.valor.toUpperCase() === prefijo.toUpperCase())

    if (!encontrado) {
      productos.value = []
      return
    }

    const { data: prodData } = await client.get('/productos/', {
      params: { codigo_uno_id: encontrado.id },
    })
    const rawProductos = prodData.results ?? prodData
    productos.value = ordenarPorSufijo(rawProductos)
  } catch (e) {
    error.value = 'No se pudieron cargar los productos.'
  } finally {
    cargando.value = false
  }
})

async function cambiarEstado(prod, nuevoEstado) {
  if (prod.estado === nuevoEstado) return
  try {
    const { data } = await client.patch(`/productos/${prod.id}/cambiar-estado/`, { estado: nuevoEstado })
    const idx = productos.value.findIndex(p => p.id === prod.id)
    if (idx !== -1) productos.value[idx] = { ...productos.value[idx], estado: data.estado }
  } catch {
    // En caso de error, recargar el estado original
    const { data } = await client.get(`/productos/${prod.id}/`)
    const idx = productos.value.findIndex(p => p.id === prod.id)
    if (idx !== -1) productos.value[idx] = data
  }
}
</script>

<style scoped>
.detalle-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--ink);
  flex: 1;
}

.btn-volver {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  color: var(--ink-2);
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  cursor: pointer;
  transition: background var(--t), color var(--t);
  white-space: nowrap;
}
.btn-volver:hover { background: var(--bg); color: var(--ink); }

.conteo-badge {
  font-size: 0.8rem;
  color: var(--ink-3);
  white-space: nowrap;
}

.estado-msg {
  color: var(--ink-3);
  font-size: 0.9rem;
  padding: 2rem 0;
  text-align: center;
}
.estado-msg.error { color: var(--rojo); }

.tabla-wrap {
  overflow-x: auto;
}

.tabla-productos {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tabla-productos th {
  text-align: left;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0 0.75rem 0.5rem;
  border-bottom: 1px solid var(--border);
}

.tabla-productos td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.tabla-productos tr:last-child td { border-bottom: none; }
.tabla-productos tr:hover td { background: var(--bg); }

.col-codigo { width: 110px; }
.col-estado { width: 140px; }

.codigo-text {
  font-family: monospace;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.03em;
}

/* Estado */
.estado-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.estado-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}
.estado-dot.verde    { background: var(--verde, #22c55e); }
.estado-dot.amarillo { background: var(--amarillo, #eab308); }
.estado-dot.rojo     { background: var(--rojo, #ef4444); }

.estado-select {
  flex: 1;
  padding: 0.25rem 0.5rem;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  background: var(--surface);
  color: var(--ink);
  cursor: pointer;
  transition: border-color var(--t);
}
.estado-select:hover { border-color: var(--ink-3); }
.estado-select:focus { outline: none; border-color: var(--ink-2); }

.estado-select.verde    { border-left: 3px solid var(--verde, #22c55e); }
.estado-select.amarillo { border-left: 3px solid var(--amarillo, #eab308); }
.estado-select.rojo     { border-left: 3px solid var(--rojo, #ef4444); }

@media (max-width: 480px) {
  .col-nombre { font-size: 0.8125rem; }
}
</style>
