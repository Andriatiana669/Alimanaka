// frontend/src/store/equipes.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Equipe, EquipeMembre } from '@/types/user'
import { equipesApi } from '@/api/equipes'

export const useEquipesStore = defineStore('equipes', () => {
  // State
  const equipes = ref<Equipe[]>([])
  const arbreEquipes = ref<Equipe[]>([])
  const currentEquipe = ref<Equipe | null>(null)
  const membresCurrentEquipe = ref<EquipeMembre[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const equipesActives = computed(() => equipes.value.filter(e => e.est_actif))
  const equipesInactives = computed(() => equipes.value.filter(e => !e.est_actif))
  
  const equipesOptions = computed(() => 
    equipes.value.map(e => ({ 
      value: e.id, 
      label: e.pole_details 
        ? `${e.nom} (${e.pole_details.code})`
        : e.nom
    }))
  )

  // Organiser par pôle pour select groupé
  const equipesParPole = computed(() => {
    const grouped = new Map<number | null, { pole: string | null, equipes: Equipe[] }>()
    
    equipes.value.forEach(equipe => {
      const poleId = equipe.pole
      const poleNom = equipe.pole_details?.nom || 'Sans pôle'
      
      if (!grouped.has(poleId)) {
        grouped.set(poleId, { pole: poleNom, equipes: [] })
      }
      grouped.get(poleId)!.equipes.push(equipe)
    })
    
    return Array.from(grouped.values())
  })

  // Actions
  const fetchEquipes = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.getAll()
      equipes.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des équipes'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchArbre = async () => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.getArbre()
      arbreEquipes.value = response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement de l\'arborescence'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchEquipeById = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.getById(id)
      currentEquipe.value = response
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement de l\'équipe'
      throw err
    } finally {
      loading.value = false
    }
  }

  const fetchMembres = async (equipeId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.getMembres(equipeId)
      membresCurrentEquipe.value = response
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des membres'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createEquipe = async (data: Omit<Equipe, 'id' | 'date_creation' | 'niveau_hierarchique'>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.create(data)
      equipes.value.push(response)
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la création'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateEquipe = async (id: number, data: Partial<Equipe>) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.update(id, data)
      const index = equipes.value.findIndex(e => e.id === id)
      if (index !== -1) {
        equipes.value[index] = response
      }
      if (currentEquipe.value?.id === id) {
        currentEquipe.value = response
      }
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la mise à jour'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteEquipe = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      await equipesApi.delete(id)
      equipes.value = equipes.value.filter(e => e.id !== id)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de la suppression'
      throw err
    } finally {
      loading.value = false
    }
  }

  const changerManager = async (equipeId: number, managerId: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await equipesApi.changerManager(equipeId, managerId)
      await fetchEquipeById(equipeId) // Rafraîchir les données
      return response
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du changement de manager'
      throw err
    } finally {
      loading.value = false
    }
  }

  const setCurrentEquipe = (equipe: Equipe | null) => {
    currentEquipe.value = equipe
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // State
    equipes,
    arbreEquipes,
    currentEquipe,
    membresCurrentEquipe,
    loading,
    error,
    // Getters
    equipesActives,
    equipesOptions,
    equipesParPole,
    // Actions
    fetchEquipes,
    fetchArbre,
    fetchEquipeById,
    fetchMembres,
    createEquipe,
    updateEquipe,
    deleteEquipe,
    changerManager,
    setCurrentEquipe,
    clearError
  }
})