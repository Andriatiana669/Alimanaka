// frontend/src/api/users.ts
import api from './index'
import type { User, UpdatePseudoData } from '@/types/user'

// frontend/src/api/users.ts
export const usersApi = {
  async getAllUsers(): Promise<User[]> {
    // Change l'URL pour utiliser /list/ au lieu de /users/
    const response = await api.get('/users/list/')
    return response.data
  },

  async getUserProfile(): Promise<User> {
    const response = await api.get('/users/profile/')
    return response.data
  },

  async updatePseudo(data: UpdatePseudoData) {
    const response = await api.post('/users/update-pseudo/', data)
    return response.data
  },


  // Pour éditer un utilisateur spécifique
  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/${id}/`, data)
    return response.data
  }
}