<template>
  <div class="events-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <h1>📋 Calendrier unifié</h1>
        <p class="header-subtitle">Tous les événements en un seul endroit</p>
      </div>
      
      <div class="header-actions">
        <!-- Sélecteur de vue -->
        <div class="view-toggle">
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'timeline' }"
            @click="viewMode = 'timeline'"
          >
            <i class="bi bi-list-ul"></i>
            Timeline
          </button>
          <button 
            class="view-btn" 
            :class="{ active: viewMode === 'calendar' }"
            @click="viewMode = 'calendar'"
          >
            <i class="bi bi-calendar-week"></i>
            Calendrier
          </button>
        </div>
        
        <button class="btn-refresh" @click="refreshData" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          {{ loading ? 'Chargement...' : 'Actualiser' }}
        </button>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-section">
      <!-- Filtre par type -->
      <div class="filters-row">
        <div class="filter-group">
          <label>Type</label>
          <div class="filter-buttons">
            <button 
              v-for="type in eventTypes" 
              :key="type.value"
              class="filter-btn"
              :class="{ active: typeFilters.includes(type.value) }"
              :style="{ borderColor: type.color }"
              @click="toggleTypeFilter(type.value)"
            >
              <span class="color-dot" :style="{ backgroundColor: type.color }"></span>
              {{ type.label }}
              <span v-if="getTypeCount(type.value)" class="count-badge">
                {{ getTypeCount(type.value) }}
              </span>
            </button>
          </div>
        </div>
      </div>

      <!-- Filtre par statut -->
      <div class="filters-row">
        <div class="filter-group">
          <label>Statut</label>
          <div class="filter-buttons">
            <button 
              v-for="status in statusOptions" 
              :key="status.value"
              class="filter-btn"
              :class="{ active: statusFilters.includes(status.value) }"
              @click="toggleStatusFilter(status.value)"
            >
              <span class="status-dot" :class="status.color"></span>
              {{ status.label }}
            </button>
          </div>
        </div>
      </div>

      <!-- Filtre par année -->
      <div class="filters-row">
        <div class="filter-group small">
          <label>Année</label>
          <select v-model="selectedYear" class="form-select">
            <option v-for="year in availableYears" :key="year" :value="year">
              {{ year }}
            </option>
          </select>
        </div>
      </div>
    </div>

    <!-- Résumé -->
    <div class="stats-summary">
      <div class="stat-card">
        <span class="stat-value">{{ stats.total }}</span>
        <span class="stat-label">Total</span>
      </div>
      <div class="stat-card">
        <span class="stat-value">{{ stats.upcoming }}</span>
        <span class="stat-label">À venir (7j)</span>
      </div>
      <div class="stat-card" v-for="(count, type) in stats.byType" :key="type">
        <span class="stat-value">{{ count }}</span>
        <span class="stat-label">{{ getTypeLabel(type) }}</span>
      </div>
    </div>

    <!-- VUE CALENDRIER -->
    <div v-if="viewMode === 'calendar'" class="calendar-view">
      <Calendar
        :events="eventsForCalendar"
        :blocked-dates="blockedDates"
        :default-view="'month'"
        class="events-calendar"
        @event-click="onEventClick"
      />
    </div>

    <!-- VUE TIMELINE -->
    <div v-if="viewMode === 'timeline'" class="timeline-view">
      <div v-if="loading && !eventsForCalendar.length" class="loading-state">
        <div class="spinner"></div>
        <p>Chargement des événements...</p>
      </div>

      <div v-else-if="filteredEvents.length === 0" class="empty-state">
        <i class="bi bi-calendar-x"></i>
        <h3>Aucun événement trouvé</h3>
      </div>

      <div v-else class="timeline">
        <div v-for="(group, dateKey) in groupedEvents" :key="dateKey" class="date-group">
          <div class="date-header">
            <span class="date-badge">{{ formatDateHeader(dateKey) }}</span>
          </div>
          
          <div class="events-group">
            <div 
              v-for="event in group" 
              :key="event.id"
              class="event-card"
              :class="{ system: event.isSystem }"
              @click="openEventDetails(event)"
            >
              <div class="event-color" :style="{ backgroundColor: event.color }"></div>
              <div class="event-content">
                <div class="event-header">
                  <span class="event-title">{{ event.title }}</span>
                  <span class="event-type">{{ getTypeLabel(event.type) }}</span>
                  <span v-if="event.statut" class="event-status" :class="event.statut">
                    {{ getStatusLabel(event.statut) }}
                  </span>
                </div>
                <div class="event-meta">
                  <span v-if="event.user_display_name" class="event-user">
                    <i class="bi bi-person-circle"></i> {{ event.user_display_name }}
                  </span>
                  <span v-if="event.isBlocked" class="event-blocked">
                    <i class="bi bi-lock"></i> Bloqué
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useEventsStore } from '@/store/events'
import Calendar from '@/components/common/Calendar.vue'
import { format, parseISO, subDays, getYear } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Store
const eventsStore = useEventsStore()

// Mode d'affichage
const viewMode = ref<'timeline' | 'calendar'>('calendar')

// Filtres
const typeFilters = ref<string[]>([])
const statusFilters = ref<string[]>([])
const selectedYear = ref(getYear(new Date()))

// Options de statut
const statusOptions = [
  { value: 'en_attente', label: 'En attente', color: 'orange' },
  { value: 'approuve', label: 'Approuvé', color: 'green' },
  { value: 'refuse', label: 'Refusé', color: 'red' },
  { value: 'annule', label: 'Annulé', color: 'gray' },
  { value: 'retourne', label: 'Retourné', color: 'blue' },
  { value: 'rattrapage', label: 'Rattrapage', color: 'purple' }
]

// Années disponibles
const availableYears = computed(() => {
  const current = getYear(new Date())
  return [current - 1, current, current + 1]
})

// Types d'événements
const eventTypes = computed(() => eventsStore.eventTypes)

// Événements filtrés
const filteredEvents = computed(() => {
  let events = eventsStore.eventsForCalendar

  if (typeFilters.value.length > 0) {
    events = events.filter(e => typeFilters.value.includes(e.type))
  }

  if (statusFilters.value.length > 0) {
    events = events.filter(e => e.statut && statusFilters.value.includes(e.statut))
  }

  return events
})

// Événements groupés par date
const groupedEvents = computed(() => {
  const groups: Record<string, any[]> = {}
  filteredEvents.value.forEach(event => {
    const dateKey = format(event.start, 'yyyy-MM-dd')
    if (!groups[dateKey]) groups[dateKey] = []
    groups[dateKey].push(event)
  })
  return groups
})

// Statistiques
const stats = computed(() => eventsStore.stats)
const eventsForCalendar = computed(() => filteredEvents.value)
const blockedDates = computed(() => eventsStore.blockedDates)
const loading = computed(() => eventsStore.loading)

// ============================================
// Méthodes
// ============================================

const toggleTypeFilter = (type: string) => {
  const index = typeFilters.value.indexOf(type)
  if (index === -1) {
    typeFilters.value.push(type)
  } else {
    typeFilters.value.splice(index, 1)
  }
}

const toggleStatusFilter = (status: string) => {
  const index = statusFilters.value.indexOf(status)
  if (index === -1) {
    statusFilters.value.push(status)
  } else {
    statusFilters.value.splice(index, 1)
  }
}

const getTypeLabel = (type: string): string => {
  const found = eventTypes.value.find(t => t.value === type)
  return found?.label || type
}

const getTypeCount = (type: string): number => {
  return eventsStore.eventsForCalendar.filter(e => e.type === type).length
}

const getStatusLabel = (status: string): string => {
  const found = statusOptions.find(s => s.value === status)
  return found?.label || status
}

const formatDateHeader = (dateKey: string): string => {
  const date = parseISO(dateKey)
  const today = new Date()
  const yesterday = subDays(today, 1)
  
  if (format(date, 'yyyy-MM-dd') === format(today, 'yyyy-MM-dd')) {
    return "Aujourd'hui"
  } else if (format(date, 'yyyy-MM-dd') === format(yesterday, 'yyyy-MM-dd')) {
    return 'Hier'
  } else {
    return format(date, 'EEEE d MMMM yyyy', { locale: fr })
  }
}

const onEventClick = (event: any) => {
  console.log('Event clicked:', event)
  // Ouvrir modal de détails (à implémenter)
}

const refreshData = async () => {
  await eventsStore.fetchCalendrier({ annee: selectedYear.value })
}


// ============================================
// Gestion des clics sur événements
// ============================================
const openEventDetails = (event: any) => {
  console.log('Ouverture des détails pour:', event)
  // À implémenter selon vos besoins
  // Par exemple, ouvrir un modal avec les détails
  // ou naviguer vers la page de détail correspondante
}


// Watch
watch(selectedYear, () => {
  refreshData()
})

// Initialisation
onMounted(async () => {
  await eventsStore.refreshAll({ annee: selectedYear.value })
})
</script>