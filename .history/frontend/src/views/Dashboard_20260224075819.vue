<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <!-- En-tête avec bienvenue personnalisée selon le rôle -->
    <div class="page-header">
      <div class="header-content">
        <h1>
          Tableau de bord
          <span class="role-badge" :class="roleClass">{{ userRole }}</span>
        </h1>
        <div class="header-right">
          <p class="welcome-date">{{ currentDate }}</p>
          <button class="btn-refresh" @click="refreshAllData" :disabled="loading">
            <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
            {{ loading ? 'Actualisation...' : 'Actualiser' }}
          </button>
        </div>
      </div>
      <p class="welcome-message">
        {{ welcomeMessage }}
      </p>
    </div>

    <!-- LOADING STATE -->
    <div v-if="loading && !hasData" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement de votre tableau de bord...</p>
    </div>

    <template v-else>
      <!-- ========== KPI CARDS (communs à tous) ========== -->
      <div class="kpi-grid">
        <!-- Carte Congés -->
        <div class="kpi-card" @click="goToModule('conges')">
          <div class="kpi-icon conges">
            <i class="bi bi-calendar-check"></i>
          </div>
          <div class="kpi-content">
            <h3>Congés</h3>
            <div class="kpi-value">{{ congesStore.soldeConge.actuelle }}j</div>
            <div class="kpi-detail">
              <span class="badge pris">{{ congesStore.soldeConge.consomme }}j pris</span>
              <span v-if="pendingCounts.conges > 0" class="badge warning">{{ pendingCounts.conges }} en attente</span>
            </div>
          </div>
        </div>

        <!-- Carte OSTIE -->
        <div class="kpi-card" @click="goToModule('ostie')">
          <div class="kpi-icon ostie">
            <i class="bi bi-hospital"></i>
          </div>
          <div class="kpi-content">
            <h3>OSTIE</h3>
            <div class="kpi-value">{{ ostieStore.totalOsties }}</div>
            <div class="kpi-detail">
              <span class="badge warning">{{ ostieStore.ostiesEnAttente.length }} en attente</span>
            </div>
          </div>
        </div>

        <!-- Carte Permissions -->
        <div class="kpi-card" @click="goToModule('permissions')">
          <div class="kpi-icon permissions">
            <i class="bi bi-door-open"></i>
          </div>
          <div class="kpi-content">
            <h3>Permissions</h3>
            <div class="kpi-value">{{ permissionsStore.totalHeuresARattraper.toFixed(1) }}h</div>
            <div class="kpi-detail">
              <span class="badge info">{{ permissionsStore.permissionsRattrapage.length }} rattrapage</span>
              <span class="badge warning">{{ permissionsStore.permissionsRetournees.length }} retournées</span>
            </div>
          </div>
        </div>

        <!-- Carte Repos Médicaux -->
        <div class="kpi-card" @click="goToModule('reposmedicale')">
          <div class="kpi-icon repos">
            <i class="bi bi-heart-pulse"></i>
          </div>
          <div class="kpi-content">
            <h3>Repos médicaux</h3>
            <div class="kpi-value">{{ reposStore.totalHeuresRepos.toFixed(1) }}h</div>
            <div class="kpi-detail">
              <span class="badge warning">{{ reposStore.reposEnAttente.length }} en attente</span>
            </div>
          </div>
        </div>

        <!-- Carte Retards -->
        <div class="kpi-card" @click="goToModule('retards')">
          <div class="kpi-icon retards">
            <i class="bi bi-clock-history"></i>
          </div>
          <div class="kpi-content">
            <h3>Retards</h3>
            <div class="kpi-value">{{ retardsStore.totalHeuresARattraper.toFixed(1) }}h</div>
            <div class="kpi-detail">
              <span class="badge info">{{ retardsStore.retardsEnCours.length }} en cours</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ========== SECTION MANAGER/ADMIN ========== -->
      <template v-if="isManagerOrAbove">
        <!-- Demandes en attente de validation -->
        <div class="dashboard-section">
          <div class="section-header">
            <h2>
              <i class="bi bi-bell"></i>
              Validations en attente
              <span v-if="totalPending > 0" class="section-badge">{{ totalPending }}</span>
            </h2>
            <button class="btn-view-all" @click="viewAllPending">Tout voir</button>
          </div>

          <div v-if="pendingRequests.length === 0" class="empty-state">
            <i class="bi bi-check2-circle empty-icon"></i>
            <p>Aucune demande en attente de validation</p>
          </div>

          <div v-else class="pending-grid">
            <div v-for="request in pendingRequests" :key="request.id" class="pending-card" :class="request.type">
              <div class="pending-header">
                <span class="pending-type">{{ request.typeLabel }}</span>
                <span class="pending-date">{{ formatRelativeDate(request.date) }}</span>
              </div>
              <div class="pending-user">
                <div class="user-avatar">{{ getInitials(request.user.display_name) }}</div>
                <div class="user-info">
                  <p class="user-name">{{ request.user.display_name }}</p>
                  <p class="user-meta">{{ request.user.username.toUpperCase() }} • {{ request.user.equipe_nom }}</p>
                </div>
              </div>
              <div class="pending-details">
                <p v-if="request.details" class="details-text">{{ request.details }}</p>
                <p v-if="request.duree" class="details-duree"><i class="bi bi-clock"></i> {{ request.duree }}</p>
              </div>
              <div class="pending-actions">
                <button class="btn-approve" @click="approveRequest(request)">Approuver</button>
                <button class="btn-reject" @click="rejectRequest(request)">Refuser</button>
                <button class="btn-view" @click="viewRequest(request)">Détails</button>
              </div>
            </div>
          </div>
        </div>

        <!-- Graphiques pour managers/admin -->
        <div class="charts-grid">
          <!-- Évolution mensuelle des absences -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>Évolution des absences</h3>
              <select v-model="selectedYear" class="chart-filter">
                <option v-for="year in availableYears" :key="year" :value="year">{{ year }}</option>
              </select>
            </div>
            <div class="chart-container">
              <canvas ref="monthlyChart"></canvas>
            </div>
          </div>

          <!-- Répartition par type -->
          <div class="chart-card">
            <div class="chart-header">
              <h3>Répartition par type</h3>
            </div>
            <div class="chart-container">
              <canvas ref="typeChart"></canvas>
            </div>
          </div>

          <!-- Top retardataires (pour managers) -->
          <div class="chart-card" v-if="isManagerOrAdmin">
            <div class="chart-header">
              <h3>Top retardataires</h3>
            </div>
            <div class="top-list">
              <div v-for="(item, index) in topRetards" :key="item.user.id" class="top-item">
                <span class="top-rank">{{ index + 1 }}</span>
                <div class="top-user">
                  <span class="top-name">{{ item.user.display_name }}</span>
                  <span class="top-equipe">{{ item.user.equipe_nom }}</span>
                </div>
                <span class="top-value">{{ item.totalHeures.toFixed(1) }}h</span>
              </div>
            </div>
          </div>

          <!-- Heures à rattraper par équipe (pour admin) -->
          <div class="chart-card" v-if="isAdmin">
            <div class="chart-header">
              <h3>Heures à rattraper par équipe</h3>
            </div>
            <div class="team-stats">
              <div v-for="stat in teamRattrapage" :key="stat.equipe_id" class="team-stat">
                <div class="team-info">
                  <span class="team-name">{{ stat.equipe_nom }}</span>
                  <span class="team-value">{{ stat.totalHeures.toFixed(1) }}h</span>
                </div>
                <div class="progress-bar">
                  <div class="progress-fill" :style="{ width: stat.percentage + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>

      <!-- ========== SECTION UTILISATEUR SIMPLE ========== -->
      <template v-else>
        <div class="dashboard-sections">
          <!-- Mes demandes en cours -->
          <div class="dashboard-section">
            <div class="section-header">
              <h2><i class="bi bi-hourglass-split"></i> Mes demandes en cours</h2>
              <button class="btn-view-all" @click="viewMyRequests">Tout voir</button>
            </div>

            <div v-if="myPendingRequests.length === 0" class="empty-state">
              <i class="bi bi-check-circle empty-icon"></i>
              <p>Aucune demande en cours</p>
            </div>

            <div v-else class="requests-list">
              <div v-for="request in myPendingRequests" :key="request.id" class="request-item" :class="request.type">
                <div class="request-header">
                  <span class="request-type">{{ request.typeLabel }}</span>
                  <span class="request-status" :class="request.statut">{{ request.statutLabel }}</span>
                </div>
                <div class="request-body">
                  <span class="request-date">{{ formatDate(request.date) }}</span>
                  <span v-if="request.duree" class="request-duree">{{ request.duree }}</span>
                </div>
                <button class="btn-view" @click="viewRequest(request)">Voir détails</button>
              </div>
            </div>
          </div>

          <!-- Calendrier personnel -->
          <div class="dashboard-section">
            <div class="section-header">
              <h2><i class="bi bi-calendar"></i> Mon calendrier</h2>
              <button class="btn-view-all" @click="goToModule('calendrier')">Voir tout</button>
            </div>
            <div class="mini-calendar">
              <Calendar
                :events="myCalendarEvents"
                :blocked-dates="blockedDates"
                :default-view="'month'"
                height="300px"
                @event-click="onEventClick"
              />
            </div>
          </div>

          <!-- Alertes personnelles -->
          <div class="dashboard-section" v-if="myAlerts.length > 0">
            <div class="section-header">
              <h2><i class="bi bi-exclamation-triangle"></i> Alertes</h2>
            </div>
            <div class="alerts-list">
              <div v-for="alert in myAlerts" :key="alert.id" class="alert-item" :class="alert.severity">
                <i class="bi" :class="alert.icon"></i>
                <span class="alert-message">{{ alert.message }}</span>
                <button class="btn-action" @click="handleAlert(alert)">Agir</button>
              </div>
            </div>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useRetardsStore } from '@/store/retards'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import { format, parseISO, differenceInDays, getYear, startOfMonth, endOfMonth, eachMonthOfInterval, subMonths } from 'date-fns'
import { fr } from 'date-fns/locale/fr'
import Chart from 'chart.js/auto'

// ========== STORES ==========
const authStore = useAuthStore()
const congesStore = useCongesStore()
const ostieStore = useOstieStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const retardsStore = useRetardsStore()
const filtersStore = useFiltersStore()

const router = useRouter()

// ========== STATE ==========
const loading = ref(true)
const hasData = ref(false)
const selectedYear = ref(getYear(new Date()))
const availableYears = ref<number[]>([])

// Références pour les graphiques
const monthlyChart = ref<HTMLCanvasElement | null>(null)
const typeChart = ref<HTMLCanvasElement | null>(null)
let monthlyChartInstance: Chart | null = null
let typeChartInstance: Chart | null = null

// ========== COMPUTED RÔLES ==========
const userRole = computed(() => {
  if (!authStore.user) return 'Visiteur'
  if (authStore.isSuperAdmin) return 'Super Administrateur'
  if (authStore.isStaff) return 'Administrateur'
  if (authStore.isManager) return 'Manager'
  if (authStore.isCoManager) return 'Co-manager'
  return 'Utilisateur'
})

const roleClass = computed(() => {
  const roles: Record<string, string> = {
    'Super Administrateur': 'superadmin',
    'Administrateur': 'admin',
    'Manager': 'manager',
    'Co-manager': 'comanager',
    'Utilisateur': 'user'
  }
  return roles[userRole.value] || 'user'
})

const isManagerOrAbove = computed(() => 
  authStore.isManager || authStore.isCoManager || authStore.isStaff || authStore.isSuperAdmin
)

const isManagerOrAdmin = computed(() => 
  authStore.isManager || authStore.isCoManager || authStore.isStaff
)

const isAdmin = computed(() => 
  authStore.isStaff || authStore.isSuperAdmin
)

// ========== COMPUTED WELCOME ==========
const welcomeMessage = computed(() => {
  if (!authStore.user) return 'Bienvenue sur votre espace personnel'
  
  const hour = new Date().getHours()
  const greeting = hour < 12 ? 'Bonjour' : hour < 18 ? 'Bon après-midi' : 'Bonsoir'
  
  if (isManagerOrAbove.value) {
    return `${greeting} ${authStore.user.display_name}, voici un résumé de votre équipe et des validations en attente.`
  }
  return `${greeting} ${authStore.user.display_name}, voici un aperçu de vos informations.`
})

const currentDate = computed(() => {
  return format(new Date(), 'EEEE d MMMM yyyy', { locale: fr })
})

// ========== COMPTAGE DES DEMANDES ==========
const pendingCounts = computed(() => {
  // À implémenter selon tes stores
  return {
    conges: congesStore.conges?.filter((c: any) => c.statut === 'en_attente').length || 0,
    ostie: ostieStore.ostiesEnAttente?.length || 0,
    permissions: permissionsStore.permissionsRetournees?.length || 0,
    repos: reposStore.reposEnAttente?.length || 0,
    retards: retardsStore.retardsEnCours?.length || 0
  }
})

const totalPending = computed(() => {
  const counts = pendingCounts.value
  return counts.conges + counts.ostie + counts.permissions + counts.repos + counts.retards
})

// ========== DEMANDES EN ATTENTE (POUR MANAGERS) ==========
const pendingRequests = computed(() => {
  const requests: any[] = []
  
  // Congés en attente (si l'utilisateur peut les gérer)
  if (congesStore.conges) {
    congesStore.conges
      .filter((c: any) => c.statut === 'en_attente' && congesStore.canManageThisConge(c))
      .forEach((c: any) => {
        requests.push({
          id: `conge_${c.id}`,
          type: 'conge',
          typeLabel: 'Congé',
          statut: c.statut,
          date: c.date_creation,
          user: c.utilisateur_details,
          details: `${c.type_conge_display} • ${formatDate(c.date_debut)} → ${formatDate(c.date_fin)}`,
          duree: `${c.jours_deduits}j`,
          data: c
        })
      })
  }
  
  // OSTIE en attente
  if (ostieStore.ostiesEnAttente) {
    ostieStore.ostiesEnAttente
      .filter((o: any) => ostieStore.canManageThisOstie(o))
      .forEach((o: any) => {
        requests.push({
          id: `ostie_${o.id}`,
          type: 'ostie',
          typeLabel: 'OSTIE',
          statut: o.statut,
          date: o.date_creation,
          user: o.utilisateur_details,
          details: o.motif || 'Sans motif',
          duree: `${formatTime(o.heure_debut)}`,
          data: o
        })
      })
  }
  
  // Permissions retournées (en attente de rattrapage)
  if (permissionsStore.permissionsRetournees) {
    permissionsStore.permissionsRetournees
      .filter((p: any) => permissionsStore.canManageThisPermission(p))
      .forEach((p: any) => {
        requests.push({
          id: `perm_${p.id}`,
          type: 'permission',
          typeLabel: 'Permission',
          statut: p.statut,
          date: p.date,
          user: p.utilisateur_details,
          details: p.motif,
          duree: `${p.heures_restantes}h restantes`,
          data: p
        })
      })
  }
  
  // Repos médicaux en attente
  if (reposStore.reposEnAttente) {
    reposStore.reposEnAttente
      .filter((r: any) => reposStore.canManageThisRepos(r))
      .forEach((r: any) => {
        requests.push({
          id: `repos_${r.id}`,
          type: 'repos',
          typeLabel: 'Repos médical',
          statut: r.statut,
          date: r.date_creation,
          user: r.utilisateur_details,
          details: r.motif || 'Malade',
          duree: `${r.duree_heures}h`,
          data: r
        })
      })
  }
  
  // Retards en cours
  if (retardsStore.retardsEnCours) {
    retardsStore.retardsEnCours
      .filter((r: any) => retardsStore.canManageThisRetard(r))
      .forEach((r: any) => {
        requests.push({
          id: `retard_${r.id}`,
          type: 'retard',
          typeLabel: 'Retard',
          statut: r.statut,
          date: r.date,
          user: r.utilisateur_details,
          details: r.motif_retard,
          duree: `${r.heures_restantes}h restantes`,
          data: r
        })
      })
  }
  
  // Trier par date (plus récent d'abord)
  return requests.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

// ========== MES DEMANDES EN COURS (UTILISATEUR SIMPLE) ==========
const myPendingRequests = computed(() => {
  const requests: any[] = []
  
  // Mes congés en attente
  if (congesStore.mesConges) {
    congesStore.mesConges
      .filter((c: any) => c.statut === 'en_attente')
      .forEach((c: any) => {
        requests.push({
          id: `conge_${c.id}`,
          type: 'conge',
          typeLabel: 'Congé',
          statut: c.statut,
          statutLabel: 'En attente',
          date: c.date_debut,
          duree: `${c.jours_deduits}j`,
          data: c
        })
      })
  }
  
  // Mes OSTIE en attente
  // À adapter selon ton store OSTIE
  if (ostieStore.mesOsties) {
    ostieStore.mesOsties
      .filter((o: any) => o.statut === 'en_attente')
      .forEach((o: any) => {
        requests.push({
          id: `ostie_${o.id}`,
          type: 'ostie',
          typeLabel: 'OSTIE',
          statut: o.statut,
          statutLabel: 'En attente',
          date: o.date,
          duree: formatTime(o.heure_debut),
          data: o
        })
      })
  }
  
  return requests.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
})

// ========== MES ALERTES ==========
const myAlerts = computed(() => {
  const alerts: any[] = []
  
  // Alertes pour les permissions à retourner
  if (permissionsStore.mesPermissions) {
    permissionsStore.mesPermissions
      .filter((p: any) => p.statut === 'en_attente' && new Date(p.date) < new Date())
      .forEach((p: any) => {
        alerts.push({
          id: `perm_retour_${p.id}`,
          severity: 'warning',
          icon: 'bi-door-open',
          message: `Permission du ${formatDate(p.date)} - Retour non enregistré`,
          action: 'retour',
          data: p
        })
      })
  }
  
  // Alertes pour les retards non rattrapés
  if (retardsStore.mesRetards) {
    retardsStore.mesRetards
      .filter((r: any) => r.statut !== 'approuve' && r.statut !== 'annule')
      .forEach((r: any) => {
        alerts.push({
          id: `retard_${r.id}`,
          severity: r.statut === 'en_cours' ? 'info' : 'danger',
          icon: 'bi-clock-history',
          message: `Retard du ${formatDate(r.date)} - ${r.heures_restantes}h à rattraper`,
          action: 'rattrapage',
          data: r
        })
      })
  }
  
  return alerts
})

// ========== TOP RETARDS (POUR MANAGERS) ==========
const topRetards = computed(() => {
  if (!retardsStore.retards || !authStore.user?.equipe) return []
  
  // Grouper par utilisateur et calculer total heures
  const userMap = new Map()
  
  retardsStore.retards.forEach((retard: any) => {
    if (retard.utilisateur_details?.equipe_id === authStore.user?.equipe?.id) {
      const userId = retard.utilisateur
      const heures = parseFloat(retard.heures_a_rattraper) || 0
      
      if (!userMap.has(userId)) {
        userMap.set(userId, {
          user: retard.utilisateur_details,
          totalHeures: 0
        })
      }
      userMap.get(userId).totalHeures += heures
    }
  })
  
  return Array.from(userMap.values())
    .sort((a, b) => b.totalHeures - a.totalHeures)
    .slice(0, 5)
})

// ========== STATS ÉQUIPE ==========
const teamRattrapage = computed(() => {
  // À implémenter selon tes données
  return []
})

// ========== CALENDRIER ==========
const myCalendarEvents = computed<CalendarEvent[]>(() => {
  const events: CalendarEvent[] = []
  
  // Ajouter mes congés
  if (congesStore.mesConges) {
    congesStore.mesConges.forEach((conge: any) => {
      events.push({
        id: `conge_${conge.id}`,
        title: `Congé ${conge.type_conge_display}`,
        start: conge.date_debut,
        end: conge.date_fin,
        type: 'conge',
        statut: conge.statut,
        color: getEventColor(conge.statut)
      })
    })
  }
  
  return events
})

const blockedDates = computed(() => {
  return congesStore.calendrierEvents
    .filter((e: any) => e.isBlocked && e.type !== 'weekend')
    .flatMap((e: any) => {
      const dates: Date[] = []
      const start = new Date(e.start)
      const end = e.end ? new Date(e.end) : start
      let current = new Date(start)
      while (current <= end) {
        dates.push(new Date(current))
        current.setDate(current.getDate() + 1)
      }
      return dates
    })
})

// ========== GRAPHIQUES ==========
const initCharts = async () => {
  // Attendre que les données soient chargées
  await loadChartData()
  
  // Détruire les instances existantes
  if (monthlyChartInstance) monthlyChartInstance.destroy()
  if (typeChartInstance) typeChartInstance.destroy()
  
  // Graphique mensuel
  if (monthlyChart.value) {
    monthlyChartInstance = new Chart(monthlyChart.value, {
      type: 'line',
      data: monthlyChartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: { beginAtZero: true }
        }
      }
    })
  }
  
  // Graphique de répartition
  if (typeChart.value) {
    typeChartInstance = new Chart(typeChart.value, {
      type: 'doughnut',
      data: typeChartData.value,
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: 'bottom' }
        }
      }
    })
  }
}

const monthlyChartData = computed(() => {
  // À remplacer par tes données réelles
  const months = eachMonthOfInterval({
    start: subMonths(new Date(), 5),
    end: new Date()
  })
  
  return {
    labels: months.map(m => format(m, 'MMM', { locale: fr })),
    datasets: [
      {
        label: 'Congés',
        data: [5, 7, 4, 6, 3, 8],
        borderColor: '#3498db',
        backgroundColor: 'rgba(52, 152, 219, 0.1)',
        tension: 0.4
      },
      {
        label: 'OSTIE',
        data: [2, 3, 1, 4, 2, 3],
        borderColor: '#e74c3c',
        backgroundColor: 'rgba(231, 76, 60, 0.1)',
        tension: 0.4
      }
    ]
  }
})

const typeChartData = computed(() => {
  return {
    labels: ['Congés', 'OSTIE', 'Permissions', 'Repos', 'Retards'],
    datasets: [
      {
        data: [
          pendingCounts.value.conges,
          pendingCounts.value.ostie,
          pendingCounts.value.permissions,
          pendingCounts.value.repos,
          pendingCounts.value.retards
        ],
        backgroundColor: [
          '#3498db',
          '#e74c3c',
          '#f39c12',
          '#2ecc71',
          '#9b59b6'
        ]
      }
    ]
  }
})

// ========== UTILITAIRES ==========
const getInitials = (name: string) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

const formatDate = (dateStr: string) => {
  if (!dateStr) return ''
  return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: fr })
}

const formatRelativeDate = (dateStr: string) => {
  const date = parseISO(dateStr)
  const diff = differenceInDays(new Date(), date)
  
  if (diff === 0) return "Aujourd'hui"
  if (diff === 1) return 'Hier'
  if (diff < 7) return `Il y a ${diff} jours`
  return format(date, 'dd MMM', { locale: fr })
}

const formatTime = (timeStr: string) => {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

const getEventColor = (statut: string) => {
  const colors: Record<string, string> = {
    approuve: '#2ecc71',
    en_attente: '#f39c12',
    refuse: '#e74c3c',
    annule: '#95a5a6'
  }
  return colors[statut] || '#3498db'
}

// ========== ACTIONS ==========
const goToModule = (module: string) => {
  router.push(`/${module}`)
}

const viewAllPending = () => {
  router.push('/approvals')
}

const viewRequest = (request: any) => {
  // Rediriger vers les détails selon le type
  const [type, id] = request.id.split('_')
  router.push(`/${type}s/${id}`)
}

const approveRequest = async (request: any) => {
  // Implémenter la logique d'approbation
  console.log('Approuver:', request)
}

const rejectRequest = async (request: any) => {
  // Implémenter la logique de refus
  console.log('Refuser:', request)
}

const viewMyRequests = () => {
  router.push('/my-requests')
}

const handleAlert = (alert: any) => {
  if (alert.action === 'retour') {
    router.push(`/permissions/${alert.data.id}?action=retour`)
  } else if (alert.action === 'rattrapage') {
    router.push(`/retards/${alert.data.id}?action=rattrapage`)
  }
}

const onEventClick = (event: CalendarEvent) => {
  const [type, id] = String(event.id).split('_')
  router.push(`/${type}s/${id}`)
}

// ========== CHARGEMENT DES DONNÉES ==========
const loadChartData = async () => {
  // Simuler chargement des données pour les graphiques
  await new Promise(resolve => setTimeout(resolve, 100))
}

const refreshAllData = async () => {
  loading.value = true
  
  const currentYear = getYear(new Date())
  const promises = []
  
  promises.push(congesStore.fetchCalendrier({ annee: currentYear }))
  promises.push(congesStore.fetchMesConges(currentYear))
  
  if (isManagerOrAbove.value) {
    promises.push(ostieStore.fetchCalendrier({ annee: currentYear }))
    promises.push(permissionsStore.fetchCalendrier({ annee: currentYear }))
    promises.push(reposStore.fetchCalendrier({ annee: currentYear }))
    promises.push(retardsStore.fetchCalendrier({ annee: currentYear }))
  }
  
  await Promise.all(promises)
  
  // Recalculer les années disponibles
  const years = new Set<number>()
  if (congesStore.conges) {
    congesStore.conges.forEach((c: any) => {
      years.add(getYear(parseISO(c.date_creation)))
    })
  }
  availableYears.value = Array.from(years).sort((a, b) => b - a)
  
  loading.value = false
  hasData.value = true
  
  // Réinitialiser les graphiques
  await initCharts()
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshAllData()
})

onUnmounted(() => {
  if (monthlyChartInstance) monthlyChartInstance.destroy()
  if (typeChartInstance) typeChartInstance.destroy()
})

// Surveiller le changement d'année pour les graphiques
watch(selectedYear, () => {
  initCharts()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1600px;
  margin: 0 auto;
}

/* En-tête */
.page-header {
  margin-bottom: 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 0.5rem;
}

.page-header h1 {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 2rem;
  color: #2c3e50;
}

.role-badge {
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  color: white;
}

.role-badge.superadmin { background: linear-gradient(135deg, #8e44ad, #9b59b6); }
.role-badge.admin { background: linear-gradient(135deg, #3498db, #2980b9); }
.role-badge.manager { background: linear-gradient(135deg, #2ecc71, #27ae60); }
.role-badge.comanager { background: linear-gradient(135deg, #f39c12, #e67e22); }
.role-badge.user { background: linear-gradient(135deg, #95a5a6, #7f8c8d); }

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.welcome-date {
  color: #7f8c8d;
  font-size: 1rem;
  text-transform: capitalize;
}

.welcome-message {
  color: #34495e;
  font-size: 1.1rem;
  font-weight: 500;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  color: #2c3e50;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-refresh:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Loading state */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem;
  color: #7f8c8d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

/* KPI Grid */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.kpi-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
  cursor: pointer;
  transition: all 0.3s ease;
}

.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #dbeafe;
}

.kpi-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  flex-shrink: 0;
}

.kpi-icon.conges { 
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1565c0;
}
.kpi-icon.ostie { 
  background: linear-gradient(135deg, #fce4ec, #f48fb1);
  color: #ad1457;
}
.kpi-icon.permissions { 
  background: linear-gradient(135deg, #fff3e0, #ffcc80);
  color: #ef6c00;
}
.kpi-icon.repos { 
  background: linear-gradient(135deg, #e8f5e9, #a5d6a7);
  color: #2e7d32;
}
.kpi-icon.retards { 
  background: linear-gradient(135deg, #e1f5fe, #81d4fa);
  color: #0277bd;
}

.kpi-content {
  flex: 1;
}

.kpi-content h3 {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.kpi-value {
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1.2;
  margin-bottom: 0.25rem;
}

.kpi-detail {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
}

.badge.pris { background: #e8f5e9; color: #2e7d32; }
.badge.warning { background: #fff3e0; color: #ef6c00; }
.badge.info { background: #e1f5fe; color: #0277bd; }

/* Sections */
.dashboard-section {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section-header h2 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.section-badge {
  background: #e74c3c;
  color: white;
  font-size: 0.8rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  margin-left: 0.5rem;
}

.btn-view-all {
  background: none;
  border: none;
  color: #3498db;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-view-all:hover {
  background: #f0f8ff;
}

/* Pending Grid */
.pending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1rem;
}

.pending-card {
  background: white;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #eef2f7;
  transition: all 0.2s;
}

.pending-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-color: #dbeafe;
}

.pending-card.conge { border-left: 4px solid #3498db; }
.pending-card.ostie { border-left: 4px solid #e74c3c; }
.pending-card.permission { border-left: 4px solid #f39c12; }
.pending-card.repos { border-left: 4px solid #2ecc71; }
.pending-card.retard { border-left: 4px solid #9b59b6; }

.pending-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.pending-type {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  background: #f8f9fa;
  color: #2c3e50;
}

.pending-date {
  font-size: 0.7rem;
  color: #95a5a6;
}

.pending-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.user-avatar {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.user-info {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 0.1rem;
}

.user-meta {
  font-size: 0.7rem;
  color: #95a5a6;
}

.pending-details {
  margin-bottom: 1rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.details-text {
  font-size: 0.9rem;
  color: #34495e;
  margin-bottom: 0.25rem;
}

.details-duree {
  font-size: 0.8rem;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.pending-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-approve {
  background: #2ecc71;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
}

.btn-approve:hover {
  background: #27ae60;
}

.btn-reject {
  background: #e74c3c;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  flex: 1;
  transition: all 0.2s;
}

.btn-reject:hover {
  background: #c0392b;
}

.btn-view {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-view:hover {
  background: #2980b9;
}

/* Charts */
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  color: #2c3e50;
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
}

.chart-filter {
  padding: 0.4rem;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  background: white;
  font-size: 0.8rem;
  color: #2c3e50;
}

.chart-container {
  height: 300px;
  position: relative;
}

/* Top list */
.top-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.top-rank {
  width: 24px;
  height: 24px;
  background: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  font-weight: 600;
}

.top-user {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-name {
  font-weight: 600;
  color: #2c3e50;
}

.top-equipe {
  font-size: 0.7rem;
  color: #95a5a6;
}

.top-value {
  font-weight: 600;
  color: #e74c3c;
}

/* Team stats */
.team-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.team-stat {
  width: 100%;
}

.team-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.25rem;
  font-size: 0.9rem;
}

.team-name {
  color: #2c3e50;
  font-weight: 500;
}

.team-value {
  font-weight: 600;
  color: #3498db;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: #ecf0f1;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #3498db, #2ecc71);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* Requests list pour utilisateur */
.requests-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.request-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid transparent;
}

.request-item.conge { border-left-color: #3498db; }
.request-item.ostie { border-left-color: #e74c3c; }
.request-item.permission { border-left-color: #f39c12; }
.request-item.repos { border-left-color: #2ecc71; }
.request-item.retard { border-left-color: #9b59b6; }

.request-header {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 120px;
}

.request-type {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  background: white;
  border-radius: 12px;
  display: inline-block;
  width: fit-content;
}

.request-status {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  display: inline-block;
  width: fit-content;
}

.request-status.en_attente {
  background: #fff3e0;
  color: #ef6c00;
}

.request-status.approuve {
  background: #e8f5e9;
  color: #2e7d32;
}

.request-body {
  flex: 1;
  display: flex;
  gap: 1rem;
  align-items: center;
}

.request-date {
  color: #7f8c8d;
  font-size: 0.9rem;
}

.request-duree {
  background: white;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  color: #2c3e50;
}

/* Mini calendrier */
.mini-calendar {
  height: 300px;
  overflow: hidden;
}

/* Alertes */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid;
}

.alert-item.warning {
  border-left-color: #f39c12;
  background: #fff3e0;
}

.alert-item.danger {
  border-left-color: #e74c3c;
  background: #fdeded;
}

.alert-item.info {
  border-left-color: #3498db;
  background: #e1f5fe;
}

.alert-item i {
  font-size: 1.2rem;
}

.alert-message {
  flex: 1;
  font-size: 0.9rem;
  color: #2c3e50;
}

.btn-action {
  background: #3498db;
  color: white;
  border: none;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-action:hover {
  background: #2980b9;
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #95a5a6;
}

.empty-icon {
  font-size: 2.5rem;
  display: block;
  margin-bottom: 0.5rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .kpi-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
    flex-wrap: wrap;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .pending-grid {
    grid-template-columns: 1fr;
  }
  
  .pending-actions {
    flex-wrap: wrap;
  }
  
  .request-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .request-header {
    width: 100%;
    flex-direction: row;
    justify-content: space-between;
  }
  
  .request-body {
    width: 100%;
    justify-content: space-between;
  }
  
  .alert-item {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .request-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .request-body {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .btn-view {
    width: 100%;
  }
}
</style>