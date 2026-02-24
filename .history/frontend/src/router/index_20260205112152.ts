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

// Garde d'authentification améliorée
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Ignorer pour les routes publiques
  if (to.meta.public) {
    next()
    return
  }
  
  // Si pas encore vérifié, vérifier l'authentification
  if (!authStore.isAuthenticated && !authStore.loading) {
    try {
      await authStore.checkAuth()
    } catch (error) {
      console.error('Erreur vérification auth:', error)
    }
  }
  
  // Si toujours pas authentifié, rediriger vers login
  if (!authStore.isAuthenticated && to.name !== 'Login') {
    // Rediriger vers le login SSO directement
    window.location.href = '/api/auth/login/'
    return
  }
  
  // Si authentifié et essaie d'accéder au login, rediriger vers dashboard
  if (authStore.isAuthenticated && to.name === 'Login') {
    next({ name: 'Dashboard' })
    return
  }
  
  next()
})

export default router