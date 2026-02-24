// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  /* =======================
   * State
   * ======================= */
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  const isAuthenticated = computed(() => !!user.value)
  
  const isAdmin = computed(() => {
    return user.value?.is_staff === true || user.value?.is_superuser === true
  })
  
  // ← CORRIGÉ: Solde réactif séparé
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

  // ← CORRIGÉ: Rafraîchir juste le solde
  async function refreshSolde() {
    if (!user.value) return null
    
    try {
      console.log('Rafraîchissement solde...')
      const soldeData = await usersApi.getSolde()
      
      // ← CORRIGÉ: Conversion string → number (l'API retourne des strings)
      user.value = {
        ...user.value,
        solde_conge_actuelle: typeof soldeData.solde_conge_actuelle === 'string' 
          ? parseFloat(soldeData.solde_conge_actuelle) 
          : soldeData.solde_conge_actuelle,
        solde_conge_consomme: typeof soldeData.solde_conge_consomme === 'string'
          ? parseFloat(soldeData.solde_conge_consomme)
          : soldeData.solde_conge_consomme,
        solde_conge_recue_par_mois: typeof soldeData.solde_conge_recue_par_mois === 'string'
          ? parseFloat(soldeData.solde_conge_recue_par_mois)
          : soldeData.solde_conge_recue_par_mois,
        motif_conge: 'motif_conge' in soldeData ? soldeData.motif_conge : user.value.motif_conge
      }
      
      console.log('Solde mis à jour:', soldeConge.value)
      return soldeData
    } catch (err) {
      console.error('Erreur refresh solde:', err)
      throw err
    }
  }

  function login() {
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
    user,
    error,
    loading,
    checked,
    isAuthenticated,
    isAdmin,
    soldeConge,
    checkAuth,
    refreshSolde,
    login,
    logout,
    clearAuth
  }
})