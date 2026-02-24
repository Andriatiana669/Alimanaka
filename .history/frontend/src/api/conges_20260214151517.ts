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
  CalendrierParams
} from '@/types/conges'

export const congesApi = {
  // Types de congés
  getTypesConge(): Promise<TypeCongeConfig[]> {
    return api.get('/api/conges/types-conge/').then(res => res.data)
  },

  // Jours fériés
  getJoursFeries(): Promise<JourFerie[]> {
    return api.get('/api/conges/jours-feries/').then(res => res.data)
  },

  // Jours exceptionnels
  getJoursExceptionnels(annee?: number): Promise<JourExceptionnel[]> {
    return api.get('/api/conges/jours-exceptionnels/', {
      params: annee ? { annee } : undefined
    }).then(res => res.data)
  },

  // Congés annuels
  getCongesAnnuels(): Promise<CongeAnnuel[]> {
    return api.get('/api/conges/conges-annuels/').then(res => res.data)
  },

  // Mes congés
  getMesConges(annee?: number, statut?: string): Promise<Conge[]> {
    return api.get('/api/conges/conges/mes_conges/', {
      params: { annee, statut }
    }).then(res => res.data)
  },

  // Calendrier complet avec filtres (événements pour le calendar)
  getCalendrier(params?: CalendrierParams): Promise<CalendarEventFromAPI[]> {
    const queryParams: any = {}
    if (params?.annee) queryParams.annee = params.annee
    if (params?.pole) queryParams.pole = params.pole
    if (params?.equipe) queryParams.equipe = params.equipe
    
    return api.get('/api/conges/conges/calendrier/', {
      params: Object.keys(queryParams).length > 0 ? queryParams : undefined
    }).then(res => res.data)
  },

  // Liste des utilisateurs gérables (pour managers)
  getUtilisateursGerables(): Promise<GerableUser[]> {
    return api.get('/api/conges/conges/utilisateurs_gerables/').then(res => res.data)
  },

  getCongeDetails(id: number): Promise<any> {
    return api.get(`/api/conges/conges/${id}/`).then(res => res.data)
  },


  // Créer une demande de congé (avec user_id optionnel pour managers)
  createConge(data: CreateCongeData & { user_id?: number }): Promise<Conge> {
    return api.post('/api/conges/conges/', data).then(res => res.data)
  },

  // Annuler un congé
  annulerConge(id: number): Promise<{ success: boolean; message: string }> {
    return api.post(`/api/conges/conges/${id}/annuler/`).then(res => res.data)
  },

  // Exporter tous les congés (super admin)
  exportAll(): Promise<Blob> {
    return api.get('/api/conges/conges/export/', {
      responseType: 'blob'
    }).then(res => res.data)
  },

  // Exporter mes congés
  exportMine(): Promise<Blob> {
    return api.get('/api/conges/conges/export_mine/', {
      responseType: 'blob'
    }).then(res => res.data)
  }
}