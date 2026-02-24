// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { authApi } from '@/api/auth'

export const useAuthStore = defineStore('auth', () => {
  // States (réactifs)
  const user = ref<User | null>(null)
  const token = ref<string | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters (computed)
  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => user.value?.is_staff || user.value?.is_superuser || false)

  // Actions
  const setUser = (userData: User) => {
    user.value = userData
  }

  const setToken = (newToken: string) => {
    token.value = newToken
  }

  const login = async () => {
    window.location.href = '/api/auth/login/'
  }

  const logout = async () => {
    try {
      loading.value = true
      window.location.href = '/api/auth/logout/'
    } catch (err) {
      error.value = 'Erreur lors de la déconnexion'
      console.error(err)
    } finally {
      loading.value = false
    }
  }

  const checkAuth = async (): Promise<User | null> => {
    try {
      loading.value = true
      const userData = await authApi.getCurrentUser()
      user.value = userData
      return userData
    } catch (err) {
      user.value = null
      return null
    } finally {
      loading.value = false
    }
  }

  // RETOURNER TOUT CE QUI DOIT ÊTRE ACCESSIBLE
  return {
    // States
    user,
    token,
    loading,
    error,
    
    // Getters (computed)
    isAuthenticated,
    isAdmin,
    
    // Actions
    setUser,
    setToken,
    login,
    logout,
    checkAuth
  }
})