// frontend/src/api/index.ts
import axios from 'axios'
import { buildAuthUrl, API_CONFIG } from '@/config/api'

// Instance axios pour toutes les requêtes vers le backend
const api = axios.create({
  baseURL: API_CONFIG.BASE_URL,  // Dynamique selon .env
  withCredentials: true,          // Envoie les cookies de session
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Intercepteur CSRF : ajoute le token à chaque requête
api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken()
  if (csrfToken && config.headers) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

// Intercepteur réponses : si 401, redirection login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = buildAuthUrl('/login/')
    }
    return Promise.reject(error)
  }
)

// Récupérer le CSRF token depuis les cookies
function getCsrfToken(): string | null {
  const cookieValue = document.cookie
    .split('; ')
    .find(row => row.startsWith('csrftoken='))
    ?.split('=')[1]
  return cookieValue || null
}

export default api