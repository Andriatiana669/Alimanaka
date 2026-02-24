// frontend/src/api/reposmedicale.ts
import api from './index'
import type { 
  ReposMedical,
  ReposMedicalCalendarEventFromAPI,
  CreateReposMedicalData,
  GerableUserReposMedical,
  ReposMedicalParams,
  CalendrierReposMedicalParams,
  ValidationResponse,
  TransformationResponse,
  AnnulationReposMedicalResponse,
} from '@/types/reposmedicale'
import type { TypeCongeConfig } from '@/types/conges'

export const reposmedicaleApi = {
  // ============================================
  // Repos Médicaux
  // ============================================
  
  /**
   * Récupère les repos médicaux de l'utilisateur connecté
   * @param annee - Filtrer par année
   * @param statut - Filtrer par statut
   */
  getMesRepos(annee?: number, statut?: string): Promise<ReposMedical[]> {
    return api.get('/api/repos-medicaux/repos-medicaux/mes_repos/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  /**
   * Récupère les détails d'un repos médical spécifique
   * @param id - ID du repos médical
   */
  getReposMedicalDetails(id: number): Promise<ReposMedical> {
    return api.get(`/api/repos-medicaux/repos-medicaux/${id}/`).then(res => res.data)
  },

  /**
   * Crée un nouveau repos médical
   * @param data - Données du repos médical
   * @param userId - ID de l'utilisateur concerné (pour les managers)
   */
  createReposMedical(data: CreateReposMedicalData, userId?: number): Promise<ReposMedical> {
    const payload: any = { ...data }
    if (userId) {
      payload.user_id = userId
    }
    return api.post('/api/repos-medicaux/repos-medicaux/', payload).then(res => res.data)
  },

  // ============================================
  // Calendrier
  // ============================================
  
  /**
   * Récupère tous les événements pour le calendrier
   * @param params - Filtres (année, statut)
   */
  getCalendrier(params?: CalendrierReposMedicalParams): Promise<ReposMedicalCalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/repos-medicaux/repos-medicaux/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Actions sur les repos médicaux
  // ============================================
  
  /**
   * Valider directement un repos médical
   * @param id - ID du repos médical
   */
  validerReposMedical(id: number): Promise<ValidationResponse> {
    return api.post(`/api/repos-medicaux/repos-medicaux/${id}/valider/`).then(res => res.data)
  },

  /**
   * Transformer le repos médical en congé
   * @param id - ID du repos médical
   * @param type_conge - Type de congé (matin/midi/journee)
   */
  transformerEnConge(id: number, type_conge: string): Promise<TransformationResponse> {
    return api.post(`/api/repos-medicaux/repos-medicaux/${id}/transformer_en_conge/`, { type_conge }).then(res => res.data)
  },

  /**
   * Annuler un repos médical
   * @param id - ID du repos médical
   * @param commentaire - Motif de l'annulation (optionnel)
   */
  annulerReposMedical(id: number, commentaire?: string): Promise<AnnulationReposMedicalResponse> {
    return api.post(`/api/repos-medicaux/repos-medicaux/${id}/annuler/`, { commentaire }).then(res => res.data)
  },

  // ============================================
  // Types de congés (pour transformation)
  // ============================================
  
  /**
   * Récupère les types de congés pour la transformation
   */
  getTypesConge(): Promise<TypeCongeConfig[]> {
    return api.get('/api/conges/types-conge/').then(res => res.data)
  },

  // ============================================
  // Utilisateurs gérables (pour managers)
  // ============================================
  
  /**
   * Récupère la liste des utilisateurs que le manager peut gérer
   */
  getUtilisateursGerables(): Promise<GerableUserReposMedical[]> {
    return api.get('/api/repos-medicaux/repos-medicaux/utilisateurs_gerables/').then(res => res.data)
  }
}