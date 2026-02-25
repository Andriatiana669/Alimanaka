// frontend/src/store/auth.ts
import { defineStore } from 'pinia'
import { ref, computed, onMounted, onUnmounted } from 'vue'  // ← Ajouté onMounted/onUnmounted
import { authApi } from '@/api/auth'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'
import { API_CONFIG, buildAuthUrl } from '@/config/api'


export const useAuthStore = defineStore('auth', () => {
  /* =======================
   * State
   * ======================= */
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false)
  const error = ref<string | null>(null)
  
  // ← NOUVEAU: Timer pour le polling
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
    if (checked.value && user.value) {
      return { authenticated: true, user: user.value }
    }
    
    loading.value = true
    try {
      const data = await authApi.checkSession()
      
      if (data.authenticated && data.user) {
        user.value = data.user
        checked.value = true
        
        // ← NOUVEAU: Démarre le polling automatique après connexion
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

  // ← NOUVEAU: Démarrer le polling (toutes les 30 secondes)
  function startSoldePolling(intervalMs = 30000) {
    // Arrête l'ancien polling si existe
    stopSoldePolling()
    
    // Rafraîchit immédiatement puis toutes les X secondes
    refreshSolde().catch(console.error)
    
    soldePollingInterval = setInterval(() => {
      if (user.value) {
        refreshSolde().catch(console.error)
      }
    }, intervalMs)
    
    console.log(`Polling solde démarré (${intervalMs}ms)`)
  }

  // ← NOUVEAU: Arrêter le polling
  function stopSoldePolling() {
    if (soldePollingInterval) {
      clearInterval(soldePollingInterval)
      soldePollingInterval = null
      console.log('Polling solde arrêté')
    }
  }

  async function refreshSolde() {
    if (!user.value) return null
    
    try {
      const soldeData = await usersApi.getSolde()
      
      // ← CORRIGÉ: Mise à jour réactive
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

  function login() {
    window.location.href = buildAuthUrl('/login/')
  }

  function logout() {
    stopSoldePolling()  // ← Arrête le polling à la déconnexion
    user.value = null
    checked.value = false
    window.location.href = buildAuthUrl('/logout/')
  }

  function clearAuth() {
    stopSoldePolling()  // ← Arrête le polling
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
    startSoldePolling,   // ← Exposé pour contrôle manuel si besoin
    stopSoldePolling,    // ← Exposé
    login,
    logout,
    clearAuth
  }
})