// frontend/src/store/conges.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Conge,
  CalendarEventFromAPI,
  CalendarEvent,
  TypeCongeConfig,
  CreateCongeData
} from '@/types/conges'
import { congesApi } from '@/api/conges'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'

export const useCongesStore = defineStore('conges', () => {
  /* =======================
   * State
   * ======================= */
  const conges = ref<Conge[]>([])
  const calendrierEvents = ref<CalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  const congesApprouves = computed(() =>
    conges.value.filter(c => c.statut === 'approuve')
  )

  const congesEnAttente = computed(() =>
    conges.value.filter(c => c.statut === 'en_attente')
  )

  /**
   * Conversion des événements API (string)
   * vers des événements Calendar (Date)
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => ({
      id: String(event.id),
      title: event.title,
      start: new Date(event.start),
      end: event.end ? new Date(event.end) : undefined,
      allDay: event.allDay,
      color: event.color
    }))
  )

  /* =======================
   * Actions
   * ======================= */
  const fetchTypesConge = async () => {
    try {
      typesConge.value = await congesApi.getTypesConge()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types de congé'
    }
  }

  const fetchCalendrier = async (annee?: number) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await congesApi.getCalendrier(annee)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
    } finally {
      loading.value = false
    }
  }

  const fetchMesConges = async (annee?: number) => {
    loading.value = true
    error.value = null
    try {
      conges.value = await congesApi.getMesConges(annee)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des congés'
    } finally {
      loading.value = false
    }
  }

  const createConge = async (data: CreateCongeData) => {
    loading.value = true
    error.value = null
    try {
      const newConge = await congesApi.createConge(data)
      conges.value.unshift(newConge)

      // Recharge le calendrier pour l'année concernée
      await fetchCalendrier(new Date(data.date_debut).getFullYear())

      return newConge
    } catch (err: any) {
      error.value =
        err.response?.data?.error ||
        err.message ||
        'Erreur lors de la création du congé'
      throw err
    } finally {
      loading.value = false
    }
  }

  const annulerConge = async (id: number) => {
    try {
      await congesApi.annulerConge(id)

      // Version sûre TypeScript
      const conge = conges.value.find(c => c.id === id)
      if (conge) {
        conge.statut = 'annule'
      }

      return true
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l’annulation'
      return false
    }
  }

  const exportAll = async () => {
    try {
      const blob = await congesApi.exportAll()
      const url = window.URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `conges_export_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l’export'
    }
  }

  const exportMine = async () => {
    try {
      const blob = await congesApi.exportMine()
      const url = window.URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `mes_conges_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l’export'
    }
  }

  /**
   * Vérifie si une date est bloquée dans le calendrier
   */
  const isDateBlocked = (date: Date): boolean => {
    const iso = date.toISOString()
    if (!iso) return false

    const dateStr = iso.split('T')[0]
    if (!dateStr) return false

    return calendrierEvents.value.some(e => {
      if (!e.isBlocked || !e.start) return false

      const startIso = new Date(e.start).toISOString()
      const start = startIso.split('T')[0]
      if (!start) return false

      const end = e.end
        ? new Date(e.end).toISOString().split('T')[0]
        : start

      if (!end) return false

      return dateStr >= start && dateStr <= end
    })
  }


  const clearError = () => {
    error.value = null
  }

  /* =======================
   * Exports
   * ======================= */
  return {
    // State
    conges,
    calendrierEvents,
    typesConge,
    loading,
    error,

    // Getters
    congesApprouves,
    congesEnAttente,
    eventsForCalendar,

    // Actions
    fetchTypesConge,
    fetchCalendrier,
    fetchMesConges,
    createConge,
    annulerConge,
    exportAll,
    exportMine,
    isDateBlocked,
    clearError
  }
})




import { authApi } from '@/api/auth'



export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const loading = ref(false)
  const checked = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!user.value)
  const isAdmin = computed(() => {
    return user.value?.is_staff === true || user.value?.is_superuser === true
  })
  
  // ← NOUVEAU: Solde réactif séparé (toujours frais)
  const soldeConge = computed(() => ({
    actuelle: user.value?.solde_conge_actuelle ?? 0,
    consomme: user.value?.solde_conge_consomme ?? 0,
    mensuel: user.value?.solde_conge_recue_par_mois ?? 2.5
  }))

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

  // ← NOUVEAU: Rafraîchir juste le solde (léger, pas de cache)
  async function refreshSolde() {
    if (!user.value) return null
    
    try {
      const soldeData = await usersApi.getSolde()
      
      // Met à jour uniquement les champs solde dans l'user existant
      user.value = {
        ...user.value,
        solde_conge_actuelle: parseFloat(soldeData.solde_conge_actuelle),
        solde_conge_consomme: parseFloat(soldeData.solde_conge_consomme),
        solde_conge_recue_par_mois: parseFloat(soldeData.solde_conge_recue_par_mois),
        motif_conge: soldeData.motif_conge
      }
      
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

  return {
    user,
    error,
    loading,
    checked,
    isAuthenticated,
    isAdmin,
    soldeConge,        // ← Exposé
    checkAuth,
    refreshSolde,      // ← Nouvelle méthode
    login,
    logout,
    clearAuth
  }
})