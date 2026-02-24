// frontend/src/api/poles.ts
import api from './index'
import type { Pole } from '@/types/user'

export const polesApi = {
  // Récupérer tous les pôles
  getAll(): Promise<Pole[]> {
    return api.get('/poles/').then(res => res.data)
  },

  // Récupérer un pôle par ID
  getById(id: number): Promise<Pole> {
    return api.get(`/poles/${id}/`).then(res => res.data)
  },

  // Créer un pôle (admin)
  create(data: Omit<Pole, 'id' | 'date_creation'>): Promise<Pole> {
    return api.post('/poles/', data).then(res => res.data)
  },

  // Mettre à jour un pôle (admin)
  update(id: number, data: Partial<Pole>): Promise<Pole> {
    return api.patch(`/poles/${id}/`, data).then(res => res.data)
  },

  // Supprimer un pôle (admin)
  delete(id: number): Promise<void> {
    return api.delete(`/poles/${id}/`)
  },

  // Récupérer seulement les pôles actifs
  getActifs(): Promise<Pole[]> {
    return api.get('/poles/actifs/').then(res => res.data)
  }
}