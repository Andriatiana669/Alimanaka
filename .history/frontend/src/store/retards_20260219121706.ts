// frontend/src/store/retards.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type {
  Retard,
  Rattrapage,
  TypeRetardConfig,
  RetardCalendarEventFromAPI,
  CreateRetardData,
  CreateRattrapageData,
  GerableUserRetard,
  RetardsParams
} from '@/types/retards'
import { retardsApi } from '@/api/retards'
import { useAuthStore } from '@/store/auth'

export const useRetardsStore = defineStore('retards', () => {
  /* =======================
   * State
   * ======================= */
  const retards = ref<Retard[]>([])
  const calendrierEvents = ref<RetardCalendarEventFromAPI[]>([])
  const typesRetard = ref<TypeRetardConfig[]>([])
  const rattrapages = ref<Rattrapage[]>([])
  const utilisateursGerables = ref<GerableUserRetard[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Filtres par statut
  const retardsEnAttente = computed(() =>
    retards.value.filter(r => r.statut === 'en_attente')
  )

  const retardsEnCours = computed(() =>
    retards.value.filter(r => r.statut === 'en_cours')
  )

  const retardsApprouves = computed(() =>
    retards.value.filter(r => r.statut === 'approuve')
  )

  const retardsAnnules = computed(() =>
    retards.value.filter(r => r.statut === 'annule')
  )

  // Total des heures à rattraper
  const totalHeuresARattraper = computed(() => {
    return retards.value
      .filter(r => r.statut !== 'approuve' && r.statut !== 'annule')
      .reduce((sum, r) => {
        // Convertir en nombre si c'est une string
        const heures = typeof r.heures_restantes === 'string' 
          ? parseFloat(r.heures_restantes) 
          : (r.heures_restantes || 0)
        return sum + heures
      }, 0)
  })

  /**
   * Conversion des événements API (string) vers des événements Calendar (Date)
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => {
      // Déterminer la couleur selon le statut pour les retards
      let color = event.color
      if (event.type === 'retard' && event.statut) {
        if (event.statut === 'approuve') {
          color = '#4caf50'  // Vert
        } else if (event.statut === 'en_cours') {
          color = '#2196f3'  // Bleu
        } else if (event.statut === 'annule') {
          color = '#9e9e9e'  // Gris
        }
      }

      return {
        id: String(event.id),
        title: event.title,
        start: new Date(event.start),
        end: event.end ? new Date(event.end) : undefined,
        allDay: event.allDay ?? true,
        color: color,
        type: event.type,
        user_id: event.user_id,
        statut: event.statut,
        minutes_retard: event.minutes_retard,
        heures_restantes: event.heures_restantes
      }
    }) as any
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
  
  /**
   * Charger les types de retard
   */
  const fetchTypesRetard = async () => {
    try {
      typesRetard.value = await retardsApi.getTypesRetard()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types de retard'
      throw err
    }
  }

  /**
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: RetardsParams) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await retardsApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger mes retards
   */
  const fetchMesRetards = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      retards.value = await retardsApi.getMesRetards(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des retards'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger les rattrapages
   */
  const fetchRattrapages = async () => {
    loading.value = true
    error.value = null
    try {
      rattrapages.value = await retardsApi.getRattrapages()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des rattrapages'
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
      utilisateursGerables.value = await retardsApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Créer un retard
   */
  const createRetard = async (data: CreateRetardData & { user_id?: number }) => {
    loading.value = true
    error.value = null
    try {
      const newRetard = await retardsApi.createRetard(data)
      retards.value.unshift(newRetard)

      // Recharger le calendrier
      await fetchCalendrier({ annee: new Date(data.date).getFullYear() })

      return newRetard
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Ajouter un rattrapage
   */
  const ajouterRattrapage = async (retardId: number, data: CreateRattrapageData) => {
    loading.value = true
    error.value = null
    try {
      const result = await retardsApi.ajouterRattrapage(retardId, data)
      
      // Mettre à jour le retard dans la liste
      const index = retards.value.findIndex(r => r.id === retardId)
      if (index !== -1) {
        const updatedRetard = await retardsApi.getRetardDetails(retardId)
        retards.value[index] = updatedRetard
      }
      
      await fetchRattrapages()
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
   * Annuler un retard
   */
  const annulerRetard = async (id: number, commentaire?: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await retardsApi.annulerRetard(id, commentaire)

      const retard = retards.value.find(r => r.id === id)
      if (retard) {
        retard.statut = 'annule'
        retard.annule_par_details = result.annule_par as any
        retard.date_annulation = result.date_annulation
        retard.commentaire_annulation = commentaire
      }

      await fetchCalendrier({ annee: new Date().getFullYear() })

      return result
    } catch (err: any) {
      error.value = err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Récupère les détails d'un retard spécifique
   */
  const getRetardDetails = async (id: number): Promise<Retard> => {
    try {
      let retard = retards.value.find(r => r.id === id)
      if (!retard) {
        retard = await retardsApi.getRetardDetails(id)
      }
      return retard
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * Exporter mes retards (utilisateur connecté)
   */
  const exportMine = async () => {
    loading.value = true
    error.value = null
    try {
      const blob = await retardsApi.exportMine()
      const url = window.URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `mes_retards_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'export'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Exporter tous les retards (admin uniquement)
   */
  const exportAll = async () => {
    loading.value = true
    error.value = null
    try {
      const blob = await retardsApi.exportAll()
      const url = window.URL.createObjectURL(blob)

      const a = document.createElement('a')
      a.href = url
      a.download = `retards_export_${new Date().toISOString().split('T')[0]}.xlsx`
      document.body.appendChild(a)
      a.click()

      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors de l\'export'
      throw err
    } finally {
      loading.value = false
    }
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
    retards,
    calendrierEvents,
    typesRetard,
    rattrapages,
    utilisateursGerables,
    loading,
    error,

    // Getters
    retardsEnAttente,
    retardsEnCours,
    retardsApprouves,
    retardsAnnules,
    totalHeuresARattraper,
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,

    // Actions
    fetchTypesRetard,
    fetchCalendrier,
    fetchMesRetards,
    fetchRattrapages,
    fetchUtilisateursGerables,
    createRetard,
    ajouterRattrapage,
    annulerRetard,
    getRetardDetails,
    exportMine,
    exportAll,
    clearError
  }
})