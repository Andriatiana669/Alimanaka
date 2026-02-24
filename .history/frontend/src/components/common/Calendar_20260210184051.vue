<template>
    <div class="calendar-container">
        <!-- En-tête avec navigation -->
        <div class="calendar-header">
            <div class="month-year-selector">
                <select v-model="selectedMonth" @change="updateDate">
                <option v-for="m in 12" :key="m" :value="m-1">
                    {{ monthNames[m-1] }}
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

        <!-- Contenu -->
        <div class="calendar-body">
        <!-- Vue Timeline (Semaine verticale avec heures) -->
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

            <!-- Placeholder pour les autres vues -->
            <div v-else class="placeholder">
                <p>Vues Mois / Agenda en cours de développement...</p>
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
  endOfMonth
} from 'date-fns'
import { fr } from 'date-fns/locale'

// ────────────────────────────────────────────────
// Types d'événements (à affiner plus tard)
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
type CalendarView = 'timeline' | 'month'

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

const years = computed(() => {
  const current = getYear(new Date())
  const range = 10
  return Array.from({ length: range * 2 + 1 }, (_, i) => current - range + i)
})

// ────────────────────────────────────────────────
// Semaine courante (lundi → dimanche)
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
// Événements (mock pour l'instant)
const events = ref<CalendarEvent[]>([])

// Exemple de données temporaires
onMounted(() => {
  // À remplacer par un appel API plus tard
  events.value = [
    {
      id: 1,
      title: 'Réunion équipe DEV',
      start: new Date(2025, 1, 11, 10, 0),
      end: new Date(2025, 1, 11, 11, 30),
      color: '#bbdefb'
    },
    {
      id: 2,
      title: 'Congé - Marie',
      start: new Date(2025, 1, 12, 8, 0),
      allDay: true,
      color: '#c8e6c9'
    }
  ]
})

// ────────────────────────────────────────────────
// Méthodes de navigation
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

const formatEventTime = (event: CalendarEvent) => {
  if (event.allDay) return 'Toute la journée'
  return format(event.start, 'HH:mm')
}

const getEventStyle = (event: CalendarEvent, day: Date) => {
  if (event.allDay) {
    return { backgroundColor: event.color || '#e3f2fd', borderLeft: `4px solid ${event.color || '#2196f3'}` }
  }

  // Calcul position/taille pour timeline (simplifié)
  const startHour = event.start.getHours() + event.start.getMinutes() / 60
  const duration = event.end
    ? (event.end.getTime() - event.start.getTime()) / (1000 * 60 * 60)
    : 1

  return {
    top: `${startHour * 60}px`,           // 60px par heure
    height: `${duration * 60}px`,
    backgroundColor: event.color || '#e3f2fd',
    borderLeft: `4px solid ${event.color || '#2196f3'}`
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