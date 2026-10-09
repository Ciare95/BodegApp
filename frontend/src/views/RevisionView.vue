<template>
  <div class="revision-page">
    <div class="page-header">
      <h1>Revisión de Bodega</h1>
    </div>

    <div v-if="cargando" class="estado-msg">Cargando prefijos…</div>
    <div v-else-if="error" class="estado-msg error">{{ error }}</div>
    <div v-else-if="prefijos.length === 0" class="estado-msg">No hay prefijos registrados.</div>

    <div v-else class="prefijos-grid">
      <button
        v-for="p in prefijos"
        :key="p.id"
        class="prefijo-card"
        :class="{ vacio: p.producto_count === 0 }"
        @click="irADetalle(p)"
      >
        <span class="prefijo-valor">{{ p.valor }}</span>
        <span v-if="p.producto_count === 0" class="prefijo-sub sin-productos">Sin productos</span>
        <span v-else class="prefijo-sub">{{ p.producto_count }} producto{{ p.producto_count === 1 ? '' : 's' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'

const router = useRouter()
const prefijos = ref([])
const cargando = ref(true)
const error = ref(null)

function sortKey(valor) {
  return /^\d+$/.test(valor)
    ? [1, parseInt(valor, 10), '']
    : [0, 0, valor.toUpperCase()]
}

function ordenarPrefijos(lista) {
  return [...lista].sort((a, b) => {
    const ka = sortKey(a.valor)
    const kb = sortKey(b.valor)
    if (ka[0] !== kb[0]) return ka[0] - kb[0]
    return ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
  })
}

onMounted(async () => {
  try {
    const { data } = await client.get('/codigos-uno/', { params: { con_conteo: 'true' } })
    prefijos.value = ordenarPrefijos(data.results ?? data)
  } catch (e) {
    error.value = 'No se pudieron cargar los prefijos.'
  } finally {
    cargando.value = false
  }
})

function irADetalle(p) {
  router.push({ name: 'revision-detalle', params: { prefijo: p.valor }, query: { id: p.id } })
}
</script>

<style scoped>
.revision-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--ink);
}

.estado-msg {
  color: var(--ink-3);
  font-size: 0.9rem;
  padding: 2rem 0;
  text-align: center;
}
.estado-msg.error { color: var(--rojo); }

.prefijos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 0.75rem;
}

.prefijo-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 1rem 0.5rem;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  cursor: pointer;
  transition: background var(--t), border-color var(--t), transform 0.1s;
  min-height: 80px;
}

.prefijo-card:hover {
  background: var(--bg);
  border-color: var(--ink-3);
  transform: translateY(-1px);
}

.prefijo-card.vacio {
  opacity: 0.55;
}

.prefijo-card.vacio:hover {
  opacity: 0.8;
}

.prefijo-valor {
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: -0.02em;
}

.prefijo-sub {
  font-size: 0.75rem;
  color: var(--ink-3);
}

.sin-productos {
  font-style: italic;
}

@media (max-width: 480px) {
  .prefijos-grid {
    grid-template-columns: repeat(auto-fill, minmax(90px, 1fr));
  }
}
</style>
