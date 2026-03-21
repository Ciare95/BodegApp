<template>
  <Transition name="modal">
    <div class="overlay" @click.self="$emit('cerrar')">
      <div class="modal">
        <div class="modal-header">
          <h2>Código QR</h2>
          <button class="btn-close" @click="$emit('cerrar')">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="modal-body">
          <div v-if="cargando" class="loading">
            <div class="loading-dots"><span></span><span></span><span></span></div>
            <p>Generando QR...</p>
          </div>

          <div v-else-if="qrBase64" class="qr-contenido">
            <div class="qr-frame">
              <img :src="`data:image/png;base64,${qrBase64}`" alt="Código QR del producto" />
            </div>
            <a :href="`/api/qr/${productoId}/descargar/`" class="btn-descargar" download>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              Descargar PNG
            </a>
          </div>

          <p v-else class="error-msg">No se pudo generar el QR</p>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const props = defineProps({ productoId: { type: [Number, String], required: true } })
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
  position: fixed; inset: 0; background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}

.modal {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); width: 100%; max-width: 340px; overflow: hidden;
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.125rem 1.5rem; border-bottom: 1px solid var(--border);
}
.modal-header h2 {
  font-size: 0.9375rem; font-weight: 600; letter-spacing: -0.02em; color: var(--ink);
}

.btn-close {
  display: flex; align-items: center; justify-content: center;
  width: 26px; height: 26px; color: var(--ink-3); background: none;
  border: none; border-radius: var(--r-sm); transition: all var(--t); cursor: pointer;
}
.btn-close:hover { color: var(--ink); background: var(--bg); }

.modal-body { padding: 1.5rem; }

.loading {
  display: flex; flex-direction: column; align-items: center;
  gap: 0.75rem; padding: 1rem 0;
}
.loading p { font-size: 0.8125rem; color: var(--ink-3); }

.loading-dots { display: flex; gap: 0.375rem; }
.loading-dots span {
  width: 6px; height: 6px; background: var(--ink-4);
  border-radius: 50%; animation: pulse 1.2s ease-in-out infinite;
}
.loading-dots span:nth-child(2) { animation-delay: 0.2s; }
.loading-dots span:nth-child(3) { animation-delay: 0.4s; }
@keyframes pulse {
  0%, 80%, 100% { transform: scale(0.7); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.qr-contenido {
  display: flex; flex-direction: column; align-items: center; gap: 1.25rem;
}

.qr-frame {
  padding: 1rem; background: white;
  border: 1px solid var(--border); border-radius: var(--r-md);
}

.qr-frame img { width: 200px; height: 200px; display: block; }

.btn-descargar {
  display: inline-flex; align-items: center; gap: 0.375rem;
  padding: 0.5rem 1.25rem; font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  border-radius: var(--r-md); text-decoration: none;
  transition: opacity var(--t);
}
.btn-descargar:hover { opacity: 0.82; }

.error-msg { font-size: 0.875rem; color: var(--rojo); text-align: center; padding: 1rem 0; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.15s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }
</style>
