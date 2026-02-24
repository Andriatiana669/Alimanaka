// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false) // ← Nouveau: éviter double check

  const isAuthenticated = computed(() => !!user.value)

  // Ajouter ce computed
  const fullName = computed(() => {
    if (!user.value) return ''
    return user.value.get_full_name || `${user.value.last_name} ${user.value.first_name}`
  })

  async function checkAuth() {
    if (checked.value && user.value) {
      console.log('Auth déjà vérifiée')
      return { authenticated: true, user: user.value }
    }
    
    loading.value = true
    try {
      console.log('Appel API /api/auth/session/')
      const data = await authApi.checkSession()
      
      if (data.authenticated && data.user) {
        user.value = data.user
        checked.value = true
        console.log('User connecté:', data.user.username)
        return data
      } else {
        throw new Error('Non authentifié')
      }
    } catch (err) {
      console.error('Échec auth:', err)
      user.value = null
      checked.value = true
      throw err
    } finally {
      loading.value = false
    }
  }

  function login() {
    // Redirection externe vers le backend
    window.location.href = 'http://localhost:8000/api/auth/login/'
  }

  function logout() {
    user.value = null
    checked.value = false
    window.location.href = 'http://localhost:8000/api/auth/logout/'
  }

  function clearAuth() {
    user.value = null
    checked.value = false
  }

  return {
    user,
    fullName,
    loading,
    checked,
    isAuthenticated,
    checkAuth,
    login,
    logout,
    clearAuth
  }
})