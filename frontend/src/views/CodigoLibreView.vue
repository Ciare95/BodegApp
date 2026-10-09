<template>
  <div class="cl-page">
    <div class="page-header">
      <h1>Código libre</h1>
      <button v-if="!modoAgregar" class="btn-primary" @click="iniciarAgregar">
        + Agregar código
      </button>
    </div>

    <!-- Formulario agregar -->
    <div v-if="modoAgregar" class="form-inline">
      <h2 class="form-titulo">Agregar código libre</h2>
      <div class="form-fila">
        <label>Prefijo</label>
        <select v-model="form.codigo_uno" class="select-field">
          <option value="" disabled>Seleccionar…</option>
          <option v-for="cu in codigos_uno" :key="cu.id" :value="cu.id">{{ cu.valor }}</option>
        </select>
        <label>Sufijo</label>
        <select v-model="form.codigo_dos" class="select-field">
          <option value="" disabled>Seleccionar…</option>
          <option v-for="cd in codigos_dos" :key="cd.id" :value="cd.id">{{ cd.valor }}</option>
        </select>
        <div class="form-acciones">
          <button class="btn-primary" :disabled="!form.codigo_uno || !form.codigo_dos || guardando" @click="guardar">
            Guardar
          </button>
          <button class="btn-secundario" @click="cancelar">Cancelar</button>
        </div>
      </div>
      <p v-if="errorForm" class="error-msg">{{ errorForm }}</p>
    </div>

    <div v-if="cargando" class="estado-msg">Cargando…</div>
    <div v-else-if="error" class="estado-msg error">{{ error }}</div>
    <div v-else-if="codigosLibres.length === 0 && !modoAgregar" class="estado-msg">
      No hay códigos libres registrados.
    </div>

    <div v-else-if="codigosLibres.length > 0" class="tabla-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Código</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="cl in codigosLibres" :key="cl.id">
            <template v-if="editandoId === cl.id">
              <td>
                <div class="edit-fila">
                  <select v-model="formEditar.codigo_uno" class="select-field-sm">
                    <option v-for="cu in codigos_uno" :key="cu.id" :value="cu.id">{{ cu.valor }}</option>
                  </select>
                  <span class="guion">-</span>
                  <select v-model="formEditar.codigo_dos" class="select-field-sm">
                    <option v-for="cd in codigos_dos" :key="cd.id" :value="cd.id">{{ cd.valor }}</option>
                  </select>
                  <p v-if="errorEditar" class="error-msg-inline">{{ errorEditar }}</p>
                </div>
              </td>
              <td class="acciones">
                <button class="btn-mini btn-ok" :disabled="guardando" @click="guardarEdicion(cl)">Guardar</button>
                <button class="btn-mini" @click="cancelarEdicion">Cancelar</button>
              </td>
            </template>
            <template v-else>
              <td class="codigo-text">{{ cl.codigo_uno_valor }}-{{ cl.codigo_dos_valor }}</td>
              <td class="acciones">
                <button class="btn-mini" @click="iniciarEdicion(cl)">Editar</button>
                <button class="btn-mini btn-danger" @click="eliminar(cl)">Eliminar</button>
              </td>
            </template>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import client from '@/api/client'

const codigosLibres = ref([])
const codigos_uno = ref([])
const codigos_dos = ref([])
const cargando = ref(true)
const error = ref(null)

const modoAgregar = ref(false)
const form = ref({ codigo_uno: '', codigo_dos: '' })
const errorForm = ref(null)
const guardando = ref(false)

const editandoId = ref(null)
const formEditar = ref({ codigo_uno: null, codigo_dos: null })
const errorEditar = ref(null)

function sortKey(valor) {
  return /^\d+$/.test(valor)
    ? [1, parseInt(valor, 10), '']
    : [0, 0, valor.toUpperCase()]
}

function ordenar(lista) {
  return [...lista].sort((a, b) => {
    const ka = sortKey(a.codigo_uno_valor)
    const kb = sortKey(b.codigo_uno_valor)
    if (ka[0] !== kb[0]) return ka[0] - kb[0]
    const cmpUno = ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
    if (cmpUno !== 0) return cmpUno
    const kda = sortKey(a.codigo_dos_valor)
    const kdb = sortKey(b.codigo_dos_valor)
    if (kda[0] !== kdb[0]) return kda[0] - kdb[0]
    return kda[0] === 1 ? kda[1] - kdb[1] : kda[2].localeCompare(kdb[2])
  })
}

async function cargar() {
  try {
    const [resLibres, resUno, resDos] = await Promise.all([
      client.get('/codigos-libres/'),
      client.get('/codigos-uno/'),
      client.get('/codigos-dos/'),
    ])
    const libres = resLibres.data.results ?? resLibres.data
    codigosLibres.value = ordenar(libres)
    codigos_uno.value = (resUno.data.results ?? resUno.data).sort((a, b) => {
      const ka = sortKey(a.valor), kb = sortKey(b.valor)
      if (ka[0] !== kb[0]) return ka[0] - kb[0]
      return ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
    })
    codigos_dos.value = (resDos.data.results ?? resDos.data).sort((a, b) => {
      const ka = sortKey(a.valor), kb = sortKey(b.valor)
      if (ka[0] !== kb[0]) return ka[0] - kb[0]
      return ka[0] === 1 ? ka[1] - kb[1] : ka[2].localeCompare(kb[2])
    })
  } catch {
    error.value = 'No se pudieron cargar los códigos libres.'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)

function iniciarAgregar() {
  modoAgregar.value = true
  form.value = { codigo_uno: '', codigo_dos: '' }
  errorForm.value = null
}

function cancelar() {
  modoAgregar.value = false
  errorForm.value = null
}

async function guardar() {
  if (!form.value.codigo_uno || !form.value.codigo_dos) return
  guardando.value = true
  errorForm.value = null
  try {
    const { data } = await client.post('/codigos-libres/', {
      codigo_uno: form.value.codigo_uno,
      codigo_dos: form.value.codigo_dos,
    })
    codigosLibres.value = ordenar([...codigosLibres.value, data])
    modoAgregar.value = false
  } catch (e) {
    errorForm.value = e.response?.data?.detail ?? 'Error al guardar el código libre.'
  } finally {
    guardando.value = false
  }
}

function iniciarEdicion(cl) {
  editandoId.value = cl.id
  formEditar.value = { codigo_uno: cl.codigo_uno, codigo_dos: cl.codigo_dos }
  errorEditar.value = null
}

function cancelarEdicion() {
  editandoId.value = null
  errorEditar.value = null
}

async function guardarEdicion(cl) {
  guardando.value = true
  errorEditar.value = null
  try {
    const { data } = await client.patch(`/codigos-libres/${cl.id}/`, {
      codigo_uno: formEditar.value.codigo_uno,
      codigo_dos: formEditar.value.codigo_dos,
    })
    const idx = codigosLibres.value.findIndex(c => c.id === cl.id)
    if (idx !== -1) {
      const actualizada = [...codigosLibres.value]
      actualizada[idx] = data
      codigosLibres.value = ordenar(actualizada)
    }
    editandoId.value = null
  } catch (e) {
    errorEditar.value = e.response?.data?.detail ?? 'Error al editar el código libre.'
  } finally {
    guardando.value = false
  }
}

async function eliminar(cl) {
  if (!confirm(`¿Eliminar el código libre ${cl.codigo_uno_valor}-${cl.codigo_dos_valor}?`)) return
  try {
    await client.delete(`/codigos-libres/${cl.id}/`)
    codigosLibres.value = codigosLibres.value.filter(c => c.id !== cl.id)
  } catch {
    alert('No se pudo eliminar el código libre.')
  }
}
</script>

<style scoped>
.cl-page {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--ink);
}

.form-inline {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-titulo {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.form-fila {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.form-fila label {
  font-size: 0.8125rem;
  color: var(--ink-2);
}

.select-field {
  padding: 0.35rem 0.6rem;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  background: var(--bg);
  color: var(--ink);
}

.form-acciones {
  display: flex;
  gap: 0.5rem;
  margin-left: 0.5rem;
}

.estado-msg {
  color: var(--ink-3);
  font-size: 0.9rem;
  padding: 2rem 0;
  text-align: center;
}
.estado-msg.error { color: var(--rojo); }

.error-msg {
  color: var(--rojo);
  font-size: 0.8rem;
  margin: 0;
}

.tabla-wrap { overflow-x: auto; }

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tabla th {
  text-align: left;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--ink-3);
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0 0.75rem 0.5rem;
  border-bottom: 1px solid var(--border);
}

.tabla td {
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid var(--border);
  vertical-align: middle;
}

.tabla tr:last-child td { border-bottom: none; }
.tabla tr:hover td { background: var(--bg); }

.codigo-text {
  font-family: monospace;
  font-weight: 600;
  color: var(--ink);
  letter-spacing: 0.03em;
}

.acciones {
  display: flex;
  gap: 0.4rem;
  width: 160px;
}

.btn-primary {
  padding: 0.4rem 0.9rem;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--ink);
  color: var(--bg);
  border: none;
  border-radius: var(--r-md);
  cursor: pointer;
  transition: opacity var(--t);
}
.btn-primary:hover { opacity: 0.85; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-secundario {
  padding: 0.4rem 0.9rem;
  font-size: 0.8125rem;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  cursor: pointer;
  color: var(--ink-2);
  transition: background var(--t);
}
.btn-secundario:hover { background: var(--bg); }

.btn-mini {
  padding: 0.2rem 0.6rem;
  font-size: 0.75rem;
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  cursor: pointer;
  color: var(--ink-2);
  transition: background var(--t);
  white-space: nowrap;
}
.btn-mini:hover { background: var(--bg); color: var(--ink); }
.btn-mini.btn-danger:hover { background: #fee2e2; color: var(--rojo); border-color: var(--rojo); }
.btn-mini.btn-ok { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.btn-mini.btn-ok:hover { opacity: 0.85; }
.btn-mini:disabled { opacity: 0.5; cursor: not-allowed; }

.edit-fila {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  flex-wrap: wrap;
}

.select-field-sm {
  padding: 0.2rem 0.4rem;
  font-size: 0.8125rem;
  border: 1px solid var(--border);
  border-radius: var(--r-sm, 4px);
  background: var(--bg);
  color: var(--ink);
}

.guion {
  font-weight: 600;
  color: var(--ink-2);
}

.error-msg-inline {
  font-size: 0.75rem;
  color: var(--rojo);
  margin: 0;
  width: 100%;
}
</style>
