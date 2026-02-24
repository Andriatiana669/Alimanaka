// frontend/src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  withCredentials: true, // Important pour les cookies de session
  headers: {
    'Content-Type': 'application/json',
  },
})

// Intercepteur pour ajouter le CSRF token
api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

// Intercepteur pour gérer les erreurs
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Rediriger vers le login si non authentifié
      window.location.href = '/api/auth/login/'
    }
    return Promise.reject(error)
  }
)

function getCsrfToken(): string | null {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1]
  return cookieValue || null
}

export default api