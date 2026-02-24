// frontend/src/api/users.ts
import api from './index'

export const usersApi = {
  // Utilise la route auto-générée par le ViewSet
  getAllUsers: () => api.get('/users/'),  // au lieu de '/users/list/'
  
  getCurrentUser: () => api.get('/users/current/'),
  updatePseudo: (data: { pseudo?: string; pseudo_format?: string }) => 
    api.post('/users/update-pseudo/', data),
}