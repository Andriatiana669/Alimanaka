// frontend/src/store/events.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getYear } from 'date-fns'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type {
  Event,
  EventCalendarEventFromAPI,
  EventParams,
  EventType,
  EventUser
} from '@/types/events'
import { eventsApi } from '@/api/events'
import { useAuthStore } from '@/store/auth'

export const useEventsStore = defineStore('events', () => {
  /* =======================
   * State
   * ======================= */
  const events = ref<Event[]>([])
  const calendrierEvents = ref<EventCalendarEventFromAPI[]>([])
  const eventTypes = ref<EventType[]>([])
  const utilisateurs = ref<EventUser[]>([])
  
  const loading = ref(false)
  const error = ref<string | null>(null)

  /* =======================
   * Getters
   * ======================= */
  
  // Événements par type
  const congesEvents = computed(() => 
    calendrierEvents.value.filter(e => e.type === 'conge')
  )

  const retardsEvents = computed(() => 
    calendrierEvents.value.filter(e => e.type === 'retard')
  )

  const permissionsEvents = computed(() => 
    calendrierEvents.value.filter(e => e.type === 'permission')
  )

  const reposEvents = computed(() => 
    calendrierEvents.value.filter(e => e.type === 'repos_medical')
  )

  const ostieEvents = computed(() => 
    calendrierEvents.value.filter(e => e.type === 'ostie')
  )

  const systemEvents = computed(() => 
    calendrierEvents.value.filter(e => e.isSystem)
  )

  // Événements par statut
  const enAttenteEvents = computed(() => 
    calendrierEvents.value.filter(e => e.statut === 'en_attente')
  )

  const approuveEvents = computed(() => 
    calendrierEvents.value.filter(e => e.statut === 'approuve')
  )

  // Événements bloqués (jours fériés, exceptionnels)
  const blockedDatesEvents = computed(() => 
    calendrierEvents.value.filter(e => e.isBlocked && e.type !== 'weekend')
  )

  /**
   * Conversion des événements API vers le format Calendar
   */
  const eventsForCalendar = computed<CalendarEvent[]>(() =>
    calendrierEvents.value.map(event => ({
      id: String(event.id),
      title: event.title,
      start: new Date(event.start),
      end: event.end ? new Date(event.end) : undefined,
      allDay: event.allDay ?? true,
      color: event.color || getEventColor(event),
      type: event.type,
      user_id: event.user_id,
      statut: event.statut,
      isBlocked: event.isBlocked,
      isSystem: event.isSystem,
      originalEvent: event
    }))
  )

  /**
   * Dates bloquées (pour le calendrier)
   */
  const blockedDates = computed(() => {
    return blockedDatesEvents.value.flatMap(event => {
      const dates: Date[] = []
      const start = new Date(event.start)
      const end = event.end ? new Date(event.end) : start
      let current = new Date(start)
      while (current <= end) {
        dates.push(new Date(current))
        current = addDays(current, 1)
      }
      return dates
    })
  })

  /**
   * Statistiques
   */
  const stats = computed(() => {
    const now = new Date()
    const upcoming = calendrierEvents.value.filter(e => {
      if (e.isSystem) return false
      const eventDate = new Date(e.start)
      return eventDate > now && eventDate < addDays(now, 7)
    })

    const byType: Record<string, number> = {}
    const byStatus: Record<string, number> = {}

    calendrierEvents.value.forEach(e => {
      // Par type
      byType[e.type] = (byType[e.type] || 0) + 1
      
      // Par statut (si existe)
      if (e.statut) {
        byStatus[e.statut] = (byStatus[e.statut] || 0) + 1
      }
    })

    return {
      total: calendrierEvents.value.length,
      byType,
      byStatus,
      upcoming: upcoming.length
    }
  })

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

  /* =======================
   * Actions
   * ======================= */
  
  /**
   * Charger les types d'événements
   */
  const fetchEventTypes = async () => {
    try {
      eventTypes.value = await eventsApi.getTypes()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des types'
      throw err
    }
  }

  /**
   * Charger les utilisateurs
   */
  const fetchUtilisateurs = async () => {
    try {
      utilisateurs.value = await eventsApi.getUtilisateurs()
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement des utilisateurs'
      throw err
    }
  }

  /**
   * Charger les événements du calendrier
   */
  const fetchCalendrier = async (params?: EventParams) => {
    loading.value = true
    error.value = null
    try {
      calendrierEvents.value = await eventsApi.getCalendrier(params)
    } catch (err: any) {
      error.value = err.message || 'Erreur lors du chargement du calendrier'
      throw err
    } finally {
      loading.value = false
    }
  }

  /**
   * Récupère les détails d'un événement
   */
  const getEventDetails = async (id: number): Promise<Event> => {
    try {
      let event = events.value.find(e => e.id === id)
      if (!event) {
        event = await eventsApi.getEventDetails(id)
      }
      return event
    } catch (err: any) {
      error.value = err.message || 'Erreur chargement détails'
      throw err
    }
  }

  /**
   * Rafraîchir toutes les données
   */
  const refreshAll = async (params?: EventParams) => {
    await Promise.all([
      fetchEventTypes(),
      fetchUtilisateurs(),
      fetchCalendrier(params)
    ])
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
    events,
    calendrierEvents,
    eventTypes,
    utilisateurs,
    loading,
    error,

    // Getters
    congesEvents,
    retardsEvents,
    permissionsEvents,
    reposEvents,
    ostieEvents,
    systemEvents,
    enAttenteEvents,
    approuveEvents,
    eventsForCalendar,
    blockedDates,
    stats,
    canManageOthers,
    isSuperAdmin,

    // Actions
    fetchEventTypes,
    fetchUtilisateurs,
    fetchCalendrier,
    getEventDetails,
    refreshAll,
    clearError
  }
})

// Helper
const addDays = (date: Date, days: number): Date => {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

const getEventColor = (event: EventCalendarEventFromAPI): string => {
  if (event.color) return event.color
  
  // Couleurs par défaut selon le type
  const colors: Record<string, string> = {
    conge: '#3498db',
    retard: '#f39c12',
    permission: '#27ae60',
    repos_medical: '#e74c3c',
    ostie: '#9b59b6',
    ferie: '#ffeb3b',
    exceptionnel: '#ff5722',
    weekend: '#e0e0e0',
  }
  
  // Couleurs selon le statut (priorité)
  if (event.statut) {
    if (event.statut === 'en_attente') return '#f39c12'
    if (event.statut === 'approuve') return '#27ae60'
    if (event.statut === 'refuse') return '#e74c3c'
    if (event.statut === 'annule') return '#95a5a6'
  }
  
  return colors[event.type] || '#95a5a6'
}