<template>
  <div class="catalogos-page">
    <div class="page-header">
      <h1>Catálogos</h1>
    </div>

    <div class="tabs-bar">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        :class="['tab', { activo: tabActiva === tab.key }]"
        @click="tabActiva = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <TablaCatalogo
      :key="tabActiva"
      :endpoint="tabActual.endpoint"
      :campo="tabActual.campo"
      :label="tabActual.label"
      :campos-extra="tabActual.camposExtra ?? []"
      :campos-creacion="tabActual.camposCreacion ?? []"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import TablaCatalogo from '@/components/TablaCatalogo.vue'
import client from '@/api/client'

const categorias = ref([])

onMounted(async () => {
  const { data } = await client.get('/categorias/')
  categorias.value = data.results ?? data
})

const tabs = computed(() => [
  { key: 'categorias', label: 'Categorías', endpoint: '/categorias/', campo: 'nombre', label: 'Categoría' },
  {
    key: 'subcategorias', label: 'Subcategorías', endpoint: '/subcategorias/',
    campo: 'nombre', label: 'Subcategoría',
    camposExtra: [{ key: 'categoria_nombre', label: 'Categoría' }],
    camposCreacion: [{ key: 'categoria_id', label: 'Categoría', opciones: categorias.value }],
  },
  { key: 'medidas-principales', label: 'Medidas principales', endpoint: '/medidas-principales/', campo: 'valor', label: 'Medida Principal' },
  { key: 'medidas-secundarias', label: 'Medidas secundarias', endpoint: '/medidas-secundarias/', campo: 'valor', label: 'Medida Secundaria' },
  { key: 'codigos-uno', label: 'Prefijos', endpoint: '/codigos-uno/', campo: 'valor', label: 'Prefijo' },
  { key: 'codigos-dos', label: 'Sufijos', endpoint: '/codigos-dos/', campo: 'valor', label: 'Sufijo' },
])

const tabActiva = ref('categorias')
const tabActual = computed(() => tabs.value.find(t => t.key === tabActiva.value))
</script>

<style scoped>
.catalogos-page { display: flex; flex-direction: column; gap: 1.5rem; }

.page-header { display: flex; align-items: center; justify-content: space-between; }

h1 {
  font-size: 1.375rem; font-weight: 600;
  letter-spacing: -0.03em; color: var(--ink);
}

.tabs-bar {
  display: flex; gap: 0; flex-wrap: wrap;
  border-bottom: 1px solid var(--border);
}

.tab {
  padding: 0.5rem 1rem; font-size: 0.8125rem; font-weight: 400;
  color: var(--ink-3); background: none; border: none;
  border-bottom: 2px solid transparent; margin-bottom: -1px;
  cursor: pointer; transition: color var(--t), border-color var(--t);
  white-space: nowrap;
}

.tab:hover { color: var(--ink-2); }

.tab.activo {
  color: var(--ink); font-weight: 500;
  border-bottom-color: var(--ink);
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .tabs-bar {
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    flex-wrap: nowrap;
    scrollbar-width: none;
  }
  .tabs-bar::-webkit-scrollbar { display: none; }
  .tab { white-space: nowrap; flex-shrink: 0; }
}
</style>
