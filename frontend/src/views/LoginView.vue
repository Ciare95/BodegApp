<template>
  <div class="login-page">
    <form class="login-form" @submit.prevent="handleLogin">
      <h1>BodegApp</h1>

      <div class="field">
        <label for="email">Correo</label>
        <input id="email" v-model="email" type="email" required autocomplete="email" />
      </div>

      <div class="field">
        <label for="password">Contraseña</label>
        <input id="password" v-model="password" type="password" required autocomplete="current-password" />
      </div>

      <p v-if="error" class="error">{{ error }}</p>

      <button type="submit" :disabled="cargando">
        {{ cargando ? 'Ingresando...' : 'Ingresar' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const email = ref('')
const password = ref('')
const error = ref('')
const cargando = ref(false)

async function handleLogin() {
  error.value = ''
  cargando.value = true
  try {
    await auth.login(email.value, password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Credenciales incorrectas'
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f1f5f9;
}

.login-form {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 360px;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

h1 {
  text-align: center;
  margin: 0 0 0.5rem;
  color: #1e293b;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

label {
  font-size: 0.875rem;
  color: #475569;
}

input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  font-size: 1rem;
}

input:focus {
  outline: none;
  border-color: #3b82f6;
}

.error {
  color: #ef4444;
  font-size: 0.875rem;
  margin: 0;
}

button {
  padding: 0.6rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
