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
      <!-- Vue Timeline (semaine horizontale - JOURS À GAUCHE, HEURES EN HAUT) -->
      <div v-if="currentView === 'timeline'" class="timeline-view">
        <div class="timeline-header-horizontal">
          <div class="corner-cell"></div>
          <div 
            v-for="hour in 24" 
            :key="hour" 
            class="hour-header-cell"
          >
            {{ formatHour(hour - 1) }}
          </div>
        </div>

        <div class="timeline-body-horizontal">
          <div class="days-column">
            <div 
              v-for="day in weekDays" 
              :key="day.date.toISOString()" 
              class="day-row-header"
              :class="{ today: day.isToday }"
            >
              <div class="day-name">{{ day.weekday }}</div>
              <div class="day-number">{{ day.date.getDate() }}</div>
            </div>
          </div>

          <div class="hours-grid-horizontal">
            <div 
              v-for="day in weekDays" 
              :key="day.date.toISOString()" 
              class="day-row"
              :class="{ today: day.isToday }"
            >
              <div class="hours-row">
                <div 
                  v-for="hour in 24" 
                  :key="hour" 
                  class="hour-cell-horizontal"
                  :class="{ 'hour-alt': hour % 2 === 0 }"
                ></div>
              </div>

              <div class="events-container-horizontal">
                <div 
                  v-for="event in getTimelineEventsForDay(day.date)" 
                  :key="event.id"
                  class="calendar-event"
                  :class="getEventClass(event)"
                  :style="getEventStyleHorizontal(event)"
                  @click="$emit('event-click', event)"
                >
                  <div class="event-time">{{ formatEventTime(event) }}</div>
                  <div class="event-title">{{ getEventTitle(event) }}</div>
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

            <!-- Événements du mois -->
            <div v-if="day.date" class="month-events">
              <!-- Événements all-day (fériés, weekends, etc.) -->
              <div
                v-for="event in getAllDayEventsForDay(day.date)"
                :key="event.id"
                class="month-event all-day"
                :style="{ backgroundColor: event.color }"
                @click.stop="$emit('event-click', event)"
              >
                {{ event.title }}
              </div>

              <!-- Congés (tous les événements de type 'conge') -->
              <div
                v-for="event in getCongeEventsForDay(day.date)"
                :key="event.id"
                class="month-event timed"
                :style="{ backgroundColor: event.color, borderLeft: '3px solid #1976d2' }"
                @click.stop="$emit('event-click', event)"
              >
                <span class="event-time">{{ formatEventTime(event) }}</span>
                <span class="event-title">{{ getEventTitle(event) }}</span>
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
  isSameMonth
} from 'date-fns'
import { fr } from 'date-fns/locale'

const emit = defineEmits<{
  (e: 'event-click', event: CalendarEvent): void
}>()

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
  user_id?: number
  conge_id?: number
  statut?: string
  motif?: string
  can_cancel?: boolean
}

// Props
const props = defineProps<{
  events: CalendarEvent[]
  blockedDates?: Date[]
}>()

// Clés de persistance
const STORAGE_KEYS = {
  VIEW: 'calendar-preferred-view',
  YEAR: 'calendar-year',
  MONTH: 'calendar-month',
  DATE: 'calendar-current-date'
}

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
const currentView = ref<CalendarView>(
  (localStorage.getItem(STORAGE_KEYS.VIEW) as CalendarView) || 'timeline'
)

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

// Méthodes
const formatHour = (hour: number) => {
  return `${hour.toString().padStart(2, '0')}:30`
}

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

// Helpers pour les événements - Timeline
const getTimelineEventsForDay = (date: Date) => {
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    // Exclure les événements allDay sauf weekends/fériés
    if (e.allDay && e.type !== 'weekend' && e.type !== 'ferie') {
      return false
    }
    
    const eventStart = new Date(e.start)
    const eventEnd = e.end ? new Date(e.end) : null
    
    // Vérifier si la date est dans l'intervalle de l'événement
    const startDay = new Date(eventStart)
    startDay.setHours(0, 0, 0, 0)
    
    if (!eventEnd) {
      return startDay.getTime() === checkDate.getTime()
    }
    
    const endDay = new Date(eventEnd)
    endDay.setHours(0, 0, 0, 0)
    
    // Pour les événements multi-jours, on inclut tous les jours
    return checkDate >= startDay && checkDate <= endDay
  })
}

// Helpers pour les événements - Mois
const getAllDayEventsForDay = (date: Date) => {
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    if (!e.allDay) return false
    
    const eventStart = new Date(e.start)
    eventStart.setHours(0, 0, 0, 0)
    
    if (!e.end) {
      return eventStart.getTime() === checkDate.getTime()
    }
    
    const eventEnd = new Date(e.end)
    eventEnd.setHours(0, 0, 0, 0)
    
    return checkDate >= eventStart && checkDate < eventEnd
  })
}

const getCongeEventsForDay = (date: Date) => {
  const checkDate = new Date(date)
  checkDate.setHours(0, 0, 0, 0)
  
  return props.events.filter(e => {
    if (e.type !== 'conge') return false
    
    const eventStart = new Date(e.start)
    const eventEnd = e.end ? new Date(e.end) : null
    
    const startDay = new Date(eventStart)
    startDay.setHours(0, 0, 0, 0)
    
    if (!eventEnd) {
      return startDay.getTime() === checkDate.getTime()
    }
    
    const endDay = new Date(eventEnd)
    endDay.setHours(0, 0, 0, 0)
    
    return checkDate >= startDay && checkDate <= endDay
  })
}

// Formatage
const formatEventTime = (event: CalendarEvent) => {
  if (event.allDay) {
    if (event.type === 'weekend') return 'Weekend'
    if (event.type === 'ferie') return 'Férié'
    if (event.type === 'exceptionnel') return 'Exceptionnel'
    if (event.type === 'conge_annuel') return 'Congé annuel'
    return 'Toute la journée'
  }
  
  const startStr = format(event.start, 'HH:mm')
  
  if (event.end) {
    const duration = (event.end.getTime() - event.start.getTime()) / (1000 * 60 * 60)
    if (duration <= 24) {
      const endStr = format(event.end, 'HH:mm')
      return `${startStr} - ${endStr}`
    }
  }
  
  return startStr
}

const getEventTitle = (event: CalendarEvent) => {
  // Extraire le nom de l'utilisateur du titre
  const title = event.title
  if (title.includes('-')) {
    return title.split('-')[0].trim()
  }
  return title
}

const getEventClass = (event: CalendarEvent) => {
  const classes = []
  
  if (event.allDay) classes.push('all-day')
  if (event.type === 'conge') {
    const hour = event.start.getHours()
    if (hour === 8 && event.end?.getHours() === 12) classes.push('conge-matin')
    else if (hour === 12 && event.end?.getHours() === 14) classes.push('conge-midi')
    else if (hour === 8 && event.end?.getHours() === 17) classes.push('conge-journee')
  }
  
  return classes.join(' ')
}

// Style pour la vue horizontale
const getEventStyleHorizontal = (event: CalendarEvent) => {
  if (event.allDay) {
    return {
      left: '0px',
      width: '100%',
      height: '30px',
      backgroundColor: event.color || '#e3f2fd',
      position: 'absolute',
      top: '2px',
      zIndex: 5,
      opacity: 0.8,
      fontSize: '0.7rem',
      padding: '2px 4px'
    }
  }

  const startHour = event.start.getHours() + event.start.getMinutes() / 60
  const left = startHour * 80
  
  let duration = 1
  if (event.end) {
    const endHour = event.end.getHours() + event.end.getMinutes() / 60
    duration = Math.max(endHour - startHour, 0.5)
  }
  const width = duration * 80

  // Décalage vertical basé sur l'ID pour éviter la superposition
  const eventId = typeof event.id === 'string' ? parseInt(event.id.split('_')[1] || '0') : (event.id as number)
  const verticalOffset = (eventId % 5) * 16

  return {
    left: `${left}px`,
    width: `${width}px`,
    top: `${2 + verticalOffset}px`,
    height: '30px',
    backgroundColor: event.color || '#bbdefb',
    position: 'absolute',
    zIndex: 10,
    overflow: 'hidden',
    minWidth: '40px',
    border: '1px solid rgba(0,0,0,0.1)',
    borderRadius: '4px',
    fontSize: '0.7rem',
    padding: '2px 4px'
  }
}

// Helper pour vérifier si une date est bloquée
const isDateBlocked = (date: Date): boolean => {
  if (!props.blockedDates) return false
  return props.blockedDates.some(blocked => isSameDay(blocked, date))
}

// Lifecycle
onMounted(() => {
  syncSelectors()
})
</script>

<style scoped>
/* Garder tout le style existant inchangé */
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
  gap: 2px;
  margin-top: 0.5rem;
  max-height: 80px;
  overflow-y: auto;
}

.month-event {
  padding: 2px 4px;
  border-radius: 3px;
  font-size: 0.7rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: pointer;
  transition: all 0.2s;
  margin-bottom: 1px;
}

.month-event:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  z-index: 10;
}

.month-event.all-day {
  font-weight: 500;
}

.month-event.timed {
  font-size: 0.65rem;
  opacity: 0.9;
  display: flex;
  gap: 2px;
  align-items: center;
}

.month-event.timed .event-time {
  font-weight: 600;
  background: rgba(0,0,0,0.1);
  padding: 0 2px;
  border-radius: 2px;
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

.timeline-header-horizontal {
  display: flex;
  border-bottom: 2px solid #dee2e6;
  background: #f8f9fa;
  flex-shrink: 0;
}

.corner-cell {
  width: 100px;
  flex: 0 0 100px;
  border-right: 1px solid #dee2e6;
}

.hour-header-cell {
  flex: 1;
  width: 80px;
  padding: 0.5rem;
  text-align: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: #495057;
  border-right: 1px solid #e9ecef;
  background: #f8f9fa;
}

.timeline-body-horizontal {
  display: flex;
  flex: 1;
  overflow: auto;
}

.days-column {
  width: 100px;
  flex: 0 0 100px;
  border-right: 1px solid #dee2e6;
  background: #f8f9fa;
  flex-shrink: 0;
}

.day-row-header {
  height: 80px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid #e9ecef;
  padding: 0.5rem;
}

.day-row-header.today {
  background: #e3f2fd;
}

.day-row-header .day-name {
  font-size: 0.75rem;
  font-weight: 600;
  color: #6c757d;
  text-transform: uppercase;
}

.day-row-header .day-number {
  font-size: 1.25rem;
  font-weight: 700;
  color: #2c3e50;
  margin-top: 0.25rem;
}

.day-row-header.today .day-number {
  background: #3498db;
  color: white;
  border-radius: 50%;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
}

.hours-grid-horizontal {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow-x: hidden;
}

.day-row {
  height: 80px;
  position: relative;
  border-bottom: 1px solid #e9ecef;
  display: flex;
}

.day-row.today {
  background: #fff8e1;
}

.hours-row {
  display: flex;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
}

.hour-cell-horizontal {
  flex: 1;
  width: 80px;
  border-right: 1px solid #e9ecef;
  height: 100%;
}

.hour-cell-horizontal.hour-alt {
  background: #f8f9fa;
}

.events-container-horizontal {
  position: relative;
  height: 100%;
  width: 100%;
  pointer-events: none;
}

.events-container-horizontal .calendar-event {
  pointer-events: auto;
}

.calendar-event {
  border-radius: 4px;
  cursor: pointer;
  overflow: hidden;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  justify-content: center;
  white-space: nowrap;
}

.calendar-event:hover {
  transform: scale(1.02);
  box-shadow: 0 2px 6px rgba(0,0,0,0.2);
  z-index: 100 !important;
}

.calendar-event.all-day {
  border-top: 2px solid #1976d2;
}

.calendar-event.conge-matin {
  background: #c8e6c9;
  border-left: 3px solid #2e7d32;
}

.calendar-event.conge-midi {
  background: #ffe0b2;
  border-left: 3px solid #e65100;
}

.calendar-event.conge-journee {
  background: #bbdefb;
  border-left: 3px solid #0d47a1;
}

.event-time {
  font-size: 0.6rem;
  opacity: 0.8;
  font-weight: 600;
  white-space: nowrap;
}

.event-title {
  font-weight: 500;
  font-size: 0.7rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Scrollbar */
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

/* Responsive */
@media (max-width: 768px) {
  .hour-header-cell {
    width: 60px;
    font-size: 0.65rem;
  }
  
  .hour-cell-horizontal {
    width: 60px;
  }
  
  .days-column,
  .corner-cell {
    width: 70px;
    flex: 0 0 70px;
  }
  
  .day-row-header {
    height: 60px;
  }
  
  .day-row {
    height: 60px;
  }
  
  .month-event {
    font-size: 0.6rem;
    padding: 1px 2px;
  }
}
</style>