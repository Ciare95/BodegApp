<template>
  <div class="app-layout">
    <nav class="navbar">
      <div class="navbar-brand">BodegApp</div>

      <div class="navbar-search">
        <BuscadorGlobal />
      </div>

      <div class="navbar-menu">
        <RouterLink to="/productos">Productos</RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/catalogos">Catálogos</RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/usuarios">Usuarios</RouterLink>
        <button class="btn-logout" @click="cerrarSesion">Salir</button>
      </div>
    </nav>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import BuscadorGlobal from '@/components/BuscadorGlobal.vue'

const auth = useAuthStore()
const router = useRouter()

async function cerrarSesion() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.5rem;
  background: #1e293b;
  color: white;
}

.navbar-brand {
  font-weight: bold;
  font-size: 1.2rem;
  margin-right: 1rem;
}

.navbar-search {
  flex: 1;
}

.navbar-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.navbar-menu a {
  color: #cbd5e1;
  text-decoration: none;
}

.navbar-menu a:hover,
.navbar-menu a.router-link-active {
  color: white;
}

.btn-logout {
  background: #ef4444;
  color: white;
  border: none;
  padding: 0.4rem 0.8rem;
  border-radius: 4px;
  cursor: pointer;
}

.main-content {
  flex: 1;
  padding: 1.5rem;
}
</style>
