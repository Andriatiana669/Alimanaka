// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'
import { buildAuthUrl } from '@/config/api'  // ← UTILISÉ POUR login/logout dynamiques
import type { User } from '@/types/user'

export const useAuthStore = defineStore('auth', () => {
  /* =======================
   * State
   * ======================= */
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false)
  const error = ref<string | null>(null)
  
  let soldePollingInterval: ReturnType<typeof setInterval> | null = null

  /* =======================
   * Getters
   * ======================= */
  const isAuthenticated = computed(() => !!user.value)
  
  const isAdmin = computed(() => {
    return user.value?.is_staff === true || user.value?.is_superuser === true
  })
  
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
    if (checked.value && user.value) return { authenticated: true, user: user.value }
    
    loading.value = true
    try {
      const data = await authApi.checkSession()
      if (data.authenticated && data.user) {
        user.value = data.user
        checked.value = true
        startSoldePolling()
        return data
      } else {
        throw new Error('Non authentifié')
      }
    } catch (err) {
      user.value = null
      checked.value = true
      throw err
    } finally {
      loading.value = false
    }
  }

  function startSoldePolling(intervalMs = 30000) {
    stopSoldePolling()
    refreshSolde().catch(console.error)
    soldePollingInterval = setInterval(() => {
      if (user.value) refreshSolde().catch(console.error)
    }, intervalMs)
  }

  function stopSoldePolling() {
    if (soldePollingInterval) {
      clearInterval(soldePollingInterval)
      soldePollingInterval = null
    }
  }

  async function refreshSolde() {
    if (!user.value) return null
    try {
      const soldeData = await usersApi.getSolde()
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
      return soldeData
    } catch (err) {
      console.error('Erreur refresh solde:', err)
      throw err
    }
  }

  // ← CHANGEMENT : login/logout dynamiques
  function login() {
    window.location.href = buildAuthUrl('/login/')
  }

  function logout() {
    stopSoldePolling()
    user.value = null
    checked.value = false
    window.location.href = buildAuthUrl('/logout/')
  }

  function clearAuth() {
    stopSoldePolling()
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
    startSoldePolling,
    stopSoldePolling,
    login,
    logout,
    clearAuth
  }
})