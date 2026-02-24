// frontend/src/api/ostie.ts
import api from './index'
import type { 
  Ostie,
  OstieCalendarEventFromAPI,
  CreateOstieData,
  GerableUserOstie,
  OstieParams,
  CalendrierOstieParams,
  ValidationOstieResponse,
  TransformationOstieResponse,
  AnnulationOstieResponse,
  ValidationOstieForm,
  TransformationOstieForm
} from '@/types/ostie'

export const ostieApi = {
  // ============================================
  // OSTIES
  // ============================================
  
  /**
   * Récupère les OSTIES de l'utilisateur connecté
   * @param annee - Filtrer par année
   * @param statut - Filtrer par statut
   */
  getMesOsties(annee?: number, statut?: string): Promise<Ostie[]> {
    return api.get('/api/osties/osties/mes_osties/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  /**
   * Récupère les détails d'un OSTIE spécifique
   * @param id - ID de l'OSTIE
   */
  getOstieDetails(id: number): Promise<Ostie> {
    return api.get(`/api/osties/osties/${id}/`).then(res => res.data)
  },

  /**
   * Crée un nouvel OSTIE
   * @param data - Données de l'OSTIE
   * @param userId - ID de l'utilisateur concerné (pour les managers)
   */
  createOstie(data: CreateOstieData, userId?: number): Promise<Ostie> {
    const payload: any = { ...data }
    if (userId) {
      payload.user_id = userId
    }
    return api.post('/api/osties/osties/', payload).then(res => res.data)
  },

  // ============================================
  // Calendrier
  // ============================================
  
  /**
   * Récupère tous les événements pour le calendrier
   * @param params - Filtres (année, statut)
   */
  getCalendrier(params?: CalendrierOstieParams): Promise<OstieCalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/osties/osties/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Actions sur les OSTIES
  // ============================================
  
  /**
   * Valider directement un OSTIE
   * @param id - ID de l'OSTIE
   * @param data - Données de validation (heure_fin)
   */
  validerOstie(id: number, data: ValidationOstieForm): Promise<ValidationOstieResponse> {
    return api.post(`/api/osties/osties/${id}/valider/`, data).then(res => res.data)
  },

  /**
   * Transformer l'OSTIE en repos médical
   * @param id - ID de l'OSTIE
   * @param data - Données de transformation
   */
  transformerEnRepos(id: number, data: TransformationOstieForm): Promise<TransformationOstieResponse> {
    return api.post(`/api/osties/osties/${id}/transformer_en_repos/`, data).then(res => res.data)
  },

  /**
   * Annuler un OSTIE
   * @param id - ID de l'OSTIE
   * @param commentaire - Motif de l'annulation (optionnel)
   */
  annulerOstie(id: number, commentaire?: string): Promise<AnnulationOstieResponse> {
    return api.post(`/api/osties/osties/${id}/annuler/`, { commentaire }).then(res => res.data)
  },

  // ============================================
  // Utilisateurs gérables (pour managers)
  // ============================================
  
  /**
   * Récupère la liste des utilisateurs que le manager peut gérer
   */
  getUtilisateursGerables(): Promise<GerableUserOstie[]> {
    return api.get('/api/osties/osties/utilisateurs_gerables/').then(res => res.data)
  }
}