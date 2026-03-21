<template>
  <div class="tabla-catalogo">
    <div class="toolbar">
      <button class="btn-primary" @click="abrirNuevo">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Agregar {{ label }}
      </button>
    </div>

    <div class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th class="col-id">ID</th>
            <th v-for="ce in camposExtra" :key="ce.key">{{ ce.label }}</th>
            <th>{{ label }}</th>
            <th class="col-actions"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="col-id">{{ item.id }}</td>
            <td v-for="ce in camposExtra" :key="ce.key" class="col-extra">{{ item[ce.key] }}</td>
            <td class="col-valor">
              <span v-if="editandoId !== item.id" class="valor-text">{{ item[campo] }}</span>
              <input
                v-else
                v-model="editValor"
                class="edit-input"
                @input="editValor = editValor.toUpperCase()"
                @keydown.enter="guardarEdicion(item)"
                @keydown.escape="cancelarEdicion"
                ref="editInputRef"
              />
            </td>
            <td class="col-actions">
              <div class="row-actions">
                <template v-if="editandoId !== item.id">
                  <button class="btn-row" @click="iniciarEdicion(item)">Editar</button>
                  <button class="btn-row danger" @click="eliminar(item)">Eliminar</button>
                </template>
                <template v-else>
                  <button class="btn-row primary" @click="guardarEdicion(item)">Guardar</button>
                  <button class="btn-row" @click="cancelarEdicion">Cancelar</button>
                </template>
              </div>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td :colspan="3 + camposExtra.length" class="empty-state">Sin registros</td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="error" class="error-msg">
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      {{ error }}
    </p>

    <!-- Modal nuevo -->
    <Transition name="modal">
      <div v-if="mostrarModal" class="overlay" @click.self="mostrarModal = false">
        <div class="modal" @keydown.enter.prevent="crear">
          <div class="modal-header">
            <h2>Agregar {{ label }}</h2>
            <button class="btn-close" @click="mostrarModal = false">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <div class="modal-body">
            <template v-for="cc in camposCreacion" :key="cc.key">
              <div class="field">
                <label>{{ cc.label }}</label>
                <div class="select-wrap">
                  <select v-model="nuevoExtra[cc.key]" required>
                    <option value="">Seleccionar...</option>
                    <option v-for="op in cc.opciones" :key="op.id" :value="op.id">{{ op.nombre ?? op.valor }}</option>
                  </select>
                </div>
              </div>
            </template>

            <div class="field">
              <label>{{ label }}</label>
              <input
                ref="nuevoInputRef"
                v-model="nuevoValor"
                :placeholder="`Valor de ${label}...`"
                @input="nuevoValor = nuevoValor.toUpperCase()"
              />
            </div>

            <p v-if="errorModal" class="error-msg">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ errorModal }}
            </p>
          </div>

          <div class="modal-footer">
            <button class="btn-cancel" @click="mostrarModal = false">Cancelar</button>
            <button class="btn-save" @click="crear">Crear</button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, nextTick } from 'vue'
import { useConfirm } from '@/composables/useConfirm'
import client from '@/api/client'

const props = defineProps({
  endpoint: { type: String, required: true },
  campo: { type: String, required: true },
  label: { type: String, required: true },
  camposExtra: { type: Array, default: () => [] },
  camposCreacion: { type: Array, default: () => [] },
})

const items = ref([])
const editandoId = ref(null)
const editValor = ref('')
const editInputRef = ref(null)
const mostrarModal = ref(false)
const nuevoValor = ref('')
const nuevoExtra = ref({})
const nuevoInputRef = ref(null)
const error = ref('')
const errorModal = ref('')
const { showConfirm } = useConfirm()

async function cargar() {
  const { data } = await client.get(props.endpoint)
  items.value = data.results ?? data
}

function iniciarEdicion(item) {
  editandoId.value = item.id
  editValor.value = item[props.campo]
  nextTick(() => editInputRef.value?.focus())
}

function cancelarEdicion() {
  editandoId.value = null
  editValor.value = ''
}

async function guardarEdicion(item) {
  try {
    await client.patch(`${props.endpoint}${item.id}/`, { [props.campo]: editValor.value })
    cancelarEdicion()
    await cargar()
  } catch (e) {
    error.value = e.response?.data?.[props.campo]?.[0] || 'Error al guardar'
  }
}

async function eliminar(item) {
  if (!await showConfirm(`¿Eliminar "${item[props.campo]}"?`, 'Eliminar registro')) return
  try {
    await client.delete(`${props.endpoint}${item.id}/`)
    await cargar()
  } catch (e) {
    error.value = e.response?.data?.detail || 'No se puede eliminar: está referenciado por un producto'
  }
}

function abrirNuevo() {
  nuevoValor.value = ''
  nuevoExtra.value = {}
  errorModal.value = ''
  mostrarModal.value = true
}

async function crear() {
  errorModal.value = ''
  try {
    const payload = { [props.campo]: nuevoValor.value, ...nuevoExtra.value }
    await client.post(props.endpoint, payload)
    mostrarModal.value = false
    await cargar()
  } catch (e) {
    errorModal.value = e.response?.data?.[props.campo]?.[0]
      || e.response?.data?.categoria_id?.[0]
      || JSON.stringify(e.response?.data)
      || 'Error al crear'
  }
}

onMounted(cargar)
watch(() => props.endpoint, cargar)
watch(mostrarModal, (val) => {
  if (val) nextTick(() => nuevoInputRef.value?.focus())
})
</script>

<style scoped>
.tabla-catalogo { display: flex; flex-direction: column; gap: 1rem; }

.toolbar { display: flex; justify-content: flex-end; }

.btn-primary {
  display: inline-flex; align-items: center; gap: 0.375rem;
  padding: 0.4375rem 0.875rem; background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md); font-size: 0.8125rem; font-weight: 500;
  transition: opacity var(--t); cursor: pointer;
}
.btn-primary:hover { opacity: 0.82; }

.table-wrap {
  border: 1px solid var(--border); border-radius: var(--r-lg);
  overflow-x: auto; -webkit-overflow-scrolling: touch; background: var(--surface);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.tabla thead tr { border-bottom: 1px solid var(--border); }
.tabla th {
  padding: 0.625rem 1rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-3); text-align: left; background: var(--bg);
  letter-spacing: 0.02em; text-transform: uppercase;
}
.tabla td {
  padding: 0.6875rem 1rem; border-bottom: 1px solid var(--border);
  color: var(--ink-2); vertical-align: middle;
}
.tabla tbody tr:last-child td { border-bottom: none; }
.tabla tbody tr { transition: background var(--t); }
.tabla tbody tr:hover { background: var(--bg); }

.col-id { width: 60px; color: var(--ink-4); font-family: var(--font-mono); font-size: 0.75rem; }
.col-extra { color: var(--ink-3); }
.col-valor { color: var(--ink); font-weight: 500; }
.col-actions { width: 160px; }

.valor-text { font-family: var(--font-mono); font-size: 0.875rem; }

.edit-input {
  padding: 0.3125rem 0.5rem; border: 1px solid var(--ink);
  border-radius: var(--r-sm); font-size: 0.875rem; font-family: var(--font-mono);
  color: var(--ink); background: var(--surface); outline: none;
  box-shadow: 0 0 0 3px rgba(17,17,17,0.06);
}

.row-actions { display: flex; gap: 0.25rem; opacity: 0; transition: opacity var(--t); }
.tabla tbody tr:hover .row-actions { opacity: 1; }

.btn-row {
  padding: 0.25rem 0.625rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-2); background: var(--bg);
  border: 1px solid var(--border); border-radius: var(--r-sm);
  transition: all var(--t); cursor: pointer;
}
.btn-row:hover { color: var(--ink); border-color: var(--ink); background: var(--surface); }
.btn-row.danger:hover { color: var(--rojo); border-color: var(--rojo-bd); background: var(--rojo-bg); }
.btn-row.primary { background: var(--ink); color: var(--accent-fg); border-color: var(--ink); }
.btn-row.primary:hover { opacity: 0.82; }

.empty-state { text-align: center; padding: 3rem; color: var(--ink-4); font-size: 0.875rem; }

.error-msg {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--rojo);
  background: var(--rojo-bg); border: 1px solid var(--rojo-bd);
  padding: 0.5rem 0.75rem; border-radius: var(--r-md);
}

/* Modal */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}

.modal {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); width: 100%; max-width: 380px; overflow: hidden;
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

.modal-body {
  padding: 1.125rem 1.5rem;
  display: flex; flex-direction: column; gap: 0.75rem;
}

.field { display: flex; flex-direction: column; gap: 0.375rem; }
label { font-size: 0.8125rem; font-weight: 500; color: var(--ink-2); }

input {
  padding: 0.5rem 0.75rem; border: 1px solid var(--border);
  border-radius: var(--r-md); font-size: 0.9375rem; color: var(--ink);
  background: var(--surface); transition: border-color var(--t); outline: none;
}
input:focus { border-color: var(--ink); box-shadow: 0 0 0 3px rgba(17,17,17,0.06); }

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

.modal-footer {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 0.625rem; padding: 0.875rem 1.5rem;
  border-top: 1px solid var(--border); background: var(--bg);
}

.btn-cancel {
  padding: 0.4375rem 0.875rem; font-size: 0.875rem; font-weight: 500;
  color: var(--ink-2); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r-md);
  transition: all var(--t); cursor: pointer;
}
.btn-cancel:hover { color: var(--ink); border-color: var(--border-md); }

.btn-save {
  padding: 0.4375rem 1rem; font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md);
  transition: opacity var(--t); cursor: pointer;
}
.btn-save:hover { opacity: 0.82; }

.modal-enter-active, .modal-leave-active { transition: opacity 0.15s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 768px) {
  .row-actions { opacity: 1; }
  .col-id { display: none; }
  .overlay { align-items: flex-end; padding: 0; }
  .modal { max-width: 100%; border-radius: var(--r-lg) var(--r-lg) 0 0; }
}

@media (max-width: 480px) {
  .tabla th, .tabla td { padding: 0.5rem 0.75rem; }
  .modal-footer { flex-direction: column-reverse; }
  .btn-cancel, .btn-save { width: 100%; justify-content: center; }
}
</style>
