// frontend/src/api/users.ts - REMPLACE LE CONTENU EXISTANT
import type { UserSoldeConge } from '@/types/conges'
import api from './index'
import type { User, UpdatePseudoData, UpdatePoleEquipeData } from '@/types/user'


export interface Pole {
  id: number
  code: string
  nom: string
  description?: string
}

export interface Equipe {
  id: number
  nom: string
  pole: number
  pole_details?: Pole
}


export const usersApi = {
  // Récupérer tous les utilisateurs
  async getAllUsers(): Promise<User[]> {
    const response = await api.get('/api/users/list/')
    return response.data
  },

  // Récupérer le profil utilisateur
  async getUserProfile(): Promise<User> {
    const response = await api.get('/api/users/profile/')
    return response.data
  },

  // Mettre à jour le pseudo
  async updatePseudo(data: any) { // Temporairement any
    console.log('API - données reçues:', data)
    const response = await api.post('/api/users/update-pseudo/', data)
    console.log('API - réponse:', response.data)
    return response.data
  },

  // Mettre à jour le pôle et l'équipe (admin)
  async updatePoleEquipe(data: UpdatePoleEquipeData) {
    const response = await api.post('/api/users/update_pole_equipe/', data)
    return response.data
  },

  // Mettre à jour l'email
  async updateEmail(data: { email: string }) {
    const response = await api.post('/api/users/update-email/', data)
    return response.data
  },

  // Éditer un utilisateur spécifique (admin)
  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/api/users/${id}/`, data)
    return response.data
  },

  // Récupérer un utilisateur par ID
  async getById(id: number): Promise<User> {
    const response = await api.get(`/api/users/${id}/`)
    return response.data
  },

  // Utilisateur actuelle
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/api/users/current/')
    return response.data
  },

  // Obtenir les soldes de conges
  async getSolde(): Promise<UserSoldeConge> {
    return api.get('/api/users/solde/').then(res =>res.data)
  },

   async getPoles(): Promise<Pole[]> {
    const response = await api.get('/api/org/poles/')
    return response.data
  },

  async getEquipesByPole(poleId: number): Promise<Equipe[]> {
    const response = await api.get(`/api/org/poles/${poleId}/equipes/`)
    return response.data
  },

  async getEquipes(): Promise<Equipe[]> {
    const response = await api.get('/api/users/equipes/')
    return response.data
  }
  
}
