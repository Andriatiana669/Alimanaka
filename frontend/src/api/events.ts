// frontend/src/api/events.ts
import api from './index'
import type { 
  Event,
  EventCalendarEventFromAPI,
  EventParams,
  EventType,
  EventUser
} from '@/types/events'

export const eventsApi = {
  // ============================================
  // Événements
  // ============================================
  
  /**
   * Récupère tous les événements pour le calendrier
   * @param params - Filtres (année, mois, type, statut)
   */
  getCalendrier(params?: EventParams): Promise<EventCalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.mois) queryParams.mois = params.mois
    if (params?.type) queryParams.type = params.type
    if (params?.statut) queryParams.statut = params.statut
    if (params?.skip_cache) queryParams.skip_cache = params.skip_cache
    
    return api.get('/api/events/events/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  /**
   * Récupère les détails d'un événement spécifique
   * @param id - ID de l'événement
   */
  getEventDetails(id: number): Promise<Event> {
    return api.get(`/api/events/events/${id}/`).then(res => res.data)
  },

  // ============================================
  // Utilitaires
  // ============================================
  
  /**
   * Récupère la liste des types d'événements
   */
  getTypes(): Promise<EventType[]> {
    return api.get('/api/events/events/types/').then(res => res.data)
  },

  /**
   * Récupère la liste des utilisateurs avec des événements
   */
  getUtilisateurs(): Promise<EventUser[]> {
    return api.get('/api/events/events/utilisateurs/').then(res => res.data)
  },

  // ============================================
  // Export (optionnel)
  // ============================================
  
  /**
   * Exporte les événements au format CSV
   * @param params - Filtres
   */
  exportEvents(params?: EventParams): Promise<Blob> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.type) queryParams.type = params.type
    if (params?.statut) queryParams.statut = params.statut
    
    return api.get('/api/events/events/export/', {
      params: queryParams,
      responseType: 'blob'
    }).then(res => res.data)
  }
}