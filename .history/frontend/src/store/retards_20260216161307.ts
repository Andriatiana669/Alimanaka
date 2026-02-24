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
  // ==================== STATE ====================
  const retards = ref<Retard[]>([]);
  const typesRetard = ref<TypeRetardConfig[]>([]);
  const currentRetard = ref<Retard | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  // State supplémentaire pour la vue
  const utilisateursGerables = ref<Array<{
    id: number;
    display_name: string;
    username: string;
    equipe_nom: string;
  }>>([]);
  
  const calendarEvents = ref<any[]>([]);

  // ==================== GETTERS ====================
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

  // ==================== ACTIONS ====================
  
  // Types de retard (configuration)
  const fetchTypesRetard = async () => {
    try {
      const response = await retardsApi.getTypesRetard();
      typesRetard.value = response.data;
    } catch (err) {
      console.error('Erreur fetch types retard:', err);
    }
  };
  
  // Récupérer mes retards
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
  
  // Récupérer tous les retards (admin/manager)
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
  
  // Récupérer un retard spécifique
  const fetchRetard = async (id: number) => {
    loading.value = true;
    try {
      const response = await retardsApi.getRetard(id);
      currentRetard.value = response.data;
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors du chargement du retard';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Créer un retard
  const createRetard = async (data: RetardCreateData) => {
    loading.value = true;
    error.value = null;
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
  
  // Mettre à jour un retard
  const updateRetard = async (id: number, data: Partial<RetardCreateData>) => {
    loading.value = true;
    try {
      const response = await retardsApi.updateRetard(id, data);
      const index = retards.value.findIndex(r => r.id === id);
      if (index !== -1) {
        retards.value[index] = response.data;
      }
      return response.data;
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la mise à jour';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Supprimer un retard
  const deleteRetard = async (id: number) => {
    loading.value = true;
    try {
      await retardsApi.deleteRetard(id);
      retards.value = retards.value.filter(r => r.id !== id);
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'Erreur lors de la suppression';
      throw err;
    } finally {
      loading.value = false;
    }
  };
  
  // Rattraper un retard (créer une session de rattrapage)
  const rattraperRetard = async (id: number, data: RattrapageCreateData) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await retardsApi.rattraperRetard(id, data);
      
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
  
  // Annuler un retard
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
  
  // Calendrier
  const fetchCalendrier = async (annee: number, poleId?: number, equipeId?: number) => {
    try {
      const response = await retardsApi.getCalendrier(annee, poleId, equipeId);
      calendarEvents.value = response.data;
      return response.data;
    } catch (err) {
      console.error('Erreur fetch calendrier retards:', err);
      throw err;
    }
  };
  
  // Utilisateurs gérables (pour managers)
  const fetchUtilisateursGerables = async () => {
    try {
      const response = await retardsApi.getUtilisateursGerables();
      utilisateursGerables.value = response.data;
    } catch (err) {
      console.error('Erreur fetch utilisateurs gerables:', err);
    }
  };
  
  // Export Excel (tous les retards - admin)
  const exportAll = async () => {
    try {
      const response = await retardsApi.exportRetards();
      return response;
    } catch (err) {
      console.error('Erreur export retards:', err);
      throw err;
    }
  };
  
  // Clear error
  const clearError = () => {
    error.value = null;
  };
  
  // Reset store
  const reset = () => {
    retards.value = [];
    typesRetard.value = [];
    currentRetard.value = null;
    utilisateursGerables.value = [];
    calendarEvents.value = [];
    error.value = null;
  };

  // ==================== RETURN ====================
  return {
    // State
    retards,
    typesRetard,
    currentRetard,
    loading,
    error,
    utilisateursGerables,
    calendarEvents,
    
    // Getters
    retardsEnAttente,
    retardsApprouves,
    retardsAnnules,
    retardsParAnnee,
    
    // Actions
    fetchTypesRetard,
    fetchMesRetards,
    fetchAllRetards,
    fetchRetard,
    createRetard,
    updateRetard,
    deleteRetard,
    rattraperRetard,
    annulerRetard,
    fetchCalendrier,
    fetchUtilisateursGerables,
    exportAll,
    clearError,
    reset,
  };
});