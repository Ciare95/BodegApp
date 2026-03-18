<template>
  <div class="cambiar-estado">
    <h3>Estado del producto</h3>
    <div class="opciones">
      <button
        v-for="op in opciones"
        :key="op.valor"
        :class="['opcion', op.valor, { activo: producto.estado === op.valor }]"
        :disabled="guardando || producto.estado === op.valor"
        @click="confirmar(op.valor)"
      >
        {{ op.label }}
      </button>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import client from '@/api/client'

const props = defineProps({
  producto: { type: Object, required: true },
})

const emit = defineEmits(['actualizado'])

const guardando = ref(false)
const error = ref('')

const opciones = [
  { valor: 'verde', label: 'Verde' },
  { valor: 'amarillo', label: 'Amarillo' },
  { valor: 'rojo', label: 'Rojo' },
]

async function confirmar(nuevoEstado) {
  if (!window.confirm(`¿Cambiar estado a "${nuevoEstado}"?`)) return
  error.value = ''
  guardando.value = true
  try {
    await client.post(`/productos/${props.producto.id}/cambiar-estado/`, { estado: nuevoEstado })
    emit('actualizado')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al cambiar estado'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.cambiar-estado {
  background: #f8fafc;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 1.5rem;
}

h3 { margin: 0 0 0.75rem; font-size: 1rem; }

.opciones { display: flex; gap: 0.5rem; }

.opcion {
  padding: 0.5rem 1.2rem;
  border: 2px solid transparent;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: opacity 0.15s;
}

.opcion:disabled { cursor: not-allowed; opacity: 0.5; }

.opcion.verde { background: #dcfce7; color: #166534; border-color: #86efac; }
.opcion.amarillo { background: #fef9c3; color: #854d0e; border-color: #fde047; }
.opcion.rojo { background: #fee2e2; color: #991b1b; border-color: #fca5a5; }

.opcion.activo { border-width: 2px; opacity: 1; font-weight: 700; cursor: default; }

.error { color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem; }
</style>
