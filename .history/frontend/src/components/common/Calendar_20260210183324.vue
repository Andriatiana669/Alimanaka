<!-- frontend/src/components/common/Calendar.vue -->
<template>
  <div class="calendar-container">
    <!-- En-tête avec navigation + vue switcher -->
    <div class="calendar-header">
      <div class="nav-buttons">
        <button @click="prevPeriod" class="btn-icon">
          <i class="bi bi-chevron-left"></i>
        </button>
        <h2>{{ currentPeriodLabel }}</h2>
        <button @click="nextPeriod" class="btn-icon">
          <i class="bi bi-chevron-right"></i>
        </button>
        <button @click="goToToday" class="btn-today">Aujourd'hui</button>
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
      <!-- Vue Semaine -->
      <div v-if="currentView === 'week'" class="week-view">
        <div class="week-days-header">
          <div v-for="day in weekDays" :key="day.date" class="day-header">
            <div class="day-name">{{ day.weekday }}</div>
            <div class="day-number" :class="{ today: day.isToday }">
              {{ day.date.getDate() }}
            </div>
          </div>
        </div>

        <div class="week-grid">
          <div v-for="day in weekDays" :key="day.date" class="day-column">
            <!-- Ici viendront les événements de la journée -->
            <div
              v-for="event in getEventsForDay(day.date)"
              :key="event.id"
              class="calendar-event"
              :style="getEventStyle(event)"
            >
              <div class="event-time">{{ formatEventTime(event) }}</div>
              <div class="event-title">{{ event.title }}</div>
              <div class="event-subtitle" v-if="event.subtitle">
                {{ event.subtitle }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Vue Mois (placeholder pour l'instant) -->
      <div v-else-if="currentView === 'month'" class="month-view">
        <p>Vista mensual en desarrollo...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { format, startOfWeek, addDays, isSameDay, isToday } from 'date-fns'
import { fr } from 'date-fns/locale'

// ────────────────────────────────────────────────
// Props (si réutilisable dans différentes pages)
defineProps<{
  events?: CalendarEvent[]          // on pourra passer les événements en props
  defaultView?: 'week' | 'month'    // vue par défaut
}>()

// ────────────────────────────────────────────────
// Types (à déplacer dans types/calendar.ts plus tard)
interface CalendarEvent {
  id: string | number
  title: string
  subtitle?: string
  start: Date
  end?: Date
  allDay?: boolean
  color?: string
  // ... autres champs (user, pole, equipe, type: 'conge'|'reunion'|'retard'...)
}

// ────────────────────────────────────────────────
// État
const currentDate = ref(new Date())
const currentView = ref<'week' | 'month'>('week')

const views = [
  { value: 'week', label: 'Semaine' },
  { value: 'month', label: 'Mois' }
]

// ────────────────────────────────────────────────
// Computed - Semaine courante
const weekDays = computed(() => {
  const start = startOfWeek(currentDate.value, { weekStartsOn: 1, locale: fr }) // lundi
  return Array.from({ length: 7 }, (_, i) => {
    const date = addDays(start, i)
    return {
      date,
      weekday: format(date, 'EEE', { locale: fr }).toUpperCase(),
      isToday: isToday(date)
    }
  })
})

const currentPeriodLabel = computed(() => {
  if (currentView.value === 'week') {
    const start = weekDays.value[0].date
    const end = weekDays.value[6].date
    return `${format(start, 'd MMM', { locale: fr })} — ${format(end, 'd MMM yyyy', { locale: fr })}`
  }
  return format(currentDate.value, 'MMMM yyyy', { locale: fr })
})

// ────────────────────────────────────────────────
// Événements (pour l'instant mock ou props)
const events = ref<CalendarEvent[]>([]) // ← à remplacer par appel API ou props

// Exemple mock (à supprimer après)
onMounted(() => {
  // events.value = [...] // chargement futur via api
})

// ────────────────────────────────────────────────
// Méthodes
const setView = (view: 'week' | 'month') => {
  currentView.value = view
}

const prevPeriod = () => {
  if (currentView.value === 'week') {
    currentDate.value = addDays(currentDate.value, -7)
  }
}

const nextPeriod = () => {
  if (currentView.value === 'week') {
    currentDate.value = addDays(currentDate.value, 7)
  }
}

const goToToday = () => {
  currentDate.value = new Date()
}

const getEventsForDay = (date: Date) => {
  return events.value.filter(e => isSameDay(e.start, date))
}

const formatEventTime = (event: CalendarEvent) => {
  if (event.allDay) return 'Toute la journée'
  return format(event.start, 'HH:mm')
}

const getEventStyle = (event: CalendarEvent) => {
  // Plus tard : calculer hauteur / position en fonction de l'heure
  return {
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e0e0e0;
  flex-wrap: wrap;
  gap: 1rem;
}

.nav-buttons {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.view-switcher {
  display: flex;
  gap: 0.5rem;
}

.view-switcher button {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
}

.view-switcher button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.btn-today {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 6px;
}

.btn-icon:hover {
  background: #f1f3f5;
}

.week-days-header {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  background: #f8f9fa;
  border-bottom: 1px solid #e0e0e0;
}

.day-header {
  text-align: center;
  padding: 0.75rem 0.5rem;
}

.day-name {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.day-number {
  font-size: 1.3rem;
  margin-top: 0.25rem;
}

.day-number.today {
  background: #3498db;
  color: white;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  line-height: 36px;
  margin: 0.25rem auto 0;
}

.week-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  flex: 1;
  overflow-y: auto;
}

.day-column {
  border-right: 1px solid #e9ecef;
  position: relative;
  min-height: 600px; /* hauteur minimale pour scroll */
}

.day-column:last-child {
  border-right: none;
}

.calendar-event {
  margin: 0.25rem 0.5rem;
  padding: 0.5rem;
  border-radius: 6px;
  font-size: 0.85rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.event-time {
  font-weight: 600;
  color: #2c3e50;
}

.event-title {
  font-weight: 500;
}
</style>