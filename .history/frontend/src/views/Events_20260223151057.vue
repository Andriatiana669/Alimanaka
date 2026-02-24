<template>
  <div class="events-container">
    <!-- Header avec titre et boutons de vue -->
    <div class="page-header">
      <div class="header-left">
        <h1>📋 Fil d'actualité</h1>
        <p class="header-subtitle">Tous les événements en attente et récents</p>
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
        
        <button class="btn-refresh" @click="refreshAll" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          {{ loading ? 'Chargement...' : 'Actualiser' }}
        </button>
      </div>
    </div>

    <!-- Filtres par type d'événement -->
    <div class="filters-section">
      <div class="filters-row">
        <div class="filter-group">
          <label>Type</label>
          <div class="filter-buttons">
            <button 
              v-for="type in eventTypes" 
              :key="type.value"
              class="filter-btn"
              :class="{ 
                active: typeFilters.includes(type.value),
                [type.color]: true
              }"
              @click="toggleTypeFilter(type.value)"
            >
              <i :class="type.icon"></i>
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

      <!-- Filtre par utilisateur (pour managers) -->
      <div v-if="canManageOthers" class="filters-row">
        <div class="filter-group large">
          <label>Utilisateur</label>
          <div class="user-filter">
            <input
              v-model="userSearchQuery"
              type="text"
              class="form-input"
              placeholder="Rechercher un utilisateur..."
              @focus="showUserDropdown = true"
              @input="onUserSearch"
            />
            <div v-if="showUserDropdown && filteredUsers.length > 0" class="user-dropdown">
              <div
                v-for="user in filteredUsers"
                :key="user.id"
                class="user-option"
                :class="{ selected: selectedUserIds.includes(user.id) }"
                @click="toggleUserFilter(user)"
              >
                <div class="user-option-info">
                  <span class="user-option-name">{{ user.display_name }}</span>
                  <span class="user-option-meta">
                    {{ user.username.toUpperCase() }} | {{ user.equipe_nom || 'Sans équipe' }}
                  </span>
                </div>
                <span v-if="selectedUserIds.includes(user.id)" class="check-icon">
                  <i class="bi bi-check-lg"></i>
                </span>
              </div>
            </div>
            <div v-if="selectedUsers.length" class="selected-users">
              <div v-for="user in selectedUsers" :key="user.id" class="selected-user-tag">
                <span class="user-tag-name">{{ user.display_name }}</span>
                <button class="remove-tag" @click="removeUserFilter(user.id)">×</button>
              </div>
              <button v-if="selectedUsers.length" class="clear-tags" @click="clearUserFilters">
                Tout effacer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtres par période -->
      <div class="filters-row">
        <div class="filter-group">
          <label>Période</label>
          <div class="filter-buttons">
            <button 
              v-for="period in periodOptions" 
              :key="period.value"
              class="filter-btn"
              :class="{ active: selectedPeriod === period.value }"
              @click="selectedPeriod = period.value"
            >
              {{ period.label }}
            </button>
          </div>
        </div>

        <!-- Filtre par date personnalisée -->
        <div v-if="selectedPeriod === 'custom'" class="filter-group date-range">
          <input 
            type="date" 
            v-model="dateRange.start" 
            class="form-input small"
            placeholder="Date début"
          />
          <span class="date-separator">→</span>
          <input 
            type="date" 
            v-model="dateRange.end" 
            class="form-input small"
            placeholder="Date fin"
          />
        </div>
      </div>
    </div>

    <!-- Résumé des filtres actifs -->
    <div v-if="hasActiveFilters" class="active-filters">
      <span class="active-filters-label">Filtres actifs :</span>
      <div class="filter-tags">
        <span v-for="type in activeTypeLabels" :key="'type-'+type" class="filter-tag" :class="getTypeClass(type)">
          <i :class="getTypeIcon(type)"></i>
          {{ type }}
          <button class="remove-filter" @click="removeTypeFilter(type)">×</button>
        </span>
        <span v-for="status in activeStatusLabels" :key="'status-'+status" class="filter-tag status-tag">
          <span class="status-dot" :class="getStatusColor(status)"></span>
          {{ status }}
          <button class="remove-filter" @click="removeStatusFilter(status)">×</button>
        </span>
        <span v-for="user in selectedUsers" :key="'user-'+user.id" class="filter-tag user-tag">
          <i class="bi bi-person-circle"></i>
          {{ user.display_name }}
          <button class="remove-filter" @click="removeUserFilter(user.id)">×</button>
        </span>
        <button class="clear-all-filters" @click="clearAllFilters">
          Tout effacer
        </button>
      </div>
    </div>

    <!-- VUE CALENDRIER -->
    <div v-if="viewMode === 'calendar'" class="calendar-view">
      <Calendar
        :events="filteredEventsForCalendar"
        :blocked-dates="blockedDates"
        :default-view="'month'"
        class="events-calendar"
        @event-click="onEventClick"
      />
      
      <!-- Légende du calendrier -->
      <div class="calendar-legend">
        <div class="legend-item" v-for="type in eventTypes" :key="type.value">
          <span class="legend-color" :class="type.color"></span>
          <span class="legend-label">{{ type.label }}</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #f39c12;"></span>
          <span class="legend-label">En attente</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #27ae60;"></span>
          <span class="legend-label">Approuvé</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #e74c3c;"></span>
          <span class="legend-label">Refusé/Annulé</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background: #9b59b6;"></span>
          <span class="legend-label">Transformé</span>
        </div>
      </div>
    </div>

    <!-- VUE TIMELINE -->
    <div v-if="viewMode === 'timeline'" class="timeline-view">
      <div class="timeline">
        <div v-if="loading && !allEvents.length" class="loading-state">
          <div class="spinner"></div>
          <p>Chargement des événements...</p>
        </div>

        <div v-else-if="filteredEvents.length === 0" class="empty-state">
          <i class="bi bi-calendar-x"></i>
          <h3>Aucun événement trouvé</h3>
          <p>Essayez de modifier vos filtres ou d'actualiser la page.</p>
        </div>

        <div v-else class="events-list">
          <!-- Grouper par date -->
          <div v-for="(group, dateKey) in groupedEvents" :key="dateKey" class="date-group">
            <div class="date-header">
              <span class="date-badge">{{ formatDateHeader(dateKey) }}</span>
              <span class="date-count">{{ group.length }} événement(s)</span>
            </div>
            
            <div class="events-group">
              <div 
                v-for="event in group" 
                :key="event.id"
                class="event-card"
                :class="[event.type, event.statut]"
                @click="openEventDetails(event)"
              >
                <!-- Icône et type -->
                <div class="event-icon" :class="event.type">
                  <i :class="getEventIcon(event.type)"></i>
                </div>

                <!-- Contenu principal -->
                <div class="event-content">
                  <div class="event-header">
                    <div class="event-title">
                      <span class="event-user">
                        <i class="bi bi-person-circle"></i>
                        {{ event.user_display_name }}
                      </span>
                      <span class="event-type-badge" :class="event.type">
                        {{ getEventTypeLabel(event.type) }}
                      </span>
                      <span class="event-statut-badge" :class="event.statut">
                        {{ getStatusLabel(event.statut, event.type) }}
                      </span>
                    </div>
                    <span class="event-time">
                      <i class="bi bi-clock"></i>
                      {{ formatTime(event.start) }}
                    </span>
                  </div>

                  <div class="event-details">
                    <!-- Détails spécifiques selon le type -->
                    <template v-if="event.type === 'conge'">
                      <span class="detail-chip">
                        <i class="bi bi-calendar-range"></i>
                        {{ event.date_debut && event.date_fin ? formatDateRange(event.date_debut, event.date_fin) : 'Dates non disponibles' }}
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-hourglass-split"></i>
                        {{ event.jours_deduits || 0 }}j
                      </span>
                      <span v-if="event.type_conge" class="detail-chip">
                        {{ event.type_conge_display || event.type_conge }}
                      </span>
                    </template>

                    <template v-else-if="event.type === 'retard'">
                      <span class="detail-chip">
                        <i class="bi bi-clock-history"></i>
                        {{ event.minutes_retard }}min de retard
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-arrow-repeat"></i>
                        {{ event.heures_restantes }}h restantes
                      </span>
                    </template>

                    <template v-else-if="event.type === 'permission'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        {{ formatTime(event.heure_depart) }} → {{ formatTime(event.heure_arrivee_max) }}
                      </span>
                      <span v-if="event.heures_restantes > 0" class="detail-chip">
                        <i class="bi bi-arrow-repeat"></i>
                        {{ event.heures_restantes }}h restantes
                      </span>
                    </template>

                    <template v-else-if="event.type === 'repos_medical'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        {{ formatTime(event.heure_debut) }} → {{ formatTime(event.heure_fin) }}
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-hourglass"></i>
                        {{ event.duree_heures }}h
                      </span>
                    </template>

                    <template v-else-if="event.type === 'ostie'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        Début {{ formatTime(event.heure_debut) }}
                      </span>
                      <span v-if="event.heure_fin" class="detail-chip">
                        Fin {{ formatTime(event.heure_fin) }}
                      </span>
                    </template>

                    <!-- Motif si présent -->
                    <span v-if="event.motif" class="detail-chip motif">
                      <i class="bi bi-chat-text"></i>
                      {{ truncateMotif(event.motif) }}
                    </span>
                  </div>

                  <!-- Actions rapides (pour les managers) -->
                  <div v-if="canManageThisEvent(event)" class="event-actions" @click.stop>
                    <button 
                      v-if="canQuickAction(event, 'valider')"
                      class="action-btn success"
                      @click="quickValidate(event)"
                      title="Valider"
                    >
                      <i class="bi bi-check-lg"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'retour')"
                      class="action-btn primary"
                      @click="quickRetour(event)"
                      title="Enregistrer retour"
                    >
                      <i class="bi bi-arrow-return-left"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'rattrapage')"
                      class="action-btn info"
                      @click="quickRattrapage(event)"
                      title="Ajouter rattrapage"
                    >
                      <i class="bi bi-plus-circle"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'transformer')"
                      class="action-btn purple"
                      @click="quickTransform(event)"
                      title="Transformer"
                    >
                      <i class="bi bi-arrow-right-circle"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'annuler')"
                      class="action-btn warning"
                      @click="quickCancel(event)"
                      title="Annuler"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                  </div>
                </div>

                <!-- Badge d'urgence -->
                <div v-if="isUrgent(event)" class="urgent-badge" title="Urgent (moins d'une semaine)">
                  ⚠️
                </div>
              </div>
            </div>
          </div>

          <!-- Bouton "Charger plus" -->
          <div v-if="hasMoreEvents" class="load-more">
            <button class="btn-load-more" @click="loadMore" :disabled="loadingMore">
              <i v-if="loadingMore" class="bi bi-arrow-repeat spin"></i>
              <span v-else>Charger plus d'événements</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useRetardsStore } from '@/store/retards'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useOstieStore } from '@/store/ostie'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent as CalendarEventType } from '@/components/common/Calendar.vue'
import { format, parseISO, subDays, differenceInDays, startOfMonth, endOfMonth } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Stores
const authStore = useAuthStore()
const congesStore = useCongesStore()
const retardsStore = useRetardsStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const ostieStore = useOstieStore()
const filtersStore = useFiltersStore()

// ============================================
// Types
// ============================================

interface FilterUser {
  id: number
  display_name: string
  username: string
  equipe_nom: string | null
}

// ============================================
// Mode d'affichage
// ============================================
const viewMode = ref<'timeline' | 'calendar'>('timeline')

// ============================================
// Types d'événements disponibles
// ============================================
const eventTypes = [
  { value: 'conge', label: 'Congés', icon: 'bi bi-calendar-check', color: 'blue' },
  { value: 'retard', label: 'Retards', icon: 'bi bi-clock-history', color: 'orange' },
  { value: 'permission', label: 'Permissions', icon: 'bi bi-door-open', color: 'green' },
  { value: 'repos_medical', label: 'Repos médicaux', icon: 'bi bi-heart-pulse', color: 'red' },
  { value: 'ostie', label: 'OSTIES', icon: 'bi bi-lightning', color: 'purple' }
]

// Options de statut
const statusOptions = [
  { value: 'en_attente', label: 'En attente', color: 'orange' },
  { value: 'retourne', label: 'Retournés', color: 'blue' },
  { value: 'rattrapage', label: 'Rattrapage', color: 'purple' },
  { value: 'en_cours', label: 'En cours', color: 'blue' },
  { value: 'approuve', label: 'Approuvés', color: 'green' },
  { value: 'transforme', label: 'Transformés', color: 'purple' },
  { value: 'refuse', label: 'Refusés', color: 'red' },
  { value: 'annule', label: 'Annulés', color: 'gray' }
]

// Options de période
const periodOptions = [
  { value: 'today', label: "Aujourd'hui" },
  { value: 'week', label: 'Cette semaine' },
  { value: 'month', label: 'Ce mois' },
  { value: 'three_months', label: '3 mois' },
  { value: 'custom', label: 'Personnalisé' }
]

// ============================================
// États
// ============================================
const loading = ref(false)
const loadingMore = ref(false)
const page = ref(1)
const pageSize = 20
const hasMoreEvents = ref(true)

// Filtres
const typeFilters = ref<string[]>([])
const statusFilters = ref<string[]>([])
const selectedPeriod = ref('month')
const dateRange = ref({
  start: format(new Date(), 'yyyy-MM-dd'),
  end: format(new Date(), 'yyyy-MM-dd')
})

// Filtres utilisateur (pour managers)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUserIds = ref<number[]>([])
const selectedUsers = ref<FilterUser[]>([])
const allUsers = ref<FilterUser[]>([])

// Événements
const allEvents = ref<any[]>([])
const selectedEvent = ref<any>(null)

// États des modals
const showCongeDetail = ref(false)
const showRetardDetail = ref(false)
const showPermissionDetail = ref(false)
const showReposDetail = ref(false)
const showOstieDetail = ref(false)
const showRetourModal = ref(false)
const showRattrapageModal = ref(false)
const showValidationOstieModal = ref(false)
const showTransformationModal = ref(false)
const showTransformationOstieModal = ref(false)

// ============================================
// Computed pour le calendrier
// ============================================

// Conversion des événements pour le calendrier
const filteredEventsForCalendar = computed<CalendarEventType[]>(() => {
  return filteredEvents.value.map(event => {
    // Déterminer la couleur selon le type et le statut
    let color = getEventColor(event)
    
    return {
      id: String(event.id),
      title: event.title || getEventTitle(event),
      start: new Date(event.start),
      end: event.end ? new Date(event.end) : undefined,
      allDay: event.allDay ?? true,
      color: color,
      type: event.type,
      user_id: event.user_id,
      statut: event.statut,
      originalEvent: event
    }
  })
})

// Dates bloquées (pour le calendrier)
const blockedDates = computed(() => {
  // Récupérer les jours fériés, exceptionnels, etc.
  return congesStore.calendrierEvents
    .filter(e => e.isBlocked && e.type !== 'weekend')
    .flatMap(e => {
      const dates: Date[] = []
      const start = new Date(e.start)
      const end = e.end ? new Date(e.end) : start
      let current = new Date(start)
      while (current <= end) {
        dates.push(new Date(current))
        current = addDays(current, 1)
      }
      return dates
    })
})

// ============================================
// Computed pour les filtres
// ============================================

const canManageOthers = computed(() => {
  return authStore.user?.is_superuser || 
         (authStore.user?.is_staff && authStore.user?.est_chef_equipe) || 
         authStore.user?.est_chef_equipe
})

const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return allUsers.value
  
  const query = userSearchQuery.value.toLowerCase()
  return allUsers.value.filter((u: FilterUser) => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

const hasActiveFilters = computed(() => {
  return typeFilters.value.length > 0 || 
         statusFilters.value.length > 0 || 
         selectedUserIds.value.length > 0
})

const activeTypeLabels = computed(() => {
  return typeFilters.value.map(t => {
    const type = eventTypes.find(et => et.value === t)
    return type?.label || t
  })
})

const activeStatusLabels = computed(() => {
  return statusFilters.value.map(s => {
    const status = statusOptions.find(so => so.value === s)
    return status?.label || s
  })
})

// Filtrage des événements
const filteredEvents = computed(() => {
  let events = [...allEvents.value]

  // Filtre par type
  if (typeFilters.value.length > 0) {
    events = events.filter(e => typeFilters.value.includes(e.type))
  }

  // Filtre par statut
  if (statusFilters.value.length > 0) {
    events = events.filter(e => e.statut && statusFilters.value.includes(e.statut))
  }

  // Filtre par utilisateur
  if (selectedUserIds.value.length > 0) {
    events = events.filter(e => e.user_id && selectedUserIds.value.includes(e.user_id))
  }

  // Filtre par période
  const now = new Date()
  let startDate: Date | null = null
  let endDate: Date | null = null

  switch (selectedPeriod.value) {
    case 'today':
      startDate = new Date(now.setHours(0, 0, 0, 0))
      endDate = new Date(now.setHours(23, 59, 59, 999))
      break
    case 'week':
      startDate = subDays(now, 7)
      endDate = now
      break
    case 'month':
      startDate = subDays(now, 30)
      endDate = now
      break
    case 'three_months':
      startDate = subDays(now, 90)
      endDate = now
      break
    case 'custom':
      if (dateRange.value.start && dateRange.value.end) {
        startDate = new Date(dateRange.value.start)
        endDate = new Date(dateRange.value.end)
        endDate.setHours(23, 59, 59, 999)
      }
      break
  }

  if (startDate && endDate) {
    events = events.filter(e => {
      const eventDate = new Date(e.start)
      return eventDate >= startDate! && eventDate <= endDate!
    })
  }

  // Trier par date (plus récent d'abord)
  return events.sort((a, b) => new Date(b.start).getTime() - new Date(a.start).getTime())
})

// Grouper par date (pour la timeline)
const groupedEvents = computed(() => {
  const groups: Record<string, any[]> = {}
  
  filteredEvents.value.forEach(event => {
    const dateKey = format(new Date(event.start), 'yyyy-MM-dd')
    if (!groups[dateKey]) {
      groups[dateKey] = []
    }
    groups[dateKey].push(event)
  })
  
  return groups
})

// Types de congés (pour transformation)
const typesConge = computed(() => permissionsStore.typesConge)

// ============================================
// Fonctions utilitaires
// ============================================

const addDays = (date: Date, days: number): Date => {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

const formatDate = (dateStr: string | undefined): string => {
  if (!dateStr) return 'Date inconnue'
  try {
    return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: fr })
  } catch (e) {
    console.error('Erreur formatage date:', dateStr, e)
    return 'Date invalide'
  }
}

const formatTime = (timeStr: string | undefined): string => {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

const formatDateHeader = (dateKey: string): string => {
  if (!dateKey) return 'Date inconnue'
  try {
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
  } catch (e) {
    return dateKey
  }
}

const formatDateRange = (start: string | undefined, end: string | undefined): string => {
  if (!start || !end) return 'Période inconnue'
  if (start === end) return formatDate(start)
  return `${formatDate(start)} → ${formatDate(end)}`
}

const getEventIcon = (type: string): string => {
  const icons: Record<string, string> = {
    conge: 'bi bi-calendar-check',
    retard: 'bi bi-clock-history',
    permission: 'bi bi-door-open',
    repos_medical: 'bi bi-heart-pulse',
    ostie: 'bi bi-lightning'
  }
  return icons[type] || 'bi bi-calendar-event'
}

const getEventTypeLabel = (type: string): string => {
  const typeObj = eventTypes.find(t => t.value === type)
  return typeObj?.label || type
}

const getEventTitle = (event: any): string => {
  const user = getUserDisplayName(event.user_id)
  
  switch (event.type) {
    case 'conge':
      return `${user} - Congé ${event.type_conge_display || ''}`
    case 'retard':
      return `${user} - Retard ${event.minutes_retard}min`
    case 'permission':
      return `${user} - Permission ${formatTime(event.heure_depart)}`
    case 'repos_medical':
      return `${user} - Repos médical ${event.duree_heures}h`
    case 'ostie':
      return `${user} - OSTIE ${formatTime(event.heure_debut)}`
    default:
      return event.title || 'Événement'
  }
}

const getEventColor = (event: any): string => {
  // Priorité au statut pour la couleur
  if (event.statut === 'en_attente') return '#f39c12'
  if (event.statut === 'retourne') return '#3498db'
  if (event.statut === 'rattrapage') return '#9b59b6'
  if (event.statut === 'en_cours') return '#3498db'
  if (event.statut === 'approuve') return '#27ae60'
  if (event.statut === 'transforme') return '#9b59b6'
  if (event.statut === 'refuse') return '#e74c3c'
  if (event.statut === 'annule') return '#95a5a6'
  
  // Sinon couleur par type
  const colors: Record<string, string> = {
    conge: '#3498db',
    retard: '#f39c12',
    permission: '#27ae60',
    repos_medical: '#e74c3c',
    ostie: '#9b59b6'
  }
  return colors[event.type] || '#95a5a6'
}

const getStatusLabel = (statut: string | undefined, type?: string): string => {
  if (!statut) return 'Inconnu'
  
  if (type === 'permission') {
    const labels: Record<string, string> = {
      en_attente: 'En attente',
      retourne: 'Retourné',
      rattrapage: 'Rattrapage',
      approuve: 'Approuvé',
      transforme: 'Transformé',
      annule: 'Annulé'
    }
    return labels[statut] || statut
  }
  
  const status = statusOptions.find(s => s.value === statut)
  return status?.label || statut
}

const getStatusColor = (status: string): string => {
  const statusObj = statusOptions.find(s => s.value === status)
  return statusObj?.color || 'gray'
}

const getTypeIcon = (type: string): string => {
  const typeObj = eventTypes.find(t => t.label === type)
  return typeObj?.icon || 'bi bi-calendar'
}

const getTypeClass = (type: string): string => {
  const typeObj = eventTypes.find(t => t.label === type)
  return typeObj?.color || ''
}

const truncateMotif = (motif: string, maxLength = 50): string => {
  if (!motif) return ''
  if (motif.length <= maxLength) return motif
  return motif.substring(0, maxLength) + '...'
}

const getTypeCount = (type: string): number => {
  return allEvents.value.filter(e => e.type === type).length
}

const isUrgent = (event: any): boolean => {
  if (event.type !== 'conge' || !event.date_debut) return false
  const eventDate = new Date(event.date_debut)
  const now = new Date()
  return differenceInDays(eventDate, now) < 7 && eventDate > now
}

// ============================================
// Gestion des filtres
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

const toggleUserFilter = (user: FilterUser) => {
  const index = selectedUserIds.value.indexOf(user.id)
  if (index === -1) {
    selectedUserIds.value.push(user.id)
    selectedUsers.value.push(user)
  } else {
    selectedUserIds.value.splice(index, 1)
    selectedUsers.value = selectedUsers.value.filter(u => u.id !== user.id)
  }
  showUserDropdown.value = false
}

const removeTypeFilter = (typeLabel: string) => {
  const type = eventTypes.find(t => t.label === typeLabel)
  if (type) {
    const index = typeFilters.value.indexOf(type.value)
    if (index !== -1) typeFilters.value.splice(index, 1)
  }
}

const removeStatusFilter = (statusLabel: string) => {
  const status = statusOptions.find(s => s.label === statusLabel)
  if (status) {
    const index = statusFilters.value.indexOf(status.value)
    if (index !== -1) statusFilters.value.splice(index, 1)
  }
}

const removeUserFilter = (userId: number) => {
  const index = selectedUserIds.value.indexOf(userId)
  if (index !== -1) {
    selectedUserIds.value.splice(index, 1)
    selectedUsers.value = selectedUsers.value.filter(u => u.id !== userId)
  }
}

const clearUserFilters = () => {
  selectedUserIds.value = []
  selectedUsers.value = []
  userSearchQuery.value = ''
}

const clearAllFilters = () => {
  typeFilters.value = []
  statusFilters.value = []
  clearUserFilters()
}

const onUserSearch = () => {
  showUserDropdown.value = true
}

// ============================================
// Gestion du calendrier
// ============================================

const onDateClick = (date: Date) => {
  console.log('Date cliquée:', date)
  // Optionnel: basculer en mode timeline et filtrer par cette date
}

const onRangeChange = (start: Date, end: Date) => {
  // Mettre à jour la période quand on navigue dans le calendrier
  selectedPeriod.value = 'custom'
  dateRange.value.start = format(start, 'yyyy-MM-dd')
  dateRange.value.end = format(end, 'yyyy-MM-dd')
}

// ============================================
// Chargement des données
// ============================================

const loadAllEvents = async (reset = true) => {
  if (reset) {
    loading.value = true
    page.value = 1
    allEvents.value = []
  } else {
    loadingMore.value = true
  }

  try {
    const currentYear = new Date().getFullYear()
    
    // Charger tous les événements en parallèle
    const promises = []

    if (typeFilters.value.length === 0 || typeFilters.value.includes('conge')) {
      promises.push(congesStore.fetchCalendrier({ annee: currentYear }))
    }
    if (typeFilters.value.length === 0 || typeFilters.value.includes('retard')) {
      promises.push(retardsStore.fetchCalendrier({ annee: currentYear }))
    }
    if (typeFilters.value.length === 0 || typeFilters.value.includes('permission')) {
      promises.push(permissionsStore.fetchCalendrier({ annee: currentYear }))
    }
    if (typeFilters.value.length === 0 || typeFilters.value.includes('repos_medical')) {
      promises.push(reposStore.fetchCalendrier({ annee: currentYear }))
    }
    if (typeFilters.value.length === 0 || typeFilters.value.includes('ostie')) {
      promises.push(ostieStore.fetchCalendrier({ annee: currentYear }))
    }

    await Promise.all(promises)

    // Fusionner tous les événements
    const newEvents = [
      ...congesStore.calendrierEvents.map(e => ({ ...e, type: 'conge' })),
      ...retardsStore.calendrierEvents.map(e => ({ ...e, type: 'retard' })),
      ...permissionsStore.calendrierEvents.map(e => ({ ...e, type: 'permission' })),
      ...reposStore.calendrierEvents.map(e => ({ ...e, type: 'repos_medical' })),
      ...ostieStore.calendrierEvents.map(e => ({ ...e, type: 'ostie' }))
    ]

    // Enrichir avec les détails utilisateur
    const enrichedEvents = newEvents.map(event => ({
      ...event,
      user_display_name: getUserDisplayName(event.user_id)
    }))

    allEvents.value = reset ? enrichedEvents : [...allEvents.value, ...enrichedEvents]
    hasMoreEvents.value = newEvents.length >= pageSize

  } catch (error) {
    console.error('Erreur chargement événements:', error)
  } finally {
    loading.value = false
    loadingMore.value = false
  }
}

const getUserDisplayName = (userId: number | undefined): string => {
  if (!userId) return 'Utilisateur inconnu'
  
  const user = allUsers.value.find(u => u.id === userId)
  return user?.display_name || `Utilisateur #${userId}`
}

const loadMore = () => {
  page.value++
  loadAllEvents(false)
}

const refreshAll = async () => {
  await Promise.all([
    filtersStore.fetchPoles(),
    congesStore.fetchTypesConge(),
    retardsStore.fetchTypesRetard(),
    permissionsStore.fetchTypesConge(),
    reposStore.fetchTypesConge()
  ])
  
  await loadAllUsers()
  await loadAllEvents(true)
}

const loadAllUsers = async () => {
  const users: FilterUser[] = []
  
  if (congesStore.utilisateursGerables) {
    users.push(...congesStore.utilisateursGerables)
  }
  if (retardsStore.utilisateursGerables) {
    users.push(...retardsStore.utilisateursGerables)
  }
  if (permissionsStore.utilisateursGerables) {
    users.push(...permissionsStore.utilisateursGerables)
  }
  if (reposStore.utilisateursGerables) {
    users.push(...reposStore.utilisateursGerables)
  }
  if (ostieStore.utilisateursGerables) {
    users.push(...ostieStore.utilisateursGerables)
  }
  
  console.log('Utilisateurs chargés:', users) // 👈 AJOUTEZ CE LOG
  
  const uniqueUsers = Array.from(
    new Map(users.map(user => [user.id, user])).values()
  )
  
  allUsers.value = uniqueUsers
  console.log('Utilisateurs uniques:', allUsers.value) // 👈 ET CELUI-CI
}

// ============================================
// Gestion des actions
// ============================================

const canManageThisEvent = (event: any): boolean => {
  if (!canManageOthers.value) return false
  return true
}

const canQuickAction = (event: any, action: string): boolean => {
  if (!canManageThisEvent(event)) return false
  
  switch (action) {
    case 'valider':
      return event.statut === 'en_attente' && 
             ['conge', 'repos_medical'].includes(event.type)
    case 'retour':
      return event.type === 'permission' && event.statut === 'en_attente'
    case 'rattrapage':
      return (event.type === 'permission' || event.type === 'retard') &&
             ['en_attente', 'en_cours', 'retourne', 'rattrapage'].includes(event.statut || '') &&
             (event.heures_restantes || 0) > 0
    case 'transformer':
      return (event.type === 'permission' && event.statut === 'retourne' && (event.minutes_depassement || 0) > 0) ||
             (event.type === 'repos_medical' && event.statut === 'en_attente') ||
             (event.type === 'ostie' && event.statut === 'en_attente')
    case 'annuler':
      return ['en_attente', 'retourne', 'rattrapage', 'en_cours'].includes(event.statut || '')
    default:
      return false
  }
}

const openEventDetails = (event: any) => {
  selectedEvent.value = event
  
  switch (event.type) {
    case 'conge':
      showCongeDetail.value = true
      break
    case 'retard':
      showRetardDetail.value = true
      break
    case 'permission':
      showPermissionDetail.value = true
      break
    case 'repos_medical':
      showReposDetail.value = true
      break
    case 'ostie':
      showOstieDetail.value = true
      break
  }
}

const closeDetailModal = () => {
  showCongeDetail.value = false
  showRetardDetail.value = false
  showPermissionDetail.value = false
  showReposDetail.value = false
  showOstieDetail.value = false
  selectedEvent.value = null
}

const quickValidate = (event: any) => {
  selectedEvent.value = event
  if (event.type === 'conge') {
    // Ouvrir modal de validation congé
  } else if (event.type === 'repos_medical' && event.id) {
    const id = typeof event.id === 'string' ? parseInt(event.id.replace('repos_', '')) : event.id
    reposStore.validerReposMedical(id).then(() => refreshAll())
  }
}

const quickRetour = (event: any) => {
  selectedEvent.value = event
  showRetourModal.value = true
}

const quickRattrapage = (event: any) => {
  selectedEvent.value = event
  showRattrapageModal.value = true
}

const quickTransform = (event: any) => {
  selectedEvent.value = event
  if (event.type === 'ostie') {
    showTransformationOstieModal.value = true
  } else {
    showTransformationModal.value = true
  }
}

const quickCancel = async (event: any) => {
  if (!event.id) return
  if (!confirm(`Voulez-vous vraiment annuler cet événement ?`)) return
  
  const id = typeof event.id === 'string' ? parseInt(event.id.replace(/[^0-9]/g, '')) : event.id
  
  try {
    switch (event.type) {
      case 'conge':
        await congesStore.annulerConge(id)
        break
      case 'retard':
        await retardsStore.annulerRetard(id)
        break
      case 'permission':
        await permissionsStore.annulerPermission(id)
        break
      case 'repos_medical':
        await reposStore.annulerReposMedical(id)
        break
      case 'ostie':
        await ostieStore.annulerOstie(id)
        break
    }
    await refreshAll()
  } catch (error) {
    console.error('Erreur annulation:', error)
  }
}

const closeRetourModal = () => {
  showRetourModal.value = false
  selectedEvent.value = null
}

const closeRattrapageModal = () => {
  showRattrapageModal.value = false
  selectedEvent.value = null
}

const closeValidationOstieModal = () => {
  showValidationOstieModal.value = false
  selectedEvent.value = null
}

const closeTransformationModal = () => {
  showTransformationModal.value = false
  selectedEvent.value = null
}

const closeTransformationOstieModal = () => {
  showTransformationOstieModal.value = false
  selectedEvent.value = null
}

const handleActionValidated = () => {
  refreshAll()
}

// Watch pour recharger quand les filtres changent
watch([typeFilters, statusFilters, selectedPeriod, dateRange, selectedUserIds], () => {
  loadAllEvents(true)
})


// ============================================
// Gestion des clics sur événements
// ============================================
const onEventClick = (calendarEvent: CalendarEventType) => {
  // L'événement du calendrier contient l'événement original dans originalEvent
  const originalEvent = (calendarEvent as any).originalEvent || calendarEvent
  openEventDetails(originalEvent)
}


// ============================================
// Cycle de vie
// ============================================

onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await congesStore.fetchTypesConge()
  await retardsStore.fetchTypesRetard()
  await permissionsStore.fetchTypesConge()
  await reposStore.fetchTypesConge()
  await loadAllUsers()
  await loadAllEvents(true)
})
</script>



<style scoped>


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
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

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
}

.btn-refresh:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 1rem;
}

.filters-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  flex: 1;
  min-width: 250px;
}

.filter-group.large {
  flex: 2;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
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
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.filter-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.filter-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.filter-btn.active.blue { background: #3498db; border-color: #3498db; }
.filter-btn.active.orange { background: #f39c12; border-color: #f39c12; }
.filter-btn.active.green { background: #27ae60; border-color: #27ae60; }
.filter-btn.active.red { background: #e74c3c; border-color: #e74c3c; }
.filter-btn.active.purple { background: #9b59b6; border-color: #9b59b6; }

.count-badge {
  background: rgba(0,0,0,0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.orange { background: #f39c12; }
.status-dot.blue { background: #3498db; }
.status-dot.purple { background: #9b59b6; }
.status-dot.green { background: #27ae60; }
.status-dot.red { background: #e74c3c; }
.status-dot.gray { background: #95a5a6; }

/* Filtre utilisateur */
.user-filter {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.95rem;
}

.form-input.small {
  padding: 0.5rem;
  font-size: 0.9rem;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  margin-top: 0.25rem;
}

.user-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f1f3f5;
}

.user-option:hover {
  background: #f8f9fa;
}

.user-option.selected {
  background: #e3f2fd;
}

.user-option-info {
  display: flex;
  flex-direction: column;
}

.user-option-name {
  font-weight: 600;
  color: #2c3e50;
}

.user-option-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

.check-icon {
  color: #27ae60;
}

.selected-users {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.selected-user-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #e3f2fd;
  border-radius: 20px;
  font-size: 0.85rem;
}

.remove-tag {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  color: #6c757d;
  padding: 0 0.25rem;
}

.remove-tag:hover {
  color: #e74c3c;
}

.clear-tags {
  background: none;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Date range */
.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-separator {
  color: #6c757d;
  font-weight: bold;
}


/* Calendrier */

.calendar-view {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  margin-top: 1.5rem;
}

.events-calendar {
  height: 600px;
  border-radius: 8px;
  overflow: hidden;
}

.calendar-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 4px;
}

.legend-color.blue { background: #3498db; }
.legend-color.orange { background: #f39c12; }
.legend-color.green { background: #27ae60; }
.legend-color.red { background: #e74c3c; }
.legend-color.purple { background: #9b59b6; }

.legend-label {
  color: #495057;
}

/* Styles pour le toggle de vue */
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

/* Adaptation responsive */
@media (max-width: 768px) {
  .calendar-legend {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .view-toggle {
    width: 100%;
  }
  
  .view-btn {
    flex: 1;
    justify-content: center;
  }
  
  .events-calendar {
    height: 500px;
  }
}


/* Filtres actifs */
.active-filters {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.active-filters-label {
  font-weight: 600;
  color: #495057;
  margin-right: 1rem;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.5rem;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #f8f9fa;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid #dee2e6;
}

.filter-tag.blue { border-left: 3px solid #3498db; }
.filter-tag.orange { border-left: 3px solid #f39c12; }
.filter-tag.green { border-left: 3px solid #27ae60; }
.filter-tag.red { border-left: 3px solid #e74c3c; }
.filter-tag.purple { border-left: 3px solid #9b59b6; }

.filter-tag.status-tag {
  border-left: 3px solid;
}

.filter-tag.user-tag {
  background: #e3f2fd;
}

.remove-filter {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  color: #6c757d;
  padding: 0 0.25rem;
}

.remove-filter:hover {
  color: #e74c3c;
}

.clear-all-filters {
  background: none;
  border: 1px solid #e74c3c;
  color: #e74c3c;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  cursor: pointer;
  margin-left: 0.5rem;
}

.clear-all-filters:hover {
  background: #e74c3c;
  color: white;
}

/* Timeline */
.timeline {
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

.date-group {
  margin-bottom: 2rem;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f1f3f5;
}

.date-badge {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
  text-transform: capitalize;
}

.date-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.events-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
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

/* Bordures colorées selon le type */
.event-card.conge { border-left: 4px solid #3498db; }
.event-card.retard { border-left: 4px solid #f39c12; }
.event-card.permission { border-left: 4px solid #27ae60; }
.event-card.repos_medical { border-left: 4px solid #e74c3c; }
.event-card.ostie { border-left: 4px solid #9b59b6; }

/* Bordures selon le statut (overlay) */
.event-card.en_attente { border-left-color: #f39c12; }
.event-card.retourne { border-left-color: #3498db; }
.event-card.rattrapage { border-left-color: #9b59b6; }
.event-card.en_cours { border-left-color: #3498db; }
.event-card.approuve { border-left-color: #27ae60; }
.event-card.transforme { border-left-color: #9b59b6; }
.event-card.refuse { border-left-color: #e74c3c; }
.event-card.annule { border-left-color: #95a5a6; }

.event-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.event-icon.conge { background: #3498db; }
.event-icon.retard { background: #f39c12; }
.event-icon.permission { background: #27ae60; }
.event-icon.repos_medical { background: #e74c3c; }
.event-icon.ostie { background: #9b59b6; }

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.event-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.event-user {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.event-type-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: white;
}

.event-type-badge.conge { background: #3498db; }
.event-type-badge.retard { background: #f39c12; }
.event-type-badge.permission { background: #27ae60; }
.event-type-badge.repos_medical { background: #e74c3c; }
.event-type-badge.ostie { background: #9b59b6; }

.event-statut-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 600;
  background: #f8f9fa;
  border: 1px solid;
}

.event-statut-badge.en_attente { 
  background: #fff3e0; 
  color: #e67e22; 
  border-color: #f39c12; 
}
.event-statut-badge.retourne { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.event-statut-badge.rattrapage { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.event-statut-badge.en_cours { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.event-statut-badge.approuve { 
  background: #e8f5e9; 
  color: #2e7d32; 
  border-color: #27ae60; 
}
.event-statut-badge.transforme { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.event-statut-badge.refuse { 
  background: #ffebee; 
  color: #c62828; 
  border-color: #e74c3c; 
}
.event-statut-badge.annule { 
  background: #eceff1; 
  color: #455a64; 
  border-color: #95a5a6; 
}

.event-time {
  color: #6c757d;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

.event-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.6rem;
  background: #f8f9fa;
  border-radius: 16px;
  font-size: 0.8rem;
  color: #495057;
}

.detail-chip.motif {
  background: #e3f2fd;
  color: #1976d2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-actions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  font-size: 1rem;
}

.action-btn.success { background: #27ae60; }
.action-btn.success:hover { background: #219a52; }

.action-btn.primary { background: #3498db; }
.action-btn.primary:hover { background: #2980b9; }

.action-btn.info { background: #9b59b6; }
.action-btn.info:hover { background: #8e44ad; }

.action-btn.purple { background: #9b59b6; }
.action-btn.purple:hover { background: #8e44ad; }

.action-btn.warning { background: #f39c12; }
.action-btn.warning:hover { background: #e67e22; }

.urgent-badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  width: 24px;
  height: 24px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  border: 2px solid white;
}

.load-more {
  text-align: center;
  margin-top: 2rem;
}

.btn-load-more {
  padding: 0.75rem 2rem;
  background: white;
  border: 1px solid #3498db;
  color: #3498db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-load-more:hover {
  background: #3498db;
  color: white;
}

/* Animations */
.event-list-enter-active,
.event-list-leave-active {
  transition: all 0.3s ease;
}

.event-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.event-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.event-list-move {
  transition: transform 0.3s ease;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .events-container {
    padding: 1rem;
  }

  .filters-row {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-group {
    min-width: 100%;
  }

  .filter-buttons {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .filter-btn {
    flex-shrink: 0;
  }

  .event-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .event-title {
    width: 100%;
  }

  .event-time {
    align-self: flex-end;
  }

  .event-actions {
    flex-wrap: wrap;
  }
}
</style>