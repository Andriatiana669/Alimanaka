// frontend/src/store/index.ts
import { createPinia } from 'pinia'

export const pinia = createPinia()

// Export des stores pour import facile
export { useUsersStore } from './users'