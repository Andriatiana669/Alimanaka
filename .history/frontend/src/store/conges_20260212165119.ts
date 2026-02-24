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

export const useCongesStore = defineStore('conges', () => {
  // State
  const conges = ref<Conge[]>([])
  const calendrierEvents = ref<CalendarEventFromAPI[]>([])
  const typesConge = ref<TypeCongeConfig[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const congesApprouves = computed(() => 
    conges.value.filter(c => c.statut === 'approuve')
  )

  const congesEnAttente = computed(() => 
    conges.value.filter(c => c.statut === 'en_attente')
  )

  // Convertit les événements API (string dates) en CalendarEvent (Date objects)
  const eventsForCalendar = computed((): CalendarEvent[] => {
    return calendrierEvents.value.map(event => ({
      id: String(event.id),
      title: event.title,
      start: new Date(event.start),
      end: event.end ? new Date(event.end) : undefined,
      allDay: event.allDay,
      color: event.color
    }))
  })

  // Actions
  const fetchTypesConge = async () => {
    try {
      const data = await congesApi.getTypesConge()
      typesConge.value = data
    } catch (err: any) {
      error.value = err.message
    }
  }

  const fetchCalendrier = async (annee?: number) => {
    loading.value = true
    error.value = null
    try {
      const data = await congesApi.getCalendrier(annee)
      calendrierEvents.value = data
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
      const data = await congesApi.getMesConges(annee)
      conges.value = data
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
      await fetchCalendrier(new Date(data.date_debut).getFullYear())
      return newConge
    } catch (err: any) {
      error.value = err.response?.data?.error || err.message || 'Erreur lors de la création'
      throw err
    } finally {
      loading.value = false
    }
  }

  const annulerConge = async (id: number) => {
    try {
      await congesApi.annulerConge(id)
      const index = conges.value.findIndex(c => c.id === id)
      if (index !== -1) {
        conges.value[index].statut = 'annule'
      }
      return true
    } catch (err: any) {
      error.value = err.message
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
      error.value = err.message
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
      error.value = err.message
    }
  }

  // Helper: Vérifier si une date est bloquée
  const isDateBlocked = (date: Date): boolean => {
    const dateStr = date.toISOString().split('T')[0]
    if (!dateStr) return false
    
    const event = calendrierEvents.value.find(e => {
      if (!e.start) return false
      
      const eventStart = new Date(e.start).toISOString().split('T')[0]
      const eventEnd = e.end 
        ? new Date(e.end).toISOString().split('T')[0] 
        : eventStart
      
      if (!eventStart || !eventEnd) return false
      
      return dateStr >= eventStart && dateStr <= eventEnd && e.isBlocked
    })
    
    return !!event
  }

  const clearError = () => {
    error.value = null
  }

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