// frontend/src/api/users.ts - REMPLACE LE CONTENU EXISTANT
import api from './index'
import type { User, UpdatePseudoData, UpdatePoleEquipeData } from '@/types/user'

export const usersApi = {
  // Récupérer tous les utilisateurs
  async getAllUsers(): Promise<User[]> {
    const response = await api.get('/users/list/')
    return response.data
  },

  // Récupérer le profil utilisateur
  async getUserProfile(): Promise<User> {
    const response = await api.get('/users/profile/')
    return response.data
  },

  // Dans frontend/src/api/users.ts
  async getCurrentUser(): Promise<User> {
    return api.get('/users/current/').then(res => res.data)
  },

  // Mettre à jour le pseudo
  async updatePseudo(data: UpdatePseudoData) {
    const response = await api.post('/users/update-pseudo/', data)
    return response.data
  },

  // Mettre à jour le pôle et l'équipe (admin)
  async updatePoleEquipe(data: UpdatePoleEquipeData) {
    const response = await api.post('/users/update_pole_equipe/', data)
    return response.data
  },

  // Mettre à jour l'email
  async updateEmail(data: { email: string }) {
    const response = await api.post('/users/update-email/', data)
    return response.data
  },

  // Éditer un utilisateur spécifique (admin)
  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/${id}/`, data)
    return response.data
  },

  // Récupérer un utilisateur par ID
  async getById(id: number): Promise<User> {
    const response = await api.get(`/users/${id}/`)
    return response.data
  }
}