// Configuration centralisée des URLs API

export const API_CONFIG = {
  // Base URL de l'API (avec fallback sécurisé)
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:4000/api',
  AUTH_URL: import.meta.env.VITE_AUTH_BASE_URL || 'http://localhost:4000/api/auth',
  FRONTEND_URL: import.meta.env.VITE_FRONTEND_URL || 'http://localhost:4002',
  
  // Endpoints spécifiques
  ENDPOINTS: {
    // Auth
    LOGIN: '/login/',
    LOGOUT: '/logout/',
    STATUS: '/status/',
    CALLBACK: '/callback/',
    
    // Users
    CURRENT_USER: '/users/current_user/',
    USERS: '/users/',
    PROFILE: '/users/profile/',
    UPDATE_PSEUDO: '/users/update_pseudo/',
  }
} as const

// Helper pour construire les URLs complètes
export const buildUrl = (endpoint: string): string => {
  return `${API_CONFIG.BASE_URL}${endpoint}`
}

export const buildAuthUrl = (endpoint: string): string => {
  return `${API_CONFIG.AUTH_URL}${endpoint}`
}