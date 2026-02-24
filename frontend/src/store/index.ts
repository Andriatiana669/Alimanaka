import { createPinia } from 'pinia'

export const pinia = createPinia()

export default pinia

// Export des stores pour import facile
export { useAuthStore } from './auth'
export { useUsersStore } from './users'
export { usePolesStore } from './poles'
export { useEquipesStore } from './equipes'
export { useCongesStore } from './conges'