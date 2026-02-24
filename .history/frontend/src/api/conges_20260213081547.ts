// frontend/src/api/conges.ts
import api from './index'
import type { 
  TypeCongeConfig, 
  JourFerie, 
  JourExceptionnel, 
  CongeAnnuel, 
  Conge, 
  CalendarEventFromAPI,
  CreateCongeData 
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

  // Calendrier complet (événements pour le calendar)
  getCalendrier(annee?: number): Promise<CalendarEvent[]> {
    return api.get('/api/conges/conges/calendrier/', {
      params: annee ? { annee } : undefined
    }).then(res => res.data)
  },

  // Créer une demande de congé
  createConge(data: CreateCongeData): Promise<Conge> {
    return api.post('/api/conges/conges/', data).then(res => res.data)
  },

  // Annuler un congé
  annulerConge(id: number): Promise<{ success: boolean; message: string }> {
    return api.post(`/api/conges/conges/${id}/annuler/`).then(res => res.data)
  },

  // Exporter tous les congés (admin)
  exportAll(): Promise<Blob> {
    return api.get('/api/conges/conges/export/', {
      responseType: 'blob'
    }).then(res => res.data)
  },

  // Exporter mes congés
  exportMine(): Promise<Blob> {
    return api.get('/api/conges/conges/mes_conges/', {
      params: { export: true },
      responseType: 'blob'
    }).then(res => res.data)
  }
}