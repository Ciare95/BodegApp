<template>
  <div>
    <div class="toolbar">
      <h2>Usuarios</h2>
      <button class="btn-primary" @click="abrirNuevo">+ Nuevo usuario</button>
    </div>

    <table class="tabla">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Correo</th>
          <th>Rol</th>
          <th>Creado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="u in usuarios" :key="u.id">
          <td>{{ u.nombre }}</td>
          <td>{{ u.email }}</td>
          <td><span :class="['badge-rol', u.rol]">{{ u.rol }}</span></td>
          <td>{{ formatFecha(u.creado_en) }}</td>
          <td>
            <button class="btn-link danger" @click="eliminar(u)" :disabled="u.id === auth.usuario?.id">
              Eliminar
            </button>
          </td>
        </tr>
        <tr v-if="!usuarios.length">
          <td colspan="5" class="vacio">Sin usuarios</td>
        </tr>
      </tbody>
    </table>

    <p v-if="error" class="error">{{ error }}</p>

    <!-- Modal nuevo usuario -->
    <div v-if="mostrarModal" class="overlay" @click.self="mostrarModal = false">
      <form class="modal" @submit.prevent="crear">
        <h3>Nuevo usuario</h3>

        <div class="field">
          <label>Nombre</label>
          <input v-model="form.nombre" required />
        </div>
        <div class="field">
          <label>Correo</label>
          <input v-model="form.email" type="email" required />
        </div>
        <div class="field">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" required />
        </div>
        <div class="field">
          <label>Rol</label>
          <select v-model="form.rol">
            <option value="empleado">Empleado</option>
            <option value="admin">Admin</option>
          </select>
        </div>

        <p v-if="errorModal" class="error">{{ errorModal }}</p>

        <div class="modal-acciones">
          <button type="button" @click="mostrarModal = false">Cancelar</button>
          <button type="submit" class="btn-primary" :disabled="guardando">
            {{ guardando ? 'Creando...' : 'Crear' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import client from '@/api/client'

const auth = useAuthStore()
const usuarios = ref([])
const error = ref('')
const errorModal = ref('')
const mostrarModal = ref(false)
const guardando = ref(false)

const form = reactive({ nombre: '', email: '', password: '', rol: 'empleado' })

function formatFecha(fecha) {
  return new Date(fecha).toLocaleDateString('es-CO')
}

async function cargar() {
  const { data } = await client.get('/usuarios/')
  usuarios.value = data.results ?? data
}

function abrirNuevo() {
  Object.assign(form, { nombre: '', email: '', password: '', rol: 'empleado' })
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
  if (!window.confirm(`¿Eliminar usuario "${u.nombre}"?`)) return
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
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

h2 { margin: 0; }

.tabla {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.tabla th, .tabla td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #e2e8f0;
  text-align: left;
}

.tabla th { background: #f8fafc; font-weight: 600; }

.badge-rol {
  padding: 0.15rem 0.5rem;
  border-radius: 3px;
  font-size: 0.8rem;
  text-transform: capitalize;
}

.badge-rol.admin { background: #dbeafe; color: #1e40af; }
.badge-rol.empleado { background: #f1f5f9; color: #475569; }

.btn-primary {
  padding: 0.4rem 0.8rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.875rem;
}

.btn-link {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0;
}

.btn-link.danger { color: #ef4444; }
.btn-link:disabled { opacity: 0.4; cursor: not-allowed; }

.vacio { text-align: center; color: #94a3b8; padding: 2rem; }

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
  width: 360px;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.modal h3 { margin: 0; }

.field { display: flex; flex-direction: column; gap: 0.25rem; }
label { font-size: 0.875rem; color: #475569; }

.modal input, .modal select {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 1rem;
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
