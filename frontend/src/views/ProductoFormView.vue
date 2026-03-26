<template>
  <div class="form-page">
    <button class="back-link" @click="volver">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"/></svg>
      {{ volverLabel }}
    </button>

    <div class="form-header">
      <h1>{{ esEdicion ? 'Editar producto' : 'Nuevo producto' }}</h1>
      <div v-if="previewNombre" class="preview-badge">
        <span class="preview-label">Vista previa</span>
        <span class="preview-nombre">{{ previewNombre }}</span>
      </div>
    </div>

    <form @submit.prevent="guardar" class="form-card">
      <div class="form-section">
        <h2 class="section-title">Clasificación</h2>
        <div class="fields-grid">
          <div class="field">
            <label>Categoría</label>
            <div v-if="contextoFijo" class="valor-fijo">{{ nombreCategoriaFija }}</div>
            <div v-else class="select-wrap">
              <select v-model="categoriaId" @change="onCategoriaChange">
                <option value="">Seleccionar...</option>
                <option v-for="c in catalogos.categorias" :key="c.id" :value="c.id">{{ c.nombre }}</option>
              </select>
            </div>
          </div>
          <div class="field">
            <label>Subcategoría <span class="req">*</span></label>
            <div v-if="contextoFijo" class="valor-fijo">{{ nombreSubcategoriaFija }}</div>
            <div v-else class="select-wrap">
              <select v-model="form.subcategoria" required>
                <option value="">Seleccionar...</option>
                <option v-for="s in subcategoriasFiltradas" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h2 class="section-title">Medidas</h2>
        <div class="fields-grid">
          <div class="field">
            <label>Medida principal <span class="req">*</span></label>
            <div class="select-wrap">
              <select v-model="form.medida_principal" required>
                <option value="">Seleccionar...</option>
                <option v-for="m in catalogos.medidas_principales" :key="m.id" :value="m.id">{{ m.valor }}</option>
              </select>
            </div>
          </div>
          <div class="field">
            <label>Medida secundaria</label>
            <div class="select-wrap">
              <select v-model="form.medida_secundaria">
                <option value="">Sin medida secundaria</option>
                <option v-for="m in catalogos.medidas_secundarias" :key="m.id" :value="m.id">{{ m.valor }}</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <div class="form-section">
        <h2 class="section-title">Código</h2>
        <div class="codigo-row">
          <div class="select-wrap">
            <select v-model="form.codigo_uno">
              <option value="">Prefijo...</option>
              <option v-for="c in catalogos.codigos_uno" :key="c.id" :value="c.id">{{ c.valor }}</option>
            </select>
          </div>
          <span class="sep">—</span>
          <div class="select-wrap">
            <select v-model="form.codigo_dos">
              <option value="">Sufijo...</option>
              <option v-for="c in catalogos.codigos_dos" :key="c.id" :value="c.id">{{ c.valor }}</option>
            </select>
          </div>
          <span v-if="previewCodigo" class="codigo-preview-tag">{{ previewCodigo }}</span>
          <button
            v-if="form.codigo_uno || form.codigo_dos"
            type="button"
            class="btn-clear-code"
            title="Quitar código"
            @click="limpiarCodigo"
          >
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
      </div>

      <div class="form-section">
        <h2 class="section-title">Estado</h2>
        <div class="estado-options">
          <label
            v-for="op in estadoOpciones"
            :key="op.valor"
            :class="['estado-option', op.valor, { activo: form.estado === op.valor }]"
          >
            <input type="radio" v-model="form.estado" :value="op.valor" class="sr-only" />
            <span class="dot"></span>
            {{ op.label }}
          </label>
        </div>
      </div>

      <div v-if="error" class="error-msg">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ error }}
      </div>

      <div class="form-footer">
        <button type="button" class="btn-cancel" @click="volver">Cancelar</button>
        <button type="submit" class="btn-save" :disabled="guardando">
          <span v-if="guardando" class="spinner"></span>
          {{ guardando ? 'Guardando...' : 'Guardar producto' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import client from '@/api/client'

const route = useRoute()
const router = useRouter()
const esEdicion = computed(() => !!route.params.id)

// Query params de contexto (vienen de ProductosView)
const qCatId = Number(route.query.categoria_id) || null
const qSubId = Number(route.query.subcategoria_id) || null
const contextoFijo = computed(() => !esEdicion.value && !!qCatId && !!qSubId)

const form = reactive({
  subcategoria: '', medida_principal: '', medida_secundaria: '',
  estado: 'verde', codigo_uno: '', codigo_dos: '',
})

const catalogos = reactive({
  categorias: [], subcategorias: [], medidas_principales: [],
  medidas_secundarias: [], codigos_uno: [], codigos_dos: [],
})

const categoriaId = ref('')
const guardando = ref(false)
const error = ref('')

const estadoOpciones = [
  { valor: 'verde', label: 'Verde' },
  { valor: 'amarillo', label: 'Amarillo' },
  { valor: 'rojo', label: 'Rojo' },
]

const subcategoriasFiltradas = computed(() => {
  if (!categoriaId.value) return catalogos.subcategorias
  return catalogos.subcategorias.filter(s => s.categoria?.id === Number(categoriaId.value))
})

const nombreCategoriaFija = computed(() =>
  catalogos.categorias.find(c => c.id === qCatId)?.nombre ?? ''
)
const nombreSubcategoriaFija = computed(() =>
  catalogos.subcategorias.find(s => s.id === qSubId)?.nombre ?? ''
)

const volverLabel = computed(() => {
  if (qSubId) return nombreSubcategoriaFija.value || 'Volver'
  return 'Productos'
})

function volver() {
  const destino = (qCatId && qSubId)
    ? { name: 'productos', query: { categoria_id: qCatId, subcategoria_id: qSubId } }
    : { name: 'productos' }
  router.push(destino)
}

const previewNombre = computed(() => {
  const sub = catalogos.subcategorias.find(s => s.id === Number(form.subcategoria))
  const mp = catalogos.medidas_principales.find(m => m.id === Number(form.medida_principal))
  const ms = catalogos.medidas_secundarias.find(m => m.id === Number(form.medida_secundaria))
  if (!sub || !mp) return ''
  return `${sub.categoria?.nombre ?? ''} ${sub.nombre} ${mp.valor}${ms ? ' X ' + ms.valor : ''}`.trim()
})

const previewCodigo = computed(() => {
  const c1 = catalogos.codigos_uno.find(c => c.id === Number(form.codigo_uno))
  const c2 = catalogos.codigos_dos.find(c => c.id === Number(form.codigo_dos))
  return c1 && c2 ? `${c1.valor}-${c2.valor}` : ''
})

function onCategoriaChange() { form.subcategoria = '' }
function limpiarCodigo() { form.codigo_uno = ''; form.codigo_dos = '' }

async function cargarCatalogos() {
  const endpoints = [
    ['categorias', '/categorias/'], ['subcategorias', '/subcategorias/'],
    ['medidas_principales', '/medidas-principales/'], ['medidas_secundarias', '/medidas-secundarias/'],
    ['codigos_uno', '/codigos-uno/'], ['codigos_dos', '/codigos-dos/'],
  ]
  await Promise.all(endpoints.map(async ([key, url]) => {
    const { data } = await client.get(url)
    catalogos[key] = data.results ?? data
  }))
}

async function cargarProducto() {
  const { data } = await client.get(`/productos/${route.params.id}/`)
  form.subcategoria = data.subcategoria
  form.medida_principal = data.medida_principal
  form.medida_secundaria = data.medida_secundaria ?? ''
  form.estado = data.estado
  form.codigo_uno = data.codigo_uno ?? ''
  form.codigo_dos = data.codigo_dos ?? ''
  if (data.subcategoria_detalle) categoriaId.value = data.subcategoria_detalle.categoria_id
}

async function guardar() {
  error.value = ''
  guardando.value = true
  try {
    const payload = {
      subcategoria: form.subcategoria, medida_principal: form.medida_principal,
      medida_secundaria: form.medida_secundaria || null, estado: form.estado,
      codigo_uno: form.codigo_uno || null,
      codigo_dos: form.codigo_dos || null,
    }
    if (esEdicion.value) {
      await client.put(`/productos/${route.params.id}/`, payload)
    } else {
      await client.post('/productos/', payload)
    }
    volver()
  } catch (e) {
    const d = e.response?.data
    if (d?.detail) {
      error.value = d.detail
    } else if (d?.non_field_errors) {
      error.value = d.non_field_errors[0]
    } else if (typeof d === 'object' && d !== null) {
      const msgs = Object.values(d).flat()
      error.value = msgs[0] ?? 'Error al guardar'
    } else {
      error.value = 'Error al guardar'
    }
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  await cargarCatalogos()
  if (esEdicion.value) {
    await cargarProducto()
  } else if (contextoFijo.value) {
    // Preseleccionar categoría y subcategoría desde query params
    categoriaId.value = qCatId
    form.subcategoria = qSubId
  }
})
</script>

<style scoped>
.form-page { display: flex; flex-direction: column; gap: 1.5rem; max-width: 640px; margin: 0 auto; width: 100%; }

.back-link {
  display: inline-flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--ink-3);
  background: none; border: none; cursor: pointer;
  text-decoration: none; transition: color var(--t); padding: 0;
}
.back-link:hover { color: var(--ink); }

.form-header {
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: 1rem; flex-wrap: wrap;
}

h1 {
  font-size: 1.375rem; font-weight: 600;
  letter-spacing: -0.03em; color: var(--ink);
}

.preview-badge {
  display: flex; flex-direction: column; gap: 0.125rem;
  background: var(--verde-bg); border: 1px solid var(--verde-bd);
  padding: 0.5rem 0.875rem; border-radius: var(--r-md);
  max-width: 280px;
}
.preview-label {
  font-size: 0.625rem; font-weight: 600; color: var(--verde);
  text-transform: uppercase; letter-spacing: 0.08em;
}
.preview-nombre { font-size: 0.875rem; font-weight: 500; color: var(--ink); }

/* Form card */
.form-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); overflow: hidden;
}

.form-section {
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid var(--border);
}
.form-section:last-of-type { border-bottom: none; }

.section-title {
  font-size: 0.75rem; font-weight: 600; color: var(--ink-3);
  text-transform: uppercase; letter-spacing: 0.06em;
  margin-bottom: 0.875rem;
}

.section-header-row {
  display: flex; align-items: center;
  justify-content: space-between; margin-bottom: 0.875rem;
}
.section-header-row .section-title { margin-bottom: 0; }

.req { color: var(--rojo); }

.valor-fijo {
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--border); border-radius: var(--r-md);
  font-size: 0.9375rem; color: var(--ink);
  background: var(--bg); font-weight: 500;
}

.fields-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem;
}

@media (max-width: 480px) { .fields-grid { grid-template-columns: 1fr; } }

.field { display: flex; flex-direction: column; gap: 0.375rem; }

label {
  font-size: 0.8125rem; font-weight: 500; color: var(--ink-2);
}

.select-wrap { position: relative; }
.select-wrap::after {
  content: ''; position: absolute; right: 0.625rem; top: 50%;
  transform: translateY(-50%); width: 0; height: 0;
  border-left: 4px solid transparent; border-right: 4px solid transparent;
  border-top: 5px solid var(--ink-3); pointer-events: none;
}

select {
  appearance: none; width: 100%;
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid var(--border); border-radius: var(--r-md);
  font-size: 0.9375rem; color: var(--ink); background: var(--surface);
  cursor: pointer; transition: border-color var(--t); outline: none;
}
select:focus { border-color: var(--ink); }

/* Código */
.codigo-row {
  display: flex; align-items: center; gap: 0.5rem;
}
.codigo-row .select-wrap { flex: 1; }

.sep { font-size: 0.875rem; color: var(--ink-4); flex-shrink: 0; }

.codigo-preview-tag {
  font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  padding: 0.1875rem 0.5rem; border-radius: var(--r-sm);
  letter-spacing: 0.04em; white-space: nowrap; flex-shrink: 0;
}

.btn-clear-code {
  display: inline-flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; flex-shrink: 0;
  color: var(--ink-4); background: none;
  border: 1px solid transparent; border-radius: var(--r-sm);
  transition: all var(--t);
}
.btn-clear-code:hover { color: var(--rojo); background: var(--rojo-bg); border-color: var(--rojo-bd); }

/* Estado */
.estado-options { display: flex; gap: 0.5rem; }

.estado-option {
  display: flex; align-items: center; gap: 0.4375rem;
  padding: 0.4375rem 0.875rem; font-size: 0.875rem; font-weight: 500;
  border: 1px solid var(--border); border-radius: var(--r-md);
  cursor: pointer; transition: all var(--t); color: var(--ink-3);
  background: var(--surface);
}
.estado-option .dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.estado-option.verde .dot { background: var(--verde); }
.estado-option.amarillo .dot { background: var(--amarillo); }
.estado-option.rojo .dot { background: var(--rojo); }

.estado-option:hover { color: var(--ink); border-color: var(--border-md); }
.estado-option.verde.activo { background: var(--verde-bg); border-color: var(--verde-bd); color: var(--verde); }
.estado-option.amarillo.activo { background: var(--amarillo-bg); border-color: var(--amarillo-bd); color: var(--amarillo); }
.estado-option.rojo.activo { background: var(--rojo-bg); border-color: var(--rojo-bd); color: var(--rojo); }

/* Error */
.error-msg {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--rojo);
  background: var(--rojo-bg); border: 1px solid var(--rojo-bd);
  padding: 0.625rem 1.5rem; margin: 0 0 -1px;
}

/* Footer */
.form-footer {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 0.625rem; padding: 1rem 1.5rem;
  border-top: 1px solid var(--border); background: var(--bg);
}

.btn-cancel {
  padding: 0.5rem 1rem; font-size: 0.875rem; font-weight: 500;
  color: var(--ink-2); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r-md);
  text-decoration: none; transition: all var(--t);
}
.btn-cancel:hover { color: var(--ink); border-color: var(--border-md); }

.btn-save {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1.25rem; font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md);
  transition: opacity var(--t);
}
.btn-save:hover:not(:disabled) { opacity: 0.82; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 13px; height: 13px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white; border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Responsive ── */
@media (max-width: 768px) {
  .form-page { max-width: 100%; }
  .form-header { flex-direction: column; gap: 0.75rem; }
  .preview-badge { max-width: 100%; }
}

@media (max-width: 480px) {
  .fields-grid { grid-template-columns: 1fr; }
  .estado-options { flex-wrap: wrap; }
  .estado-option { flex: 1; justify-content: center; min-width: 80px; }
  .form-footer { flex-direction: column-reverse; }
  .btn-cancel, .btn-save { width: 100%; justify-content: center; text-align: center; }
}
</style>
