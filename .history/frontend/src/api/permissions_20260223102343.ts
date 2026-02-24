// frontend/src/api/permissions.ts
import api from './index'
import type { 
  Permission,
  PermissionCalendarEventFromAPI,
  CreatePermissionData,
  GerableUserPermission,
  PermissionsParams,
  CalendrierPermissionsParams,
  RetourResponse,
  RattrapageResponse,
  TransformationResponse,
  AnnulationPermissionResponse,
} from '@/types/permissions'
import type { TypeCongeConfig } from '@/types/conges'

export const permissionsApi = {
  // ============================================
  // Permissions
  // ============================================
  
  /**
   * Récupère les permissions de l'utilisateur connecté
   * @param annee - Filtrer par année
   * @param statut - Filtrer par statut
   */
  getMesPermissions(annee?: number, statut?: string): Promise<Permission[]> {
    return api.get('/api/permissions/permissions/mes_permissions/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  /**
   * Récupère les détails d'une permission spécifique
   * @param id - ID de la permission
   */
  getPermissionDetails(id: number): Promise<Permission> {
    return api.get(`/api/permissions/permissions/${id}/`).then(res => res.data)
  },

  /**
   * Crée une nouvelle permission
   * @param data - Données de la permission (incluant optionnellement user_id pour les managers)
   */
  createPermission(data: CreatePermissionData & { user_id?: number }): Promise<Permission> {
    return api.post('/api/permissions/permissions/', data).then(res => res.data)
  },

  // ============================================
  // Calendrier
  // ============================================
  
  /**
   * Récupère tous les événements pour le calendrier
   * @param params - Filtres (année, statut)
   */
  getCalendrier(params?: CalendrierPermissionsParams): Promise<PermissionCalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/permissions/permissions/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Actions sur les permissions
  // ============================================
  
  /**
   * Enregistrer le retour (bouton 'De retour')
   * @param id - ID de la permission
   * @param heure_arrivee_reelle - Heure d'arrivée réelle
   */
  enregistrerRetour(id: number, heure_arrivee_reelle: string): Promise<RetourResponse> {
    return api.post(`/api/permissions/permissions/${id}/retour/`, { heure_arrivee_reelle }).then(res => res.data)
  },

  /**
   * Ajouter une session de rattrapage
   * @param id - ID de la permission
   * @param data - Données du rattrapage
   */
  ajouterRattrapage(id: number, data: {
    date_rattrapage: string
    heure_debut: string
    heure_fin: string
    commentaire?: string | null
  }): Promise<RattrapageResponse> {
    return api.post(`/api/permissions/permissions/${id}/ajouter_rattrapage/`, data).then(res => res.data)
  },

  /**
   * Transformer la permission en congé
   * @param id - ID de la permission
   * @param type_conge - Type de congé (matin/midi/journee)
   */
  transformerEnConge(id: number, type_conge: string): Promise<TransformationResponse> {
    return api.post(`/api/permissions/permissions/${id}/transformer_en_conge/`, { type_conge }).then(res => res.data)
  },

  /**
   * Annuler une permission
   * @param id - ID de la permission
   * @param commentaire - Motif de l'annulation (optionnel)
   */
  annulerPermission(id: number, commentaire?: string): Promise<AnnulationPermissionResponse> {
    return api.post(`/api/permissions/permissions/${id}/annuler/`, { commentaire }).then(res => res.data)
  },


  /* Valider complètement un congé */
  approuverPermission(id: number): Promise<{
    success: boolean;
    message: string;
    valide_par: string;
    date_validation: string;
  }> {
    return api.post(`/api/permissions/permissions/${id}/valider/`).then(res => res.data)
  }

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
  getUtilisateursGerables(): Promise<GerableUserPermission[]> {
    return api.get('/api/permissions/permissions/utilisateurs_gerables/').then(res => res.data)
  }
}