import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import client from '@/api/client'
import axios from 'axios'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem('access_token') || null)
  const refreshToken = ref(localStorage.getItem('refresh_token') || null)
  const usuario = ref(JSON.parse(localStorage.getItem('usuario') || 'null'))

  const estaAutenticado = computed(() => !!accessToken.value)
  const esAdmin = computed(() => usuario.value?.rol === 'admin')
  const esEmpleado = computed(() => usuario.value?.rol === 'empleado')

  async function login(username, password) {
    const { data } = await axios.post('/api/token/', { username, password })
    accessToken.value = data.access
    refreshToken.value = data.refresh
    localStorage.setItem('access_token', data.access)
    localStorage.setItem('refresh_token', data.refresh)
    await cargarPerfil()
  }

  async function cargarPerfil() {
    const { data } = await client.get('/usuarios/me/')
    usuario.value = data
    localStorage.setItem('usuario', JSON.stringify(data))
  }

  async function logout() {
    try {
      await client.post('/token/revocar/', { refresh: refreshToken.value })
    } catch {
      // ignorar error al revocar
    }
    accessToken.value = null
    refreshToken.value = null
    usuario.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('usuario')
  }

  return { accessToken, refreshToken, usuario, estaAutenticado, esAdmin, esEmpleado, login, logout, cargarPerfil }
})
