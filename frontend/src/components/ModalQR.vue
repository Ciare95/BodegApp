<template>
  <div class="overlay" @click.self="$emit('cerrar')">
    <div class="modal">
      <div class="modal-header">
        <h3>Código QR</h3>
        <button class="btn-cerrar" @click="$emit('cerrar')">✕</button>
      </div>

      <div v-if="cargando" class="cargando">Generando QR...</div>

      <div v-else-if="qrBase64" class="qr-contenido">
        <img :src="`data:image/png;base64,${qrBase64}`" alt="Código QR del producto" />
        <a :href="`/api/qr/${productoId}/descargar/`" class="btn-descargar" download>
          Descargar PNG
        </a>
      </div>

      <p v-else class="error">No se pudo generar el QR</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const props = defineProps({
  productoId: { type: [Number, String], required: true },
})

defineEmits(['cerrar'])

const qrBase64 = ref('')
const cargando = ref(false)

onMounted(async () => {
  cargando.value = true
  try {
    const { data } = await client.get(`/qr/${props.productoId}/`)
    qrBase64.value = data.qr
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  width: 320px;
  max-width: 90vw;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.modal-header h3 { margin: 0; }

.btn-cerrar {
  background: none;
  border: none;
  font-size: 1.1rem;
  cursor: pointer;
  color: #64748b;
}

.qr-contenido {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.qr-contenido img {
  width: 220px;
  height: 220px;
}

.btn-descargar {
  padding: 0.5rem 1rem;
  background: #1e293b;
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.875rem;
}

.cargando, .error { text-align: center; padding: 1rem; color: #64748b; }
.error { color: #ef4444; }
</style>
