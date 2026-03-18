<template>
  <div>
    <div v-if="cargando" class="cargando">Cargando historial...</div>
    <table v-else-if="registros.length" class="tabla">
      <thead>
        <tr>
          <th>Fecha</th>
          <th>Campo</th>
          <th>Anterior</th>
          <th>Nuevo</th>
          <th>Usuario</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="r in registros" :key="r.id">
          <td>{{ formatFecha(r.fecha) }}</td>
          <td><code>{{ r.campo_modificado }}</code></td>
          <td class="valor-anterior">{{ r.valor_anterior }}</td>
          <td class="valor-nuevo">{{ r.valor_nuevo }}</td>
          <td>{{ r.usuario_nombre }}</td>
        </tr>
      </tbody>
    </table>
    <p v-else class="vacio">Sin registros de cambios</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const props = defineProps({
  productoId: { type: [Number, String], required: true },
})

const registros = ref([])
const cargando = ref(false)

function formatFecha(fecha) {
  return new Date(fecha).toLocaleString('es-CO')
}

onMounted(async () => {
  cargando.value = true
  try {
    const { data } = await client.get('/historial/', { params: { producto_id: props.productoId } })
    registros.value = data.results ?? data
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tabla th, .tabla td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.tabla th { background: #f8fafc; font-weight: 600; }

code { font-size: 0.8rem; background: #f1f5f9; padding: 0.1rem 0.3rem; border-radius: 3px; }

.valor-anterior { color: #ef4444; }
.valor-nuevo { color: #16a34a; }

.vacio, .cargando { color: #94a3b8; font-size: 0.875rem; padding: 0.5rem 0; }
</style>
