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



<style scoped>
.events-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* ============================================
   Header
   ============================================ */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 0.95rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

/* ============================================
   View Toggle
   ============================================ */
.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: #f1f3f5;
  padding: 0.25rem;
  border-radius: 8px;
  margin-right: 0.5rem;
}

.view-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #6c757d;
  transition: all 0.2s;
}

.view-btn i {
  font-size: 1rem;
}

.view-btn:hover {
  background: rgba(255,255,255,0.5);
  color: #495057;
}

.view-btn.active {
  background: white;
  color: #3498db;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* ============================================
   Bouton Rafraîchir
   ============================================ */
.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}

.btn-refresh:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* ============================================
   Filtres
   ============================================ */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.filters-row {
  margin-bottom: 1rem;
}

.filters-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  width: 100%;
}

.filter-group.small {
  max-width: 200px;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.filter-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.filter-btn.active {
  background: #e3f2fd;
  border-color: #3498db;
  color: #1976d2;
  font-weight: 500;
}

.color-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.orange { background: #f39c12; }
.status-dot.green { background: #27ae60; }
.status-dot.red { background: #e74c3c; }
.status-dot.gray { background: #95a5a6; }
.status-dot.blue { background: #3498db; }
.status-dot.purple { background: #9b59b6; }

.count-badge {
  background: rgba(0,0,0,0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 12px;
  font-size: 0.7rem;
  margin-left: 0.25rem;
}

.form-select {
  padding: 0.6rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  width: 100%;
  background: white;
  cursor: pointer;
}

/* ============================================
   Statistiques
   ============================================ */
.stats-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1rem 1.5rem;
  box-shadow: 0 2px 6px rgba(0,0,0,0.05);
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 100px;
}

.stat-value {
  font-size: 1.8rem;
  font-weight: 700;
  color: #2c3e50;
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

/* ============================================
   Vue Calendrier
   ============================================ */
.calendar-view {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.events-calendar {
  height: 600px;
  border-radius: 8px;
  overflow: hidden;
}

/* ============================================
   Vue Timeline
   ============================================ */
.timeline-view {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.loading-state i, .empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.timeline {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.date-group {
  border-bottom: 1px solid #f1f3f5;
  padding-bottom: 1.5rem;
}

.date-header {
  margin-bottom: 1rem;
}

.date-badge {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
  text-transform: uppercase;
  background: #f8f9fa;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.events-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-card {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #adb5bd;
}

.event-card.system {
  opacity: 0.8;
  background: #f8f9fa;
}

.event-color {
  width: 6px;
  border-radius: 3px;
  flex-shrink: 0;
}

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.25rem;
  flex-wrap: wrap;
}

.event-title {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
}

.event-type {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  background: #f1f3f5;
  border-radius: 12px;
  color: #495057;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.event-status {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
}

.event-status.en_attente {
  background: #fff3e0;
  color: #e67e22;
}

.event-status.approuve {
  background: #e8f5e9;
  color: #2e7d32;
}

.event-status.refuse {
  background: #ffebee;
  color: #c62828;
}

.event-status.annule {
  background: #eceff1;
  color: #455a64;
}

.event-meta {
  display: flex;
  gap: 1rem;
  font-size: 0.8rem;
  color: #6c757d;
}

.event-user i, .event-blocked i {
  margin-right: 0.25rem;
}

.event-blocked {
  color: #e74c3c;
}

/* ============================================
   Animations
   ============================================ */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* ============================================
   Responsive
   ============================================ */
@media (max-width: 768px) {
  .events-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: space-between;
  }

  .view-toggle {
    flex: 1;
  }

  .view-btn {
    flex: 1;
    justify-content: center;
  }

  .filter-group.small {
    max-width: 100%;
  }

  .stats-summary {
    gap: 0.5rem;
  }

  .stat-card {
    flex: 1;
    min-width: 60px;
    padding: 0.75rem;
  }

  .stat-value {
    font-size: 1.2rem;
  }

  .stat-label {
    font-size: 0.7rem;
  }

  .events-calendar {
    height: 500px;
  }

  .event-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>