<template>
  <div class="calendar-container">
    <!-- En-tête -->
    <div class="calendar-header">
      <div class="month-year-selector">
        <select v-model="selectedMonth" @change="updateDate">
          <option v-for="(name, index) in monthNames" :key="index" :value="index">
            {{ name }}
          </option>
        </select>
        <select v-model="selectedYear" @change="updateDate">
          <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>

      <div class="nav-buttons">
        <button @click="prevPeriod" class="btn-icon">
          <i class="bi bi-chevron-left"></i>
        </button>
        <button @click="goToToday" class="btn-today">Aujourd'hui</button>
        <button @click="nextPeriod" class="btn-icon">
          <i class="bi bi-chevron-right"></i>
        </button>
      </div>

      <div class="view-switcher">
        <button
          v-for="view in views"
          :key="view.value"
          :class="{ active: currentView === view.value }"
          @click="setView(view.value)"
        >
          {{ view.label }}
        </button>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="calendar-body">
      <!-- Vue Timeline (semaine verticale) -->
      <div v-if="currentView === 'timeline'" class="timeline-view">
        <div class="timeline-header">
          <div class="timeline-header-cell time-header"></div>
          <div 
            v-for="day in weekDays" 
            :key="day.date.toISOString()" 
            class="timeline-header-cell"
            :class="{ today: day.isToday }"
          >
            <div class="day-name">{{ day.weekday }}</div>
            <div class="day-number">{{ day.date.getDate() }}</div>
          </div>
        </div>

        <div class="timeline-body">
          <div class="hours-column">
            <div v-for="hour in 24" :key="hour" class="hour-label">
              {{ (hour - 1).toString().padStart(2, '0') }}:00
            </div>
          </div>

          <div class="days-grid">
            <div 
              v-for="day in weekDays" 
              :key="day.date.toISOString()" 
              class="day-column"
              :class="{ today: day.isToday }"
            >
              <div class="hours-grid">
                <div 
                  v-for="hour in 24" 
                  :key="hour" 
                  class="hour-cell"
                  :class="{ 'hour-alt': hour % 2 === 0 }"
                ></div>
              </div>

              <div class="events-container">
                <div v-for="event in getEventsForDay(day.date)" class="calendar-event"
                  
                  :key="event.id"
                  :class="{ 'all-day': event.allDay }"
                  :style="getEventStyle(event)"
                  @click="$emit('event-click', event)"
                >
                  <div class="event-time">{{ formatEventTime(event) }}</div>
                  <div class="event-title">{{ event.title }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vue Mois -->
      <div v-else-if="currentView === 'month'" class="month-view">
        <div class="month-grid">
          <!-- En-têtes des jours de la semaine -->
          <div v-for="day in weekdaysShort" :key="day" class="month-cell header">
            {{ day }}
          </div>

          <!-- Jours du mois -->
          <div
            v-for="day in monthDays"
            :key="day.date ? day.date.toISOString() : 'empty-' + Math.random()"
            class="month-cell"
            :class="{
              'empty': !day.date,
              'today': day.isToday,
              'other-month': day.isOtherMonth,
              'blocked': day.date && isDateBlocked(day.date)
            }"
          >
            <div v-if="day.date" class="day-number">
              {{ day.date.getDate() }}
            </div>

            <!-- Indicateur de jour bloqué -->
            <div v-if="day.date && isDateBlocked(day.date)" class="blocked-indicator">
              ⛔
            </div>

            <!-- Événements all-day -->
            <div v-if="day.date" class="month-events">
              <div
                v-for="event in getAllDayEventsForDay(day.date)"
                :key="event.id"
                class="month-event all-day"
                :style="{ backgroundColor: event.color }"
              >
                {{ event.title }}
              </div>

              <!-- Événements horaires (petits indicateurs) -->
              <div
                v-for="event in getTimedEventsForDay(day.date)"
                :key="event.id"
                class="month-event timed"
                :style="{ backgroundColor: event.color }"
                :title="formatEventTime(event)"
              >
                {{ formatEventTime(event) }} {{ event.title }}
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
import {
  startOfWeek,
  addDays,
  isSameDay,
  isToday,
  format,
  setMonth,
  setYear,
  getMonth,
  getYear,
  startOfMonth,
  endOfMonth,
  eachDayOfInterval,
  isSameMonth,
  parseISO
} from 'date-fns'
import { fr } from 'date-fns/locale'


const emit = defineEmits<{
  (e: 'event-click', event: CalendarEvent): void
}>()


// ────────────────────────────────────────────────
// Types
type CalendarView = 'timeline' | 'month'

export interface CalendarEvent {
  id: string | number
  title: string
  start: Date
  end?: Date
  allDay?: boolean
  color?: string
  type?: 'conge' | 'ferie' | 'exceptionnel' | 'conge_annuel' | 'weekend'
  isBlocked?: boolean
}

// ────────────────────────────────────────────────
// Props
const props = defineProps<{
  events: CalendarEvent[]
  blockedDates?: Date[]
}>()

// ────────────────────────────────────────────────
// Clés de persistance
const STORAGE_KEYS = {
  VIEW: 'calendar-preferred-view',
  YEAR: 'calendar-year',
  MONTH: 'calendar-month',
  DATE: 'calendar-current-date'
}

// ────────────────────────────────────────────────
// État local avec persistance
const loadInitialDate = (): Date => {
  const savedDate = localStorage.getItem(STORAGE_KEYS.DATE)
  if (savedDate) {
    try {
      const parsed = new Date(savedDate)
      if (!isNaN(parsed.getTime())) {
        return parsed
      }
    } catch (e) {
      console.warn('Failed to parse saved date')
    }
  }
  return new Date()
}

const currentDate = ref<Date>(loadInitialDate())
const selectedMonth = ref<number>(getMonth(currentDate.value))
const selectedYear = ref<number>(getYear(currentDate.value))

// Persistance de la vue choisie
const currentView = ref<CalendarView>(
  (localStorage.getItem(STORAGE_KEYS.VIEW) as CalendarView) || 'timeline'
)

// ────────────────────────────────────────────────
// Watchers pour la persistance
watch(currentDate, (newDate) => {
  localStorage.setItem(STORAGE_KEYS.DATE, newDate.toISOString())
})

watch(selectedMonth, (newMonth) => {
  localStorage.setItem(STORAGE_KEYS.MONTH, String(newMonth))
})

watch(selectedYear, (newYear) => {
  localStorage.setItem(STORAGE_KEYS.YEAR, String(newYear))
})

watch(currentView, (newView) => {
  localStorage.setItem(STORAGE_KEYS.VIEW, newView)
})

// ────────────────────────────────────────────────
// Constantes
const views: { value: CalendarView; label: string }[] = [
  { value: 'timeline', label: 'Timeline' },
  { value: 'month', label: 'Mois' }
]

const monthNames = [
  'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
  'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre'
]

const weekdaysShort = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const years = computed(() => {
  const current = getYear(new Date())
  return Array.from({ length: 11 }, (_, i) => current - 5 + i)
})

// ────────────────────────────────────────────────
// Computed - Semaine (Timeline)
const weekDays = computed(() => {
  const start = startOfWeek(currentDate.value, { weekStartsOn: 1 })
  return Array.from({ length: 7 }, (_, i) => {
    const date = addDays(start, i)
    return {
      date,
      weekday: format(date, 'EEE', { locale: fr }).toUpperCase(),
      isToday: isToday(date)
    }
  })
})

// ────────────────────────────────────────────────
// Computed - Mois
const monthDays = computed(() => {
  const monthStart = startOfMonth(currentDate.value)
  const monthEnd = endOfMonth(currentDate.value)
  const start = startOfWeek(monthStart, { weekStartsOn: 1 })
  const end = startOfWeek(addDays(monthEnd, 6), { weekStartsOn: 1 })
  
  const days = eachDayOfInterval({ start, end })
  
  return days.map(date => ({
    date,
    isToday: isToday(date),
    isOtherMonth: !isSameMonth(date, monthStart)
  }))
})

// ────────────────────────────────────────────────
// Méthodes
const setView = (view: CalendarView) => {
  currentView.value = view
}

const updateDate = () => {
  currentDate.value = setMonth(setYear(currentDate.value, selectedYear.value), selectedMonth.value)
}

const prevPeriod = () => {
  if (currentView.value === 'timeline') {
    currentDate.value = addDays(currentDate.value, -7)
  } else {
    currentDate.value = setMonth(currentDate.value, getMonth(currentDate.value) - 1)
  }
  syncSelectors()
}

const nextPeriod = () => {
  if (currentView.value === 'timeline') {
    currentDate.value = addDays(currentDate.value, 7)
  } else {
    currentDate.value = setMonth(currentDate.value, getMonth(currentDate.value) + 1)
  }
  syncSelectors()
}

const goToToday = () => {
  currentDate.value = new Date()
  syncSelectors()
}

const syncSelectors = () => {
  selectedMonth.value = getMonth(currentDate.value)
  selectedYear.value = getYear(currentDate.value)
}

// ────────────────────────────────────────────────
// Helpers pour les événements
const getEventsForDay = (date: Date) => {
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    const eventStart = new Date(e.start)
    eventStart.setHours(0, 0, 0, 0)
    
    if (!e.end) {
      return eventStart.getTime() === checkDate.getTime()
    }
    
    const eventEnd = new Date(e.end)
    eventEnd.setHours(0, 0, 0, 0)
    // Soustraire 1 jour car end est exclusif
    const eventEndInclusive = new Date(eventEnd)
    eventEndInclusive.setDate(eventEndInclusive.getDate() - 1)
    
    return checkDate >= eventStart && checkDate <= eventEndInclusive
  })
}

// REMPLACE getAllDayEventsForDay par ceci :

const getAllDayEventsForDay = (date: Date) => {
  // Normaliser la date sans l'heure pour comparaison
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    if (!e.allDay) return false
    
    // Date de début de l'événement
    const eventStart = new Date(e.start)
    eventStart.setHours(0, 0, 0, 0)
    
    // Si pas de date de fin, vérifier l'égalité simple
    if (!e.end) {
      return eventStart.getTime() === checkDate.getTime()
    }
    
    // Date de fin (exclusif dans FullCalendar, donc on prend la veille)
    const eventEnd = new Date(e.end)
    eventEnd.setHours(0, 0, 0, 0)
    // Soustraire 1 jour car end est exclusif
    const eventEndInclusive = new Date(eventEnd)
    eventEndInclusive.setDate(eventEndInclusive.getDate() - 1)
    
    // Vérifier si checkDate est dans [start, endInclusive]
    return checkDate >= eventStart && checkDate <= eventEndInclusive
  })
}

const getTimedEventsForDay = (date: Date) => {
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    if (e.allDay) return false
    
    const eventStart = new Date(e.start)
    eventStart.setHours(0, 0, 0, 0)
    
    if (!e.end) {
      return eventStart.getTime() === checkDate.getTime()
    }
    
    const eventEnd = new Date(e.end)
    eventEnd.setHours(0, 0, 0, 0)
    const eventEndInclusive = new Date(eventEnd)
    eventEndInclusive.setDate(eventEndInclusive.getDate() - 1)
    
    return checkDate >= eventStart && checkDate <= eventEndInclusive
  })
}

const formatEventTime = (event: CalendarEvent) => {
  if (event.allDay) return 'Toute la journée'
  return format(event.start, 'HH:mm', { locale: fr })
}

const getEventStyle = (event: CalendarEvent) => {
  // Si allDay ou pas de heures spécifiques, afficher en haut
  if (event.allDay || !hasSpecificTime(event)) {
    return {
      top: '0px',
      height: '40px',
      backgroundColor: event.color || '#e3f2fd',
      position: 'absolute',
      left: '2px',
      right: '2px',
      zIndex: 10
    }
  }

  // Calculer position basée sur l'heure de début
  const startHour = event.start.getHours() + event.start.getMinutes() / 60
  const top = startHour * 60 // 60px par heure
  
  // Calculer durée
  let duration = 1 // 1 heure par défaut
  if (event.end) {
    const endHour = event.end.getHours() + event.end.getMinutes() / 60
    duration = Math.max(endHour - startHour, 0.5)
  }
  const height = duration * 60

  return {
    top: `${top}px`,
    height: `${height}px`,
    backgroundColor: event.color || '#bbdefb',
    position: 'absolute',
    left: '2px',
    right: '2px',
    zIndex: 10
  }
}


const hasSpecificTime = (event: CalendarEvent) => {
  // Vérifier si l'événement a une heure spécifique (pas 00:00)
  return event.start.getHours() !== 0 || event.start.getMinutes() !== 0
}


// Helper pour vérifier si une date est bloquée
const isDateBlocked = (date: Date): boolean => {
  if (!props.blockedDates) return false
  return props.blockedDates.some(blocked => isSameDay(blocked, date))
}

// ────────────────────────────────────────────────
// Lifecycle
onMounted(() => {
  // Synchroniser les sélecteurs avec la date chargée
  syncSelectors()
})
</script>



<style scoped>
.calendar-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}

.calendar-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  align-items: center;
  gap: 1.5rem;
  flex-wrap: wrap;
}

.month-year-selector {
  display: flex;
  gap: 0.75rem;
}

.month-year-selector select {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 1rem;
  cursor: pointer;
}

.month-year-selector select:hover {
  border-color: #3498db;
}

.view-switcher {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.view-switcher button {
  padding: 0.5rem 1.2rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
}

.view-switcher button:hover {
  background: #f8f9fa;
}

.view-switcher button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

/* Vue mois */
.month-view {
  flex: 1;
  overflow: auto;
  padding: 1rem;
}

.month-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  height: 100%;
}

.month-cell {
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  padding: 0.5rem;
  min-height: 100px;
  background: #fafafa;
  position: relative;
  transition: all 0.2s;
}

.month-cell:hover:not(.empty) {
  background: #f0f7ff;
  border-color: #90caf9;
}

.month-cell.header {
  background: #f0f4f8;
  font-weight: bold;
  text-align: center;
  padding: 0.75rem;
  min-height: auto;
}

.month-cell.empty {
  background: #f5f5f5;
  border-color: #e8ecef;
}

.month-cell.today {
  background: #e3f2fd;
  border-color: #90caf9;
}

.month-cell.other-month {
  opacity: 0.5;
}

.month-cell.blocked {
  background: repeating-linear-gradient(
    45deg,
    #f5f5f5,
    #f5f5f5 10px,
    #e0e0e0 10px,
    #e0e0e0 20px
  );
  position: relative;
}

.day-number {
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.month-events {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin-top: 0.5rem;
}

.month-event {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: all 0.2s;
}

.month-event:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.month-event.all-day {
  font-weight: 500;
}

.month-event.timed {
  font-size: 0.75rem;
  opacity: 0.9;
}

/* Indicateur de jour bloqué */
.blocked-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.5rem;
  opacity: 0.3;
  pointer-events: none;
}

/* Navigation */
.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.8rem;
}

.btn-today {
  padding: 0.5rem 1.2rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-today:hover {
  background: #e9ecef;
  border-color: #ced4da;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #f1f3f5;
}

/* Timeline View */
.timeline-view {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}


.timeline-header {
  display: flex;
  border-bottom: 2px solid #dee2e6;
  background: #f8f9fa;
}

.timeline-header-cell {
  flex: 1;
  padding: 0.75rem;
  text-align: center;
  border-right: 1px solid #dee2e6;
  min-width: 120px;
}

.timeline-header-cell.time-header {
  width: 60px;
  flex: 0 0 60px;
}

.timeline-header-cell.today {
  background: #e3f2fd;
}


.timeline-body {
  display: flex;
  flex: 1;
  overflow: auto;
}

.hours-column {
  width: 60px;
  flex: 0 0 60px;
  border-right: 1px solid #dee2e6;
  background: #f8f9fa;
}

.hour-label {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: #6c757d;
  border-bottom: 1px solid #e9ecef;
}

.days-grid {
  display: flex;
  flex: 1;
}

.day-column {
  flex: 1;
  min-width: 120px;
  border-right: 1px solid #dee2e6;
  position: relative;
}

.day-column.today {
  background: #fff8e1;
}


.day-header {
  text-align: center;
  padding: 0.75rem 0.5rem;
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.day-name {
  font-weight: 600;
  color: #495057;
}

.day-number.today {
  background: #3498db;
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  line-height: 32px;
  margin: 0.5rem auto 0;
}


.hours-grid {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.hour-cell {
  height: 60px;
  border-bottom: 1px solid #e9ecef;
}

.hour-cell.hour-alt {
  background: #f8f9fa;
}


.events-container {
  position: relative;
  height: 1440px; /* 24h * 60px */
}

.calendar-event {
  border-radius: 4px;
  padding: 4px 8px;
  font-size: 0.8rem;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.calendar-event:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
  z-index: 20 !important;
}

.calendar-event.all-day {
  border-left: 3px solid #1976d2;
}

.event-time {
  font-size: 0.7rem;
  opacity: 0.8;
  font-weight: 600;
}

.event-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Scrollbar personnalisée */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}
</style>