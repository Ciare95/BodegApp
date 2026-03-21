<template>
  <div class="app-layout">
    <nav class="navbar">
      <RouterLink to="/productos" class="navbar-brand">
        <span class="brand-icon">⬡</span>
        <span class="brand-name">BodegApp</span>
      </RouterLink>

      <div class="navbar-menu">
        <RouterLink to="/productos" class="nav-link">Productos</RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/catalogos" class="nav-link">Catálogos</RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/usuarios" class="nav-link">Usuarios</RouterLink>
        <div class="nav-divider"></div>
        <button class="btn-logout" @click="cerrarSesion" title="Cerrar sesión">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
          <span>Salir</span>
        </button>
      </div>

      <!-- Mobile hamburger -->
      <button class="btn-hamburger" @click="menuAbierto = !menuAbierto" :aria-expanded="menuAbierto" aria-label="Menú">
        <svg v-if="!menuAbierto" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
        <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>
    </nav>

    <!-- Mobile dropdown menu -->
    <Transition name="slide-down">
      <div v-if="menuAbierto" class="mobile-menu">
        <RouterLink to="/productos" class="mobile-link" @click="menuAbierto = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
          Productos
        </RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/catalogos" class="mobile-link" @click="menuAbierto = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 6h16M4 10h16M4 14h16M4 18h16"/></svg>
          Catálogos
        </RouterLink>
        <RouterLink v-if="auth.esAdmin" to="/usuarios" class="mobile-link" @click="menuAbierto = false">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Usuarios
        </RouterLink>
        <div class="mobile-divider"></div>
        <button class="mobile-link danger" @click="cerrarSesion">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
          Cerrar sesión
        </button>
      </div>
    </Transition>

    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const menuAbierto = ref(false)

async function cerrarSesion() {
  menuAbierto.value = false
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  background: var(--bg);
}

/* ── Navbar ── */
.navbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0 1.75rem;
  height: 56px;
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 50;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-shrink: 0;
  text-decoration: none;
}

.brand-icon { font-size: 1.25rem; color: var(--ink); line-height: 1; }

.brand-name {
  font-size: 0.9375rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--ink);
}

.navbar-search { display: none; }

/* Desktop menu */
.navbar-menu {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-left: auto;
}

.nav-link {
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  font-weight: 400;
  color: var(--ink-2);
  border-radius: var(--r-md);
  transition: color var(--t), background var(--t);
  text-decoration: none;
  white-space: nowrap;
}

.nav-link:hover { color: var(--ink); background: var(--bg); }
.nav-link.router-link-active { color: var(--ink); font-weight: 500; background: var(--bg); }

.nav-divider { width: 1px; height: 20px; background: var(--border); margin: 0 0.5rem; }

.btn-logout {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  color: var(--ink-3);
  background: none;
  border: none;
  border-radius: var(--r-md);
  transition: color var(--t), background var(--t);
  white-space: nowrap;
}
.btn-logout:hover { color: var(--rojo); background: var(--rojo-bg); }

/* Hamburger — hidden on desktop */
.btn-hamburger {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  margin-left: auto;
  color: var(--ink-2);
  background: none;
  border: none;
  border-radius: var(--r-md);
  flex-shrink: 0;
  transition: background var(--t);
}
.btn-hamburger:hover { background: var(--bg); }

/* Mobile dropdown */
.mobile-menu {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0.5rem 0;
  display: flex;
  flex-direction: column;
  position: sticky;
  top: 56px;
  z-index: 49;
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 400;
  color: var(--ink-2);
  text-decoration: none;
  background: none;
  border: none;
  text-align: left;
  transition: background var(--t), color var(--t);
}
.mobile-link:hover { background: var(--bg); color: var(--ink); }
.mobile-link.router-link-active { color: var(--ink); font-weight: 500; }
.mobile-link.danger { color: var(--rojo); }
.mobile-link.danger:hover { background: var(--rojo-bg); }

.mobile-divider {
  height: 1px;
  background: var(--border);
  margin: 0.375rem 0;
}

/* Transition */
.slide-down-enter-active, .slide-down-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.slide-down-enter-from, .slide-down-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* ── Main ── */
.main-content {
  flex: 1;
  padding: 2rem 1.75rem;
  max-width: 1280px;
  width: 100%;
  margin: 0 auto;
}

/* ── Responsive ── */
@media (max-width: 768px) {
  .navbar { padding: 0 1rem; gap: 0.75rem; }
  .navbar-search { max-width: none; }
  .navbar-menu { display: none; }
  .btn-hamburger { display: flex; }
  .main-content { padding: 1.25rem 1rem; }
}

@media (max-width: 480px) {
  .navbar { padding: 0 0.875rem; }
  .brand-name { font-size: 0.875rem; }
  .main-content { padding: 1rem 0.875rem; }
}
</style>
