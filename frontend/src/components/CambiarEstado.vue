<template>
  <div class="cambiar-estado">
    <span class="section-label">Estado del producto</span>
    <div class="opciones">
      <button
        v-for="op in opciones"
        :key="op.valor"
        :class="['opcion', op.valor, { activo: producto.estado === op.valor }]"
        :disabled="guardando || producto.estado === op.valor"
        @click="confirmar(op.valor)"
      >
        <span class="dot"></span>
        {{ op.label }}
      </button>
    </div>
    <p v-if="error" class="error-msg">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useConfirm } from '@/composables/useConfirm'
import client from '@/api/client'

const props = defineProps({ producto: { type: Object, required: true } })
const emit = defineEmits(['actualizado'])

const guardando = ref(false)
const error = ref('')
const { showConfirm } = useConfirm()

const opciones = [
  { valor: 'verde', label: 'Disponible' },
  { valor: 'amarillo', label: 'Queda poco' },
  { valor: 'rojo', label: 'Sin stock' },
]

async function confirmar(nuevoEstado) {
  if (!await showConfirm(`¿Cambiar estado a "${opciones.find(o => o.valor === nuevoEstado)?.label}"?`, 'Cambiar estado')) return
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
  display: flex; flex-direction: column; gap: 0.625rem;
  padding: 1rem 1.25rem;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg);
}

.section-label {
  font-size: 0.6875rem; font-weight: 600; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.06em;
}

.opciones { display: flex; gap: 0.5rem; flex-wrap: wrap; }

.opcion {
  display: flex; align-items: center; gap: 0.4375rem;
  padding: 0.4375rem 0.875rem; font-size: 0.875rem; font-weight: 500;
  border: 1px solid var(--border); border-radius: var(--r-md);
  cursor: pointer; transition: all var(--t);
  color: var(--ink-3); background: var(--surface);
  opacity: 0.6;
}

.opcion .dot {
  width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
}

.opcion.verde .dot { background: var(--verde); }
.opcion.amarillo .dot { background: var(--amarillo); }
.opcion.rojo .dot { background: var(--rojo); }

.opcion:hover:not(:disabled) { opacity: 0.85; border-color: var(--border-md); color: var(--ink); }

.opcion.verde.activo {
  opacity: 1; background: var(--verde-bg);
  border-color: var(--verde-bd); color: var(--verde); cursor: default;
}
.opcion.amarillo.activo {
  opacity: 1; background: var(--amarillo-bg);
  border-color: var(--amarillo-bd); color: var(--amarillo); cursor: default;
}
.opcion.rojo.activo {
  opacity: 1; background: var(--rojo-bg);
  border-color: var(--rojo-bd); color: var(--rojo); cursor: default;
}

.opcion:disabled:not(.activo) { cursor: not-allowed; }

.error-msg { font-size: 0.8125rem; color: var(--rojo); }

/* Responsive */
@media (max-width: 480px) {
  .opcion { flex: 1; justify-content: center; }
}
</style>
