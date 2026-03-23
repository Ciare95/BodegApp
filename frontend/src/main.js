import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'

import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Inicializar tema antes del primer render
import { useThemeStore } from '@/stores/theme'
useThemeStore()

app.mount('#app')
