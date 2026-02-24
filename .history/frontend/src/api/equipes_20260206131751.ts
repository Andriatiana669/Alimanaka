// frontend/src/api/equipes.ts
import api from './index'
import type { Equipe, EquipeMembre } from '@/types/user'

export const equipesApi = {
  // Récupérer toutes les équipes
  getAll(): Promise<Equipe[]> {
    return api.get('/equipes/').then(res => res.data)
  },

  // Récupérer un équipe par ID
  getById(id: number): Promise<Equipe> {
    return api.get(`/equipes/${id}/`).then(res => res.data)
  },

  // Créer une équipe (admin)
  create(data: Omit<Equipe, 'id' | 'date_creation' | 'niveau_hierarchique'>): Promise<Equipe> {
    return api.post('/equipes/', data).then(res => res.data)
  },

  // Mettre à jour une équipe (admin ou manager)
  update(id: number, data: Partial<Equipe>): Promise<Equipe> {
    return api.patch(`/equipes/${id}/`, data).then(res => res.data)
  },

  // Supprimer une équipe (admin)
  delete(id: number): Promise<void> {
    return api.delete(`/equipes/${id}/`)
  },

  // Récupérer l'arborescence complète
  getArbre(): Promise<Equipe[]> {
    return api.get('/equipes/arbre/').then(res => res.data)
  },

  // Récupérer les membres d'une équipe
  getMembres(equipeId: number): Promise<EquipeMembre[]> {
    return api.get(`/equipes/${equipeId}/membres/`).then(res => res.data)
  },

  // Changer le manager d'une équipe
  changerManager(equipeId: number, managerId: number): Promise<{ success: boolean }> {
    return api.post(`/equipes/${equipeId}/changer_manager/`, { manager_id: managerId })
      .then(res => res.data)
  }
}