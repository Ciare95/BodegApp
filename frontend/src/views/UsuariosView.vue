<template>
  <div class="usuarios-page">
    <div class="page-header">
      <div class="page-title">
        <h1>Usuarios</h1>
        <span class="count-badge">{{ usuarios.length }}</span>
      </div>
      <button class="btn-primary" @click="abrirNuevo">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        Nuevo usuario
      </button>
    </div>

    <p v-if="error" class="error-msg">
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      {{ error }}
    </p>

    <div class="table-wrap">
      <table class="tabla">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Correo</th>
            <th>Rol</th>
            <th>Creado</th>
            <th class="col-actions"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in usuarios" :key="u.id">
            <td class="col-nombre">
              <div class="user-avatar">{{ u.nombre.charAt(0).toUpperCase() }}</div>
              {{ u.nombre }}
            </td>
            <td class="col-email">{{ u.email }}</td>
            <td>
              <span :class="['badge-rol', u.rol]">{{ u.rol }}</span>
            </td>
            <td class="col-fecha">{{ formatFecha(u.creado_en) }}</td>
            <td class="col-actions">
              <div class="row-actions">
                <button
                  class="btn-danger"
                  @click="eliminar(u)"
                  :disabled="u.id === auth.usuario?.id"
                  title="Eliminar usuario"
                >
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
                  Eliminar
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!usuarios.length">
            <td colspan="5" class="empty-state">Sin usuarios registrados</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal -->
    <Transition name="modal">
      <div v-if="mostrarModal" class="overlay" @click.self="mostrarModal = false">
        <form class="modal" @submit.prevent="crear">
          <div class="modal-header">
            <h2>Nuevo usuario</h2>
            <button type="button" class="btn-close" @click="mostrarModal = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="field">
              <label>Nombre</label>
              <input v-model="form.nombre" required placeholder="Nombre completo" />
            </div>
            <div class="field">
              <label>Usuario</label>
              <input v-model="form.username" required placeholder="nombre_usuario" />
            </div>
            <div class="field">
              <label>Correo electrónico</label>
              <input v-model="form.email" type="email" required placeholder="usuario@empresa.com" />
            </div>
            <div class="field">
              <label>Contraseña</label>
              <input v-model="form.password" type="password" required placeholder="••••••••" />
            </div>
            <div class="field">
              <label>Rol</label>
              <div class="rol-options">
                <label :class="['rol-option', { activo: form.rol === 'empleado' }]">
                  <input type="radio" v-model="form.rol" value="empleado" class="sr-only" />
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                  Empleado
                </label>
                <label :class="['rol-option', { activo: form.rol === 'admin' }]">
                  <input type="radio" v-model="form.rol" value="admin" class="sr-only" />
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                  Admin
                </label>
              </div>
            </div>

            <p v-if="errorModal" class="error-msg">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
              {{ errorModal }}
            </p>
          </div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="mostrarModal = false">Cancelar</button>
            <button type="submit" class="btn-save" :disabled="guardando">
              <span v-if="guardando" class="spinner"></span>
              {{ guardando ? 'Creando...' : 'Crear usuario' }}
            </button>
          </div>
        </form>
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useConfirm } from '@/composables/useConfirm'
import client from '@/api/client'

const auth = useAuthStore()
const { showConfirm } = useConfirm()
const usuarios = ref([])
const error = ref('')
const errorModal = ref('')
const mostrarModal = ref(false)
const guardando = ref(false)

const form = reactive({ nombre: '', username: '', email: '', password: '', rol: 'empleado' })

function formatFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-CO')
}

async function cargar() {
  const { data } = await client.get('/usuarios/')
  usuarios.value = data.results ?? data
}

function abrirNuevo() {
  Object.assign(form, { nombre: '', username: '', email: '', password: '', rol: 'empleado' })
  errorModal.value = ''
  mostrarModal.value = true
}

async function crear() {
  errorModal.value = ''
  guardando.value = true
  try {
    await client.post('/usuarios/registro/', form)
    mostrarModal.value = false
    await cargar()
  } catch (e) {
    const data = e.response?.data
    errorModal.value = typeof data === 'object' ? Object.values(data).flat().join(' ') : 'Error al crear'
  } finally {
    guardando.value = false
  }
}

async function eliminar(u) {
  if (!await showConfirm(`¿Eliminar usuario "${u.nombre}"?`, 'Eliminar usuario')) return
  try {
    await client.delete(`/usuarios/${u.id}/`)
    await cargar()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Error al eliminar'
  }
}

onMounted(cargar)
</script>

<style scoped>
.usuarios-page { display: flex; flex-direction: column; gap: 1.5rem; }

.page-header {
  display: flex; align-items: center;
  justify-content: space-between; gap: 1rem;
}

.page-title { display: flex; align-items: baseline; gap: 0.625rem; }

h1 {
  font-size: 1.375rem; font-weight: 600;
  letter-spacing: -0.03em; color: var(--ink);
}

.count-badge {
  font-size: 0.75rem; font-weight: 500; color: var(--ink-3);
  background: var(--bg); border: 1px solid var(--border);
  padding: 0.125rem 0.5rem; border-radius: 99px;
}

.btn-primary {
  display: inline-flex; align-items: center; gap: 0.375rem;
  padding: 0.4375rem 0.875rem; background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md); font-size: 0.8125rem; font-weight: 500;
  transition: opacity var(--t); cursor: pointer;
}
.btn-primary:hover { opacity: 0.82; }

.error-msg {
  display: flex; align-items: center; gap: 0.375rem;
  font-size: 0.8125rem; color: var(--rojo);
  background: var(--rojo-bg); border: 1px solid var(--rojo-bd);
  padding: 0.5rem 0.75rem; border-radius: var(--r-md);
}

/* Table */
.table-wrap {
  border: 1px solid var(--border); border-radius: var(--r-lg);
  overflow: hidden; background: var(--surface);
}

.tabla { width: 100%; border-collapse: collapse; font-size: 0.875rem; }

.tabla thead tr { border-bottom: 1px solid var(--border); }

.tabla th {
  padding: 0.625rem 1rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-3); text-align: left; background: var(--bg);
  letter-spacing: 0.02em; text-transform: uppercase;
}

.tabla td {
  padding: 0.75rem 1rem; border-bottom: 1px solid var(--border);
  color: var(--ink-2); vertical-align: middle;
}

.tabla tbody tr:last-child td { border-bottom: none; }
.tabla tbody tr { transition: background var(--t); }
.tabla tbody tr:hover { background: var(--bg); }

.col-nombre {
  display: flex; align-items: center; gap: 0.625rem;
  color: var(--ink); font-weight: 500;
}

.user-avatar {
  width: 28px; height: 28px; border-radius: 50%;
  background: var(--ink); color: var(--accent-fg);
  font-size: 0.75rem; font-weight: 600;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}

.col-email { color: var(--ink-3); font-size: 0.8125rem; }
.col-fecha { color: var(--ink-3); font-size: 0.8125rem; }

.badge-rol {
  display: inline-block; padding: 0.1875rem 0.5rem;
  border-radius: var(--r-sm); font-size: 0.75rem; font-weight: 500;
  text-transform: capitalize;
}
.badge-rol.admin { background: var(--ink); color: var(--accent-fg); }
.badge-rol.empleado { background: var(--bg); color: var(--ink-2); border: 1px solid var(--border); }

.col-actions { width: 100px; }

.row-actions { opacity: 0; transition: opacity var(--t); }
.tabla tbody tr:hover .row-actions { opacity: 1; }

.btn-danger {
  display: inline-flex; align-items: center; gap: 0.3125rem;
  padding: 0.25rem 0.625rem; font-size: 0.75rem; font-weight: 500;
  color: var(--ink-3); background: none;
  border: 1px solid var(--border); border-radius: var(--r-sm);
  transition: all var(--t); cursor: pointer;
}
.btn-danger:hover:not(:disabled) { color: var(--rojo); border-color: var(--rojo-bd); background: var(--rojo-bg); }
.btn-danger:disabled { opacity: 0.3; cursor: not-allowed; }

.empty-state { text-align: center; padding: 3rem; color: var(--ink-4); font-size: 0.875rem; }

/* Modal */
.overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.35);
  display: flex; align-items: center; justify-content: center;
  z-index: 200; padding: 1rem;
}

.modal {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); width: 100%; max-width: 400px;
  overflow: hidden;
}

.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.25rem 1.5rem; border-bottom: 1px solid var(--border);
}

.modal-header h2 {
  font-size: 1rem; font-weight: 600; letter-spacing: -0.02em; color: var(--ink);
}

.btn-close {
  display: flex; align-items: center; justify-content: center;
  width: 28px; height: 28px; color: var(--ink-3); background: none;
  border: none; border-radius: var(--r-sm); transition: all var(--t); cursor: pointer;
}
.btn-close:hover { color: var(--ink); background: var(--bg); }

.modal-body {
  padding: 1.25rem 1.5rem;
  display: flex; flex-direction: column; gap: 0.875rem;
}

.field { display: flex; flex-direction: column; gap: 0.375rem; }

label {
  font-size: 0.8125rem; font-weight: 500; color: var(--ink-2);
}

input {
  padding: 0.5rem 0.75rem; border: 1px solid var(--border);
  border-radius: var(--r-md); font-size: 0.9375rem; color: var(--ink);
  background: var(--surface); transition: border-color var(--t); outline: none;
}
input::placeholder { color: var(--ink-4); }
input:focus { border-color: var(--ink); box-shadow: 0 0 0 3px rgba(17,17,17,0.06); }

.rol-options { display: flex; gap: 0.5rem; }

.rol-option {
  display: flex; align-items: center; gap: 0.375rem;
  padding: 0.4375rem 0.875rem; font-size: 0.875rem; font-weight: 500;
  border: 1px solid var(--border); border-radius: var(--r-md);
  cursor: pointer; transition: all var(--t); color: var(--ink-3);
  background: var(--surface);
}
.rol-option:hover { color: var(--ink); border-color: var(--border-md); }
.rol-option.activo { background: var(--ink); color: var(--accent-fg); border-color: var(--ink); }

.modal-footer {
  display: flex; align-items: center; justify-content: flex-end;
  gap: 0.625rem; padding: 1rem 1.5rem;
  border-top: 1px solid var(--border); background: var(--bg);
}

.btn-cancel {
  padding: 0.5rem 1rem; font-size: 0.875rem; font-weight: 500;
  color: var(--ink-2); background: var(--surface);
  border: 1px solid var(--border); border-radius: var(--r-md);
  transition: all var(--t); cursor: pointer;
}
.btn-cancel:hover { color: var(--ink); border-color: var(--border-md); }

.btn-save {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1.25rem; font-size: 0.875rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  border: none; border-radius: var(--r-md);
  transition: opacity var(--t); cursor: pointer;
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

/* Transition */
.modal-enter-active, .modal-leave-active { transition: opacity 0.15s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; }

/* Responsive */
@media (max-width: 768px) {
  .table-wrap { overflow-x: auto; -webkit-overflow-scrolling: touch; }
  .col-email, .col-fecha { display: none; }
  .row-actions { opacity: 1; }
  .overlay { align-items: flex-end; padding: 0; }
  .modal { max-width: 100%; border-radius: var(--r-lg) var(--r-lg) 0 0; }
}

@media (max-width: 480px) {
  .page-header { flex-direction: column; align-items: flex-start; }
  .btn-primary { width: 100%; justify-content: center; }
  .rol-options { flex-direction: column; }
  .rol-option { justify-content: center; }
  .modal-footer { flex-direction: column-reverse; }
  .btn-cancel, .btn-save { width: 100%; justify-content: center; }
}
</style>
