<template>
  <div class="dashboard">
    <!-- Header avec titre et info utilisateur -->
    <div class="dashboard-header">
      <div class="header-welcome">
        <h1>Tableau de bord</h1>
        <p class="welcome-text">
          Bienvenue, <strong>{{ authStore.user?.display_name }}</strong>
          <span class="role-badge" :class="userRoleClass">{{ userRoleLabel }}</span>
        </p>
      </div>
      <div class="header-date">
        <span class="current-date">{{ currentDate }}</span>
      </div>
    </div>

    <!-- KPI Cards - Vue d'ensemble -->
    <div class="kpi-grid">
      <!-- Solde Congés - Visible pour tous -->
      <div class="kpi-card conges" @click="navigateTo('conges')">
        <div class="kpi-icon">
          <i class="bi bi-calendar-check"></i>
        </div>
        <div class="kpi-content">
          <h3>Solde Congés</h3>
          <div class="kpi-value">
            <span class="value-main">{{ authStore.soldeConge?.actuelle || 0 }}j</span>
            <span class="value-sub">/ {{ authStore.soldeConge?.total || 0 }}j</span>
          </div>
          <div class="kpi-progress">
            <div class="progress-bar" :style="{ width: congesProgress + '%' }"></div>
          </div>
          <p class="kpi-detail">{{ authStore.soldeConge?.consomme || 0 }}j pris cette année</p>
        </div>
      </div>

      <!-- OSTIE en attente -->
      <div class="kpi-card ostie" @click="navigateTo('ostie')">
        <div class="kpi-icon">
          <i class="bi bi-clock-history"></i>
        </div>
        <div class="kpi-content">
          <h3>OSTIE</h3>
          <div class="kpi-value">
            <span class="value-main">{{ ostieStore.ostiesEnAttente?.length || 0 }}</span>
            <span class="value-label">en attente</span>
          </div>
          <p class="kpi-detail" v-if="isManagerOrAbove">
            {{ ostieStore.totalOsties || 0 }} total sur l'année
          </p>
          <p class="kpi-detail" v-else>
            Cliquez pour voir le calendrier
          </p>
        </div>
      </div>

      <!-- Permissions à rattraper -->
      <div class="kpi-card permissions" @click="navigateTo('permissions')">
        <div class="kpi-icon">
          <i class="bi bi-arrow-left-right"></i>
        </div>
        <div class="kpi-content">
          <h3>Permissions</h3>
          <div class="kpi-value">
            <span class="value-main">{{ permissionsStore.totalHeuresARattraper?.toFixed(2) || '0.00' }}h</span>
            <span class="value-label">à rattraper</span>
          </div>
          <p class="kpi-detail">
            {{ permissionsStore.permissionsRattrapage?.length || 0 }} en cours de rattrapage
          </p>
        </div>
      </div>

      <!-- Retards -->
      <div class="kpi-card retards" @click="navigateTo('retards')">
        <div class="kpi-icon">
          <i class="bi bi-alarm"></i>
        </div>
        <div class="kpi-content">
          <h3>Retards</h3>
          <div class="kpi-value">
            <span class="value-main">{{ retardsStore.totalHeuresARattraper?.toFixed(2) || '0.00' }}h</span>
            <span class="value-label">à rattraper</span>
          </div>
          <p class="kpi-detail">
            {{ retardsStore.retardsEnCours?.length || 0 }} en cours
          </p>
        </div>
      </div>

      <!-- Repos Médicaux - Visible pour tous -->
      <div class="kpi-card repos" @click="navigateTo('reposmedicale')">
        <div class="kpi-icon">
          <i class="bi bi-heart-pulse"></i>
        </div>
        <div class="kpi-content">
          <h3>Repos Médicaux</h3>
          <div class="kpi-value">
            <span class="value-main">{{ reposStore.totalHeuresRepos?.toFixed(2) || '0.00' }}h</span>
            <span class="value-label">cette année</span>
          </div>
          <p class="kpi-detail" v-if="isManagerOrAbove">
            {{ reposStore.reposEnAttente?.length || 0 }} en attente de validation
          </p>
          <p class="kpi-detail" v-else>
            Cliquez pour déclarer un repos
          </p>
        </div>
      </div>

      <!-- Actions rapides managers -->
      <div class="kpi-card actions-manager" v-if="pendingValidationsCount > 0">
        <div class="kpi-icon alert">
          <i class="bi bi-bell-fill"></i>
          <span class="alert-badge">{{ pendingValidationsCount }}</span>
        </div>
        <div class="kpi-content">
          <h3>Validations en attente</h3>
          <div class="kpi-value">
            <span class="value-main alert-text">{{ pendingValidationsCount }}</span>
            <span class="value-label">à traiter</span>
          </div>
          <button class="btn-quick-action" @click="scrollToValidations">
            Voir les demandes
          </button>
        </div>
      </div>
    </div>

    <!-- Section Graphiques - Visible pour Managers et Admin -->
    <div class="charts-section" v-if="isManagerOrAbove">
      <div class="section-header">
        <h2><i class="bi bi-graph-up"></i> Statistiques {{ currentYear }}</h2>
        <div class="chart-filters">
          <select v-model="chartPeriod" class="form-select">
            <option value="month">Ce mois</option>
            <option value="quarter">Ce trimestre</option>
            <option value="year">Cette année</option>
          </select>
        </div>
      </div>

      <div class="charts-grid">
        <!-- Graphique des demandes par type -->
        <div class="chart-card">
          <h4>Répartition des demandes</h4>
          <div class="chart-container" ref="demandsChartRef">
            <canvas id="demandsChart"></canvas>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="dot conges"></span> Congés
            </div>
            <div class="legend-item">
              <span class="dot ostie"></span> OSTIE
            </div>
            <div class="legend-item">
              <span class="dot permissions"></span> Permissions
            </div>
            <div class="legend-item">
              <span class="dot repos"></span> Repos médicaux
            </div>
          </div>
        </div>

        <!-- Graphique des tendances mensuelles -->
        <div class="chart-card wide">
          <h4>Tendances mensuelles</h4>
          <div class="chart-container" ref="trendsChartRef">
            <canvas id="trendsChart"></canvas>
          </div>
        </div>

        <!-- Top utilisateurs (SuperAdmin/Admin uniquement) -->
        <div class="chart-card" v-if="isAdminOrAbove">
          <h4>Top demandeurs</h4>
          <div class="top-users-list">
            <div v-for="(user, index) in topUsers" :key="user.id" class="top-user-item">
              <span class="rank">{{ index + 1 }}</span>
              <div class="user-info">
                <span class="name">{{ user.display_name }}</span>
                <span class="count">{{ user.demandes_count }} demandes</span>
              </div>
              <div class="bar-container">
                <div class="bar" :style="{ width: user.percentage + '%' }"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Section Validations en attente (Managers/Admins) -->
    <div class="validations-section" v-if="isManagerOrAbove && pendingValidations.length > 0" id="validations">
      <div class="section-header">
        <h2><i class="bi bi-check2-square"></i> Validations en attente</h2>
        <span class="badge-count">{{ pendingValidations.length }}</span>
      </div>

      <div class="validations-list">
        <div 
          v-for="item in pendingValidations.slice(0, 5)" 
          :key="item.id + '-' + item.type"
          class="validation-item"
          :class="item.type"
        >
          <div class="validation-icon">
            <i :class="getValidationIcon(item.type)"></i>
          </div>
          <div class="validation-info">
            <h4>{{ item.user_name }}</h4>
            <p class="validation-type">{{ getValidationTypeLabel(item.type) }}</p>
            <p class="validation-date">{{ formatDate(item.date) }}</p>
          </div>
          <div class="validation-actions">
            <button class="btn-icon success" @click="handleValidation(item, 'approve')" title="Valider">
              <i class="bi bi-check-lg"></i>
            </button>
            <button class="btn-icon danger" @click="handleValidation(item, 'reject')" title="Refuser">
              <i class="bi bi-x-lg"></i>
            </button>
            <button class="btn-icon info" @click="viewDetails(item)" title="Voir détails">
              <i class="bi bi-eye"></i>
            </button>
          </div>
        </div>

        <div v-if="pendingValidations.length > 5" class="show-more">
          <button class="btn-link" @click="showAllValidations = true">
            Voir les {{ pendingValidations.length - 5 }} demandes restantes
          </button>
        </div>
      </div>
    </div>

    <!-- Calendrier consolidé -->
    <div class="calendar-section">
      <div class="section-header">
        <h2><i class="bi bi-calendar3"></i> Calendrier consolidé</h2>
        <div class="calendar-filters">
          <label class="checkbox-label">
            <input type="checkbox" v-model="calendarFilters.conges" />
            <span class="check-conges">Congés</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="calendarFilters.ostie" />
            <span class="check-ostie">OSTIE</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="calendarFilters.permissions" />
            <span class="check-permissions">Permissions</span>
          </label>
          <label class="checkbox-label">
            <input type="checkbox" v-model="calendarFilters.repos" />
            <span class="check-repos">Repos</span>
          </label>
          <label class="checkbox-label" v-if="isManagerOrAbove">
            <input type="checkbox" v-model="calendarFilters.retards" />
            <span class="check-retards">Retards</span>
          </label>
        </div>
      </div>

      <div class="calendar-wrapper">
        <Calendar
          :events="consolidatedEvents"
          :blocked-dates="blockedDates"
          :default-view="'month'"
          class="dashboard-calendar"
          @event-click="onCalendarEventClick"
        />
      </div>
    </div>

    <!-- Actions rapides selon le rôle -->
    <div class="quick-actions-section">
      <h2><i class="bi bi-lightning-charge"></i> Actions rapides</h2>
      <div class="quick-actions-grid">
        <!-- Actions Utilisateur -->
        <button class="quick-action-btn" @click="openModal('conge')">
          <i class="bi bi-calendar-plus"></i>
          <span>Demander des congés</span>
        </button>
        <button class="quick-action-btn" @click="openModal('ostie')">
          <i class="bi bi-clock"></i>
          <span>Demander un OSTIE</span>
        </button>
        <button class="quick-action-btn" @click="openModal('permission')">
          <i class="bi bi-arrow-left-right"></i>
          <span>Demander une permission</span>
        </button>
        <button class="quick-action-btn" @click="openModal('repos')">
          <i class="bi bi-heart-pulse"></i>
          <span>Déclarer un repos médical</span>
        </button>

        <!-- Actions Manager -->
        <button class="quick-action-btn manager" v-if="isManagerOrAbove" @click="openModal('conge-manager')">
          <i class="bi bi-calendar-check"></i>
          <span>Ajouter un congé (équipe)</span>
        </button>
        <button class="quick-action-btn manager" v-if="isManagerOrAbove" @click="openModal('ostie-manager')">
          <i class="bi bi-clock-history"></i>
          <span>Ajouter un OSTIE (équipe)</span>
        </button>

        <!-- Actions Admin -->
        <button class="quick-action-btn admin" v-if="isAdminOrAbove" @click="exportData">
          <i class="bi bi-download"></i>
          <span>Exporter les données</span>
        </button>
        <button class="quick-action-btn admin" v-if="isSuperAdmin" @click="navigateTo('admin')">
          <i class="bi bi-gear"></i>
          <span>Administration</span>
        </button>
      </div>
    </div>

    <!-- Modal de confirmation rapide -->
    <Teleport to="body">
      <div v-if="showQuickValidationModal" class="modal-overlay" @click.self="closeQuickModal">
        <div class="modal modal-medium">
          <div class="modal-header" :class="quickActionType">
            <h3>{{ quickModalTitle }}</h3>
            <button class="btn-close" @click="closeQuickModal">×</button>
          </div>
          <div class="modal-body">
            <div class="validation-preview">
              <div class="user-avatar">{{ getInitials(selectedQuickItem?.user_name || '') }}</div>
              <div class="user-details">
                <h4>{{ selectedQuickItem?.user_name }}</h4>
                <p>{{ getValidationTypeLabel(selectedQuickItem?.type) }} - {{ formatDate(selectedQuickItem?.date) }}</p>
              </div>
            </div>

            <div v-if="quickActionType === 'reject'" class="form-group">
              <label>Motif du refus</label>
              <textarea v-model="rejectComment" rows="3" class="form-textarea"></textarea>
            </div>

            <div v-if="quickError" class="alert-error">{{ quickError }}</div>
          </div>
          <div class="modal-actions">
            <button class="btn-secondary" @click="closeQuickModal">Annuler</button>
            <button 
              class="btn-primary" 
              :class="quickActionType"
              @click="confirmQuickAction"
              :disabled="quickSubmitting"
            >
              <i v-if="quickSubmitting" class="bi bi-arrow-repeat spin"></i>
              <span v-else>{{ quickActionType === 'approve' ? 'Valider' : 'Refuser' }}</span>
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Modal liste complète des validations -->
    <Teleport to="body">
      <div v-if="showAllValidations" class="modal-overlay" @click.self="showAllValidations = false">
        <div class="modal modal-large">
          <div class="modal-header">
            <h3>Toutes les validations en attente ({{ pendingValidations.length }})</h3>
            <button class="btn-close" @click="showAllValidations = false">×</button>
          </div>
          <div class="modal-body">
            <div class="validations-list full">
              <div 
                v-for="item in pendingValidations" 
                :key="item.id + '-' + item.type"
                class="validation-item"
                :class="item.type"
              >
                <div class="validation-icon">
                  <i :class="getValidationIcon(item.type)"></i>
                </div>
                <div class="validation-info">
                  <h4>{{ item.user_name }}</h4>
                  <p class="validation-type">{{ getValidationTypeLabel(item.type) }}</p>
                  <p class="validation-date">{{ formatDate(item.date) }}</p>
                </div>
                <div class="validation-actions">
                  <button class="btn-icon success" @click="handleValidation(item, 'approve')">
                    <i class="bi bi-check-lg"></i>
                  </button>
                  <button class="btn-icon danger" @click="handleValidation(item, 'reject')">
                    <i class="bi bi-x-lg"></i>
                  </button>
                  <button class="btn-icon info" @click="viewDetails(item)">
                    <i class="bi bi-eye"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useRetardsStore } from '@/store/retards'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import { format, parseISO, getYear, startOfMonth, endOfMonth, eachMonthOfInterval } from 'date-fns'
import { fr } from 'date-fns/locale/fr'
import Chart from 'chart.js/auto'

// Router
const router = useRouter()

// Stores
const authStore = useAuthStore()
const congesStore = useCongesStore()
const ostieStore = useOstieStore()
const permissionsStore = usePermissionsStore()
const retardsStore = useRetardsStore()
const reposStore = useReposMedicaleStore()
const filtersStore = useFiltersStore()

// État local
const loading = ref(true)
const chartPeriod = ref('month')
const showAllValidations = ref(false)
const showQuickValidationModal = ref(false)
const quickActionType = ref<'approve' | 'reject'>('approve')
const selectedQuickItem = ref<any>(null)
const quickSubmitting = ref(false)
const quickError = ref<string | null>(null)
const rejectComment = ref('')

// Filtres du calendrier
const calendarFilters = ref({
  conges: true,
  ostie: true,
  permissions: true,
  repos: true,
  retards: false
})

// Refs pour les graphiques
const demandsChartRef = ref<HTMLCanvasElement | null>(null)
const trendsChartRef = ref<HTMLCanvasElement | null>(null)
let demandsChart: Chart | null = null
let trendsChart: Chart | null = null

// ============================================
// COMPUTED - Rôles et permissions
// ============================================

const userRole = computed(() => {
  if (!authStore.user) return 'user'
  if (authStore.user.is_superuser) return 'superadmin'
  if (authStore.user.is_staff) return 'admin'
  // Détection manager/co-manager basée sur les équipes gérables
  if (congesStore.utilisateursGerables?.length > 0 || congesStore.isManagerOrAdmin) return 'manager'
  return 'user'
})

const userRoleLabel = computed(() => {
  const labels: Record<string, string> = {
    'superadmin': 'Super Administrateur',
    'admin': 'Administrateur',
    'manager': 'Manager',
    'user': 'Utilisateur'
  }
  return labels[userRole.value] || 'Utilisateur'
})

const userRoleClass = computed(() => {
  return `role-${userRole.value}`
})

const isManagerOrAbove = computed(() => {
  return ['manager', 'admin', 'superadmin'].includes(userRole.value)
})

const isAdminOrAbove = computed(() => {
  return ['admin', 'superadmin'].includes(userRole.value)
})

const isSuperAdmin = computed(() => {
  return userRole.value === 'superadmin'
})

// ============================================
// COMPUTED - Données et métriques
// ============================================

const currentDate = computed(() => {
  return format(new Date(), "EEEE d MMMM yyyy", { locale: fr })
})

const currentYear = computed(() => getYear(new Date()))

const congesProgress = computed(() => {
  const total = authStore.soldeConge?.total || 0
  const current = authStore.soldeConge?.actuelle || 0
  if (total === 0) return 0
  return ((total - current) / total) * 100
})

// Événements consolidés pour le calendrier
const consolidatedEvents = computed<CalendarEvent[]>(() => {
  const events: CalendarEvent[] = []

  if (calendarFilters.value.conges) {
    events.push(...congesStore.eventsForCalendar)
  }
  if (calendarFilters.value.ostie) {
    events.push(...ostieStore.eventsForCalendar)
  }
  if (calendarFilters.value.permissions) {
    events.push(...permissionsStore.eventsForCalendar)
  }
  if (calendarFilters.value.repos) {
    events.push(...reposStore.eventsForCalendar)
  }
  if (calendarFilters.value.retards && isManagerOrAbove.value) {
    events.push(...retardsStore.eventsForCalendar)
  }

  return events
})

const blockedDates = computed(() => {
  return congesStore.calendrierEvents
    .filter(e => e.isBlocked)
    .flatMap(e => {
      const dates: Date[] = []
      const start = new Date(e.start)
      const end = e.end ? new Date(e.end) : start
      let current = new Date(start)
      while (current <= end) {
        dates.push(new Date(current))
        current = new Date(current.setDate(current.getDate() + 1))
      }
      return dates
    })
})

// ============================================
// COMPUTED - Validations en attente
// ============================================

const pendingValidations = computed(() => {
  const validations: any[] = []

  if (!isManagerOrAbove.value) return validations

  // Congés en attente
  congesStore.conges
    ?.filter(c => c.statut === 'en_attente')
    ?.forEach(c => {
      validations.push({
        id: c.id,
        type: 'conge',
        user_name: c.utilisateur_details?.display_name || 'Utilisateur',
        user_id: c.utilisateur,
        date: c.date_debut,
        details: c
      })
    })

  // OSTIE en attente
  ostieStore.ostiesEnAttente
    ?.forEach(o => {
      validations.push({
        id: o.id,
        type: 'ostie',
        user_name: o.utilisateur_details?.display_name || 'Utilisateur',
        user_id: o.utilisateur,
        date: o.date,
        details: o
      })
    })

  // Permissions en attente
  permissionsStore.permissions
    ?.filter(p => p.statut === 'en_attente')
    ?.forEach(p => {
      validations.push({
        id: p.id,
        type: 'permission',
        user_name: p.utilisateur_details?.display_name || 'Utilisateur',
        user_id: p.utilisateur,
        date: p.date,
        details: p
      })
    })

  // Repos médicaux en attente
  reposStore.reposEnAttente
    ?.forEach(r => {
      validations.push({
        id: r.id,
        type: 'repos',
        user_name: r.utilisateur_details?.display_name || 'Utilisateur',
        user_id: r.utilisateur,
        date: r.date,
        details: r
      })
    })

  return validations.sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
})

const pendingValidationsCount = computed(() => pendingValidations.value.length)

// ============================================
// COMPUTED - Top utilisateurs (Admin)
// ============================================

const topUsers = computed(() => {
  if (!isAdminOrAbove.value) return []

  const userStats: Record<number, { id: number; display_name: string; demandes_count: number }> = {}

  // Agréger toutes les demandes par utilisateur
  const allRequests = [
    ...(congesStore.conges || []),
    ...(ostieStore.osties || []),
    ...(permissionsStore.permissions || []),
    ...(reposStore.repos || [])
  ]

  allRequests.forEach(req => {
    const userId = req.utilisateur
    if (!userStats[userId]) {
      userStats[userId] = {
        id: userId,
        display_name: req.utilisateur_details?.display_name || 'Utilisateur',
        demandes_count: 0
      }
    }
    userStats[userId].demandes_count++
  })

  const sorted = Object.values(userStats).sort((a, b) => b.demandes_count - a.demandes_count).slice(0, 5)
  const max = sorted[0]?.demandes_count || 1

  return sorted.map(u => ({
    ...u,
    percentage: (u.demandes_count / max) * 100
  }))
})

// ============================================
// METHODS - Navigation et actions
// ============================================

const navigateTo = (route: string) => {
  router.push({ name: route })
}

const scrollToValidations = () => {
  const element = document.getElementById('validations')
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

const openModal = (type: string) => {
  // Redirection vers la page concernée avec ouverture automatique du modal
  const routeMap: Record<string, string> = {
    'conge': 'conges',
    'conge-manager': 'conges',
    'ostie': 'ostie',
    'ostie-manager': 'ostie',
    'permission': 'permissions',
    'repos': 'reposmedicale'
  }

  const route = routeMap[type]
  if (route) {
    // Stocker dans sessionStorage pour ouvrir le modal automatiquement
    sessionStorage.setItem('openModal', type)
    router.push({ name: route })
  }
}

const exportData = () => {
  // Logique d'export globale
  alert('Fonctionnalité d'export en cours de développement')
}

// ============================================
// METHODS - Validation rapide
// ============================================

const getValidationIcon = (type: string) => {
  const icons: Record<string, string> = {
    'conge': 'bi bi-calendar-check',
    'ostie': 'bi bi-clock-history',
    'permission': 'bi bi-arrow-left-right',
    'repos': 'bi bi-heart-pulse'
  }
  return icons[type] || 'bi bi-circle'
}

const getValidationTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'conge': 'Demande de congés',
    'ostie': 'OSTIE',
    'permission': 'Permission de sortie',
    'repos': 'Repos médical'
  }
  return labels[type] || type
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: fr })
}

const getInitials = (name: string) => {
  return name?.charAt(0)?.toUpperCase() || '?'
}

const handleValidation = (item: any, action: 'approve' | 'reject') => {
  selectedQuickItem.value = item
  quickActionType.value = action
  quickError.value = null
  rejectComment.value = ''
  showQuickValidationModal.value = true
}

const closeQuickModal = () => {
  showQuickValidationModal.value = false
  selectedQuickItem.value = null
  quickSubmitting.value = false
}

const quickModalTitle = computed(() => {
  return quickActionType.value === 'approve' ? 'Valider la demande' : 'Refuser la demande'
})

const confirmQuickAction = async () => {
  if (!selectedQuickItem.value) return

  quickSubmitting.value = true
  quickError.value = null

  try {
    const { type, id, details } = selectedQuickItem.value

    if (quickActionType.value === 'approve') {
      switch (type) {
        case 'conge':
          await congesStore.validerConge(id)
          break
        case 'ostie':
          await ostieStore.validerOstie(id, { heure_fin: details.heure_fin || '17:00' })
          break
        case 'permission':
          await permissionsStore.enregistrerRetour(id, details.heure_arrivee_max || '17:00')
          break
        case 'repos':
          await reposStore.validerReposMedical(id)
          break
      }
    } else {
      // Rejet
      switch (type) {
        case 'conge':
          await congesStore.refuserConge(id, rejectComment.value)
          break
        case 'ostie':
        case 'permission':
        case 'repos':
          // Annulation pour les autres types
          const storeMap: any = {
            'ostie': ostieStore,
            'permission': permissionsStore,
            'repos': reposStore
          }
          await storeMap[type]?.annuler?.(id, rejectComment.value)
          break
      }
    }

    closeQuickModal()
    await refreshAllData()

  } catch (err: any) {
    quickError.value = err.message || 'Erreur lors de l'action'
  } finally {
    quickSubmitting.value = false
  }
}

const viewDetails = (item: any) => {
  const routeMap: Record<string, string> = {
    'conge': 'conges',
    'ostie': 'ostie',
    'permission': 'permissions',
    'repos': 'reposmedicale'
  }

  const route = routeMap[item.type]
  if (route) {
    router.push({ 
      name: route,
      query: { highlight: item.id }
    })
  }
}

const onCalendarEventClick = (event: CalendarEvent) => {
  // Extraire l'ID et le type de l'événement
  const [type, idStr] = String(event.id).split('_')
  const id = parseInt(idStr)

  if (id && type) {
    viewDetails({ type: type === 'repos' ? 'repos' : type, id, details: event })
  }
}

// ============================================
// METHODS - Graphiques
// ============================================

const initCharts = () => {
  if (!isManagerOrAbove.value) return

  nextTick(() => {
    initDemandsChart()
    initTrendsChart()
  })
}

const initDemandsChart = () => {
  const canvas = document.getElementById('demandsChart') as HTMLCanvasElement
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Données pour le graphique
  const data = {
    labels: ['Congés', 'OSTIE', 'Permissions', 'Repos'],
    datasets: [{
      data: [
        congesStore.conges?.length || 0,
        ostieStore.totalOsties || 0,
        permissionsStore.permissions?.length || 0,
        reposStore.totalHeuresRepos || 0
      ],
      backgroundColor: [
        '#4CAF50',  // Congés - vert
        '#FF9800',  // OSTIE - orange
        '#2196F3',  // Permissions - bleu
        '#9C27B0'   // Repos - violet
      ],
      borderWidth: 0
    }]
  }

  if (demandsChart) {
    demandsChart.destroy()
  }

  demandsChart = new Chart(ctx, {
    type: 'doughnut',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      }
    }
  })
}

const initTrendsChart = () => {
  const canvas = document.getElementById('trendsChart') as HTMLCanvasElement
  if (!canvas) return

  const ctx = canvas.getContext('2d')
  if (!ctx) return

  // Générer les 6 derniers mois
  const months = eachMonthOfInterval({
    start: startOfMonth(new Date(new Date().setMonth(new Date().getMonth() - 5))),
    end: endOfMonth(new Date())
  })

  const monthLabels = months.map(m => format(m, 'MMM', { locale: fr }))

  // Données simulées (à remplacer par des données réelles)
  const data = {
    labels: monthLabels,
    datasets: [
      {
        label: 'Congés',
        data: [3, 5, 2, 8, 4, 6],
        borderColor: '#4CAF50',
        backgroundColor: 'rgba(76, 175, 80, 0.1)',
        tension: 0.4
      },
      {
        label: 'OSTIE',
        data: [5, 3, 7, 4, 6, 5],
        borderColor: '#FF9800',
        backgroundColor: 'rgba(255, 152, 0, 0.1)',
        tension: 0.4
      },
      {
        label: 'Permissions',
        data: [2, 4, 3, 5, 3, 4],
        borderColor: '#2196F3',
        backgroundColor: 'rgba(33, 150, 243, 0.1)',
        tension: 0.4
      }
    ]
  }

  if (trendsChart) {
    trendsChart.destroy()
  }

  trendsChart = new Chart(ctx, {
    type: 'line',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  })
}

// ============================================
// METHODS - Data fetching
// ============================================

const refreshAllData = async () => {
  loading.value = true

  const currentYear = getYear(new Date())

  try {
    await Promise.all([
      authStore.checkAuth(),
      authStore.refreshSolde(),
      congesStore.fetchMesConges(currentYear),
      congesStore.fetchCalendrier({ annee: currentYear }),
      ostieStore.fetchMesOsties(currentYear),
      ostieStore.fetchCalendrier({ annee: currentYear }),
      permissionsStore.fetchMesPermissions(currentYear),
      permissionsStore.fetchCalendrier({ annee: currentYear }),
      retardsStore.fetchMesRetards(currentYear),
      retardsStore.fetchCalendrier({ annee: currentYear }),
      reposStore.fetchMesRepos(currentYear),
      reposStore.fetchCalendrier({ annee: currentYear })
    ])

    // Si manager/admin, charger les données d'équipe
    if (isManagerOrAbove.value) {
      await Promise.all([
        congesStore.fetchUtilisateursGerables(),
        ostieStore.fetchUtilisateursGerables(),
        permissionsStore.fetchUtilisateursGerables(),
        reposStore.fetchUtilisateursGerables()
      ])
    }

    // Initialiser les graphiques après chargement des données
    initCharts()

  } catch (error) {
    console.error('Erreur chargement dashboard:', error)
  } finally {
    loading.value = false
  }
}

// Watch pour mettre à jour les graphiques quand les filtres changent
watch(chartPeriod, () => {
  initCharts()
})

// ============================================
// LIFECYCLE
// ============================================

onMounted(() => {
  refreshAllData()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
}

// Header
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e2e8f0;

  .header-welcome {
    h1 {
      font-size: 2rem;
      font-weight: 700;
      color: #1e293b;
      margin-bottom: 0.5rem;
    }

    .welcome-text {
      font-size: 1.1rem;
      color: #64748b;

      strong {
        color: #1e293b;
      }
    }
  }

  .role-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    margin-left: 0.75rem;

    &.role-superadmin {
      background: #fef3c7;
      color: #92400e;
    }

    &.role-admin {
      background: #dbeafe;
      color: #1e40af;
    }

    &.role-manager {
      background: #d1fae5;
      color: #065f46;
    }

    &.role-user {
      background: #f3f4f6;
      color: #4b5563;
    }
  }

  .header-date {
    .current-date {
      font-size: 1rem;
      color: #64748b;
      font-weight: 500;
    }
  }
}

// KPI Grid
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
  border-left: 4px solid transparent;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  &.conges {
    border-left-color: #4CAF50;
    .kpi-icon { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }
  }

  &.ostie {
    border-left-color: #FF9800;
    .kpi-icon { background: rgba(255, 152, 0, 0.1); color: #FF9800; }
  }

  &.permissions {
    border-left-color: #2196F3;
    .kpi-icon { background: rgba(33, 150, 243, 0.1); color: #2196F3; }
  }

  &.retards {
    border-left-color: #f44336;
    .kpi-icon { background: rgba(244, 67, 54, 0.1); color: #f44336; }
  }

  &.repos {
    border-left-color: #9C27B0;
    .kpi-icon { background: rgba(156, 39, 176, 0.1); color: #9C27B0; }
  }

  &.actions-manager {
    border-left-color: #ef4444;
    background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);

    .kpi-icon {
      background: #ef4444;
      color: white;
      position: relative;

      .alert-badge {
        position: absolute;
        top: -8px;
        right: -8px;
        background: #dc2626;
        color: white;
        font-size: 0.7rem;
        padding: 0.15rem 0.4rem;
        border-radius: 9999px;
        font-weight: 700;
      }
    }

    .alert-text {
      color: #dc2626;
    }
  }

  .kpi-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    flex-shrink: 0;
  }

  .kpi-content {
    flex: 1;

    h3 {
      font-size: 0.875rem;
      font-weight: 600;
      color: #64748b;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 0.5rem;
    }

    .kpi-value {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 0.5rem;

      .value-main {
        font-size: 1.875rem;
        font-weight: 700;
        color: #1e293b;
      }

      .value-sub {
        font-size: 1rem;
        color: #94a3b8;
      }

      .value-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 500;
      }
    }

    .kpi-progress {
      height: 4px;
      background: #e2e8f0;
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 0.5rem;

      .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #81C784);
        border-radius: 2px;
        transition: width 0.5s ease;
      }
    }

    .kpi-detail {
      font-size: 0.875rem;
      color: #94a3b8;
    }
  }

  .btn-quick-action {
    margin-top: 0.75rem;
    padding: 0.5rem 1rem;
    background: #ef4444;
    color: white;
    border: none;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background: #dc2626;
      transform: translateY(-1px);
    }
  }
}

// Sections
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;

  h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    i {
      color: #64748b;
    }
  }

  .badge-count {
    background: #ef4444;
    color: white;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.875rem;
    font-weight: 600;
  }
}

// Charts Section
.charts-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .chart-filters {
    .form-select {
      padding: 0.5rem 1rem;
      border: 1px solid #e2e8f0;
      border-radius: 8px;
      background: white;
      font-size: 0.875rem;
      cursor: pointer;
    }
  }
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;

  .chart-card {
    background: #f8fafc;
    border-radius: 12px;
    padding: 1rem;

    &.wide {
      grid-column: 1 / -1;
    }

    h4 {
      font-size: 0.875rem;
      font-weight: 600;
      color: #64748b;
      margin-bottom: 1rem;
    }

    .chart-container {
      height: 250px;
      position: relative;
    }

    .chart-legend {
      display: flex;
      flex-wrap: wrap;
      gap: 1rem;
      margin-top: 1rem;
      justify-content: center;

      .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.875rem;
        color: #64748b;

        .dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;

          &.conges { background: #4CAF50; }
          &.ostie { background: #FF9800; }
          &.permissions { background: #2196F3; }
          &.repos { background: #9C27B0; }
        }
      }
    }
  }
}

// Top Users List
.top-users-list {
  .top-user-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 0;
    border-bottom: 1px solid #e2e8f0;

    &:last-child {
      border-bottom: none;
    }

    .rank {
      width: 28px;
      height: 28px;
      background: #e2e8f0;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 0.875rem;
      color: #64748b;
    }

    .user-info {
      flex: 1;

      .name {
        display: block;
        font-weight: 600;
        color: #1e293b;
        font-size: 0.875rem;
      }

      .count {
        font-size: 0.75rem;
        color: #94a3b8;
      }
    }

    .bar-container {
      width: 100px;
      height: 6px;
      background: #e2e8f0;
      border-radius: 3px;
      overflow: hidden;

      .bar {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #81C784);
        border-radius: 3px;
        transition: width 0.5s ease;
      }
    }
  }
}

// Validations Section
.validations-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.validations-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;

  &.full {
    max-height: 60vh;
    overflow-y: auto;
  }

  .validation-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    border-left: 4px solid transparent;
    transition: all 0.2s;

    &:hover {
      background: #f1f5f9;
      transform: translateX(4px);
    }

    &.conge { border-left-color: #4CAF50; }
    &.ostie { border-left-color: #FF9800; }
    &.permission { border-left-color: #2196F3; }
    &.repos { border-left-color: #9C27B0; }

    .validation-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      background: white;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #64748b;
      font-size: 1.25rem;
    }

    .validation-info {
      flex: 1;

      h4 {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
      }

      .validation-type {
        font-size: 0.875rem;
        color: #64748b;
      }

      .validation-date {
        font-size: 0.75rem;
        color: #94a3b8;
      }
    }

    .validation-actions {
      display: flex;
      gap: 0.5rem;

      .btn-icon {
        width: 36px;
        height: 36px;
        border-radius: 8px;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s;

        &.success {
          background: #d1fae5;
          color: #065f46;

          &:hover {
            background: #a7f3d0;
          }
        }

        &.danger {
          background: #fee2e2;
          color: #991b1b;

          &:hover {
            background: #fecaca;
          }
        }

        &.info {
          background: #dbeafe;
          color: #1e40af;

          &:hover {
            background: #bfdbfe;
          }
        }
      }
    }
  }

  .show-more {
    text-align: center;
    padding: 1rem;

    .btn-link {
      background: none;
      border: none;
      color: #3b82f6;
      font-weight: 600;
      cursor: pointer;

      &:hover {
        text-decoration: underline;
      }
    }
  }
}

// Calendar Section
.calendar-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .calendar-filters {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;

    .checkbox-label {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      cursor: pointer;
      font-size: 0.875rem;
      color: #64748b;

      input {
        width: 16px;
        height: 16px;
        cursor: pointer;
      }

      span {
        padding: 0.25rem 0.5rem;
        border-radius: 4px;
        font-weight: 500;

        &.check-conges { background: rgba(76, 175, 80, 0.1); color: #4CAF50; }
        &.check-ostie { background: rgba(255, 152, 0, 0.1); color: #FF9800; }
        &.check-permissions { background: rgba(33, 150, 243, 0.1); color: #2196F3; }
        &.check-repos { background: rgba(156, 39, 176, 0.1); color: #9C27B0; }
        &.check-retards { background: rgba(244, 67, 54, 0.1); color: #f44336; }
      }
    }
  }

  .calendar-wrapper {
    margin-top: 1.5rem;
  }
}

// Quick Actions
.quick-actions-section {
  h2 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    i {
      color: #fbbf24;
    }
  }
}

.quick-actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;

  .quick-action-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.75rem;
    padding: 1.5rem;
    background: white;
    border: 2px solid #e2e8f0;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.2s;

    i {
      font-size: 1.5rem;
      color: #64748b;
    }

    span {
      font-size: 0.875rem;
      font-weight: 600;
      color: #475569;
      text-align: center;
    }

    &:hover {
      border-color: #3b82f6;
      background: #eff6ff;
      transform: translateY(-2px);

      i {
        color: #3b82f6;
      }
    }

    &.manager {
      border-color: #10b981;
      background: #ecfdf5;

      i {
        color: #10b981;
      }

      &:hover {
        background: #d1fae5;
      }
    }

    &.admin {
      border-color: #8b5cf6;
      background: #f5f3ff;

      i {
        color: #8b5cf6;
      }

      &:hover {
        background: #ede9fe;
      }
    }
  }
}

// Modals
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);

  &.modal-medium {
    max-width: 450px;
  }

  &.modal-large {
    max-width: 700px;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;

  h3 {
    font-size: 1.25rem;
    font-weight: 700;
    color: #1e293b;
  }

  &.approve {
    background: #d1fae5;
    border-bottom-color: #a7f3d0;
  }

  &.reject {
    background: #fee2e2;
    border-bottom-color: #fecaca;
  }

  .btn-close {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: none;
    background: rgba(0, 0, 0, 0.05);
    color: #64748b;
    font-size: 1.25rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background: rgba(0, 0, 0, 0.1);
    }
  }
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;

  .validation-preview {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: #f8fafc;
    border-radius: 12px;
    margin-bottom: 1.5rem;

    .user-avatar {
      width: 48px;
      height: 48px;
      border-radius: 50%;
      background: #3b82f6;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.25rem;
      font-weight: 600;
    }

    .user-details {
      h4 {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.25rem;
      }

      p {
        font-size: 0.875rem;
        color: #64748b;
      }
    }
  }

  .form-group {
    margin-bottom: 1rem;

    label {
      display: block;
      font-size: 0.875rem;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.5rem;
    }
  }

  .form-textarea {
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    font-size: 0.875rem;
    resize: vertical;
    min-height: 80px;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      ring: 2px solid rgba(59, 130, 246, 0.5);
    }
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #e2e8f0;
  background: #f8fafc;

  button {
    padding: 0.625rem 1.25rem;
    border-radius: 8px;
    font-size: 0.875rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    &.btn-secondary {
      background: white;
      border: 1px solid #d1d5db;
      color: #374151;

      &:hover {
        background: #f9fafb;
      }
    }

    &.btn-primary {
      background: #3b82f6;
      border: none;
      color: white;

      &:hover:not(:disabled) {
        background: #2563eb;
      }

      &.approve {
        background: #10b981;

        &:hover {
          background: #059669;
        }
      }

      &.reject {
        background: #ef4444;

        &:hover {
          background: #dc2626;
        }
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.alert-error {
  padding: 0.75rem;
  background: #fee2e2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.875rem;
  margin-top: 1rem;
}

// Responsive
@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }

  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;

    .header-welcome h1 {
      font-size: 1.5rem;
    }
  }

  .kpi-grid {
    grid-template-columns: 1fr;
  }

  .charts-grid {
    grid-template-columns: 1fr;
  }

  .calendar-filters {
    flex-direction: column;
    gap: 0.5rem;
  }

  .quick-actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

// Animations
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.bi-arrow-repeat.spin {
  animation: spin 1s linear infinite;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.kpi-card {
  animation: slideIn 0.3s ease-out;
}
</style>