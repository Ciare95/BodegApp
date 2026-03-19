<template>
  <div class="form-page">
    <h2>{{ esEdicion ? 'Editar producto' : 'Nuevo producto' }}</h2>

    <form @submit.prevent="guardar" class="form">
      <!-- Categoría (solo para filtrar subcategorías) -->
      <div class="field">
        <label>Categoría</label>
        <select v-model="categoriaId" @change="onCategoriaChange">
          <option value="">Seleccionar...</option>
          <option v-for="c in catalogos.categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </div>

      <div class="field">
        <label>Subcategoría *</label>
        <select v-model="form.subcategoria" required>
          <option value="">Seleccionar...</option>
          <option v-for="s in subcategoriasFiltradas" :key="s.id" :value="s.id">{{ s.nombre }}</option>
        </select>
      </div>

      <div class="field">
        <label>Medida principal *</label>
        <select v-model="form.medida_principal" required>
          <option value="">Seleccionar...</option>
          <option v-for="m in catalogos.medidas_principales" :key="m.id" :value="m.id">{{ m.valor }}</option>
        </select>
      </div>

      <div class="field">
        <label>Medida secundaria</label>
        <select v-model="form.medida_secundaria">
          <option value="">Sin medida secundaria</option>
          <option v-for="m in catalogos.medidas_secundarias" :key="m.id" :value="m.id">{{ m.valor }}</option>
        </select>
      </div>

      <div class="field">
        <label>Código (prefijo) *</label>
        <select v-model="form.codigo_uno" required>
          <option value="">Seleccionar...</option>
          <option v-for="c in catalogos.codigos_uno" :key="c.id" :value="c.id">{{ c.valor }}</option>
        </select>
      </div>

      <div class="field">
        <label>Código (sufijo) *</label>
        <select v-model="form.codigo_dos" required>
          <option value="">Seleccionar...</option>
          <option v-for="c in catalogos.codigos_dos" :key="c.id" :value="c.id">{{ c.valor }}</option>
        </select>
      </div>

      <div class="field">
        <label>Estado *</label>
        <select v-model="form.estado" required>
          <option value="verde">Verde</option>
          <option value="amarillo">Amarillo</option>
          <option value="rojo">Rojo</option>
        </select>
      </div>

      <!-- Preview -->
      <div v-if="preview.nombre || preview.codigo" class="preview">
        <span class="preview-codigo">{{ preview.codigo }}</span>
        <span class="preview-nombre">{{ preview.nombre }}</span>
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <div class="form-acciones">
        <RouterLink to="/productos" class="btn-secondary">Cancelar</RouterLink>
        <button type="submit" class="btn-primary" :disabled="guardando">
          {{ guardando ? 'Guardando...' : 'Guardar' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'

const route = useRoute()
const router = useRouter()

const esEdicion = computed(() => !!route.params.id)

const form = reactive({
  subcategoria: '',
  medida_principal: '',
  medida_secundaria: '',
  codigo_uno: '',
  codigo_dos: '',
  estado: 'verde',
})

const catalogos = reactive({
  categorias: [],
  subcategorias: [],
  medidas_principales: [],
  medidas_secundarias: [],
  codigos_uno: [],
  codigos_dos: [],
})

const categoriaId = ref('')
const guardando = ref(false)
const error = ref('')

const subcategoriasFiltradas = computed(() => {
  if (!categoriaId.value) return catalogos.subcategorias
  return catalogos.subcategorias.filter((s) => s.categoria?.id === Number(categoriaId.value))
})

const preview = computed(() => {
  const sub = catalogos.subcategorias.find((s) => s.id === Number(form.subcategoria))
  const mp = catalogos.medidas_principales.find((m) => m.id === Number(form.medida_principal))
  const ms = catalogos.medidas_secundarias.find((m) => m.id === Number(form.medida_secundaria))
  const c1 = catalogos.codigos_uno.find((c) => c.id === Number(form.codigo_uno))
  const c2 = catalogos.codigos_dos.find((c) => c.id === Number(form.codigo_dos))

  const nombre = sub && mp
    ? `${sub.categoria?.nombre ?? ''} ${sub.nombre} ${mp.valor}${ms ? ' X ' + ms.valor : ''}`.trim()
    : ''
  const codigo = c1 && c2 ? `${c1.valor}-${c2.valor}` : ''

  return { nombre, codigo }
})

function onCategoriaChange() {
  form.subcategoria = ''
}

async function cargarCatalogos() {
  const endpoints = [
    ['categorias', '/categorias/'],
    ['subcategorias', '/subcategorias/'],
    ['medidas_principales', '/medidas-principales/'],
    ['medidas_secundarias', '/medidas-secundarias/'],
    ['codigos_uno', '/codigos-uno/'],
    ['codigos_dos', '/codigos-dos/'],
  ]
  await Promise.all(
    endpoints.map(async ([key, url]) => {
      const { data } = await client.get(url)
      catalogos[key] = data.results ?? data
    }),
  )
}

async function cargarProducto() {
  const { data } = await client.get(`/productos/${route.params.id}/`)
  form.subcategoria = data.subcategoria
  form.medida_principal = data.medida_principal
  form.medida_secundaria = data.medida_secundaria ?? ''
  form.codigo_uno = data.codigo_uno
  form.codigo_dos = data.codigo_dos
  form.estado = data.estado
  // Preseleccionar categoría usando el detalle anidado
  if (data.subcategoria_detalle) {
    categoriaId.value = data.subcategoria_detalle.categoria_id
  }
}

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const payload = {
      subcategoria: form.subcategoria,
      medida_principal: form.medida_principal,
      medida_secundaria: form.medida_secundaria || null,
      codigo_uno: form.codigo_uno,
      codigo_dos: form.codigo_dos,
      estado: form.estado,
    }
    if (esEdicion.value) {
      await client.put(`/productos/${route.params.id}/`, payload)
    } else {
      await client.post('/productos/', payload)
    }
    router.push('/productos')
  } catch (e) {
    const data = e.response?.data
    error.value = typeof data === 'string' ? data : JSON.stringify(data) || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarCatalogos()
  if (esEdicion.value) await cargarProducto()
})
</script>

<style scoped>
.form-page { max-width: 560px; }
h2 { margin-bottom: 1.5rem; }

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

label { font-size: 0.875rem; color: #475569; }

select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 1rem;
  background: white;
}

.preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: #f0fdf4;
  border: 1px solid #86efac;
  padding: 0.75rem 1rem;
  border-radius: 6px;
}

.preview-codigo {
  font-family: monospace;
  font-weight: bold;
  font-size: 1rem;
  background: #1e293b;
  color: white;
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
}

.preview-nombre { color: #166534; font-weight: 500; }

.error { color: #ef4444; font-size: 0.875rem; }

.form-acciones {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 0.5rem;
}

.btn-primary {
  padding: 0.5rem 1.2rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
  padding: 0.5rem 1.2rem;
  background: #e2e8f0;
  color: #1e293b;
  border-radius: 4px;
  text-decoration: none;
  font-size: 0.9rem;
}
</style>
