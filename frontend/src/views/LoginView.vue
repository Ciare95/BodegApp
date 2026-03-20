<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-header">
        <span class="login-icon">⬡</span>
        <h1>BodegApp</h1>
        <p class="login-sub">Gestión de inventario de bodega</p>
      </div>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="field">
          <label for="username">Usuario</label>
          <input
            id="username"
            v-model="username"
            type="text"
            autocomplete="username"
            placeholder="tu_usuario"
          />
          <span v-if="errorUsername" class="field-error">El usuario es requerido</span>
        </div>

        <div class="field">
          <label for="password">Contraseña</label>
          <input
            id="password"
            v-model="password"
            type="password"
            required
            autocomplete="current-password"
            placeholder="••••••••"
          />
        </div>

        <p v-if="error" class="error-msg">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ error }}
        </p>

        <button type="submit" class="btn-submit" :disabled="cargando">
          <span v-if="cargando" class="spinner"></span>
          {{ cargando ? 'Ingresando...' : 'Ingresar' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const username = ref('')
const password = ref('')
const error = ref('')
const errorUsername = ref(false)
const cargando = ref(false)

async function handleLogin() {
  error.value = ''
  errorUsername.value = false
  if (!username.value.trim()) {
    errorUsername.value = true
    return
  }
  cargando.value = true
  try {
    await auth.login(username.value.trim(), password.value)
    router.push('/')
  } catch (e) {
    error.value = e.response?.status === 401
      ? 'Usuario o contraseña incorrectos'
      : (e.response?.data?.detail || 'Error al iniciar sesión')
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
  background: var(--bg);
  padding: 1.5rem;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 2.5rem 2rem;
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.login-icon {
  display: block;
  font-size: 2rem;
  margin-bottom: 0.75rem;
  color: var(--ink);
}

h1 {
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.03em;
  color: var(--ink);
  margin-bottom: 0.25rem;
}

.login-sub {
  font-size: 0.8125rem;
  color: var(--ink-3);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-2);
}

input {
  padding: 0.5625rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  font-size: 0.9375rem;
  color: var(--ink);
  background: var(--surface);
  transition: border-color var(--t), box-shadow var(--t);
  outline: none;
}

input::placeholder { color: var(--ink-4); }

input:focus {
  border-color: var(--ink);
  box-shadow: 0 0 0 3px rgba(17,17,17,0.06);
}

.field-error {
  font-size: 0.75rem;
  color: var(--rojo);
}

.error-msg {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--rojo);
  background: var(--rojo-bg);
  border: 1px solid var(--rojo-bd);
  padding: 0.5rem 0.75rem;
  border-radius: var(--r-md);
}

.btn-submit {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem;
  background: var(--ink);
  color: var(--accent-fg);
  border: none;
  border-radius: var(--r-md);
  font-size: 0.9375rem;
  font-weight: 500;
  transition: opacity var(--t), transform var(--t);
  margin-top: 0.25rem;
}

.btn-submit:hover:not(:disabled) { opacity: 0.85; }
.btn-submit:active:not(:disabled) { transform: scale(0.99); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }

.spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }
</style>
