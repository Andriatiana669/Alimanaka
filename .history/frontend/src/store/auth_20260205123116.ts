import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  // State
  const user = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const isAuthenticated = computed(() => !!user.value)
  const displayName = computed(() => user.value?.display_name || user.value?.username || 'Utilisateur')

  // Actions
  async function checkAuth() {
    loading.value = true
    try {
      const data = await authApi.checkSession()
      if (data.authenticated) {
        user.value = data.user
      }
      return data
    } catch (err) {
      user.value = null
      throw err
    } finally {
      loading.value = false
    }
  }

  function login() {
    authApi.login() // Redirection complète
  }

  function logout() {
    user.value = null
    authApi.logout() // Redirection complète
  }

  // Mise à jour locale du user (ex: après modif pseudo)
  function updateUser(updates: Partial<User>) {
    if (user.value) {
      user.value = { ...user.value, ...updates }
    }
  }

  return {
    user,
    loading,
    error,
    isAuthenticated,
    displayName,
    checkAuth,
    login,
    logout,
    updateUser,
  }
})