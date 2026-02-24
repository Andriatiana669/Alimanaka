<!-- frontend/src/views/Dashboard.vue -->
<template>
  <AppLayout>
  <div class="dashboard">
    <!-- En-tête de la page -->
    <div class="page-header">
      <h1>Tableau de bord</h1>
      <p class="welcome">Bienvenue, {{ fullName }}</p>
    </div>

    <!-- Grille de statistiques -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon conges">📅</div>
        <div class="stat-info">
          <h3>Congés</h3>
          <p class="stat-value">{{ stats.leaves }}</p>
          <span class="stat-label">Jours disponibles</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon retard">⏰</div>
        <div class="stat-info">
          <h3>Retards</h3>
          <p class="stat-value">{{ stats.lates }}</p>
          <span class="stat-label">Ce mois</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon equipe">👥</div>
        <div class="stat-info">
          <h3>Équipe</h3>
          <p class="stat-value">{{ stats.teamMembers }}</p>
          <span class="stat-label">Membres</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon ostie">🏥</div>
        <div class="stat-info">
          <h3>OSTIE</h3>
          <p class="stat-value" :class="{ 'active': stats.ostieActive }">
            {{ stats.ostieActive ? 'Actif' : 'Inactif' }}
          </p>
          <span class="stat-label">Statut</span>
        </div>
      </div>
    </div>

    <!-- Sections du dashboard -->
    <div class="dashboard-sections">
      <div class="section">
        <div class="section-header">
          <h2>Activités récentes</h2>
          <button class="btn-view-all" @click="viewAllActivities">Tout voir</button>
        </div>
        <div class="activity-list">
          <div 
            v-for="activity in recentActivities" 
            :key="activity.id"
            class="activity-item"
          >
            <span class="activity-date">{{ formatDate(activity.date) }}</span>
            <span class="activity-text">{{ activity.text }}</span>
            <span class="activity-type" :class="activity.type">{{ activity.typeLabel }}</span>
          </div>
          <div v-if="recentActivities.length === 0" class="empty-state">
            <span class="empty-icon">📊</span>
            <p>Aucune activité récente</p>
          </div>
        </div>
      </div>

      <div class="section">
        <div class="section-header">
          <h2>En attente d'approbation</h2>
          <button class="btn-view-all" @click="viewAllPending">Tout voir</button>
        </div>
        <div class="pending-list">
          <div 
            v-for="item in pendingApprovals" 
            :key="item.id"
            class="pending-item"
          >
            <span class="pending-type" :class="item.type">{{ item.typeLabel }}</span>
            <span class="pending-details">{{ item.details }}</span>
            <button class="btn-action" @click="viewPendingItem(item)">Voir</button>
          </div>
          <div v-if="pendingApprovals.length === 0" class="empty-state">
            <span class="empty-icon">✅</span>
            <p>Aucun élément en attente</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Graphiques ou informations supplémentaires -->
    <div class="charts-container">
      <div class="chart-card">
        <div class="chart-header">
          <h3>Congés par mois</h3>
          <select v-model="selectedMonthRange" class="chart-filter">
            <option value="6">6 derniers mois</option>
            <option value="12">12 derniers mois</option>
            <option value="24">2 ans</option>
          </select>
        </div>
        <div class="chart-placeholder">
          <div class="chart-bars">
            <div 
              v-for="(month, index) in leaveStats.months" 
              :key="index"
              class="bar"
              :style="{
                height: `${month.value}%`,
                backgroundColor: getBarColor(index)
              }"
              :title="`${month.label}: ${month.count} congés`"
            ></div>
          </div>
          <div class="chart-labels">
            <span v-for="month in leaveStats.months" :key="month.label">{{ month.label }}</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="chart-header">
          <h3>Répartition par équipe</h3>
          <select v-model="selectedTeamView" class="chart-filter">
            <option value="department">Par département</option>
            <option value="role">Par rôle</option>
            <option value="status">Par statut</option>
          </select>
        </div>
        <div class="chart-placeholder">
          <div class="pie-chart">
            <div 
              v-for="(segment, index) in teamDistribution" 
              :key="segment.label"
              class="pie-segment"
              :style="{
                '--percentage': segment.percentage,
                '--color': getSegmentColor(index)
              }"
            ></div>
          </div>
          <div class="chart-legend">
            <div 
              v-for="(segment, index) in teamDistribution" 
              :key="segment.label"
              class="legend-item"
            >
              <span 
                class="legend-color" 
                :style="{ backgroundColor: getSegmentColor(index) }"
              ></span>
              <span>{{ segment.label }} ({{ segment.percentage }}%)</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="quick-actions">
      <h3>Actions rapides</h3>
      <div class="actions-grid">
        <button class="action-btn" @click="requestLeave">
          <span class="action-icon">📝</span>
          <span>Demander un congé</span>
        </button>
        <button class="action-btn" @click="reportLate">
          <span class="action-icon">⏰</span>
          <span>Signaler un retard</span>
        </button>
        <button class="action-btn" @click="updateProfile">
          <span class="action-icon">👤</span>
          <span>Mettre à jour mon profil</span>
        </button>
        <button class="action-btn" @click="viewTeam" v-if="isAdmin">
          <span class="action-icon">👥</span>
          <span>Voir mon équipe</span>
        </button>
      </div>
    </div>
  </div>
</AppLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import MainLayout from '../components/Layout/AppLayout.vue'

const router = useRouter()
const { user, isAdmin } = useAuth()

// État local
const selectedMonthRange = ref('6')
const selectedTeamView = ref('department')
const loading = ref(false)

// Données mockées (à remplacer par des appels API)
const stats = ref({
  leaves: 12,
  lates: 2,
  teamMembers: 8,
  ostieActive: true
})

const recentActivities = ref([
  { id: 1, date: new Date(), text: 'Demande de congé approuvée', type: 'success', typeLabel: 'Approuvé' },
  { id: 2, date: new Date(Date.now() - 86400000), text: 'Mise à jour du profil', type: 'info', typeLabel: 'Info' },
  { id: 3, date: new Date(Date.now() - 86400000 * 2), text: 'Retard signalé', type: 'warning', typeLabel: 'Retard' },
  { id: 4, date: new Date(Date.now() - 86400000 * 4), text: 'Nouveau membre d\'équipe', type: 'success', typeLabel: 'Nouveau' }
])

const pendingApprovals = ref([
  { id: 1, type: 'leave', typeLabel: 'Congé', details: 'Jean Dupuis - 3 jours' },
  { id: 2, type: 'permission', typeLabel: 'Permission', details: 'Marie Curie - 2h' }
])

const leaveStats = ref({
  months: [
    { label: 'Jan', count: 5, value: 60 },
    { label: 'Fév', count: 7, value: 80 },
    { label: 'Mar', count: 4, value: 45 },
    { label: 'Avr', count: 6, value: 70 },
    { label: 'Mai', count: 3, value: 35 },
    { label: 'Jun', count: 8, value: 90 }
  ]
})

const teamDistribution = ref([
  { label: 'Équipe A', percentage: 40 },
  { label: 'Équipe B', percentage: 25 },
  { label: 'Équipe C', percentage: 20 },
  { label: 'Équipe D', percentage: 15 }
])

// Computed properties
const fullName = computed(() => {
  if (!user.value) return ''
  return user.value.display_name || `${user.value.last_name} ${user.value.first_name}`
})

// Méthodes
const formatDate = (date: Date) => {
  const now = new Date()
  const diffTime = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
  
  if (diffDays === 0) return 'Aujourd\'hui'
  if (diffDays === 1) return 'Hier'
  if (diffDays < 7) return `Il y a ${diffDays} jours`
  
  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })
}

const getBarColor = (index: number) => {
  const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
  return colors[index % colors.length]
}

const getSegmentColor = (index: number) => {
  const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6', '#1abc9c']
  return colors[index % colors.length]
}

const viewAllActivities = () => {
  router.push('/activities') // Tu devras créer cette route
}

const viewAllPending = () => {
  router.push('/approvals') // Tu devras créer cette route
}

const viewPendingItem = (item: any) => {
  console.log('Voir élément:', item)
  // TODO: Implémenter la logique pour voir l'élément
}

const requestLeave = () => {
  router.push('/leaves/request') // Tu devras créer cette route
}

const reportLate = () => {
  console.log('Signaler un retard')
  // TODO: Implémenter la logique de signalement
}

const updateProfile = () => {
  router.push('/profile')
}

const viewTeam = () => {
  router.push('/team') // Tu devras créer cette route
}

// Fetch des données réelles
const fetchDashboardData = async () => {
  loading.value = true
  try {
    // TODO: Remplacer par des appels API réels
    // Exemple:
    // const response = await fetch('/api/dashboard/stats/')
    // stats.value = await response.json()
    
    // Simuler un délai de chargement
    await new Promise(resolve => setTimeout(resolve, 500))
    
  } catch (error) {
    console.error('Erreur lors du chargement du dashboard:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchDashboardData()
})
</script>

<style scoped>
.dashboard {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* En-tête de page */
.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome {
  color: #7f8c8d;
  font-size: 1.1rem;
  font-weight: 500;
}

/* Grille de statistiques */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  border: 1px solid #eef2f7;
  cursor: pointer;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #dbeafe;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.stat-icon.conges { 
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1565c0;
}

.stat-icon.retard { 
  background: linear-gradient(135deg, #fff3e0, #ffcc80);
  color: #ef6c00;
}

.stat-icon.equipe { 
  background: linear-gradient(135deg, #e8f5e9, #a5d6a7);
  color: #2e7d32;
}

.stat-icon.ostie { 
  background: linear-gradient(135deg, #fce4ec, #f48fb1);
  color: #ad1457;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.stat-value {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  line-height: 1.2;
}

.stat-value.active {
  color: #2e7d32;
}

.stat-label {
  color: #95a5a6;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Sections du dashboard */
.dashboard-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.section h2 {
  color: #2c3e50;
  font-size: 1.3rem;
  font-weight: 600;
  margin: 0;
}

.btn-view-all {
  background: none;
  border: none;
  color: #3498db;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  transition: all 0.2s;
}

.btn-view-all:hover {
  background-color: #f0f8ff;
}

/* Liste d'activités */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
  border-radius: 12px;
  border-left: 4px solid #3498db;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: linear-gradient(to right, #eef2f7, #f8f9fa);
  transform: translateX(4px);
}

.activity-date {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 600;
  min-width: 80px;
}

.activity-text {
  color: #2c3e50;
  font-weight: 500;
}

.activity-type {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.activity-type.success {
  background-color: #d4edda;
  color: #155724;
}

.activity-type.info {
  background-color: #d1ecf1;
  color: #0c5460;
}

.activity-type.warning {
  background-color: #fff3cd;
  color: #856404;
}

/* Liste en attente */
.pending-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pending-item {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background-color: #fff8e1;
  border-radius: 12px;
  border: 1px solid #ffecb3;
}

.pending-type {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
}

.pending-type.leave {
  background-color: #ff9800;
  color: white;
}

.pending-type.permission {
  background-color: #2196f3;
  color: white;
}

.pending-details {
  color: #5d4037;
  font-weight: 500;
}

.btn-action {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background-color: #2980b9;
  transform: scale(1.05);
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #95a5a6;
}

.empty-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin: 0;
}

/* Conteneur de graphiques */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.chart-card h3 {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: 600;
  margin: 0;
}

.chart-filter {
  padding: 0.5rem;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  background-color: white;
  font-size: 0.85rem;
  color: #2c3e50;
  outline: none;
}

.chart-filter:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* Placeholder graphique */
.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 120px;
  padding: 0 1rem;
}

.bar {
  width: 40px;
  border-radius: 8px 8px 0 0;
  transition: height 0.3s ease;
  cursor: pointer;
}

.bar:hover {
  opacity: 0.8;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  padding: 0.5rem 1rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Graphique circulaire */
.pie-chart {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto;
  background: conic-gradient(
    #3498db 0% 40%,
    #2ecc71 40% 65%,
    #e74c3c 65% 85%,
    #f39c12 85% 100%
  );
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #2c3e50;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

/* Quick actions */
.quick-actions {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.quick-actions h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.action-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem 1rem;
  background: linear-gradient(135deg, #f8f9fa, #ffffff);
  border: 1px solid #e1e8ed;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.1);
  border-color: #3498db;
  background: linear-gradient(135deg, #eef2f7, #f8f9fa);
}

.action-icon {
  font-size: 2rem;
}

.action-btn span:last-child {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .dashboard {
    padding: 1rem;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-sections {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .activity-date {
    order: 1;
  }
  
  .activity-text {
    order: 0;
  }
  
  .activity-type {
    order: 2;
    justify-self: start;
  }
  
  .pending-item {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }
  
  .btn-action {
    justify-self: start;
  }
  
  .actions-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .chart-filter {
    width: 100%;
  }
}
</style>