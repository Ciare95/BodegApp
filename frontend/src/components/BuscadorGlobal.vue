<template>
  <div class="buscador" ref="contenedor">
    <div class="input-wrap">
      <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input
        v-model="query"
        type="search"
        placeholder="Buscar por nombre o código..."
        @input="buscar"
        @focus="mostrarResultados = true"
        @keydown.escape="cerrar"
      />
    </div>

    <Transition name="dropdown">
      <ul v-if="mostrarResultados && resultados.length" class="resultados">
        <li v-for="p in resultados" :key="p.id" @click="irAProducto(p)">
          <span class="res-codigo">{{ p.codigo_completo }}</span>
          <span class="res-nombre">{{ p.nombre_completo }}</span>
          <span :class="['res-estado', p.estado]">
            <span class="dot"></span>
          </span>
        </li>
      </ul>
      <div v-else-if="mostrarResultados && query && !resultados.length && !cargando" class="sin-resultados">
        Sin resultados para "{{ query }}"
      </div>
    </Transition>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import client from '@/api/client'

const router = useRouter()
const query = ref('')
const resultados = ref([])
const mostrarResultados = ref(false)
const cargando = ref(false)
const contenedor = ref(null)
let timer = null

function buscar() {
  clearTimeout(timer)
  if (!query.value.trim()) { resultados.value = []; return }
  timer = setTimeout(async () => {
    cargando.value = true
    try {
      const { data } = await client.get('/productos/', { params: { q: query.value } })
      resultados.value = data.results ?? data
    } finally {
      cargando.value = false
    }
  }, 300)
}

function irAProducto(producto) {
  router.push(`/productos/${producto.id}`)
  cerrar()
}

function cerrar() {
  mostrarResultados.value = false
  query.value = ''
  resultados.value = []
}

function clickFuera(e) {
  if (contenedor.value && !contenedor.value.contains(e.target)) mostrarResultados.value = false
}

onMounted(() => document.addEventListener('click', clickFuera))
onUnmounted(() => document.removeEventListener('click', clickFuera))
</script>

<style scoped>
.buscador { position: relative; width: 100%; }

.input-wrap { position: relative; display: flex; align-items: center; }

.search-icon {
  position: absolute; left: 0.625rem;
  color: var(--ink-4); pointer-events: none; flex-shrink: 0;
}

input {
  width: 100%; padding: 0.4375rem 0.75rem 0.4375rem 2rem;
  border: 1px solid var(--border-md); border-radius: var(--r-md);
  background: var(--bg); color: var(--ink);
  font-size: 0.8125rem; outline: none;
  transition: border-color var(--t), background var(--t), box-shadow var(--t);
}

input::placeholder { color: var(--ink-4); }

input:focus {
  border-color: var(--ink); background: var(--surface);
  box-shadow: 0 0 0 3px rgba(17,17,17,0.06);
}

/* Resultados */
.resultados {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); list-style: none;
  z-index: 100; max-height: 300px; overflow-y: auto;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

.resultados li {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.625rem 0.875rem; cursor: pointer;
  transition: background var(--t);
  border-bottom: 1px solid var(--border);
}
.resultados li:last-child { border-bottom: none; }
.resultados li:hover { background: var(--bg); }

.res-codigo {
  font-family: var(--font-mono); font-size: 0.75rem; font-weight: 500;
  background: var(--ink); color: var(--accent-fg);
  padding: 0.125rem 0.4375rem; border-radius: var(--r-sm);
  letter-spacing: 0.04em; flex-shrink: 0;
}

.res-nombre { flex: 1; font-size: 0.8125rem; color: var(--ink-2); }

.res-estado { flex-shrink: 0; }
.res-estado .dot { width: 7px; height: 7px; border-radius: 50%; display: block; }
.res-estado.verde .dot { background: var(--verde); }
.res-estado.amarillo .dot { background: var(--amarillo); }
.res-estado.rojo .dot { background: var(--rojo); }

.sin-resultados {
  position: absolute; top: calc(100% + 6px); left: 0; right: 0;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--r-lg); padding: 0.875rem;
  color: var(--ink-3); font-size: 0.8125rem; text-align: center;
  box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}

/* Transition */
.dropdown-enter-active, .dropdown-leave-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.dropdown-enter-from, .dropdown-leave-to {
  opacity: 0; transform: translateY(-4px);
}
</style>
