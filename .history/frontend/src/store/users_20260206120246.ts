// frontend/src/store/users.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usersApi } from '@/api/users'
import type { User, UpdatePseudoData } from '@/types/user'

export const useUsersStore = defineStore('users', () => {
  // State
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const allUsers = computed(() => users.value)
  const getUserById = computed(() => (id: number) => 
    users.value.find(u => u.id === id)
  )

  // Actions
  const fetchAllUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getAllUsers()
      users.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchCurrentUser = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getCurrentUser()
      currentUser.value = response.data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du profil'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePseudo = async (data: UpdatePseudoData) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.updatePseudo(data)
      // Met à jour le currentUser avec les nouvelles données
      if (currentUser.value) {
        currentUser.value = { ...currentUser.value, ...response.data }
      }
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour du pseudo'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    // State
    users,
    currentUser,
    loading,
    error,
    // Getters
    allUsers,
    getUserById,
    // Actions
    fetchAllUsers,
    fetchCurrentUser,
    updatePseudo
  }
})