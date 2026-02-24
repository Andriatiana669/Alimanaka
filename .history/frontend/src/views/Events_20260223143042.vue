<template>
  <!-- Header avec résumé global -->
  <div class="page-header">
    <div class="header-left">
      <h1>📅 Tous les événements</h1>
      <div v-if="authStore.user" class="events-badge">
        <span class="badge-conges">{{ congesCount }} congés</span>
        <span class="badge-retards">{{ retardsEnCoursCount }} retards</span>
        <span class="badge-permissions">{{ permissionsEnCoursCount }} permissions</span>
        <span class="badge-repos">{{ reposEnAttenteCount }} repos</span>
        <span class="badge-osties">{{ ostiesEnAttenteCount }} OSTIES</span>
      </div>
    </div>
    
    <div class="header-actions">
      <!-- Boutons de filtrage rapide -->
      <div class="view-toggle">
        <button 
          class="toggle-btn" 
          :class="{ active: viewMode === 'calendar' }"
          @click="viewMode = 'calendar'"
        >
          <i class="bi bi-calendar-week"></i> Calendrier
        </button>
        <button 
          class="toggle-btn" 
          :class="{ active: viewMode === 'list' }"
          @click="viewMode = 'list'"
        >
          <i class="bi bi-list-ul"></i> Liste
        </button>
      </div>

      <!-- Filtre par type d'événement -->
      <div class="filter-types">
        <label class="type-filter" :class="{ active: selectedTypes.includes('conge') }">
          <input 
            type="checkbox" 
            value="conge" 
            v-model="selectedTypes"
          />
          <span class="type-dot" style="background: #2196f3"></span>
          Congés
        </label>
        <label class="type-filter" :class="{ active: selectedTypes.includes('retard') }">
          <input 
            type="checkbox" 
            value="retard" 
            v-model="selectedTypes"
          />
          <span class="type-dot" style="background: #ff9800"></span>
          Retards
        </label>
        <label class="type-filter" :class="{ active: selectedTypes.includes('permission') }">
          <input 
            type="checkbox" 
            value="permission" 
            v-model="selectedTypes"
          />
          <span class="type-dot" style="background: #4caf50"></span>
          Permissions
        </label>
        <label class="type-filter" :class="{ active: selectedTypes.includes('repos_medical') }">
          <input 
            type="checkbox" 
            value="repos_medical" 
            v-model="selectedTypes"
          />
          <span class="type-dot" style="background: #9c27b0"></span>
          Repos médicaux
        </label>
        <label class="type-filter" :class="{ active: selectedTypes.includes('ostie') }">
          <input 
            type="checkbox" 
            value="ostie" 
            v-model="selectedTypes"
          />
          <span class="type-dot" style="background: #e91e63"></span>
          OSTIES
        </label>
      </div>

      <button class="btn-refresh" @click="refreshData" :disabled="loading">
        <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
      </button>
    </div>
  </div>

  <!-- Filtres avancés -->
  <div class="filters-bar">
    <!-- Filtres pôle/équipe -->
    <div class="filter-tabs">
      <div class="custom-select">
        <button
          class="select-button"
          :class="{ active: filters.pole !== null }"
          @click="togglePoleDropdown"
        >
          {{ filters.pole ? selectedPoleName : 'Tous les pôles' }}
        </button>
        <div v-if="showPoleDropdown" class="select-dropdown">
          <div class="select-option" @click="selectPole(null)">Tous les pôles</div>
          <div
            v-for="pole in availablePoles"
            :key="pole.id"
            class="select-option"
            @click="selectPole(pole.id)"
          >
            {{ pole.nom }}
          </div>
        </div>
      </div>
    </div>

    <div class="filter-tabs">
      <div class="custom-select">
        <button
          class="select-button"
          :class="{ active: filters.equipe !== null, disabled: !filters.pole }"
          @click="toggleEquipeDropdown"
          :disabled="!filters.pole"
        >
          {{ filters.equipe ? selectedEquipeName : 'Toutes les équipes' }}
        </button>
        <div v-if="showEquipeDropdown && filters.pole" class="select-dropdown">
          <div class="select-option" @click="selectEquipe(null)">Toutes les équipes</div>
          <div
            v-for="equipe in availableEquipes"
            :key="equipe.id"
            class="select-option"
            @click="selectEquipe(equipe.id)"
          >
            {{ equipe.nom }}
          </div>
        </div>
      </div>
    </div>

    <!-- Filtre par statut -->
    <div class="filter-tabs">
      <select v-model="statusFilter" class="status-select">
        <option value="all">Tous les statuts</option>
        <option value="en_attente">⏳ En attente</option>
        <option value="approuve">✅ Approuvé</option>
        <option value="retourne">🔄 Retourné</option>
        <option value="rattrapage">⏱️ Rattrapage</option>
        <option value="transforme">🔄 Transformé</option>
        <option value="annule">❌ Annulé</option>
        <option value="refuse">✗ Refusé</option>
      </select>
    </div>

    <!-- Sélection de l'année -->
    <div class="filter-tabs">
      <select v-model="selectedYear" class="year-select">
        <option v-for="year in availableYears" :key="year" :value="year">
          {{ year }}
        </option>
      </select>
    </div>

    <!-- Filtre utilisateur (pour managers) -->
    <div v-if="canManageOthers" class="filter-tabs user-filter">
      <div class="custom-select">
        <button
          class="select-button"
          :class="{ active: filters.user !== null }"
          @click="toggleUserDropdown"
        >
          {{ filters.user ? selectedUserName : 'Tous les utilisateurs' }}
        </button>
        <div v-if="showUserDropdown" class="select-dropdown">
          <div class="select-option" @click="selectUser(null)">Tous les utilisateurs</div>
          <div
            v-for="user in allUsers"
            :key="user.id"
            class="select-option"
            @click="selectUser(user.id)"
          >
            {{ user.display_name }} ({{ user.username }})
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- Vue Calendrier -->
  <div v-if="viewMode === 'calendar'" class="calendar-view">
    <Calendar
      :events="filteredCalendarEvents"
      :blocked-dates="blockedDates"
      :default-view="'month'"
      class="events-calendar"
      @event-click="onEventClick"
      @date-click="onDateClick"
    />
  </div>

  <!-- Vue Liste -->
  <div v-if="viewMode === 'list'" class="list-view">
    <div class="list-header">
      <div class="list-stats">
        <span>Total: <strong>{{ filteredEventsList.length }}</strong> événements</span>
        <span>Période: <strong>{{ selectedYear }}</strong></span>
      </div>
      <button class="btn-export" @click="exportFiltered">
        <i class="bi bi-download"></i> Exporter la vue
      </button>
    </div>

    <div class="events-list">
      <div v-for="(group, date) in groupedEvents" :key="date" class="date-group">
        <div class="date-header">
          <h3>{{ formatDateHeader(date) }}</h3>
          <span class="date-count">{{ group.length }} événement(s)</span>
        </div>
        
        <div class="events-cards">
          <div
            v-for="event in group"
            :key="event.id"
            class="event-card"
            :style="{ borderLeftColor: getEventColor(event) }"
            @click="onEventClick(event)"
          >
            <div class="event-icon">{{ getEventIcon(event) }}</div>
            <div class="event-content">
              <div class="event-title">{{ event.title }}</div>
              <div class="event-meta">
                <span class="event-user">{{ event.user_name }}</span>
                <span class="event-type" :style="{ backgroundColor: getEventColor(event) + '20', color: getEventColor(event) }">
                  {{ getEventTypeLabel(event.type) }}
                </span>
                <span class="event-statut" :class="event.statut">
                  {{ getStatutLabel(event.statut, event.type) }}
                </span>
              </div>
              <div v-if="event.details" class="event-details">
                {{ event.details }}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="Object.keys(groupedEvents).length === 0" class="no-events">
        <i class="bi bi-calendar-x"></i>
        <p>Aucun événement trouvé</p>
      </div>
    </div>
  </div>

  <!-- Modal Détails unifié -->
  <Teleport to="body">
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal modal-large">
        <div class="modal-header" :class="'header-' + (selectedEvent?.statut || '')">
          <h3>
            {{ getEventTypeLabel(selectedEvent?.type) }}
            <span class="header-badge" :class="selectedEvent?.statut">
              {{ getStatutLabel(selectedEvent?.statut, selectedEvent?.type) }}
            </span>
          </h3>
          <button class="btn-close" @click="closeDetailModal">×</button>
        </div>

        <div class="modal-body" v-if="selectedEvent">
          <!-- Contenu dynamique selon le type -->
          <component
            :is="getDetailComponent(selectedEvent.type)"
            :event="selectedEvent"
            @action="handleEventAction"
          />
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
          <button
            v-if="canManageEvent(selectedEvent)"
            class="btn-primary"
            @click="goToNativeModule"
          >
            <i class="bi bi-box-arrow-up-right"></i>
            Voir dans le module dédié
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useRetardsStore } from '@/store/retards'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useOstieStore } from '@/store/ostie'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import { format, parseISO, getYear, addDays } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Composants dynamiques pour les détails
import CongeDetail from '@/components/events/CongeDetail.vue'
import RetardDetail from '@/components/events/RetardDetail.vue'
import PermissionDetail from '@/components/events/PermissionDetail.vue'
import ReposDetail from '@/components/events/ReposDetail.vue'
import OstieDetail from '@/components/events/OstieDetail.vue'

const router = useRouter()
const authStore = useAuthStore()
const congesStore = useCongesStore()
const retardsStore = useRetardsStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const ostieStore = useOstieStore()
const filtersStore = useFiltersStore()

// ============================================
// État local
// ============================================
const viewMode = ref<'calendar' | 'list'>('calendar')
const selectedTypes = ref<string[]>(['conge', 'retard', 'permission', 'repos_medical', 'ostie'])
const selectedYear = ref(getYear(new Date()))
const statusFilter = ref('all')
const loading = ref(false)
const showDetailModal = ref(false)
const selectedEvent = ref<any>(null)

// Filtres
const filters = ref({
  pole: null as number | null,
  equipe: null as number | null,
  user: null as number | null
})

const showPoleDropdown = ref(false)
const showEquipeDropdown = ref(false)
const showUserDropdown = ref(false)

// Utilisateurs pour le filtre (tous les utilisateurs gérables)
const allUsers = ref<any[]>([])

// ============================================
// Computed pour les filtres
// ============================================
const availablePoles = computed(() => filtersStore.poles)
const availableEquipes = computed(() => filtersStore.equipes)

const selectedPoleName = computed(() => {
  const pole = availablePoles.value.find(p => p.id === filters.value.pole)
  return pole ? pole.nom : 'Tous les pôles'
})

const selectedEquipeName = computed(() => {
  const equipe = availableEquipes.value.find(e => e.id === filters.value.equipe)
  return equipe ? equipe.nom : 'Toutes les équipes'
})

const selectedUserName = computed(() => {
  const user = allUsers.value.find(u => u.id === filters.value.user)
  return user ? user.display_name : 'Tous les utilisateurs'
})

const canManageOthers = computed(() => {
  return authStore.user?.is_superuser || authStore.user?.est_chef_equipe
})

// Années disponibles (2024-2030)
const availableYears = computed(() => {
  const currentYear = getYear(new Date())
  return [currentYear - 1, currentYear, currentYear + 1, currentYear + 2]
})

// ============================================
// Agrégation des événements
// ============================================
const allCalendarEvents = computed<CalendarEvent[]>(() => {
  const events: CalendarEvent[] = []

  // Congés
  if (selectedTypes.value.includes('conge')) {
    events.push(...congesStore.eventsForCalendar)
  }

  // Retards
  if (selectedTypes.value.includes('retard')) {
    events.push(...retardsStore.eventsForCalendar)
  }

  // Permissions
  if (selectedTypes.value.includes('permission')) {
    events.push(...permissionsStore.eventsForCalendar)
  }

  // Repos médicaux
  if (selectedTypes.value.includes('repos_medical')) {
    events.push(...reposStore.eventsForCalendar)
  }

  // OSTIES
  if (selectedTypes.value.includes('ostie')) {
    events.push(...ostieStore.eventsForCalendar)
  }

  return events
})

// Événements filtrés pour le calendrier
const filteredCalendarEvents = computed<CalendarEvent[]>(() => {
  return allCalendarEvents.value.filter(event => {
    // Filtre par année
    const eventYear = getYear(new Date(event.start))
    if (eventYear !== selectedYear.value) return false

    // Filtre par statut
    if (statusFilter.value !== 'all' && event.statut !== statusFilter.value) return false

    // Filtre par pôle/équipe (si applicable)
    if (filters.value.pole && event.pole_id && event.pole_id !== filters.value.pole) return false
    if (filters.value.equipe && event.equipe_id && event.equipe_id !== filters.value.equipe) return false
    if (filters.value.user && event.user_id && event.user_id !== filters.value.user) return false

    return true
  })
})

// Événements pour la vue liste (avec plus de détails)
const filteredEventsList = computed<any[]>(() => {
  const events: any[] = []

  // Fonction pour ajouter des événements avec des détails
  const addEvents = (store: any, type: string, mapper: (e: any) => any) => {
    if (!selectedTypes.value.includes(type)) return
    events.push(...store[`${type}s`]?.map(mapper) || [])
  }

  // TODO: Ajouter les mappings selon vos structures de données
  // Ceci est un exemple, à adapter selon vos stores
  addEvents(congesStore, 'conge', (c: any) => ({
    id: `conge_${c.id}`,
    type: 'conge',
    title: `Congé ${c.type_conge}`,
    date: c.date_debut,
    user_name: c.utilisateur_details?.display_name,
    statut: c.statut,
    details: `${c.jours_deduits}j - ${c.motif || ''}`,
    ...c
  }))

  // Filtrer et trier par date
  return events
    .filter(e => {
      const eventYear = getYear(parseISO(e.date))
      if (eventYear !== selectedYear.value) return false
      if (statusFilter.value !== 'all' && e.statut !== statusFilter.value) return false
      return true
    })
    .sort((a, b) => parseISO(b.date).getTime() - parseISO(a.date).getTime())
})

// Événements groupés par date pour la vue liste
const groupedEvents = computed(() => {
  const groups: Record<string, any[]> = {}
  
  filteredEventsList.value.forEach(event => {
    if (!groups[event.date]) {
      groups[event.date] = []
    }
    groups[event.date].push(event)
  })
  
  return groups
})

// ============================================
// Statistiques
// ============================================
const congesCount = computed(() => congesStore.conges?.length || 0)
const retardsEnCoursCount = computed(() => retardsStore.retardsEnCours?.length || 0)
const permissionsEnCoursCount = computed(() => 
  (permissionsStore.permissionsRattrapage?.length || 0) + 
  (permissionsStore.permissionsRetournees?.length || 0)
)
const reposEnAttenteCount = computed(() => reposStore.reposEnAttente?.length || 0)
const ostiesEnAttenteCount = computed(() => ostieStore.ostiesEnAttente?.length || 0)

// Dates bloquées (jours fériés, etc.)
const blockedDates = computed(() => {
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
// Méthodes utilitaires
// ============================================
const getEventColor = (event: any): string => {
  const colors: Record<string, string> = {
    conge: '#2196f3',
    retard: '#ff9800',
    permission: '#4caf50',
    repos_medical: '#9c27b0',
    ostie: '#e91e63'
  }
  return colors[event.type] || '#9e9e9e'
}

const getEventIcon = (event: any): string => {
  const icons: Record<string, string> = {
    conge: '🏖️',
    retard: '⏰',
    permission: '🚪',
    repos_medical: '🏥',
    ostie: '⚡'
  }
  return icons[event.type] || '📌'
}

const getEventTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    conge: 'Congé',
    retard: 'Retard',
    permission: 'Permission',
    repos_medical: 'Repos médical',
    ostie: 'OSTIE'
  }
  return labels[type] || type
}

const getStatutLabel = (statut: string, type?: string): string => {
  const labels: Record<string, string> = {
    en_attente: '⏳ En attente',
    approuve: '✅ Approuvé',
    retourne: '🔄 Retourné',
    rattrapage: '⏱️ Rattrapage',
    transforme: '🔄 Transformé',
    annule: '❌ Annulé',
    refuse: '✗ Refusé'
  }
  return labels[statut] || statut
}

const formatDateHeader = (dateStr: string): string => {
  return format(parseISO(dateStr), 'EEEE d MMMM yyyy', { locale: fr })
}

// ============================================
// Actions sur les filtres
// ============================================
const togglePoleDropdown = () => {
  showPoleDropdown.value = !showPoleDropdown.value
  showEquipeDropdown.value = false
  showUserDropdown.value = false
}

const toggleEquipeDropdown = () => {
  if (!filters.value.pole) return
  showEquipeDropdown.value = !showEquipeDropdown.value
  showPoleDropdown.value = false
  showUserDropdown.value = false
}

const toggleUserDropdown = () => {
  showUserDropdown.value = !showUserDropdown.value
  showPoleDropdown.value = false
  showEquipeDropdown.value = false
}

const selectPole = async (id: number | null) => {
  filters.value.pole = id
  filters.value.equipe = null
  showPoleDropdown.value = false
  
  if (id) {
    await filtersStore.fetchEquipesByPole(id)
  } else {
    filtersStore.clearEquipes()
  }
  
  refreshData()
}

const selectEquipe = (id: number | null) => {
  filters.value.equipe = id
  showEquipeDropdown.value = false
  refreshData()
}

const selectUser = (id: number | null) => {
  filters.value.user = id
  showUserDropdown.value = false
  refreshData()
}

// ============================================
// Gestion des événements
// ============================================
const onEventClick = (event: CalendarEvent) => {
  // Ici, vous devrez charger les détails complets selon le type
  // Pour l'exemple, on ouvre juste le modal avec l'événement brut
  selectedEvent.value = event
  showDetailModal.value = true
}

const onDateClick = (date: Date) => {
  // Optionnel: basculer en vue liste et filtrer par cette date
  viewMode.value = 'list'
  // TODO: filtrer par date
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedEvent.value = null
}

const getDetailComponent = (type: string) => {
  const components: Record<string, any> = {
    conge: CongeDetail,
    retard: RetardDetail,
    permission: PermissionDetail,
    repos_medical: ReposDetail,
    ostie: OstieDetail
  }
  return components[type] || 'div'
}

const handleEventAction = (action: any) => {
  // Gérer les actions depuis les composants de détail
  console.log('Action:', action)
  closeDetailModal()
  refreshData()
}

const canManageEvent = (event: any): boolean => {
  if (!event) return false
  if (!canManageOthers.value) return false
  // Vérifier si l'utilisateur peut gérer cet événement
  // Selon vos règles métier
  return true
}

const goToNativeModule = () => {
  if (!selectedEvent.value) return
  
  const routes: Record<string, string> = {
    conge: '/conges',
    retard: '/retards',
    permission: '/permissions',
    repos_medical: '/repos-medical',
    ostie: '/ostie'
  }
  
  const route = routes[selectedEvent.value.type]
  if (route) {
    router.push(route)
  }
}

const exportFiltered = () => {
  // TODO: Exporter la vue liste en CSV
  console.log('Export des données filtrées')
}

// ============================================
// Rafraîchissement des données
// ============================================
const refreshData = async () => {
  loading.value = true
  
  const params = {
    annee: selectedYear.value,
    statut: statusFilter.value === 'all' ? undefined : statusFilter.value,
    pole: filters.value.pole || undefined,
    equipe: filters.value.equipe || undefined
  }

  await Promise.allSettled([
    congesStore.fetchCalendrier(params),
    congesStore.fetchMesConges(selectedYear.value),
    retardsStore.fetchCalendrier(params),
    retardsStore.fetchMesRetards(selectedYear.value),
    permissionsStore.fetchCalendrier(params),
    permissionsStore.fetchMesPermissions(selectedYear.value),
    reposStore.fetchCalendrier(params),
    reposStore.fetchMesRepos(selectedYear.value),
    ostieStore.fetchCalendrier(params),
    ostieStore.fetchMesOsties(selectedYear.value)
  ])

  loading.value = false
}

// Watch pour rafraîchir quand les filtres changent
watch([selectedYear, statusFilter, selectedTypes], () => {
  refreshData()
})

// ============================================
// Initialisation
// ============================================
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  
  // Charger tous les utilisateurs si manager
  if (canManageOthers.value) {
    // TODO: Charger tous les utilisateurs depuis une API dédiée
  }
  
  await refreshData()
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

.events-badge {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.events-badge span {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  color: white;
}

.badge-conges { background: #2196f3; }
.badge-retards { background: #ff9800; }
.badge-permissions { background: #4caf50; }
.badge-repos { background: #9c27b0; }
.badge-osties { background: #e91e63; }

.header-actions {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: #f3f4f6;
  padding: 0.25rem;
  border-radius: 8px;
}

.toggle-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  color: #3498db;
}

.filter-types {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.type-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  transition: background 0.2s;
}

.type-filter:hover {
  background: #f3f4f6;
}

.type-filter.active {
  background: #e5e7eb;
}

.type-filter input {
  display: none;
}

.type-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.btn-refresh {
  width: 36px;
  height: 36px;
  border: none;
  background: #f3f4f6;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e5e7eb;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  background: #f9fafb;
  padding: 1rem;
  border-radius: 12px;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.custom-select {
  position: relative;
  display: inline-block;
}

.select-button {
  padding: 0.6rem 1.2rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  text-align: left;
  min-width: 150px;
}

.select-button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.select-button.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  z-index: 10;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
}

.select-option {
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.select-option:hover {
  background: #f8f9fa;
}

.status-select,
.year-select {
  padding: 0.6rem 1.2rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  min-width: 150px;
}

.events-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Vue Liste */
.list-view {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
  overflow: hidden;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  background: #f8f9fa;
}

.list-stats {
  display: flex;
  gap: 2rem;
}

.btn-export {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-export:hover {
  background: #f3f4f6;
  border-color: #3498db;
}

.events-list {
  max-height: calc(105vh - 350px);
  overflow-y: auto;
  padding: 1.5rem;
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
  border-bottom: 2px solid #e9ecef;
}

.date-header h3 {
  margin: 0;
  color: #2c3e50;
  text-transform: capitalize;
}

.date-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.events-cards {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid;
  cursor: pointer;
  transition: all 0.2s;
}

.event-card:hover {
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.event-icon {
  font-size: 2rem;
  line-height: 1;
}

.event-content {
  flex: 1;
}

.event-title {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.event-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 0.5rem;
}

.event-user {
  color: #6c757d;
  font-size: 0.9rem;
}

.event-type {
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.event-statut {
  padding: 0.2rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  background: #e9ecef;
}

.event-statut.en_attente { background: #fff3e0; color: #e65100; }
.event-statut.approuve { background: #e8f5e9; color: #2e7d32; }
.event-statut.retourne { background: #e3f2fd; color: #0d47a1; }
.event-statut.rattrapage { background: #f3e5f5; color: #6a1b9a; }
.event-statut.transforme { background: #f3e5f5; color: #6a1b9a; }
.event-statut.annule { background: #ffebee; color: #c62828; }
.event-statut.refuse { background: #ffebee; color: #c62828; }

.event-details {
  color: #6c757d;
  font-size: 0.9rem;
  font-style: italic;
}

.no-events {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.no-events i {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 700px;
  max-height: 90vh;
  overflow: hidden;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-large {
  max-width: 700px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-close {
  background: rgba(255,255,255,0.2);
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: white;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.btn-close:hover {
  background: rgba(255,255,255,0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-actions {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-primary {
  padding: 0.625rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #2980b9;
}

/* Header variants */
.header-en_attente { background: #ff9800 !important; }
.header-approuve { background: #4caf50 !important; }
.header-retourne { background: #2196f3 !important; }
.header-rattrapage { background: #9c27b0 !important; }
.header-transforme { background: #9c27b0 !important; }
.header-annule { background: #9e9e9e !important; }
.header-refuse { background: #f44336 !important; }

.header-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.7em;
  margin-left: 10px;
  font-weight: bold;
  background: rgba(255,255,255,0.3);
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .filter-types {
    width: 100%;
  }
  
  .list-stats {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .event-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .modal {
    width: 95%;
  }
}
</style>