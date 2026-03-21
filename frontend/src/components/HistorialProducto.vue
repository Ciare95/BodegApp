<template>
  <div class="historial">
    <div v-if="cargando" class="loading">
      <div class="loading-dots"><span></span><span></span><span></span></div>
    </div>

    <div v-else-if="registros.length" class="table-wrap">
      <table class="tabla">
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
            <td class="col-fecha">{{ formatFecha(r.fecha) }}</td>
            <td><code class="campo-code">{{ r.campo_modificado }}</code></td>
            <td class="valor-anterior">{{ r.valor_anterior }}</td>
            <td class="valor-nuevo">{{ r.valor_nuevo }}</td>
            <td class="col-usuario">{{ r.usuario_nombre }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-else class="empty">Sin registros de cambios</p>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const props = defineProps({ productoId: { type: [Number, String], required: true } })

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
.historial { display: flex; flex-direction: column; }

.loading { display: flex; justify-content: center; padding: 2rem; }
.loading-dots { display: flex; gap: 0.375rem; }
.loading-dots span {
  width: 5px; height: 5px; background: var(--ink-4);
  border-radius: 50%; animation: pulse 1.2s ease-in-out infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.table-wrap {
  border: 1px solid var(--border); border-radius: var(--r-lg);
  overflow-x: auto; -webkit-overflow-scrolling: touch; background: var(--surface);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.tabla thead tr { border-bottom: 1px solid var(--border); }
.tabla th {
  padding: 0.5rem 0.875rem; font-size: 0.6875rem; font-weight: 500;
  color: var(--ink-3); text-align: left; background: var(--bg);
  letter-spacing: 0.04em; text-transform: uppercase;
}
.tabla td {
  padding: 0.625rem 0.875rem; border-bottom: 1px solid var(--border);
  color: var(--ink-2); vertical-align: middle;
}
.tabla tbody tr:last-child td { border-bottom: none; }
.tabla tbody tr { transition: background var(--t); }
.tabla tbody tr:hover { background: var(--bg); }

.col-fecha { color: var(--ink-3); font-size: 0.75rem; white-space: nowrap; }
.col-usuario { color: var(--ink-3); font-size: 0.75rem; }

.campo-code {
  font-family: var(--font-mono); font-size: 0.75rem;
  background: var(--bg); border: 1px solid var(--border);
  padding: 0.125rem 0.375rem; border-radius: var(--r-sm); color: var(--ink-2);
}

.valor-anterior { color: var(--rojo); font-family: var(--font-mono); font-size: 0.8125rem; }
.valor-nuevo { color: var(--verde); font-family: var(--font-mono); font-size: 0.8125rem; }

.empty { color: var(--ink-4); font-size: 0.875rem; padding: 1rem 0; }

/* Responsive */
@media (max-width: 768px) {
  .col-usuario { display: none; }
}

@media (max-width: 480px) {
  .col-fecha { font-size: 0.6875rem; }
  .valor-anterior, .valor-nuevo { font-size: 0.75rem; }
}
</style>
