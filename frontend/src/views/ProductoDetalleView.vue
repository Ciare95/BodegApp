<template>
  <div v-if="cargando" class="loading-state">
    <div class="loading-dots"><span></span><span></span><span></span></div>
  </div>

  <div v-else-if="producto" class="detalle-page">
    <RouterLink to="/productos" class="back-link">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      Productos
    </RouterLink>

    <div class="detalle-hero">
      <div class="hero-left">
        <div class="codigos-row">
          <span v-for="c in producto.codigos" :key="c.id" class="codigo-hero">{{ c.codigo_completo }}</span>
          <span :class="['estado-pill', producto.estado]">
            <span class="dot"></span>{{ producto.estado }}
          </span>
        </div>
        <h1 class="producto-nombre">{{ producto.nombre_completo }}</h1>
      </div>
      <div class="hero-actions">
        <button class="btn-qr" @click="mostrarQR = true">
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="3" height="3"/></svg>
          Ver QR
        </button>
        <RouterLink v-if="auth.esAdmin" :to="`/productos/${producto.id}/editar`" class="btn-edit">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          Editar
        </RouterLink>
      </div>
    </div>

    <div class="info-grid">
      <div class="info-card">
        <span class="info-label">Categoría</span>
        <span class="info-value">{{ producto.subcategoria_detalle?.categoria_nombre ?? '—' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">Subcategoría</span>
        <span class="info-value">{{ producto.subcategoria_detalle?.nombre ?? '—' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">Medida principal</span>
        <span class="info-value mono">{{ producto.medida_principal_detalle?.valor ?? '—' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">Medida secundaria</span>
        <span class="info-value mono">{{ producto.medida_secundaria_detalle?.valor ?? '—' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">Actualizado por</span>
        <span class="info-value">{{ producto.actualizado_por_nombre ?? '—' }}</span>
      </div>
      <div class="info-card">
        <span class="info-label">Última actualización</span>
        <span class="info-value">{{ formatFecha(producto.actualizado_en) }}</span>
      </div>
    </div>

    <CambiarEstado :producto="producto" @actualizado="recargar" />

    <div v-if="auth.esAdmin" class="historial-section">
      <h2 class="section-title">Historial de cambios</h2>
      <HistorialProducto :producto-id="producto.id" :key="historialKey" />
    </div>

    <ModalQR v-if="mostrarQR" :producto-id="producto.id" @cerrar="mostrarQR = false" />
  </div>

  <div v-else class="loading-state">
    <p style="color: var(--ink-3); font-size: 0.875rem;">Producto no encontrado</p>
  </div>
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
.detalle-page { display: flex; flex-direction: column; gap: 1.5rem; max-width: 860px; }

.back-link {
  display: inline-flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--ink-3); text-decoration: none;
  transition: color var(--t);
}
.back-link:hover { color: var(--ink); }

.detalle-hero {
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}

.codigos-row {
  display: flex; align-items: center; gap: 0.5rem;
  flex-wrap: wrap; margin-bottom: 0.5rem;
}

.codigo-hero {
  font-family: var(--font-mono); font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  padding: 0.25rem 0.625rem; border-radius: var(--r-sm); letter-spacing: 0.06em;
}

.estado-pill {
  display: inline-flex; align-items: center; gap: 0.3125rem;
  font-size: 0.75rem; font-weight: 500; padding: 0.25rem 0.625rem;
  border-radius: 99px; text-transform: capitalize; border: 1px solid;
}
.estado-pill .dot { width: 6px; height: 6px; border-radius: 50%; }
.estado-pill.verde { background: var(--verde-bg); color: var(--verde); border-color: var(--verde-bd); }
.estado-pill.verde .dot { background: var(--verde); }
.estado-pill.amarillo { background: var(--amarillo-bg); color: var(--amarillo); border-color: var(--amarillo-bd); }
.estado-pill.amarillo .dot { background: var(--amarillo); }
.estado-pill.rojo { background: var(--rojo-bg); color: var(--rojo); border-color: var(--rojo-bd); }
.estado-pill.rojo .dot { background: var(--rojo); }

.producto-nombre {
  font-size: 1.5rem; font-weight: 600; letter-spacing: -0.03em;
  color: var(--ink); line-height: 1.2;
}

.hero-actions { display: flex; gap: 0.5rem; flex-shrink: 0; }

.btn-qr, .btn-edit {
  display: inline-flex; align-items: center; gap: 0.375rem;
  padding: 0.4375rem 0.875rem; font-size: 0.8125rem; font-weight: 500;
  border-radius: var(--r-md); transition: all var(--t);
  text-decoration: none; cursor: pointer;
}
.btn-qr {
  background: var(--surface); color: var(--ink-2);
  border: 1px solid var(--border);
}
.btn-qr:hover { color: var(--ink); border-color: var(--ink); }
.btn-edit {
  background: var(--ink); color: var(--accent-fg);
  border: 1px solid var(--ink);
}
.btn-edit:hover { opacity: 0.82; }

.info-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1px; background: var(--border);
  border: 1px solid var(--border); border-radius: var(--r-lg); overflow: hidden;
}
.info-card {
  display: flex; flex-direction: column; gap: 0.25rem;
  padding: 0.875rem 1rem; background: var(--surface);
}
.info-label {
  font-size: 0.6875rem; font-weight: 500; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.06em;
}
.info-value { font-size: 0.9375rem; color: var(--ink); }
.info-value.mono { font-family: var(--font-mono); font-size: 0.875rem; }

.historial-section { display: flex; flex-direction: column; gap: 0.75rem; }
.section-title {
  font-size: 1rem; font-weight: 600; letter-spacing: -0.02em; color: var(--ink);
}

.loading-state {
  display: flex; justify-content: center; align-items: center; padding: 5rem 0;
}
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

/* ── Responsive ── */
@media (max-width: 768px) {
  .detalle-page { max-width: 100%; }

  .detalle-hero { flex-direction: column; gap: 1rem; }
  .hero-actions { width: 100%; }
  .btn-qr, .btn-edit { flex: 1; justify-content: center; }

  .producto-nombre { font-size: 1.25rem; }

  .info-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 480px) {
  .info-grid { grid-template-columns: 1fr 1fr; }
  .producto-nombre { font-size: 1.125rem; }
}
</style>
