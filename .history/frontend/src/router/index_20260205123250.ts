import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const routes = [
  {
    path: '/',
    name: 'Root',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { public: true }
  },
  {
    path: '/auth/callback',  // Page de retour optionnelle
    name: 'AuthCallback',
    component: () => import('@/views/Auth/Callback.vue'),
    meta: { public: true }
  },
  {
    path: '/auth/error',
    name: 'AuthError',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/calendrier',
    name: 'Calendrier',
    component: () => import('@/views/Calendar.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/evenements',
    name: 'Evenements',
    component: () => import('@/views/Events.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Garde de navigation
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Routes publiques
  if (to.meta.public) {
    next()
    return
  }
  
  // Vérifier auth si pas encore fait
  if (!authStore.user && !authStore.loading) {
    try {
      await authStore.checkAuth()
    } catch {
      // 401 reçu, rediriger vers login SSO
      authStore.login()
      return
    }
  }
  
  // Si pas authentifié après vérification
  if (!authStore.isAuthenticated) {
    authStore.login()
    return
  }
  
  next()
})

export default router