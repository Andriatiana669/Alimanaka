// frontend/src/api/conges.ts
import api from './index'
import type { 
  TypeCongeConfig, 
  JourFerie, 
  JourExceptionnel, 
  CongeAnnuel, 
  Conge, 
  CalendarEventFromAPI,
  CreateCongeData,
  GerableUser,
  CalendrierParams,
  // NOUVEAU
  Droit,
  ValidationPartielleResponse,
  AnnulationPartielleResponse,
  ValidationResponse,
  RefusResponse
} from '@/types/conges'

export const congesApi = {
  // ============================================
  // Configuration des types de congés
  // ============================================
  
  /**
   * Récupère la liste des types de congés configurés
   */
  getTypesConge(): Promise<TypeCongeConfig[]> {
    return api.get('/api/conges/types-conge/').then(res => res.data)
  },

  // ============================================
  // Jours fériés
  // ============================================
  
  /**
   * Récupère la liste des jours fériés actifs
   */
  getJoursFeries(): Promise<JourFerie[]> {
    return api.get('/api/conges/jours-feries/').then(res => res.data)
  },

  // ============================================
  // Jours exceptionnels
  // ============================================
  
  /**
   * Récupère les jours exceptionnels pour une année donnée
   * @param annee - Année (optionnelle, année courante par défaut)
   */
  getJoursExceptionnels(annee?: number): Promise<JourExceptionnel[]> {
    return api.get('/api/conges/jours-exceptionnels/', {
      params: annee ? { annee } : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Congés annuels
  // ============================================
  
  /**
   * Récupère les périodes de congés annuels actives
   */
  getCongesAnnuels(): Promise<CongeAnnuel[]> {
    return api.get('/api/conges/conges-annuels/').then(res => res.data)
  },

  // ============================================
  // NOUVEAU : Droits (congés exceptionnels)
  // ============================================
  
  /**
   * Récupère la liste des droits disponibles
   */
  getDroits(): Promise<Droit[]> {
    return api.get('/api/conges/droits/').then(res => res.data)
  },

  // ============================================
  // Mes congés
  // ============================================
  
  /**
   * Récupère les congés de l'utilisateur connecté
   * @param annee - Filtrer par année
   * @param statut - Filtrer par statut
   */
  getMesConges(annee?: number, statut?: string): Promise<Conge[]> {
    return api.get('/api/conges/conges/mes_conges/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  // ============================================
  // Calendrier
  // ============================================
  
  /**
   * Récupère tous les événements pour le calendrier
   * @param params - Filtres (année, pôle, équipe, statut)
   */
  getCalendrier(params?: CalendrierParams & { statut?: string }): Promise<CalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.pole) queryParams.pole = params.pole
    if (params?.equipe) queryParams.equipe = params.equipe
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/conges/conges/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // ============================================
  // Utilisateurs gérables (pour managers)
  // ============================================
  
  /**
   * Récupère la liste des utilisateurs que le manager peut gérer
   */
  getUtilisateursGerables(): Promise<GerableUser[]> {
    return api.get('/api/conges/conges/utilisateurs_gerables/').then(res => res.data)
  },

  // ============================================
  // Détails d'un congé
  // ============================================
  
  /**
   * Récupère les détails complets d'un congé spécifique
   * @param id - ID du congé
   */
  getCongeDetails(id: number): Promise<Conge> {
    return api.get(`/api/conges/conges/${id}/`).then(res => res.data)
  },

  // ============================================
  // Création de congé
  // ============================================
  
  /**
   * Crée une nouvelle demande de congé
   * @param data - Données du congé (incluant optionnellement user_id pour les managers)
   */
  createConge(data: CreateCongeData & { user_id?: number }): Promise<Conge> {
    return api.post('/api/conges/conges/', data).then(res => res.data)
  },

  // ============================================
  // Actions sur les congés
  // ============================================
  
  /**
   * Valider complètement un congé
   * @param id - ID du congé
   */
  validerConge(id: number): Promise<ValidationResponse> {
    return api.post(`/api/conges/conges/${id}/valider/`).then(res => res.data)
  },

  /**
   * Valider partiellement un congé (certains jours seulement)
   * @param id - ID du congé
   * @param dates - Liste des dates à valider (format YYYY-MM-DD)
   */
  validerCongePartiel(id: number, dates: string[]): Promise<ValidationPartielleResponse> {
    return api.post(`/api/conges/conges/${id}/valider/`, { dates }).then(res => res.data)
  },

  /**
   * Refuser un congé
   * @param id - ID du congé
   * @param commentaire - Motif du refus (optionnel)
   */
  refuserConge(id: number, commentaire?: string): Promise<RefusResponse> {
    return api.post(`/api/conges/conges/${id}/refuser/`, { commentaire }).then(res => res.data)
  },

  /**
   * Annuler complètement un congé
   * @param id - ID du congé
   */
  annulerConge(id: number): Promise<{ success: boolean; message: string; remboursement_effectue?: boolean }> {
    return api.post(`/api/conges/conges/${id}/annuler/`).then(res => res.data)
  },

  /**
   * Annuler partiellement un congé (rembourser certains jours)
   * @param id - ID du congé
   * @param dates - Liste des dates à annuler (format YYYY-MM-DD)
   */
  annulerCongePartiel(id: number, dates: string[]): Promise<AnnulationPartielleResponse> {
    return api.post(`/api/conges/conges/${id}/annuler_partiel/`, { dates }).then(res => res.data)
  },

  // ============================================
  // Export Excel
  // ============================================
  
  /**
   * Exporter tous les congés (admin uniquement)
   * Retourne un Blob à télécharger
   */
  exportAll(): Promise<Blob> {
    return api.get('/api/conges/conges/export/', {
      responseType: 'blob'
    }).then(res => res.data)
  },

  /**
   * Exporter mes congés (utilisateur connecté)
   * Retourne un Blob à télécharger
   */
  exportMine(): Promise<Blob> {
    return api.get('/api/conges/conges/export_mine/', {
      responseType: 'blob'
    }).then(res => res.data)
  },

  // ============================================
  // Vérifications diverses
  // ============================================
  
  /**
   * Vérifie si une date est disponible pour une demande
   * Utile pour le frontend avant soumission
   * @param date - Date à vérifier (format YYYY-MM-DD)
   */
  async checkDateDisponible(date: string): Promise<{ disponible: boolean; raison?: string }> {
    try {
      const events = await this.getCalendrier({ annee: new Date(date).getFullYear() })
      const dateObj = new Date(date)
      dateObj.setHours(0, 0, 0, 0)
      
      const event = events.find(e => {
        const start = new Date(e.start)
        start.setHours(0, 0, 0, 0)
        
        if (!e.end) {
          return start.getTime() === dateObj.getTime() && e.isBlocked
        }
        
        const end = new Date(e.end)
        end.setHours(0, 0, 0, 0)
        const endInclusive = new Date(end)
        endInclusive.setDate(endInclusive.getDate() - 1)
        
        return dateObj >= start && dateObj <= endInclusive && e.isBlocked
      })
      
      if (event) {
        return { disponible: false, raison: event.title }
      }
      
      return { disponible: true }
    } catch (error) {
      console.error('Erreur vérification date:', error)
      return { disponible: true } // En cas d'erreur, on laisse passer
    }
  },

  /**
   * Calcule la déduction estimée pour une période donnée
   * (Version frontend, mais idéalement à faire côté backend)
   */
  async estimerDeduction(
    type_conge: string,
    date_debut: string,
    date_fin: string
  ): Promise<{ jours_ouvres: number; deduction: number }> {
    try {
      // Idéalement, appeler une API backend pour ce calcul
      // Mais pour l'instant, on retourne une estimation basique
      const start = new Date(date_debut)
      const end = new Date(date_fin)
      const types = await this.getTypesConge()
      const type = types.find(t => t.type_conge === type_conge)
      
      if (!type) {
        return { jours_ouvres: 0, deduction: 0 }
      }
      
      let jours_ouvres = 0
      let deduction = 0
      const current = new Date(start)
      
      while (current <= end) {
        const jourSemaine = current.getDay() // 0 = Dimanche, 6 = Samedi
        if (jourSemaine !== 0 && jourSemaine !== 6) { // Pas weekend
          jours_ouvres++
          
          if (jourSemaine === 5 && type.vendredi_deduction) { // Vendredi
            deduction += type.vendredi_deduction
          } else {
            deduction += type.deduction_jours
          }
        }
        current.setDate(current.getDate() + 1)
      }
      
      return { jours_ouvres, deduction }
    } catch (error) {
      console.error('Erreur estimation:', error)
      return { jours_ouvres: 0, deduction: 0 }
    }
  }
}