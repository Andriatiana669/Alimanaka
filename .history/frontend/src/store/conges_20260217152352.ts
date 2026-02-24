// frontend/src/store/conges.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  Conge,
  CalendarEventFromAPI,
  CalendarEvent,
  TypeCongeConfig,
  CreateCongeData,
  GerableUser,
  CalendrierParams
} from '@/types/conges'
import { congesApi } from '@/api/conges'
import { useAuthStore } from '@/store/auth'
import { getYear } from 'date-fns';

export const useCongesStore = defineStore('conges', () => {
  /* =======================
   * State
   * ======================= */
  const conges = ref<Conge[]>([])
  const calendrierEvents = ref<CalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const utilisateursGerables = ref<GerableUser[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const droits = ref<Droit[]>([])

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
      color: event.color,
      type: event.type,
      isBlocked: event.isBlocked,
      statut: event.statut,
      user_id: event.user_id
    }))
  )

  /**
   * Permissions utilisateur
   */
  const canManageOthers = computed(() => {
    const user = useAuthStore().user
    if (!user) return false
    return user.is_superuser || 
           (user.is_staff && user.est_chef_equipe) || 
           user.est_chef_equipe
  })

  const isSuperAdmin = computed(() => {
    const user = useAuthStore().user
    return user?.is_superuser || false
  })

  const isManagerOrAdmin = computed(() => {
    const user = useAuthStore().user
    if (!user) return false
    return (user.is_staff && user.est_chef_equipe) || user.est_chef_equipe
  })

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

  const fetchCalendrier = async (params?: CalendrierParams & { statut?: string }) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await congesApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
    } finally {
      loading.value = false
    }
  }

  const fetchMesConges = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      conges.value = await congesApi.getMesConges(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des congés'
    } finally {
      loading.value = false
    }
  }

  const fetchUtilisateursGerables = async () => {
    loading.value = true
    error.value = null
    try {
      utilisateursGerables.value = await congesApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
    } finally {
      loading.value = false
    }
  }

  const createConge = async (data: CreateCongeData & { user_id?: number }) => {
    loading.value = true
    error.value = null
    try {
      const newConge = await congesApi.createConge(data)
      conges.value.unshift(newConge)

      // ← RAFRAÎCHIT LE SOLDE IMMÉDIATEMENT APRÈS CRÉATION
      const authStore = useAuthStore()
      await authStore.refreshSolde()

      // Recharge le calendrier avec les params actuels
      await fetchCalendrier({ annee: new Date(data.date_debut).getFullYear() })

      return newConge
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  const annulerConge = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      await congesApi.annulerConge(id)

      const conge = conges.value.find(c => c.id === id)
      if (conge) {
        conge.statut = 'annule'
      }

      // ← RAFRAÎCHIT LE SOLDE IMMÉDIATEMENT APRÈS ANNULATION
      const authStore = useAuthStore()
      await authStore.refreshSolde()

      return true
    } catch (err: any) {
      error.value = err.message || 'Erreur'
      return false
    } finally {
      loading.value = false
    }
  }


  const validerCongePartiel = async (id: number, dates: string[]) => {
    loading.value = true
    try {
      const result = await congesApi.validerCongePartiel(id, dates)
      
      // Rafraîchir le solde
      const authStore = useAuthStore()
      await authStore.refreshSolde()
      
      // Recharger complètement les données
      await fetchCalendrier({ annee: new Date().getFullYear() })
      await fetchMesConges(getYear(new Date()))
      
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const annulerCongePartiel = async (id: number, dates: string[]) => {
    loading.value = true
    error.value = null
    try {
      const result = await congesApi.annulerCongePartiel(id, dates)
      
      // Rafraîchir le solde
      const authStore = useAuthStore()
      await authStore.refreshSolde()
      
      // Recharger les données
      await fetchCalendrier({ annee: new Date().getFullYear() })
      await fetchMesConges(getYear(new Date()))
      
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }


  const fetchDroits = async () => {
    try {
      droits.value = await congesApi.getDroits()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement droits'
    }
  }


  const exportAll = async () => {
    loading.value = true
    error.value = null
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
    } finally {
      loading.value = false
    }
  }

  const exportMine = async () => {
    loading.value = true
    error.value = null
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
    } finally {
      loading.value = false
    }
  }

  /**
   * Vérifie si une date est bloquée dans le calendrier
   */
  const isDateBlocked = (date: Date): boolean => {
    const dateTime = date.setHours(0, 0, 0, 0)
    
    return calendrierEvents.value.some(e => {
      if (!e.isBlocked) return false
      
      const start = new Date(e.start).setHours(0, 0, 0, 0)
      const end = e.end 
        ? new Date(e.end).setHours(0, 0, 0, 0) 
        : start
      
      return dateTime >= start && dateTime <= end
    })
  }


  const validerConge = async (id: number) => {
    loading.value = true
    try {
      const result = await congesApi.validerConge(id)
      
      // Mettre à jour le congé localement
      const conge = conges.value.find(c => c.id === id)
      if (conge) {
        conge.statut = 'approuve'
        conge.valide_par_details = result.valide_par as any
        conge.date_validation = result.date_validation
      }
      
      // ← AJOUTER ICI : Rafraîchir le solde
      const authStore = useAuthStore()
      await authStore.refreshSolde()
      
      // Rafraîchir le calendrier
      await fetchCalendrier({ annee: new Date().getFullYear() })
      
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
  }

  const refuserConge = async (id: number, commentaire?: string) => {
    loading.value = true
    try {
      const result = await congesApi.refuserConge(id, commentaire)
      
      // Mettre à jour le congé localement
      const conge = conges.value.find(c => c.id === id)
      if (conge) {
        conge.statut = 'refuse'
        conge.refuse_par_details = result.refuse_par as any
        conge.date_refus = result.date_refus
        conge.commentaire_refus = result.commentaire_refus
      }
      
      // ← AJOUTER ICI : Rafraîchir le solde (remboursement)
      const authStore = useAuthStore()
      await authStore.refreshSolde()
      
      // Rafraîchir le calendrier
      await fetchCalendrier({ annee: new Date().getFullYear() })
      
      return result
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message
      throw err
    } finally {
      loading.value = false
    }
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
    utilisateursGerables,
    loading,
    error,
    droits,

    // Getters
    congesApprouves,
    congesEnAttente,
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,

    // Actions
    fetchTypesConge,
    fetchCalendrier,
    fetchMesConges,
    fetchDroits,
    fetchUtilisateursGerables,
    createConge,
    annulerConge,
    validerConge,
    refuserConge,
    validerCongePartiel,
    annulerCongePartiel,
    exportAll,
    exportMine,
    isDateBlocked,
    clearError,
    
  }
})