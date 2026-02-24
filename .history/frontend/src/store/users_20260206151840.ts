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
  const usersActifs = computed(() => users.value.filter(u => u.is_active !== false))
  
  const usersSansEquipe = computed(() => 
    users.value.filter(u => !u.equipe)
  )

  // Actions
  const fetchUsers = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getAllUsers()
      users.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchUserById = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.getById(id)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (id: number, data: Partial<User>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.updateUser(id, data)
      const index = users.value.findIndex(u => u.id === id)
      if (index !== -1) {
        users.value[index] = { ...users.value[index], ...response }
      }
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePoleEquipe = async (userId: number, poleId: number | null, equipeId: number | null) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await usersApi.updatePoleEquipe({
        user_id: userId,
        pole_id: poleId || 0,
        equipe_id: equipeId || 0
      })
      await fetchUsers()
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    users,
    currentUser,
    loading,
    error,
    // Getters
    usersActifs,
    usersSansEquipe,
    // Actions
    fetchUsers,
    fetchUserById,
    updateUser,
    updatePoleEquipe,
    clearError
  }
})