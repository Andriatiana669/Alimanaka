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
    </div>

    <!-- Contenu principal - Vue Mois uniquement -->
    <div class="calendar-body">
      <div class="month-view">
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
                :class="{
                  'validated': event.type === 'conge' && getCongeStatus(event.id) === 'approuve',
                  'refused': event.type === 'conge' && getCongeStatus(event.id) === 'refuse'
                }"
                :style="{ backgroundColor: event.color }"
                @click.stop="$emit('event-click', event)"
              >
                <span v-if="event.type === 'conge' && getCongeStatus(event.id) === 'approuve'" class="status-icon">✓</span>
                <span v-if="event.type === 'conge' && getCongeStatus(event.id) === 'refuse'" class="status-icon">✗</span>
                {{ event.title }}
              </div>

              <!-- Événements horaires (petits indicateurs) -->
              <div
                v-for="event in getTimedEventsForDay(day.date)"
                :key="event.id"
                class="month-event timed"
                :class="{
                  'validated': event.type === 'conge' && getCongeStatus(event.id) === 'approuve',
                  'refused': event.type === 'conge' && getCongeStatus(event.id) === 'refuse'
                }"
                :style="{ backgroundColor: event.color }"
                :title="formatEventTime(event)"
                @click.stop="$emit('event-click', event)"
              >
                <span v-if="event.type === 'conge' && getCongeStatus(event.id) === 'approuve'" class="status-icon">✓</span>
                <span v-if="event.type === 'conge' && getCongeStatus(event.id) === 'refuse'" class="status-icon">✗</span>
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
  conges?: any[]
}>()

// ────────────────────────────────────────────────
// Helper pour récupérer le statut d'un congé
const getCongeStatus = (eventId: string | number): string | null => {
  const congeId = parseInt(String(eventId).replace('conge_', ''))
  const conge = props.conges?.find(c => c.id === congeId)
  return conge?.statut || null
}

// ────────────────────────────────────────────────
// Clés de persistance
const STORAGE_KEYS = {
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

// ────────────────────────────────────────────────
// Constantes
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
// Méthodes de navigation
const updateDate = () => {
  currentDate.value = setMonth(setYear(currentDate.value, selectedYear.value), selectedMonth.value)
}

const prevPeriod = () => {
  currentDate.value = setMonth(currentDate.value, getMonth(currentDate.value) - 1)
  syncSelectors()
}

const nextPeriod = () => {
  currentDate.value = setMonth(currentDate.value, getMonth(currentDate.value) + 1)
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
    const eventEndInclusive = new Date(eventEnd)
    eventEndInclusive.setDate(eventEndInclusive.getDate() - 1)
    
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
  if (event.allDay) return 'Tlj'
  return format(event.start, 'HH:mm', { locale: fr })
}

// Helper pour vérifier si une date est bloquée
const isDateBlocked = (date: Date): boolean => {
  if (!props.blockedDates) return false
  return props.blockedDates.some(blocked => isSameDay(blocked, date))
}

// ────────────────────────────────────────────────
// Lifecycle
onMounted(() => {
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

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-left: auto;
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
  min-height: 500px;
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
  max-height: calc(100% - 30px);
  overflow-y: auto;
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
  display: flex;
  align-items: center;
  gap: 4px;
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

/* Styles pour validé/refusé */
.month-event.validated {
  border-left: 3px solid #4caf50;
  background: linear-gradient(90deg, #e8f5e9 0%, var(--bg-color, inherit) 100%);
}

.month-event.refused {
  border-left: 3px solid #f44336;
  background: linear-gradient(90deg, #ffebee 0%, var(--bg-color, inherit) 100%);
  opacity: 0.8;
}

.status-icon {
  font-size: 0.7rem;
  font-weight: bold;
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

/* Indicateur Droit */
.month-event.droit {
  background: linear-gradient(135deg, #9b59b6, #8e44ad);
  color: white;
  border-left: 3px solid #f1c40f;
}

.month-event.droit::before {
  content: "⚖️";
  margin-right: 4px;
}

/* Scrollbar personnalisée */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
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
  .calendar-header {
    flex-direction: column;
    align-items: stretch;
  }

  .nav-buttons {
    margin-left: 0;
    justify-content: center;
  }

  .month-cell {
    min-height: 80px;
    padding: 0.25rem;
  }

  .month-event {
    font-size: 0.7rem;
    padding: 2px 4px;
  }
}
</style>