import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/LoginView.vue'),
      meta: { publica: true },
    },
    {
      path: '/',
      component: () => import('@/layouts/AppLayout.vue'),
      children: [
        {
          path: '',
          redirect: '/productos',
        },
        {
          path: 'productos',
          name: 'productos',
          component: () => import('@/views/ProductosView.vue'),
        },
        {
          path: 'productos/nuevo',
          name: 'producto-nuevo',
          component: () => import('@/views/ProductoFormView.vue'),
          meta: { soloAdmin: true },
        },
        {
          path: 'productos/:id',
          name: 'producto-detalle',
          component: () => import('@/views/ProductoDetalleView.vue'),
        },
        {
          path: 'productos/:id/editar',
          name: 'producto-editar',
          component: () => import('@/views/ProductoFormView.vue'),
          meta: { soloAdmin: true },
        },
        {
          path: 'catalogos',
          name: 'catalogos',
          component: () => import('@/views/CatalogosView.vue'),
          meta: { soloAdmin: true },
        },
        {
          path: 'usuarios',
          name: 'usuarios',
          component: () => import('@/views/UsuariosView.vue'),
          meta: { soloAdmin: true },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

// Guard global
router.beforeEach((to) => {
  const auth = useAuthStore()

  if (!to.meta.publica && !auth.estaAutenticado) {
    return { name: 'login' }
  }

  if (to.meta.soloAdmin && !auth.esAdmin) {
    return { name: 'productos' }
  }

  if (to.name === 'login' && auth.estaAutenticado) {
    return { name: 'productos' }
  }
})

export default router
