// frontend/src/store/conges.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type {
  Conge,
  CalendarEventFromAPI,
  CalendarEvent,
  TypeCongeConfig,
  CreateCongeData,
  GerableUser,
  CalendrierParams,
  // NOUVEAU
  Droit,
  ValidationPartielleResponse,
  AnnulationPartielleResponse
} from '@/types/conges'
import { congesApi } from '@/api/conges'
import { useAuthStore } from '@/store/auth'

export const useCongesStore = defineStore('conges', () => {
  /* =======================
   * State
   * ======================= */
  const conges = ref<Conge[]>([])
  const calendrierEvents = ref<CalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const utilisateursGerables = ref<GerableUser[]>([])
  // NOUVEAU
  const droits = ref<Droit[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Filtres par statut
  const congesApprouves = computed(() =>
    conges.value.filter(c => c.statut === 'approuve')
  )

  const congesEnAttente = computed(() =>
    conges.value.filter(c => c.statut === 'en_attente')
  )

  const congesRefuses = computed(() =>
    conges.value.filter(c => c.statut === 'refuse')
  )

  const congesAnnules = computed(() =>
    conges.value.filter(c => c.statut === 'annule')
  )

  // NOUVEAU : Filtre pour les droits
  const congesDroits = computed(() =>
    conges.value.filter(c => c.est_droit === true)
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
      user_id: event.user_id,
      // NOUVEAU
      isDroit: event.isDroit,
      droit_nom: event.droit_nom
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

  /**
   * Statistiques sur les droits (NOUVEAU)
   */
  const droitsUtilisesCetteAnnee = computed(() => {
    const currentYear = getYear(new Date())
    return conges.value.filter(c => 
      c.est_droit && 
      new Date(c.date_debut).getFullYear() === currentYear
    ).length
  })

  /* =======================
   * Actions
   * ======================= */
  
  /**
   * Charger les types de congés
   */
  const fetchTypesConge = async () => {
    try {
      typesConge.value = await congesApi.getTypesConge()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types de congé'
      throw err
    }
  }

  /**
   * NOUVEAU : Charger les droits
   */
  const fetchDroits = async () => {
    try {
      droits.value = await congesApi.getDroits()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des droits'
      throw err
    }
  }

  /**
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: CalendrierParams & { statut?: string }) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await congesApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger mes congés
   */
  const fetchMesConges = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      conges.value = await congesApi.getMesConges(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des congés'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger les utilisateurs gérables (pour managers)
   */
  const fetchUtilisateursGerables = async () => {
    loading.value = true
    error.value = null
    try {
      utilisateursGerables.value = await congesApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Créer une demande de congé
   */
  const createConge = async (data: CreateCongeData & { user_id?: number }) => {
    loading.value = true
    error.value = null
    try {
      const newConge = await congesApi.createConge(data)
      conges.value.unshift(newConge)

      // Rafraîchir le solde
      const authStore = useAuthStore()
      await authStore.refreshSolde()

      // Recharger le calendrier
      await fetchCalendrier({ annee: new Date(data.date_debut).getFullYear() })

      return newConge
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Valider un congé (complet)
   */
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
      
      // Rafraîchir le solde
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

  /**
   * Valider partiellement un congé
   */
  const validerCongePartiel = async (id: number, dates: string[]): Promise<ValidationPartielleResponse> => {
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

  /**
   * Refuser un congé
   */
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
      
      // Rafraîchir le solde (remboursement)
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

  /**
   * Annuler un congé
   */
  const annulerConge = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const result = await congesApi.annulerConge(id)

      const conge = conges.value.find(c => c.id === id)
      if (conge) {
        conge.statut = 'annule'
      }

      // Rafraîchir le solde
      const authStore = useAuthStore()
      await authStore.refreshSolde()

      return result
    } catch (err: any) {
      error.value = err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Annuler partiellement un congé
   */
  const annulerCongePartiel = async (id: number, dates: string[]): Promise<AnnulationPartielleResponse> => {
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

  /**
   * Exporter tous les congés (admin)
   */
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
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Exporter mes congés
   */
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
      throw err
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

  /**
   * Récupère les détails d'un congé spécifique
   */
  const getCongeDetails = async (id: number): Promise<Conge> => {
    try {
      // Chercher d'abord dans le store
      let conge = conges.value.find(c => c.id === id)
      
      // Si pas trouvé, charger depuis l'API
      if (!conge) {
        conge = await congesApi.getCongeDetails(id)
      }
      
      return conge
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * NOUVEAU : Vérifie si un droit est disponible pour l'utilisateur
   */
  const droitEstDisponible = (droitId: number, utilisateurId?: number): boolean => {
    // Logique à implémenter selon vos règles métier
    // Par exemple: limite d'1 droit par an, etc.
    const targetId = utilisateurId || useAuthStore().user?.id
    if (!targetId) return false
    
    const currentYear = getYear(new Date())
    const droitsUtilises = conges.value.filter(c => 
      c.est_droit && 
      c.droit === droitId &&
      c.utilisateur === targetId &&
      new Date(c.date_debut).getFullYear() === currentYear
    ).length
    
    // Par défaut, on autorise 1 droit par type et par an
    return droitsUtilises < 1
  }

  /**
   * Effacer l'erreur
   */
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
    droits, // NOUVEAU
    loading,
    error,

    // Getters
    congesApprouves,
    congesEnAttente,
    congesRefuses,
    congesAnnules,
    congesDroits, // NOUVEAU
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,
    droitsUtilisesCetteAnnee, // NOUVEAU

    // Actions
    fetchTypesConge,
    fetchDroits, // NOUVEAU
    fetchCalendrier,
    fetchMesConges,
    fetchUtilisateursGerables,
    createConge,
    validerConge,
    validerCongePartiel,
    refuserConge,
    annulerConge,
    annulerCongePartiel,
    exportAll,
    exportMine,
    isDateBlocked,
    getCongeDetails,
    droitEstDisponible, // NOUVEAU
    clearError
  }
})