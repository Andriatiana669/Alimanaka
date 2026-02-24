import api from './index'
import type { User } from '@/types/user'

export const authApi = {
  // Vérifier la session active
  async checkSession(): Promise<{ authenticated: boolean; user: User }> {
    const response = await api.get('/api/auth/session/')
    return response.data
  },

  // Lancer le login SSO (redirection complète)
  login(): void {
    window.location.href = 'http://localhost:8000/api/auth/login/'
  },

  // Lancer le logout SSO (redirection complète)
  logout(): void {
    window.location.href = 'http://localhost:8000/api/auth/logout/'
  },

  // Logout via API (pour usage AJAX si besoin)
  async logoutApi(): Promise<{ redirect_url: string }> {
    const response = await api.post('/auth/api/logout/')
    return response.data
  }
}