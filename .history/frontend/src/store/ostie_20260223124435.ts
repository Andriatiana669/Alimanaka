// frontend/src/store/ostie.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type {
  Ostie,
  OstieCalendarEventFromAPI,
  CreateOstieData,
  GerableUserOstie,
  OstieParams,
  ValidationOstieForm,
  TransformationOstieForm
} from '@/types/ostie'
import { ostieApi } from '@/api/ostie'
import { useAuthStore } from '@/store/auth'

export const useOstieStore = defineStore('ostie', () => {
  /* =======================
   * State
   * ======================= */
  const osties = ref<Ostie[]>([])
  const calendrierEvents = ref<OstieCalendarEventFromAPI[]>([])
  const utilisateursGerables = ref<GerableUserOstie[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Filtres par statut
  const ostiesEnAttente = computed(() =>
    osties.value.filter(o => o.statut === 'en_attente')
  )

  const ostiesApprouves = computed(() =>
    osties.value.filter(o => o.statut === 'approuve')
  )

  const ostiesTransformes = computed(() =>
    osties.value.filter(o => o.statut === 'transforme')
  )

  const ostiesAnnules = computed(() =>
    osties.value.filter(o => o.statut === 'annule')
  )

  // Total des OSTIES (compteur)
  const totalOsties = computed(() => osties.value.length)

  /**
   * Conversion des événements API (string) vers des événements Calendar (Date)
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => {
      // Déterminer la couleur selon le statut
      let color = event.color
      if (event.type === 'ostie' && event.statut) {
        if (event.statut === 'approuve') {
          color = '#4caf50'  // Vert
        } else if (event.statut === 'transforme') {
          color = '#9c27b0'  // Violet
        } else if (event.statut === 'annule') {
          color = '#9e9e9e'  // Gris
        }
        // 'en_attente' reste orange (#ff9800)
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
        heure_debut: event.heure_debut,
        heure_fin: event.heure_fin,
        repos_genere_id: event.repos_genere_id
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
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: OstieParams) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await ostieApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger mes OSTIES
   */
  const fetchMesOsties = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      osties.value = await ostieApi.getMesOsties(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des OSTIES'
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
      utilisateursGerables.value = await ostieApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Créer un OSTIE
   */
  const createOstie = async (data: CreateOstieData, userId?: number) => {
    loading.value = true
    error.value = null
    try {
      const newOstie = await ostieApi.createOstie(data, userId)
      osties.value.unshift(newOstie)

      // Recharger le calendrier
      await fetchCalendrier({ annee: new Date(data.date).getFullYear() })

      return newOstie
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Valider un OSTIE
   */
  const validerOstie = async (id: number, data: ValidationOstieForm) => {
    loading.value = true
    error.value = null
    try {
      const result = await ostieApi.validerOstie(id, data)
      
      // Mettre à jour l'OSTIE localement
      const index = osties.value.findIndex(o => o.id === id)
      if (index !== -1) {
        const updated = await ostieApi.getOstieDetails(id)
        osties.value[index] = updated
      }
      
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
   * Transformer en repos médical
   */
  const transformerEnRepos = async (id: number, data: TransformationOstieForm) => {
    loading.value = true
    error.value = null
    try {
      const result = await ostieApi.transformerEnRepos(id, data)
      
      // Mettre à jour l'OSTIE localement
      const index = osties.value.findIndex(o => o.id === id)
      if (index !== -1) {
        const updated = await ostieApi.getOstieDetails(id)
        osties.value[index] = updated
      }
      
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
   * Annuler un OSTIE
   */
  const annulerOstie = async (id: number, commentaire?: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await ostieApi.annulerOstie(id, commentaire)

      const ostie = osties.value.find(o => o.id === id)
      if (ostie) {
        ostie.statut = 'annule'
        ostie.annule_par_details = result.annule_par as any
        ostie.date_annulation = result.date_annulation
        ostie.commentaire_annulation = commentaire
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
   * Récupère les détails d'un OSTIE spécifique
   */
  const getOstieDetails = async (id: number): Promise<Ostie> => {
    try {
      let ostie = osties.value.find(o => o.id === id)
      if (!ostie) {
        ostie = await ostieApi.getOstieDetails(id)
      }
      return ostie
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * Vérifie si un OSTIE peut être validé
   */
  const peutValider = (ostie: Ostie | null): boolean => {
    if (!ostie) return false
    return ostie.statut === 'en_attente'
  }

  /**
   * Vérifie si un OSTIE peut être transformé en repos médical
   */
  const peutTransformerEnRepos = (ostie: Ostie | null): boolean => {
    if (!ostie) return false
    return ostie.statut === 'en_attente'
  }

  /**
   * Vérifie si un OSTIE peut être annulé
   */
  const peutAnnuler = (ostie: Ostie | null): boolean => {
    if (!ostie) return false
    return ostie.statut === 'en_attente'
  }

  /**
   * Vérifie si l'utilisateur peut gérer cet OSTIE
   */
  const canManageThisOstie = (ostie: Ostie | null): boolean => {
    if (!ostie) return false
    
    // Si l'utilisateur n'est pas manager/admin, il ne peut pas gérer les OSTIES des autres
    if (!isManagerOrAdmin.value && !isSuperAdmin.value) return false
    
    // Super admin peut tout faire
    if (isSuperAdmin.value) return true
    
    // Vérifier si l'utilisateur de l'OSTIE est dans les équipes gérables
    const gerableUser = utilisateursGerables.value.find(u => u.id === ostie.utilisateur)
    return !!gerableUser
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
    osties,
    calendrierEvents,
    utilisateursGerables,
    loading,
    error,

    // Getters
    ostiesEnAttente,
    ostiesApprouves,
    ostiesTransformes,
    ostiesAnnules,
    totalOsties,
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,

    // Actions
    fetchCalendrier,
    fetchMesOsties,
    fetchUtilisateursGerables,
    createOstie,
    validerOstie,
    transformerEnRepos,
    annulerOstie,
    getOstieDetails,
    peutValider,
    peutTransformerEnRepos,
    peutAnnuler,
    canManageThisOstie,
    clearError
  }
})