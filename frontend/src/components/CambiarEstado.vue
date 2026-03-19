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
        <span class="circulo"></span>
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
    await client.patch(`/productos/${props.producto.id}/cambiar-estado/`, { estado: nuevoEstado })
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

.opciones { display: flex; gap: 0.75rem; align-items: center; }

.opcion {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.2rem;
  border: 2px solid transparent;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  font-size: 0.95rem;
  opacity: 0.35;
  transition: opacity 0.15s, border-color 0.15s, transform 0.1s;
  background: white;
}

.opcion:hover:not(:disabled) {
  opacity: 0.7;
}

.opcion.activo {
  opacity: 1;
  font-weight: 700;
  cursor: default;
  transform: scale(1.05);
}

.opcion:disabled:not(.activo) { cursor: not-allowed; }

/* Círculo de color */
.circulo {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.opcion.verde .circulo { background: #16a34a; }
.opcion.amarillo .circulo { background: #ca8a04; }
.opcion.rojo .circulo { background: #dc2626; }

/* Borde y fondo del activo */
.opcion.verde.activo  { border-color: #16a34a; background: #dcfce7; color: #166534; }
.opcion.amarillo.activo { border-color: #ca8a04; background: #fef9c3; color: #854d0e; }
.opcion.rojo.activo   { border-color: #dc2626; background: #fee2e2; color: #991b1b; }

.error { color: #ef4444; font-size: 0.875rem; margin-top: 0.5rem; }
</style>
