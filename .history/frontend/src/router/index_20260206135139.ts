// frontend/src/router/index.ts
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'

// Layouts
import AppLayout from '@/components/Layout/AppLayout.vue'

const routes = [
  // Routes publiques (sans layout)
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Auth/Login.vue'),
    meta: { public: true, checkAuth: true }
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
  
  // Routes avec layout AppLayout (nécessitent authentification)
  {
    path: '/',
    component: AppLayout,
    meta: { requiresAuth: true },
    children: [
      // Dashboard
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: 'Tableau de bord' }
      },
      
      // Gestion des utilisateurs
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/Users.vue'),
        meta: { title: 'Gestion des utilisateurs' }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: { title: 'Mon profil' }
      },
      
      // Gestion des équipes
      {
        path: 'equipes',
        name: 'Equipes',
        component: () => import('@/views/Equipes.vue'),
        meta: { title: 'Gestion des équipes' }
      },
      
      // Gestion des congés et permissions
      {
        path: 'permissions',
        name: 'Permissions',
        component: () => import('@/views/Permissions.vue'),
        meta: { title: 'Gestion des permissions' }
      },
      {
        path: 'conges',
        name: 'Conges',
        component: () => import('@/views/Conges.vue'),
        meta: { title: 'Gestion des congés' }
      },
      {
        path: 'repos-medicale',
        name: 'ReposMedicale',
        component: () => import('@/views/ReposMedicale.vue'),
        meta: { title: 'Repos médical' }
      },
      {
        path: 'retards',
        name: 'Retards',
        component: () => import('@/views/Retards.vue'),
        meta: { title: 'Suivi des retards' }
      },
      
      // Calendrier et événements
      {
        path: 'calendar',
        name: 'Calendar',
        component: () => import('@/views/Calendar.vue'),
        meta: { title: 'Calendrier' }
      },
      {
        path: 'events',
        name: 'Events',
        component: () => import('@/views/Events.vue'),
        meta: { title: 'Événements' }
      },
      
      // Administration
      {
        path: 'ostie',
        name: 'Ostie',
        component: () => import('@/views/Ostie.vue'),
        meta: { title: 'Gestion OSTIE' }
      },
      {
        path: '/poles',
        name: 'Poles',
        component: () => import('@/views/Poles.vue'),
        meta: { requiresAuth: true, adminOnly: true }
      },
      {
        path: '/equipes',
        name: 'Equipes',
        component: () => import('@/views/Equipes.vue'),
        meta: { requiresAuth: true }
      },
    ]
  },
  
  // 404 - Page non trouvée (sans layout)
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { public: true, title: 'Page non trouvée' }
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
    } catch (err) {
      console.error('Session invalide:', err)
      // Seulement si route protégée, rediriger vers login
      if (to.meta.requiresAuth) {
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
  
  // 5. Mettre à jour le titre de la page
  if (to.meta.title) {
    document.title = `${to.meta.title} - Alimanaka`
  } else {
    document.title = 'Alimanaka'
  }
  
  next()
})

export default router