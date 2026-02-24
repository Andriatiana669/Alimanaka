// frontend/src/api/users.ts
import api from './index'
import type { User, UpdatePseudoData } from '@/types/user'

// frontend/src/api/users.ts
// frontend/src/api/users.ts
export const usersApi = {
  async getAllUsers(): Promise<User[]> {
    const response = await api.get('/users/all/')  // ← /all/ au lieu de /users/
    return response.data
  },

  async getUserProfile(): Promise<User> {
    const response = await api.get('/users/me/profile/')  // ← /me/profile/
    return response.data
  },

  async updatePseudo(data: UpdatePseudoData) {
    const response = await api.post('/users/me/update-pseudo/', data)  // ← /me/
    return response.data
  },

  async updateEmail(data: { email: string }) {
    const response = await api.post('/users/me/update-email/', data)  // ← /me/
    return response.data
  },

  async updateUser(id: number, data: Partial<User>): Promise<User> {
    const response = await api.patch(`/users/${id}/detail/`, data)  // ← /detail/
    return response.data
  }
}