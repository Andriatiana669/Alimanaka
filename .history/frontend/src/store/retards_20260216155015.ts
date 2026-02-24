// Store Pinia pour les retards (similaire à conges.ts)

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { retardsApi } from '@/api/retards';
import type { 
  Retard, 
  TypeRetardConfig, 
  RetardCreateData, 
  RattrapageCreateData,
  RetardFilters 
} from '@/types/retards';

export const useRetardsStore = defineStore('retards', () => {
  // State
  const retards = ref<Retard[]>([]);
  const typesRetard = ref<TypeRetardConfig[]>([]);
  const currentRetard = ref<Retard | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // Getters
  const retardsEnAttente = computed(() => 
    retards.value.filter(r => r.statut === 'en_attente')
  );
  
  const retardsApprouves = computed(() => 
    retards.value.filter(r => r.statut === 'approuve')
  );
  
  const retardsAnnules = computed(() => 
    retards.value.filter(r => r.statut === 'annule')
  );
  
  const retardsParAnnee = computed(() => {
    const grouped: Record<number, Retard[]> = {};
    retards.value.forEach(retard => {
      const annee = new Date(retard.date).getFullYear();
      if (!grouped[annee]) grouped[annee] = [];
      grouped[annee].push(retard);
    });
    return grouped;
  });
  
  // Actions
  const fetchTypesRetard = async () => {
    try {
      const response = await retardsApi.getTypesRetard();
      typesRetard.value = response.data;
    } catch (err) {
      console.error('Erreur fetch types retard:', err);
    }
  };
  
  const fetchMesRetards = async (filters?: RetardFilters) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await retardsApi.getMesRetards(filters);
      retards.value = response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement des retards';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const fetchAllRetards = async (filters?: RetardFilters) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await retardsApi.getRetards(filters);
      retards.value = response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement des retards';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const createRetard = async (data: RetardCreateData) => {
    loading.value = true;
    try {
      const response = await retardsApi.createRetard(data);
      retards.value.unshift(response.data);
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la création';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const rattraperRetard = async (id: number, data: RattrapageCreateData) => {
    loading.value = true;
    try {
      const response = await retardsApi.rattrapageretard(id, data);
      
      // Mettre à jour le retard dans la liste
      const index = retards.value.findIndex(r => r.id === id);
      if (index !== -1) {
        // Recharger le retard pour avoir les données à jour
        const retardResponse = await retardsApi.getRetard(id);
        retards.value[index] = retardResponse.data;
      }
      
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors du rattrapage';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const annulerRetard = async (id: number, commentaire?: string) => {
    loading.value = true;
    try {
      await retardsApi.annulerRetard(id, commentaire);
      
      // Mettre à jour localement
      const index = retards.value.findIndex(r => r.id === id);
      if (index !== -1) {
        retards.value[index].statut = 'annule';
      }
    } catch (err: any) {
      error.value = err.response?.data?.error || 'Erreur lors de l\'annulation';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  const fetchCalendrier = async (annee: number, poleId?: number, equipeId?: number) => {
    try {
      const response = await retardsApi.getCalendrier(annee, poleId, equipeId);
      return response.data;
    } catch (err) {
      console.error('Erreur fetch calendrier retards:', err);
      throw err;
    }
  };
  
  const clearError = () => {
    error.value = null;
  };
  
  return {
    // State
    retards,
    typesRetard,
    currentRetard,
    loading,
    error,
    
    // Getters
    retardsEnAttente,
    retardsApprouves,
    retardsAnnules,
    retardsParAnnee,
    
    // Actions
    fetchTypesRetard,
    fetchMesRetards,
    fetchAllRetards,
    createRetard,
    rattraperRetard,
    annulerRetard,
    fetchCalendrier,
    clearError,
  };
});