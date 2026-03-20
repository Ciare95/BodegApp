<template>
  <div>
    <div class="toolbar">
      <button class="btn-primary" @click="abrirNuevo">+ Agregar</button>
    </div>

    <table class="tabla">
      <thead>
        <tr>
          <th>ID</th>
          <th v-for="ce in camposExtra" :key="ce.key">{{ ce.label }}</th>
          <th>{{ label }}</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="item in items" :key="item.id">
          <td>{{ item.id }}</td>
          <td v-for="ce in camposExtra" :key="ce.key">{{ item[ce.key] }}</td>
          <td>
            <span v-if="editandoId !== item.id">{{ item[campo] }}</span>
            <input
              v-else
              v-model="editValor"
              @input="editValor = editValor.toUpperCase()"
              @keydown.enter="guardarEdicion(item)"
              @keydown.escape="cancelarEdicion"
            />
          </td>
          <td>
            <template v-if="editandoId !== item.id">
              <button class="btn-link" @click="iniciarEdicion(item)">Editar</button>
              <button class="btn-link danger" @click="eliminar(item)">Eliminar</button>
            </template>
            <template v-else>
              <button class="btn-link" @click="guardarEdicion(item)">Guardar</button>
              <button class="btn-link" @click="cancelarEdicion">Cancelar</button>
            </template>
          </td>
        </tr>
        <tr v-if="!items.length">
          <td :colspan="3 + camposExtra.length" class="vacio">Sin registros</td>
        </tr>
      </tbody>
    </table>

    <!-- Modal nuevo -->
    <div v-if="mostrarModal" class="overlay" @click.self="mostrarModal = false">
      <div class="modal">
        <h3>Agregar {{ label }}</h3>

        <!-- Campos extra requeridos para crear (ej: categoria_id en subcategoría) -->
        <template v-for="cc in camposCreacion" :key="cc.key">
          <label>{{ cc.label }}</label>
          <select v-model="nuevoExtra[cc.key]" required>
            <option value="">Seleccionar...</option>
            <option v-for="op in cc.opciones" :key="op.id" :value="op.id">{{ op.nombre ?? op.valor }}</option>
          </select>
        </template>

        <input
          v-model="nuevoValor"
          :placeholder="label"
          @input="nuevoValor = nuevoValor.toUpperCase()"
          @keydown.enter="crear"
        />
        <p v-if="errorModal" class="error">{{ errorModal }}</p>
        <div class="modal-acciones">
          <button @click="mostrarModal = false">Cancelar</button>
          <button class="btn-primary" @click="crear">Crear</button>
        </div>
      </div>
    </div>

    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import client from '@/api/client'

const props = defineProps({
  endpoint: { type: String, required: true },
  campo: { type: String, required: true },
  label: { type: String, required: true },
  camposExtra: { type: Array, default: () => [] },       // columnas extra en la tabla (solo lectura)
  camposCreacion: { type: Array, default: () => [] },    // campos extra requeridos al crear (ej: categoria_id)
})

const items = ref([])
const editandoId = ref(null)
const editValor = ref('')
const mostrarModal = ref(false)
const nuevoValor = ref('')
const nuevoExtra = ref({})
const error = ref('')
const errorModal = ref('')

async function cargar() {
  const { data } = await client.get(props.endpoint)
  items.value = data.results ?? data
}

function iniciarEdicion(item) {
  editandoId.value = item.id
  editValor.value = item[props.campo]
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
  if (!window.confirm(`¿Eliminar "${item[props.campo]}"?`)) return
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
</script>

<style scoped>
.toolbar { margin-bottom: 0.75rem; }

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tabla th, .tabla td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.tabla th { background: #f8fafc; font-weight: 600; }

.tabla input {
  padding: 0.3rem 0.5rem;
  border: 1px solid #3b82f6;
  border-radius: 3px;
  font-size: 0.9rem;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.875rem;
  margin-right: 0.5rem;
  padding: 0;
}

.btn-link.danger { color: #ef4444; }

.btn-primary {
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.vacio { text-align: center; color: #94a3b8; padding: 1.5rem; }

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.modal {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  width: 320px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal h3 { margin: 0; }

.modal input,
.modal select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 1rem;
  background: white;
}

.modal-acciones {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

.modal-acciones button {
  padding: 0.4rem 0.8rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  cursor: pointer;
  background: white;
}

.error { color: #ef4444; font-size: 0.875rem; margin: 0; }
</style>
