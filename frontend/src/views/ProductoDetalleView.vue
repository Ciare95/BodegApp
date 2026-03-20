<template>
  <div v-if="cargando" class="estado-carga">Cargando...</div>

  <div v-else-if="producto" class="detalle">
    <div class="detalle-header">
      <div>
        <h2>{{ producto.nombre_completo }}</h2>
        <div class="codigos-badges">
          <span
            v-for="c in producto.codigos"
            :key="c.id"
            class="codigo-badge"
          >{{ c.codigo_completo }}</span>
        </div>
      </div>
      <div class="acciones">
        <RouterLink v-if="auth.esAdmin" :to="`/productos/${producto.id}/editar`" class="btn-secondary">
          Editar
        </RouterLink>
        <button class="btn-primary" @click="mostrarQR = true">Ver QR</button>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-item">
        <span class="label">Categoría</span>
        <span>{{ producto.subcategoria_detalle?.categoria_nombre }}</span>
      </div>
      <div class="info-item">
        <span class="label">Subcategoría</span>
        <span>{{ producto.subcategoria_detalle?.nombre }}</span>
      </div>
      <div class="info-item">
        <span class="label">Medida principal</span>
        <span>{{ producto.medida_principal_detalle?.valor }}</span>
      </div>
      <div class="info-item">
        <span class="label">Medida secundaria</span>
        <span>{{ producto.medida_secundaria_detalle?.valor ?? '—' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Actualizado por</span>
        <span>{{ producto.actualizado_por_nombre ?? '—' }}</span>
      </div>
      <div class="info-item">
        <span class="label">Última actualización</span>
        <span>{{ formatFecha(producto.actualizado_en) }}</span>
      </div>
    </div>

    <CambiarEstado :producto="producto" @actualizado="recargar" />

    <div v-if="auth.esAdmin" class="seccion-historial">
      <h3>Historial de cambios</h3>
      <HistorialProducto :producto-id="producto.id" :key="historialKey" />
    </div>

    <ModalQR v-if="mostrarQR" :producto-id="producto.id" @cerrar="mostrarQR = false" />
  </div>

  <div v-else class="estado-carga">Producto no encontrado</div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'
import CambiarEstado from '@/components/CambiarEstado.vue'
import HistorialProducto from '@/components/HistorialProducto.vue'
import ModalQR from '@/components/ModalQR.vue'

const route = useRoute()
const auth = useAuthStore()

const producto = ref(null)
const cargando = ref(false)
const mostrarQR = ref(false)
const historialKey = ref(0)

async function cargar() {
  cargando.value = true
  try {
    const { data } = await client.get(`/productos/${route.params.id}/`)
    producto.value = data
  } finally {
    cargando.value = false
  }
}

async function recargar() {
  await cargar()
  historialKey.value++
}

function formatFecha(fecha) {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleString('es-CO')
}

onMounted(cargar)
</script>

<style scoped>
.detalle { max-width: 800px; }

.detalle-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

h2 { margin: 0 0 0.25rem; }

.codigos-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.25rem;
}

.codigo-badge {
  font-family: monospace;
  font-size: 1.1rem;
  font-weight: bold;
  background: #1e293b;
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
}

.acciones { display: flex; gap: 0.5rem; }

.btn-primary {
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  font-size: 0.875rem;
}

.btn-secondary {
  padding: 0.4rem 0.8rem;
  background: #e2e8f0;
  color: #1e293b;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.875rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
  background: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.label {
  font-size: 0.75rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.seccion-historial { margin-top: 2rem; }
.seccion-historial h3 { margin-bottom: 0.75rem; }

.estado-carga { text-align: center; padding: 3rem; color: #64748b; }
</style>
