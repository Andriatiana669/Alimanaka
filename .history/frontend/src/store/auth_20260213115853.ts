// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'  // ← Nouveau: API dédiée pour le solde
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  /* =======================
   * State
   * ======================= */
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false) // ← Nouveau: éviter double check
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  const isAuthenticated = computed(() => !!user.value)
  
  const isAdmin = computed(() => {
    return user.value?.is_staff === true || user.value?.is_superuser === true
  })
  
  // ← NOUVEAU: Solde réactif séparé (toujours frais, pas de cache)
  const soldeConge = computed(() => ({
    actuelle: user.value?.solde_conge_actuelle ?? 0,
    consomme: user.value?.solde_conge_consomme ?? 0,
    mensuel: user.value?.solde_conge_recue_par_mois ?? 2.5,
    motif: user.value?.motif_conge ?? null
  }))

  /* =======================
   * Actions
   * ======================= */
  async function checkAuth() {
    if (checked.value && user.value) {
      console.log('Auth déjà vérifiée')
      return { authenticated: true, user: user.value }
    }
    
    loading.value = true
    try {
      console.log('Appel API /api/auth/session/')
      const data = await authApi.checkSession()
      
      if (data.authenticated && data.user) {
        user.value = data.user
        checked.value = true
        console.log('User connecté:', data.user.username)
        return data
      } else {
        throw new Error('Non authentifié')
      }
    } catch (err) {
      console.error('Échec auth:', err)
      user.value = null
      checked.value = true
      throw err
    } finally {
      loading.value = false
    }
  }

  // ← NOUVEAU: Rafraîchir juste le solde (léger, pas de cache)
  async function refreshSolde() {
    if (!user.value) return null
    
    try {
      console.log('Rafraîchissement solde...')
      const soldeData = await usersApi.getSolde()
      
      // Met à jour uniquement les champs solde dans l'user existant
      user.value = {
        ...user.value,
        solde_conge_actuelle: parseFloat(soldeData.solde_conge_actuelle),
        solde_conge_consomme: parseFloat(soldeData.solde_conge_consomme),
        solde_conge_recue_par_mois: parseFloat(soldeData.solde_conge_recue_par_mois),
        motif_conge: soldeData.motif_conge
      }
      
      console.log('Solde mis à jour:', soldeConge.value)
      return soldeData
    } catch (err) {
      console.error('Erreur refresh solde:', err)
      throw err
    }
  }

  function login() {
    // Redirection externe vers le backend
    window.location.href = 'http://localhost:8000/api/auth/login/'
  }

  function logout() {
    user.value = null
    checked.value = false
    window.location.href = 'http://localhost:8000/api/auth/logout/'
  }

  function clearAuth() {
    user.value = null
    checked.value = false
  }

  /* =======================
   * Exports
   * ======================= */
  return {
    // State
    user,
    error,
    loading,
    checked,
    
    // Getters
    isAuthenticated,
    isAdmin,
    soldeConge,        // ← Nouveau: solde réactif
    
    // Actions
    checkAuth,
    refreshSolde,      // ← Nouveau: rafraîchissement solde
    login,
    logout,
    clearAuth
  }
})