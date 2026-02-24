import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Layouts
import MainLayout from '@/components/Layout/MainLayout.vue'
import AppLayout from '@/components/Layout/AppLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'login',
        name: 'Login',
        component: () => import('@/views/Auth/Login.vue'),
        meta: { public: true }
      },
      {
        path: 'logout',
        name: 'Logout',
        component: () => import('@/views/Auth/Logout.vue')
      },
      {
        path: 'auth/callback',
        name: 'Callback',
        component: () => import('@/views/Auth/Callback.vue'),
        meta: { public: true }
      }
    ]
  },
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue')
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue')
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Garde d'authentification
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Vérifier l'authentification
  if (!authStore.isAuthenticated) {
    await authStore.checkAuth()
  }
  
  // Si la route nécessite une authentification et l'utilisateur n'est pas connecté
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'Login' })
  } 
  // Si l'utilisateur est connecté et essaie d'accéder à une route publique (login)
  else if (to.meta.public && authStore.isAuthenticated) {
    next({ name: 'Dashboard' })
  } 
  else {
    next()
  }
})

export default router