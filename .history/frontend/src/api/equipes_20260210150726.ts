// frontend/src/api/equipes.ts
import api from './index'
import type { Equipe, EquipeMembre } from '@/types/user'

export const equipesApi = {
  // ← MODIFIER : Ajouter paramètre inclureInactives
  getAll(inclureInactives: boolean = true): Promise<Equipe[]> {
    return api.get('/equipes/', {
      params: { inclure_inactives: inclureInactives }
    }).then(res => res.data)
  },

  getById(id: number): Promise<Equipe> {
    return api.get(`/equipes/${id}/`).then(res => res.data)
  },

  create(data: Omit<Equipe, 'id' | 'date_creation' | 'niveau_hierarchique'>): Promise<Equipe> {
    return api.post('/equipes/', data).then(res => res.data)
  },

  // Dans frontend/src/api/equipes.ts
  // update(id: number, data: Partial<Equipe>): Promise<Equipe> {
  //   console.log('Appel API:', api.defaults.baseURL + `equipes/${id}/`)
  //   return api.patch(`/equipes/${id}/`, data).then(res => res.data)
  // },

  update(id: number, data: Partial<Equipe>): Promise<Equipe> {
    // Debug l'URL complète
    const fullUrl = api.defaults.baseURL + `equipes/${id}/`
    console.log('URL complète PATCH:', fullUrl)
    
    return api.patch(`equipes/${id}/`, data).then(res => res.data)
  },

  delete(id: number): Promise<void> {
    return api.delete(`/equipes/${id}/`)
  },

  // ← MODIFIER : Ajouter paramètre inclureInactives
  getArbre(inclureInactives: boolean = true): Promise<Equipe[]> {
    return api.get('/equipes/arbre/', {
      params: { inclure_inactives: inclureInactives }
    }).then(res => res.data)
  },

  getMembres(equipeId: number): Promise<EquipeMembre[]> {
    return api.get(`/equipes/${equipeId}/membres/`).then(res => res.data)
  },

  changerManager(equipeId: number, managerId: number): Promise<{ success: boolean }> {
    return api.post(`/equipes/${equipeId}/changer_manager/`, { manager_id: managerId })
      .then(res => res.data)
  }
}