// API Retards (similaire à cnges.ts)

import api from './index';
import type { 
  TypeRetardConfig, 
  Retard, 
  RetardCreateData, 
  Rattrapage,
  RattrapageCreateData,
  RetardFilters 
} from '@/types/retards';

export const retardsApi = {
  // Types de retard (config)
  getTypesRetard: () => 
    api.get<TypeRetardConfig[]>('/retards/types-retard/'),
  
  // CRUD Retards
  getRetards: (filters?: RetardFilters) => {
    const params = new URLSearchParams();
    if (filters?.statut) params.append('statut', filters.statut);
    if (filters?.annee) params.append('annee', filters.annee.toString());
    return api.get<Retard[]>(`/retards/retards/?${params.toString()}`);
  },
  
  getMesRetards: (filters?: RetardFilters) => {
    const params = new URLSearchParams();
    if (filters?.statut) params.append('statut', filters.statut);
    if (filters?.annee) params.append('annee', filters.annee.toString());
    return api.get<Retard[]>(`/retards/retards/mes_retards/?${params.toString()}`);
  },
  
  getRetard: (id: number) => 
    api.get<Retard>(`/retards/retards/${id}/`),
  
  createRetard: (data: RetardCreateData) => 
    api.post<Retard>('/retards/retards/', data),
  
  updateRetard: (id: number, data: Partial<RetardCreateData>) => 
    api.patch<Retard>(`/retards/retards/${id}/`, data),
  
  deleteRetard: (id: number) => 
    api.delete(`/retards/retards/${id}/`),
  
  // Actions spécifiques
  rattraperRetard: (id: number, data: RattrapageCreateData) => 
    api.post<{ success: boolean; message: string; heures_restantes: string; statut: string; rattrapage: Rattrapage }>(
      `/retards/retards/${id}/rattraper/`, 
      data
    ),
  
  annulerRetard: (id: number, commentaire?: string) => 
    api.post<{ success: boolean; message: string }>(
      `/retards/retards/${id}/annuler/`,
      { commentaire }
    ),
  
  // Calendrier
  getCalendrier: (annee: number, poleId?: number, equipeId?: number) => {
    const params = new URLSearchParams();
    params.append('annee', annee.toString());
    if (poleId) params.append('pole', poleId.toString());
    if (equipeId) params.append('equipe', equipeId.toString());
    return api.get(`/retards/retards/calendrier/?${params.toString()}`);
  },
  
  // Utilisateurs gérables (pour managers)
  getUtilisateursGerables: () => 
    api.get<Array<{
      id: number;
      display_name: string;
      username: string;
      equipe_nom: string;
    }>>('/retards/retards/utilisateurs_gerables/'),
  
  // Export
  exportRetards: () => 
    api.get('/retards/retards/export/', { responseType: 'blob' }),
};