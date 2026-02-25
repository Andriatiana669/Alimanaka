import api from './index'
import type { User } from '@/types/user'
import { buildAuthUrl } from '@/config/api'  // ← IMPORTANT

export const authApi = {
  async checkSession(): Promise<{ authenticated: boolean; user: User }> {
    const response = await api.get('/session/')  // attention au path, pas de /api/auth ici
    return response.data
  },

  login(): void {
    window.location.href = buildAuthUrl('/login/')
  },

  logout(): void {
    window.location.href = buildAuthUrl('/logout/')
  },

  async logoutApi(): Promise<{ redirect_url: string }> {
    const response = await api.post('/logout/')
    return response.data
  }
}