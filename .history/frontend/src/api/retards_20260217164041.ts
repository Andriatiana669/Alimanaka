// frontend/src/api/retards.ts
import api from './index'
import type { 
  TypeRetardConfig,
  Retard,
  Rattrapage,
  RetardCalendarEventFromAPI,
  CreateRetardData,
  CreateRattrapageData,
  GerableUserRetard,
  RetardsParams,
  CalendrierRetardsParams,
  RattrapageResponse,
  AnnulationRetardResponse
} from '@/types/retards'

export const retardsApi = {
  // ============================================
  // Configuration des types de retard
  // ============================================
  
  getTypesRetard(): Promise<TypeRetardConfig[]> {
    return api.get('/api/retards/types-retard/').then(res => res.data)
  },

  // ============================================
  // Retards
  // ============================================
  
  getMesRetards(annee?: number, statut?: string): Promise<Retard[]> {
    return api.get('/api/retards/retards/mes_retards/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  getRetardDetails(id: number): Promise<Retard> {
    return api.get(`/api/retards/retards/${id}/`).then(res => res.data)
  },

  createRetard(data: CreateRetardData & { user_id?: number }): Promise<Retard> {
    return api.post('/api/retards/retards/', data).then(res => res.data)
  },

  annulerRetard(id: number, commentaire?: string): Promise<AnnulationRetardResponse> {
    return api.post(`/api/retards/retards/${id}/annuler/`, { commentaire }).then(res => res.data)
  },

  // ============================================
  // Calendrier
  // ============================================
  
  getCalendrier(params?: CalendrierRetardsParams): Promise<RetardCalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/retards/retards/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Rattrapages
  // ============================================
  
  ajouterRattrapage(retardId: number, data: CreateRattrapageData): Promise<RattrapageResponse> {
    return api.post(`/api/retards/retards/${retardId}/ajouter_rattrapage/`, data).then(res => res.data)
  },

  getRattrapages(): Promise<Rattrapage[]> {
    return api.get('/api/retards/rattrapages/').then(res => res.data)
  },

  getRattrapageDetails(id: number): Promise<Rattrapage> {
    return api.get(`/api/retards/rattrapages/${id}/`).then(res => res.data)
  },

  // ============================================
  // Utilisateurs gérables (pour managers)
  // ============================================
  
  getUtilisateursGerables(): Promise<GerableUserRetard[]> {
    return api.get('/api/retards/retards/utilisateurs_gerables/').then(res => res.data)
  }
}