<template>
  <div>
    <h2>Gestión de catálogos</h2>

    <div class="tabs">
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
  {
    key: 'categorias',
    label: 'Categorías',
    endpoint: '/categorias/',
    campo: 'nombre',
    label: 'Categoría',
  },
  {
    key: 'subcategorias',
    label: 'Subcategorías',
    endpoint: '/subcategorias/',
    campo: 'nombre',
    label: 'Subcategoría',
    camposExtra: [{ key: 'categoria_nombre', label: 'Categoría' }],
    camposCreacion: [
      {
        key: 'categoria_id',
        label: 'Categoría',
        opciones: categorias.value,
      },
    ],
  },
  {
    key: 'medidas-principales',
    label: 'Medidas principales',
    endpoint: '/medidas-principales/',
    campo: 'valor',
    label: 'Valor',
  },
  {
    key: 'medidas-secundarias',
    label: 'Medidas secundarias',
    endpoint: '/medidas-secundarias/',
    campo: 'valor',
    label: 'Valor',
  },
  {
    key: 'codigos-uno',
    label: 'Códigos (prefijo)',
    endpoint: '/codigos-uno/',
    campo: 'valor',
    label: 'Valor',
  },
  {
    key: 'codigos-dos',
    label: 'Códigos (sufijo)',
    endpoint: '/codigos-dos/',
    campo: 'valor',
    label: 'Valor',
  },
])

const tabActiva = ref('categorias')
const tabActual = computed(() => tabs.value.find((t) => t.key === tabActiva.value))
</script>

<style scoped>
h2 { margin-bottom: 1rem; }

.tabs {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tab {
  padding: 0.4rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.875rem;
  color: #475569;
}

.tab.activo {
  background: #1e293b;
  color: white;
  border-color: #1e293b;
}
</style>
