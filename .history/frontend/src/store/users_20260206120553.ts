import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User } from '@/types/user'
import { usersApi } from '@/api/users'

export const useUsersStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const userCount = computed(() => users.value.length)
  const getUserById = (id: number) => users.value.find(u => u.id === id)

  // Actions
  const fetchUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getAllUsers()
      users.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getUserProfile()
      currentUser.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du profil'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePseudo = async (data: { pseudo?: string; pseudo_format?: string }) => {
    try {
      const response = await usersApi.updatePseudo(data)
      if (currentUser.value) {
        currentUser.value.pseudo = response.pseudo
        currentUser.value.pseudo_format = response.pseudo_format
      }
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour'
      throw err
    }
  }

  const clearError = () => {
    error.value = null
  }

  const reset = () => {
    users.value = []
    currentUser.value = null
    loading.value = false
    error.value = null
  }

  return {
    // State
    users,
    currentUser,
    loading,
    error,
    // Getters
    userCount,
    getUserById,
    // Actions
    fetchUsers,
    fetchCurrentUser,
    updatePseudo,
    clearError,
    reset
  }
})