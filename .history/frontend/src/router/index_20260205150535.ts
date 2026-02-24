// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

import AppLayout from '@/components/Layout/AppLayout.vue'

const routes = [
  {
    path: '/',
    component: AppLayout,
    name: 'Root',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { public: true, checkAuth: true } // ← Flag spécial
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: () => import('@/views/Auth/Callback.vue'),
    meta: { public: true }
  },
  {
    path: '/auth/error',
    name: 'AuthError',
    component: () => import('@/views/Auth/Error.vue'),
    meta: { public: true }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue'),
    meta: { requiresAuth: true }
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
  },
  {
    path: 'permissions',
    name: 'Permissions',
    component: () => import('@/views/Permissions.vue')
  },
  {
    path: 'equipes',
    name: 'Equipes',
    component: () => import('@/views/Equipes.vue')
  },
  {
    path: 'conges',
    name: 'Conges',
    component: () => import('@/views/Conges.vue')
  },
  {
    path: 'repos-medicale',
    name: 'ReposMedicale',
    component: () => import('@/views/ReposMedicale.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Garde de navigation corrigée
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  console.log('Router guard:', to.path, 'Auth:', authStore.isAuthenticated, 'User:', !!authStore.user)
  
  // 1. Routes publiques sans vérification
  if (to.meta.public && !to.meta.checkAuth) {
    next()
    return
  }
  
  // 2. Si on va sur /login et qu'on est déjà auth, rediriger vers dashboard
  if (to.path === '/login' && authStore.isAuthenticated) {
    console.log('Déjà authentifié, redirection dashboard')
    next('/dashboard')
    return
  }
  
  // 3. Vérifier l'authentification si pas encore chargée
  if (!authStore.user && !authStore.loading) {
    try {
      console.log('Vérification session...')
      await authStore.checkAuth()
      // console.log('Session OK, user:', authStore.user?.username)
    } catch (err) {
      console.error('Session invalide:', err)
      // Seulement si route protégée, rediriger vers login
      if (to.meta.requiresAuth) {
        // ❌ NE PAS appeler authStore.login() ici !
        // ✅ Redirection simple vers la page de login Vue
        next('/login?reason=session_expired')
        return
      }
    }
  }
  
  // 4. Route protégée mais pas authentifié
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    console.log('Accès refusé, redirection login')
    next('/login?redirect=' + encodeURIComponent(to.fullPath))
    return
  }
  
  next()
})

export default router