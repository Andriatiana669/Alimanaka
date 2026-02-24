// frontend/src/composables/useAuth.ts
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'

export function useAuth() {
  const store = useAuthStore()
  
  return {
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isAdmin: computed(() => store.isAdmin),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    login: store.login,
    logout: store.logout,
    checkAuth: store.checkAuth
  }
}