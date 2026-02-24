// frontend/src/store/poles.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Pole } from '@/types/user'
import { polesApi } from '@/api/poles'

export const usePolesStore = defineStore('poles', () => {
  // State
  const poles = ref<Pole[]>([])
  const currentPole = ref<Pole | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const polesActifs = computed(() => poles.value.filter(p => p.est_actif))
  const polesOptions = computed(() => 
    poles.value.map(p => ({ value: p.id, label: `${p.code} - ${p.nom}` }))
  )

  // Actions
  const fetchPoles = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await polesApi.getAll()
      poles.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des pôles'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchPoleById = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await polesApi.getById(id)
      currentPole.value = response
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du pôle'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createPole = async (data: Omit<Pole, 'id' | 'date_creation'>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await polesApi.create(data)
      poles.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la création'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updatePole = async (id: number, data: Partial<Pole>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await polesApi.update(id, data)
      const index = poles.value.findIndex(p => p.id === id)
      if (index !== -1) {
        poles.value[index] = response
      }
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deletePole = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await polesApi.delete(id)
      poles.value = poles.value.filter(p => p.id !== id)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la suppression'
      throw err
    } finally {
      loading.value = false
    }
  }

  const setCurrentPole = (pole: Pole | null) => {
    currentPole.value = pole
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    poles,
    currentPole,
    loading,
    error,
    // Getters
    polesActifs,
    polesOptions,
    // Actions
    fetchPoles,
    fetchPoleById,
    createPole,
    updatePole,
    deletePole,
    setCurrentPole,
    clearError
  }
})