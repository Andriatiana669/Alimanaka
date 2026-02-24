// frontend/src/composables/useAuth.ts
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'

export function useAuth() {
  const store = useAuthStore()
  
  return {
    // State
    user: computed(() => store.user),
    isAuthenticated: computed(() => store.isAuthenticated),
    isAdmin: computed(() => store.isAdmin),
    loading: computed(() => store.loading),
    error: computed(() => store.error),
    
    // Getters
    fullName: computed(() => {
      if (!store.user) return ''
      return store.user.get_full_name || `${store.user.last_name} ${store.value.first_name}`
    }),
    
    // Actions
    login: store.login,
    logout: store.logout,
    checkAuth: store.checkAuth
  }
}