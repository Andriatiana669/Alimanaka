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
          @click="currentView = view.value"
        >
          {{ view.label }}
        </button>
      </div>
    </div>

    <!-- Contenu principal -->
    <div class="calendar-body">
      <!-- Vue Timeline (semaine verticale) -->
      <div v-if="currentView === 'timeline'" class="timeline-view">
        <div class="hours-column">
          <div v-for="hour in 24" :key="hour" class="hour-label">
            {{ hour.toString().padStart(2, '0') }}:00
          </div>
        </div>

        <div class="days-grid">
          <div v-for="day in weekDays" :key="day.date.toISOString()" class="day-column">
            <div class="day-header">
              <div class="day-name">{{ day.weekday }}</div>
              <div class="day-number" :class="{ today: day.isToday }">
                {{ day.date.getDate() }}
              </div>
            </div>

            <div class="events-container">
              <div
                v-for="event in getEventsForDay(day.date)"
                :key="event.id"
                class="calendar-event"
                :style="getEventStyle(event, day.date)"
              >
                <div class="event-time">{{ formatEventTime(event) }}</div>
                <div class="event-title">{{ event.title }}</div>
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
            :key="day.date ? day.date.toISOString() : 'empty'"
            class="month-cell"
            :class="{
              'empty': !day.date,
              'today': day.isToday,
              'other-month': day.isOtherMonth
            }"
          >
            <div v-if="day.date" class="day-number">
              {{ day.date.getDate() }}
            </div>

            <!-- Événements all-day -->
            <div v-if="day.date" class="month-events">
              <div
                v-for="event in getAllDayEventsForDay(day.date)"
                :key="event.id"
                class="month-event all-day"
                :style="{ backgroundColor: event.color || '#e3f2fd' }"
              >
                {{ event.title }}
              </div>

              <!-- Événements horaires (petits indicateurs) -->
              <div
                v-for="event in getTimedEventsForDay(day.date)"
                :key="event.id"
                class="month-event timed"
                :style="{ backgroundColor: event.color || '#bbdefb' }"
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
import { ref, computed, onMounted } from 'vue'
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

// ────────────────────────────────────────────────
// Types
type CalendarView = 'timeline' | 'month'

interface CalendarEvent {
  id: string | number
  title: string
  start: Date
  end?: Date
  allDay?: boolean
  color?: string
}

// ────────────────────────────────────────────────
// État
const currentDate = ref(new Date())
const currentView = ref<CalendarView>('timeline')

const selectedMonth = ref(getMonth(currentDate.value))
const selectedYear = ref(getYear(currentDate.value))

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
// Vue Semaine (Timeline)
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
// Vue Mois
const monthDays = computed(() => {
  const monthStart = startOfMonth(currentDate.value)
  const monthEnd = endOfMonth(currentDate.value)
  const start = startOfWeek(monthStart, { weekStartsOn: 1 })
  const end = startOfWeek(addDays(monthEnd, 1), { weekStartsOn: 1 })
  
  const days = eachDayOfInterval({ start, end })
  
  return days.map(date => ({
    date,
    isToday: isToday(date),
    isOtherMonth: !isSameMonth(date, monthStart)
  }))
})

// ────────────────────────────────────────────────
// Événements (mock pour tester)
const events = ref<CalendarEvent[]>([])

onMounted(() => {
  // Données de test
  events.value = [
    { id: 'e1', title: 'Réunion DEV', start: new Date(2025, 1, 17, 10, 0), end: new Date(2025, 1, 17, 11, 30), color: '#bbdefb' },
    { id: 'e2', title: 'Congé annuel', start: new Date(2025, 1, 18), allDay: true, color: '#c8e6c9' },
    { id: 'e3', title: 'RDV médical', start: new Date(2025, 1, 19, 14, 0), end: new Date(2025, 1, 19, 15, 30), color: '#ffe0b2' },
    { id: 'e4', title: 'Formation', start: new Date(2025, 1, 20), allDay: true, color: '#d1c4e9' }
  ]
})

// ────────────────────────────────────────────────
// Méthodes
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
// Helpers événements
const getEventsForDay = (date: Date) => {
  return events.value.filter(e => isSameDay(e.start, date))
}

const getAllDayEventsForDay = (date: Date) => {
  return events.value.filter(e => isSameDay(e.start, date) && e.allDay)
}

const getTimedEventsForDay = (date: Date) => {
  return events.value.filter(e => isSameDay(e.start, date) && !e.allDay)
}

const formatEventTime = (event: CalendarEvent) => {
  if (event.allDay) return 'Toute la journée'
  return format(event.start, 'HH:mm')
}

const getEventStyle = (event: CalendarEvent, day: Date) => {
  if (event.allDay) {
    return { backgroundColor: event.color || '#e3f2fd' }
  }

  const startHour = event.start.getHours() + event.start.getMinutes() / 60
  const duration = event.end
    ? (event.end.getTime() - event.start.getTime()) / (1000 * 60 * 60)
    : 1

  return {
    top: `${startHour * 60}px`,
    height: `${duration * 60}px`,
    backgroundColor: event.color || '#bbdefb'
  }
}
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
}

.month-event.all-day {
  font-weight: 500;
}

.month-event.timed {
  font-size: 0.75rem;
  opacity: 0.9;
}

/* Fin Vue Mois */

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
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.4rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
}

.btn-icon:hover {
  background: #f1f3f5;
}

/* Timeline View */
.timeline-view {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.hours-column {
  width: 60px;
  flex-shrink: 0;
  background: #f8f9fa;
  border-right: 1px solid #e0e0e0;
}

.hour-label {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  color: #6c757d;
  border-bottom: 1px solid #e9ecef;
}

.days-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  overflow-x: auto;
}

.day-column {
  border-right: 1px solid #e9ecef;
  position: relative;
  min-width: 180px;
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

.events-container {
  position: relative;
  height: 1440px; /* 24h × 60px */
}

.calendar-event {
  position: absolute;
  left: 4px;
  right: 4px;
  border-radius: 6px;
  padding: 0.5rem;
  font-size: 0.85rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
}

.event-time {
  font-weight: 600;
  font-size: 0.9rem;
}

.event-title {
  margin-top: 0.2rem;
}
</style>