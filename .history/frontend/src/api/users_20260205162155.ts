// frontend/src/api/users.ts
import api from './index'
import type { User, UpdatePseudoData } from '@/types/user'

export const usersApi = {
  async getAllUsers(): Promise<User[]> {
    const response = await api.get('/users/users/')
    return response.data
  },

  async getUserProfile(): Promise<User> {
    const response = await api.get('/users/profile/')
    return response.data
  },

  async updatePseudo(data: UpdatePseudoData): Promise<{ message: string; display_name: string }> {
    const response = await api.post('/users/update-pseudo/', data, {
      headers: {
        'X-CSRFToken': getCsrfToken(),
      }
    })
    return response.data
  },

  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/users/${id}/`, data)
    return response.data
  }
}