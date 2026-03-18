<template>
  <div class="buscador" ref="contenedor">
    <input
      v-model="query"
      type="search"
      placeholder="Buscar producto por nombre o código..."
      @input="buscar"
      @focus="mostrarResultados = true"
      @keydown.escape="cerrar"
    />

    <ul v-if="mostrarResultados && resultados.length" class="resultados">
      <li v-for="p in resultados" :key="p.id" @click="irAProducto(p)">
        <span class="codigo">{{ p.codigo_completo }}</span>
        <span class="nombre">{{ p.nombre_completo }}</span>
        <span :class="['estado', p.estado]">{{ p.estado }}</span>
      </li>
    </ul>

    <p v-if="mostrarResultados && query && !resultados.length && !cargando" class="sin-resultados">
      Sin resultados
    </p>
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
  if (!query.value.trim()) {
    resultados.value = []
    return
  }
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
  if (contenedor.value && !contenedor.value.contains(e.target)) {
    mostrarResultados.value = false
  }
}

onMounted(() => document.addEventListener('click', clickFuera))
onUnmounted(() => document.removeEventListener('click', clickFuera))
</script>

<style scoped>
.buscador {
  position: relative;
  width: 100%;
  max-width: 480px;
}

input {
  width: 100%;
  padding: 0.4rem 0.75rem;
  border-radius: 4px;
  border: 1px solid #475569;
  background: #334155;
  color: white;
  font-size: 0.9rem;
  box-sizing: border-box;
}

input::placeholder {
  color: #94a3b8;
}

.resultados {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  list-style: none;
  margin: 0;
  padding: 0;
  z-index: 100;
  max-height: 320px;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.resultados li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  color: #1e293b;
  font-size: 0.875rem;
}

.resultados li:hover {
  background: #f1f5f9;
}

.codigo {
  font-weight: bold;
  min-width: 60px;
}

.nombre {
  flex: 1;
}

.estado {
  font-size: 0.75rem;
  padding: 0.1rem 0.4rem;
  border-radius: 3px;
  text-transform: capitalize;
}

.estado.verde { background: #dcfce7; color: #166534; }
.estado.amarillo { background: #fef9c3; color: #854d0e; }
.estado.rojo { background: #fee2e2; color: #991b1b; }

.sin-resultados {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  padding: 0.75rem;
  color: #64748b;
  font-size: 0.875rem;
  text-align: center;
}
</style>
