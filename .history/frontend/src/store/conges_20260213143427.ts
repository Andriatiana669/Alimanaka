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
import { useAuthStore } from '@/store/auth'

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

      // ← RAFRAÎCHIT LE SOLDE IMMÉDIATEMENT APRÈS CRÉATION
      const authStore = useAuthStore()
      await authStore.refreshSolde()

      // Recharge le calendrier
      await fetchCalendrier(new Date(data.date_debut).getFullYear())

      return newConge
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Erreur'
      throw err
    } finally {
      loading.value = false
    }
  }

  const annulerConge = async (id: number) => {
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

