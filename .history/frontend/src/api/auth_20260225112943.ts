// frontend/src/api/auth.ts
import api from './index'
import type { User } from '@/types/user'
import { buildAuthUrl } from '@/config/api'

export const authApi = {
  /**
   * Vérifier si une session est active
   */
  async checkSession(): Promise<{ authenticated: boolean; user: User }> {
    const response = await api.get('/api/auth/session/')
    return response.data
  },

  /**
   * Login SSO (redirection complète)
   */
  login(): void {
    window.location.href = buildAuthUrl('/login/')
  },

  /**
   * Logout SSO (redirection complète)
   */
  logout(): void {
    window.location.href = buildAuthUrl('/logout/')
  },

  /**
   * Logout via API (AJAX), renvoie URL de redirection si besoin
   */
  async logoutApi(): Promise<{ redirect_url: string }> {
    const response = await api.post('/auth/api/logout/')
    return response.data
  }
}