// frontend/src/store/reposmedicale.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type {
  ReposMedical,
  ReposMedicalCalendarEventFromAPI,
  CreateReposMedicalData,
  GerableUserReposMedical,
  ReposMedicalParams
} from '@/types/reposmedicale'
import type { TypeCongeConfig } from '@/types/conges'
import { reposmedicaleApi } from '@/api/reposmedicale'
import { useAuthStore } from '@/store/auth'

export const useReposMedicaleStore = defineStore('reposmedicale', () => {
  /* =======================
   * State
   * ======================= */
  const reposMedicaux = ref<ReposMedical[]>([])
  const calendrierEvents = ref<ReposMedicalCalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const utilisateursGerables = ref<GerableUserReposMedical[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Filtres par statut
  const reposEnAttente = computed(() =>
    reposMedicaux.value.filter(r => r.statut === 'en_attente')
  )

  const reposApprouves = computed(() =>
    reposMedicaux.value.filter(r => r.statut === 'approuve')
  )

  const reposTransformes = computed(() =>
    reposMedicaux.value.filter(r => r.statut === 'transforme')
  )

  const reposAnnules = computed(() =>
    reposMedicaux.value.filter(r => r.statut === 'annule')
  )

  // Total des heures de repos
  const totalHeuresRepos = computed(() => {
    return reposMedicaux.value
      .filter(r => r.statut !== 'annule')
      .reduce((sum, r) => sum + r.duree_heures, 0)
  })

  /**
   * Conversion des événements API (string) vers des événements Calendar (Date)
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => {
      // Déterminer la couleur selon le statut
      let color = event.color
      if (event.type === 'repos_medical' && event.statut) {
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
        duree_heures: event.duree_heures,
        conge_genere_id: event.conge_genere_id
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
   * Charger les types de congés (pour transformation)
   */
  const fetchTypesConge = async () => {
    try {
      typesConge.value = await reposmedicaleApi.getTypesConge()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types de congé'
      throw err
    }
  }

  /**
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: ReposMedicalParams) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await reposmedicaleApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger mes repos médicaux
   */
  const fetchMesRepos = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      reposMedicaux.value = await reposmedicaleApi.getMesRepos(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des repos médicaux'
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
      utilisateursGerables.value = await reposmedicaleApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Créer un repos médical
   */
  const createReposMedical = async (data: CreateReposMedicalData, userId?: number) => {
    loading.value = true
    error.value = null
    try {
      const newRepos = await reposmedicaleApi.createReposMedical(data, userId)
      reposMedicaux.value.unshift(newRepos)

      // Recharger le calendrier
      await fetchCalendrier({ annee: new Date(data.date).getFullYear() })

      return newRepos
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Valider un repos médical
   */
  const validerReposMedical = async (id: number) => {
    loading.value = true
    error.value = null
    try {
      const result = await reposmedicaleApi.validerReposMedical(id)
      
      // Mettre à jour le repos localement
      const index = reposMedicaux.value.findIndex(r => r.id === id)
      if (index !== -1) {
        const updated = await reposmedicaleApi.getReposMedicalDetails(id)
        reposMedicaux.value[index] = updated
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
   * Transformer en congé
   */
  const transformerEnConge = async (id: number, type_conge: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await reposmedicaleApi.transformerEnConge(id, type_conge)
      
      // Mettre à jour le repos localement
      const index = reposMedicaux.value.findIndex(r => r.id === id)
      if (index !== -1) {
        const updated = await reposmedicaleApi.getReposMedicalDetails(id)
        reposMedicaux.value[index] = updated
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
   * Annuler un repos médical
   */
  const annulerReposMedical = async (id: number, commentaire?: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await reposmedicaleApi.annulerReposMedical(id, commentaire)

      const repos = reposMedicaux.value.find(r => r.id === id)
      if (repos) {
        repos.statut = 'annule'
        repos.annule_par_details = result.annule_par as any
        repos.date_annulation = result.date_annulation
        repos.commentaire_annulation = commentaire
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
   * Récupère les détails d'un repos médical spécifique
   */
  const getReposMedicalDetails = async (id: number): Promise<ReposMedical> => {
    try {
      let repos = reposMedicaux.value.find(r => r.id === id)
      if (!repos) {
        repos = await reposmedicaleApi.getReposMedicalDetails(id)
      }
      return repos
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * Vérifie si un repos médical peut être validé
   */
  const peutValider = (repos: ReposMedical | null): boolean => {
    if (!repos) return false
    return repos.statut === 'en_attente'
  }

  /**
   * Vérifie si un repos médical peut être transformé en congé
   */
  const peutTransformerEnConge = (repos: ReposMedical | null): boolean => {
    if (!repos) return false
    return repos.statut === 'en_attente'
  }

  /**
   * Vérifie si un repos médical peut être annulé
   */
  const peutAnnuler = (repos: ReposMedical | null): boolean => {
    if (!repos) return false
    return repos.statut === 'en_attente'
  }

  /**
   * Vérifie si l'utilisateur peut gérer ce repos médical
   */
  const canManageThisRepos = (repos: ReposMedical | null): boolean => {
    if (!repos) return false
    
    // Si l'utilisateur n'est pas manager/admin, il ne peut pas gérer les repos des autres
    if (!isManagerOrAdmin.value && !isSuperAdmin.value) return false
    
    // Super admin peut tout faire
    if (isSuperAdmin.value) return true
    
    // Vérifier si l'utilisateur du repos est dans les équipes gérables
    const gerableUser = utilisateursGerables.value.find(u => u.id === repos.utilisateur)
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
    reposMedicaux,
    calendrierEvents,
    typesConge,
    utilisateursGerables,
    loading,
    error,

    // Getters
    reposEnAttente,
    reposApprouves,
    reposTransformes,
    reposAnnules,
    totalHeuresRepos,
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,

    // Actions
    fetchTypesConge,
    fetchCalendrier,
    fetchMesRepos,
    fetchUtilisateursGerables,
    createReposMedical,
    validerReposMedical,
    transformerEnConge,
    annulerReposMedical,
    getReposMedicalDetails,
    peutValider,
    peutTransformerEnConge,
    peutAnnuler,
    canManageThisRepos,
    clearError
  }
})