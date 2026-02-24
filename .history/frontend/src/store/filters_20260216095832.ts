// frontend/src/store/filters.ts

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { usersApi, type Pole, type Equipe } from '@/api/users'

export const useFiltersStore = defineStore('filters', () => {
  const poles = ref<Pole[]>([])
  const equipes = ref<Equipe[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchPoles = async () => {
    loading.value = true
    error.value = null
    try {
      poles.value = await usersApi.getPoles()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement pôles'
    } finally {
      loading.value = false
    }
  }

  const fetchEquipesByPole = async (poleId: number) => {
    loading.value = true
    error.value = null
    try {
      equipes.value = await usersApi.getEquipesByPole(poleId)
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement équipes'
    } finally {
      loading.value = false
    }
  }

  const clearEquipes = () => {
    equipes.value = []
  }

  return {
    poles,
    equipes,
    loading,
    error,
    fetchPoles,
    fetchEquipesByPole,
    clearEquipes
  }
})