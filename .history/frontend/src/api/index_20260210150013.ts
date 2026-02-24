import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',  // URL complète du backend
  // baseURL: 'http://localhost:8000/api',  // A changer
  withCredentials: true,  // CRUCIAL: envoie les cookies de session
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
})

// Intercepteur CSRF
api.interceptors.request.use((config) => {
  const csrfToken = getCsrfToken()
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
})

// Intercepteur erreurs d'auth
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Rediriger vers le login SSO
      window.location.href = 'http://localhost:8000/api/auth/login/'
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