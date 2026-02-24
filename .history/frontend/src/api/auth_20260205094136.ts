// frontend/src/api/auth.ts
import api from './index'
import type { User } from '@/types/user'

export const authApi = {
  async getCurrentUser(): Promise<User> {
    const response = await api.get('/users/current/')
    return response.data
  },

  async login(): Promise<void> {
    window.location.href = '/api/auth/login/'
  },

  async logout(): Promise<void> {
    window.location.href = '/api/auth/logout/'
  }
}