// frontend/src/store/permissions.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type {
  Permission,
  PermissionCalendarEventFromAPI,
  CreatePermissionData,
  GerableUserPermission,
  PermissionsParams,
  RattrapageJSON
} from '@/types/permissions'
import type { TypeCongeConfig } from '@/types/conges'
import { permissionsApi } from '@/api/permissions'
import { useAuthStore } from '@/store/auth'

export const usePermissionsStore = defineStore('permissions', () => {
  /* =======================
   * State
   * ======================= */
  const permissions = ref<Permission[]>([])
  const calendrierEvents = ref<PermissionCalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const utilisateursGerables = ref<GerableUserPermission[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Filtres par statut
  const permissionsEnAttente = computed(() =>
    permissions.value.filter(p => p.statut === 'en_attente')
  )

  const permissionsRetournees = computed(() =>
    permissions.value.filter(p => p.statut === 'retourne')
  )

  const permissionsRattrapage = computed(() =>
    permissions.value.filter(p => p.statut === 'rattrapage')
  )

  const permissionsApprouvees = computed(() =>
    permissions.value.filter(p => p.statut === 'approuve')
  )

  const permissionsTransformees = computed(() =>
    permissions.value.filter(p => p.statut === 'transforme')
  )

  const permissionsAnnulees = computed(() =>
    permissions.value.filter(p => p.statut === 'annule')
  )

  // Total des heures à rattraper
  const totalHeuresARattraper = computed(() => {
    return permissions.value
      .filter(p => ['retourne', 'rattrapage'].includes(p.statut))
      .reduce((sum, p) => {
        const heures = typeof p.heures_restantes === 'string' 
          ? parseFloat(p.heures_restantes) 
          : (p.heures_restantes || 0)
        return sum + heures
      }, 0)
  })

  /**
   * Conversion des événements API (string) vers des événements Calendar (Date)
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => {
      // Déterminer la couleur selon le statut
      let color = event.color
      if (event.type === 'permission' && event.statut) {
        if (event.statut === 'approuve') {
          color = '#4caf50'  // Vert
        } else if (event.statut === 'rattrapage') {
          color = '#2196f3'  // Bleu
        } else if (event.statut === 'transforme') {
          color = '#9c27b0'  // Violet
        } else if (event.statut === 'annule') {
          color = '#9e9e9e'  // Gris
        } else if (event.statut === 'retourne') {
          color = '#ff9800'  // Orange (en attente de décision)
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
        heures_restantes: event.heures_restantes,
        peut_retourner: event.peut_retourner,
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
      typesConge.value = await permissionsApi.getTypesConge()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types de congé'
      throw err
    }
  }

  /**
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: PermissionsParams) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await permissionsApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Charger mes permissions
   */
  const fetchMesPermissions = async (annee?: number, statut?: string) => {
    loading.value = true
    error.value = null
    try {
      permissions.value = await permissionsApi.getMesPermissions(annee, statut)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des permissions'
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
      utilisateursGerables.value = await permissionsApi.getUtilisateursGerables()
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement utilisateurs'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Créer une permission
   */
  const createPermission = async (data: CreatePermissionData & { user_id?: number }) => {
    loading.value = true
    error.value = null
    try {
      const newPermission = await permissionsApi.createPermission(data)
      permissions.value.unshift(newPermission)

      // Recharger le calendrier
      await fetchCalendrier({ annee: new Date(data.date).getFullYear() })

      return newPermission
    } catch (err: any) {
      error.value = err.response?.data?.error || err.response?.data?.detail || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Enregistrer le retour (bouton 'De retour')
   */
  const enregistrerRetour = async (id: number, heure_arrivee_reelle: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await permissionsApi.enregistrerRetour(id, heure_arrivee_reelle)
      
      // Mettre à jour la permission localement
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        const updated = await permissionsApi.getPermissionDetails(id)
        permissions.value[index] = updated
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
   * Ajouter un rattrapage
   */
  const ajouterRattrapage = async (id: number, data: {
    date_rattrapage: string
    heure_debut: string
    heure_fin: string
    commentaire?: string | null
  }) => {
    loading.value = true
    error.value = null
    try {
      const result = await permissionsApi.ajouterRattrapage(id, data)
      
      // Mettre à jour la permission localement
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        const updated = await permissionsApi.getPermissionDetails(id)
        permissions.value[index] = updated
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
      const result = await permissionsApi.transformerEnConge(id, type_conge)
      
      // Mettre à jour la permission localement
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        const updated = await permissionsApi.getPermissionDetails(id)
        permissions.value[index] = updated
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
   * Annuler une permission
   */
  const annulerPermission = async (id: number, commentaire?: string) => {
    loading.value = true
    error.value = null
    try {
      const result = await permissionsApi.annulerPermission(id, commentaire)

      const permission = permissions.value.find(p => p.id === id)
      if (permission) {
        permission.statut = 'annule'
        permission.annule_par_details = result.annule_par as any
        permission.date_annulation = result.date_annulation
        permission.commentaire_annulation = commentaire
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
   * Récupère les détails d'une permission spécifique
   */
  const getPermissionDetails = async (id: number): Promise<Permission> => {
    try {
      let permission = permissions.value.find(p => p.id === id)
      if (!permission) {
        permission = await permissionsApi.getPermissionDetails(id)
      }
      return permission
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * Vérifie si une permission peut être retournée (bouton 'De retour')
   */
  const peutRetourner = (permission: Permission): boolean => {
    if (!permission) return false
    const today = new Date().toISOString().split('T')[0] ?? ''
    // Vérifier que permission.date existe et est une string
    return permission.statut === 'en_attente' && 
           typeof permission.date === 'string' && 
           permission.date <= today
  }

  /**
   * Vérifie si une permission peut être transformée en congé
   */
  const peutTransformerEnConge = (permission: Permission): boolean => {
    if (!permission) return false
    // Transformation possible UNIQUEMENT s'il y a eu dépassement
    return permission.statut === 'retourne' && 
          typeof permission.minutes_depassement === 'number' && 
          permission.minutes_depassement > 0
  }


  /* Valider complètement un congé */
  const validerPermission = async (id: number) => {
    loading.value = true
    try {
      const result = await permissionsApi.validerPermission(id)
      
      // Mettre à jour localement
      const index = permissions.value.findIndex(p => p.id === id)
      if (index !== -1) {
        permissions.value[index].statut = 'approuve'
        permissions.value[index].valide_par = result.valide_par  // ← Ou recharger les détails
        permissions.value[index].date_validation = result.date_validation
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
   * Vérifie si un rattrapage peut être ajouté
   */
  const peutAjouterRattrapage = (permission: Permission): boolean => {
    if (!permission) return false
    
    const heuresRestantes = typeof permission.heures_restantes === 'string'
      ? parseFloat(permission.heures_restantes)
      : (permission.heures_restantes || 0)
    
    // Rattrapage possible pour retourne ou rattrapage, avec heures restantes
    return (permission.statut === 'retourne' || permission.statut === 'rattrapage') && 
          heuresRestantes > 0
  }

  /**
   * Vérifie si l'utilisateur peut gérer cette permission
   */
  const canManageThisPermission = (permission: Permission): boolean => {
    if (!permission) return false
    
    // Si l'utilisateur n'est pas manager/admin, il ne peut pas gérer les permissions des autres
    if (!isManagerOrAdmin.value && !isSuperAdmin.value) return false
    
    // Super admin peut tout faire
    if (isSuperAdmin.value) return true
    
    // Vérifier si l'utilisateur de la permission est dans les équipes gérables
    const gerableUser = utilisateursGerables.value.find(u => u.id === permission.utilisateur)
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
    permissions,
    calendrierEvents,
    typesConge,
    utilisateursGerables,
    loading,
    error,

    // Getters
    permissionsEnAttente,
    permissionsRetournees,
    permissionsRattrapage,
    permissionsApprouvees,
    permissionsTransformees,
    permissionsAnnulees,
    totalHeuresARattraper,
    eventsForCalendar,
    canManageOthers,
    isSuperAdmin,
    isManagerOrAdmin,

    // Actions
    fetchTypesConge,
    fetchCalendrier,
    fetchMesPermissions,
    fetchUtilisateursGerables,
    createPermission,
    enregistrerRetour,
    ajouterRattrapage,
    transformerEnConge,
    annulerPermission,
    getPermissionDetails,
    peutRetourner,
    peutTransformerEnConge,
    peutAjouterRattrapage,
    canManageThisPermission,
    clearError
  }
})