<template>
  <div class="dashboard">
    <!-- En-tête personnalisé selon le rôle -->
    <div class="dashboard-header">
      <div class="header-left">
        <h1>
          Bonjour, {{ displayName }}
          <span class="role-badge" :class="userRoleClass">{{ userRole }}</span>
        </h1>
        <p class="date-today">{{ currentDate }}</p>
      </div>
      <div class="header-right">
        <button class="btn-refresh" @click="refreshAllData" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          {{ loading ? 'Rafraîchissement...' : 'Actualiser' }}
        </button>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SÉLECTEUR DE VUE (Membre/Équipe/Global)    -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="view-selector-section">
      <div class="view-selector-header">
        <h3><i class="bi bi-funnel"></i> Filtrer la vue</h3>
        <button v-if="selectedView !== 'me'" class="btn-reset" @click="resetView">
          <i class="bi bi-x-circle"></i> Réinitialiser
        </button>
      </div>
      
      <div class="view-options">
        <!-- Vue personnelle -->
        <button 
          class="view-option" 
          :class="{ active: selectedView === 'me' }"
          @click="selectedView = 'me'"
        >
          <i class="bi bi-person"></i>
          <span>Ma vue</span>
        </button>

        <!-- Vue par équipe (si manager/co-manager) -->
        <div v-if="managedEquipes.length > 0" class="view-group">
          <span class="view-label">Mes équipes :</span>
          <div class="view-buttons">
            <button 
              v-for="equipe in managedEquipes" 
              :key="equipe.id"
              class="view-option"
              :class="{ active: selectedView === 'equipe-' + equipe.id }"
              @click="selectedView = 'equipe-' + equipe.id"
              :title="equipe.nom + (equipe.sous_equipes?.length ? ' + ' + countSubEquipes(equipe) + ' sous-équipes' : '')"
            >
              <i class="bi bi-people"></i>
              <span>{{ equipe.nom }}</span>
              <span v-if="equipe.sous_equipes?.length" class="sub-count">
                +{{ countSubEquipes(equipe) }}
              </span>
            </button>
          </div>
        </div>

        <!-- Vue par membre (si manager/co-manager) -->
        <div v-if="managedMembres.length > 0" class="view-group">
          <span class="view-label">Membres :</span>
          <div class="member-search">
            <i class="bi bi-search"></i>
            <input 
              v-model="memberSearchQuery"
              type="text"
              placeholder="Rechercher un membre..."
              class="member-search-input"
            />
          </div>
          <div class="view-buttons members-list">
            <button 
              v-for="membre in filteredManagedMembres" 
              :key="membre.id"
              class="view-option member"
              :class="{ active: selectedView === 'membre-' + membre.id }"
              @click="selectedView = 'membre-' + membre.id"
            >
              <div class="member-avatar">{{ getInitials(membre.display_name) }}</div>
              <div class="member-info">
                <span class="member-name">{{ membre.display_name }}</span>
                <span class="member-equipe">{{ membre.equipe_nom || 'Sans équipe' }}</span>
              </div>
            </button>
          </div>
        </div>
      </div>

      <!-- Indicateur de vue active -->
      <div class="current-view-indicator">
        <i class="bi bi-eye"></i>
        Vue actuelle : <strong>{{ currentViewLabel }}</strong>
        <span v-if="selectedView.startsWith('equipe-')" class="view-scope">
          (équipe + sous-équipes : {{ currentScopeEquipeIds.length }} équipes)
        </span>
        <span v-if="selectedView.startsWith('membre-')" class="view-scope">
          (membre individuel)
        </span>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- KPI CARDS - Adaptés selon la vue sélectionnée -->
    <!-- ============================================ -->
    <div class="kpi-grid">
      <!-- Carte Congés -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('conges') }" @click="goToModule('conges')">
        <div class="kpi-icon" style="background: #e3f2fd; color: #1976d2">
          <i class="bi bi-calendar-check"></i>
        </div>
        <div class="kpi-content">
          <h3>Congés</h3>
          <div class="kpi-value" :class="{ 'small-text': selectedView !== 'me' }">
            {{ congesKPI.solde }}j
          </div>
          <div class="kpi-detail" v-if="selectedView === 'me'">
            <span class="badge-success">{{ congesKPI.approuves }} approuvés</span>
            <span class="badge-warning">{{ congesKPI.enAttente }} en attente</span>
          </div>
          <div class="kpi-detail stacked" v-else>
            <span class="badge-success" title="Approuvés">{{ congesKPI.approuves }} ✓</span>
            <span class="badge-warning" title="En attente">{{ congesKPI.enAttente }} ⏳</span>
            <span class="badge-danger" title="Refusés">{{ congesKPI.refuses }} ✗</span>
            <span class="badge-secondary" title="Annulés">{{ congesKPI.annules }} ⊘</span>
          </div>
        </div>
      </div>

      <!-- Carte OSTIE -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('ostie') }" @click="goToModule('ostie')">
        <div class="kpi-icon" style="background: #fff3e0; color: #f57c00">
          <i class="bi bi-heart-pulse"></i>
        </div>
        <div class="kpi-content">
          <h3>OSTIE</h3>
          <div class="kpi-value">{{ ostieKPI.total }}</div>
          <div class="kpi-detail stacked">
            <span class="badge-warning" title="En attente">{{ ostieKPI.enAttente }} ⏳</span>
            <span class="badge-success" title="Approuvés">{{ ostieKPI.approuves }} ✓</span>
            <span class="badge-info" title="Transformés">{{ ostieKPI.transformes }} ↻</span>
            <span class="badge-secondary" title="Annulés">{{ ostieKPI.annules }} ⊘</span>
          </div>
        </div>
      </div>

      <!-- Carte Permissions -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('permissions') }" @click="goToModule('permissions')">
        <div class="kpi-icon" style="background: #e8f5e9; color: #388e3c">
          <i class="bi bi-door-open"></i>
        </div>
        <div class="kpi-content">
          <h3>Permissions</h3>
          <div class="kpi-value">{{ permissionsKPI.heures }}h</div>
          <div class="kpi-detail stacked">
            <span class="badge-warning" title="À rattraper">{{ permissionsKPI.rattrapage }} ⏳</span>
            <span class="badge-info" title="Retournées">{{ permissionsKPI.retournees }} ↩</span>
            <span class="badge-success" title="Approuvées">{{ permissionsKPI.approuves }} ✓</span>
            <span class="badge-secondary" title="Annulées">{{ permissionsKPI.annules }} ⊘</span>
          </div>
        </div>
      </div>

      <!-- Carte Repos Médicaux -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('repos') }" @click="goToModule('repos')">
        <div class="kpi-icon" style="background: #f3e5f5; color: #7b1fa2">
          <i class="bi bi-hospital"></i>
        </div>
        <div class="kpi-content">
          <h3>Repos médicaux</h3>
          <div class="kpi-value">{{ reposKPI.heures }}h</div>
          <div class="kpi-detail stacked">
            <span class="badge-warning" title="En attente">{{ reposKPI.enAttente }} ⏳</span>
            <span class="badge-success" title="Approuvés">{{ reposKPI.approuves }} ✓</span>
            <span class="badge-info" title="Transformés">{{ reposKPI.transformes }} ↻</span>
            <span class="badge-secondary" title="Annulés">{{ reposKPI.annules }} ⊘</span>
          </div>
        </div>
      </div>

      <!-- Carte Retards -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('retards') }" @click="goToModule('retards')">
        <div class="kpi-icon" style="background: #ffebee; color: #c62828">
          <i class="bi bi-clock-history"></i>
        </div>
        <div class="kpi-content">
          <h3>Retards</h3>
          <div class="kpi-value">{{ retardsKPI.heures }}h</div>
          <div class="kpi-detail stacked">
            <span class="badge-warning" title="En cours">{{ retardsKPI.enCours }} ⏳</span>
            <span class="badge-success" title="Rattrapés">{{ retardsKPI.rattrapes }} ✓</span>
            <span class="badge-secondary" title="Annulés">{{ retardsKPI.annules }} ⊘</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION MANAGER/ADMIN - Demandes en attente  -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-bell"></i>
        Demandes en attente de validation
        <span class="section-badge">{{ totalEnAttente }}</span>
        <span v-if="selectedView !== 'me'" class="view-filter-badge">
          ({{ currentViewLabel }})
        </span>
      </h2>
      
      <div v-if="totalEnAttente === 0" class="empty-state">
        <i class="bi bi-check2-circle"></i>
        <p>Aucune demande en attente</p>
        <p v-if="selectedView !== 'me'" class="hint">Pour l'équipe/membre sélectionné(e)</p>
      </div>

      <div v-else class="pending-grid">
        <!-- Congés en attente -->
        <div v-if="congesEnAttenteList.length > 0" class="pending-card conges">
          <h3>
            <i class="bi bi-calendar-check"></i>
            Congés ({{ congesEnAttenteList.length }})
          </h3>
          <div class="pending-list">
            <div v-for="conge in congesEnAttenteList.slice(0, 3)" :key="conge.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(conge.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ conge.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(conge.date_debut) }} → {{ formatDate(conge.date_fin) }}</p>
                <span v-if="selectedView !== 'me'" class="item-equipe">{{ conge.utilisateur_details?.equipe_nom }}</span>
              </div>
              <button class="btn-small" @click="goToModule('conges', conge.id)">Voir</button>
            </div>
            <div v-if="congesEnAttenteList.length > 3" class="more-link" @click="goToModule('conges')">
              + {{ congesEnAttenteList.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- OSTIE en attente -->
        <div v-if="ostieEnAttenteList.length > 0" class="pending-card ostie">
          <h3>
            <i class="bi bi-heart-pulse"></i>
            OSTIE ({{ ostieEnAttenteList.length }})
          </h3>
          <div class="pending-list">
            <div v-for="ostie in ostieEnAttenteList.slice(0, 3)" :key="ostie.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(ostie.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ ostie.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(ostie.date) }} à {{ formatTime(ostie.heure_debut) }}</p>
                <span v-if="selectedView !== 'me'" class="item-equipe">{{ ostie.utilisateur_details?.equipe_nom }}</span>
              </div>
              <button class="btn-small" @click="goToModule('ostie', ostie.id)">Voir</button>
            </div>
            <div v-if="ostieEnAttenteList.length > 3" class="more-link" @click="goToModule('ostie')">
              + {{ ostieEnAttenteList.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Permissions en attente -->
        <div v-if="permissionsEnAttenteList.length > 0" class="pending-card permissions">
          <h3>
            <i class="bi bi-door-open"></i>
            Permissions ({{ permissionsEnAttenteList.length }})
          </h3>
          <div class="pending-list">
            <div v-for="perm in permissionsEnAttenteList.slice(0, 3)" :key="perm.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(perm.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ perm.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(perm.date) }} - {{ formatTime(perm.heure_depart) }}</p>
                <span v-if="selectedView !== 'me'" class="item-equipe">{{ perm.utilisateur_details?.equipe_nom }}</span>
              </div>
              <button class="btn-small" @click="goToModule('permissions', perm.id)">Voir</button>
            </div>
            <div v-if="permissionsEnAttenteList.length > 3" class="more-link" @click="goToModule('permissions')">
              + {{ permissionsEnAttenteList.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Repos médicaux en attente -->
        <div v-if="reposEnAttenteList.length > 0" class="pending-card repos">
          <h3>
            <i class="bi bi-hospital"></i>
            Repos médicaux ({{ reposEnAttenteList.length }})
          </h3>
          <div class="pending-list">
            <div v-for="repos in reposEnAttenteList.slice(0, 3)" :key="repos.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(repos.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ repos.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(repos.date) }} - {{ repos.duree_heures }}h</p>
                <span v-if="selectedView !== 'me'" class="item-equipe">{{ repos.utilisateur_details?.equipe_nom }}</span>
              </div>
              <button class="btn-small" @click="goToModule('repos', repos.id)">Voir</button>
            </div>
            <div v-if="reposEnAttenteList.length > 3" class="more-link" @click="goToModule('repos')">
              + {{ reposEnAttenteList.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Retards en attente -->
        <div v-if="retardsEnAttenteList.length > 0" class="pending-card retards">
          <h3>
            <i class="bi bi-clock-history"></i>
            Retards ({{ retardsEnAttenteList.length }})
          </h3>
          <div class="pending-list">
            <div v-for="retard in retardsEnAttenteList.slice(0, 3)" :key="retard.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(retard.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ retard.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(retard.date) }} - {{ retard.minutes_retard }}min</p>
                <span v-if="selectedView !== 'me'" class="item-equipe">{{ retard.utilisateur_details?.equipe_nom }}</span>
              </div>
              <button class="btn-small" @click="goToModule('retards', retard.id)">Voir</button>
            </div>
            <div v-if="retardsEnAttenteList.length > 3" class="more-link" @click="goToModule('retards')">
              + {{ retardsEnAttenteList.length - 3 }} autres...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION POUR TOUS - Mes demandes récentes    -->
    <!-- ============================================ -->
    <div class="dashboard-section">
      <h2>
        <i class="bi bi-list-ul"></i>
        {{ selectedView === 'me' ? 'Mes dernières demandes' : 'Dernières demandes' }}
        <span v-if="selectedView !== 'me'" class="view-filter-badge">
          ({{ currentViewLabel }})
        </span>
      </h2>
      
      <div v-if="mesDemandes.length === 0" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p>Aucune demande récente</p>
      </div>

      <div v-else class="recent-list">
        <div v-for="demande in mesDemandes" :key="demande.id" class="recent-item" :class="demande.type">
          <div class="recent-icon" :style="{ background: getTypeColor(demande.type) }">
            <i :class="getTypeIcon(demande.type)"></i>
          </div>
          <div class="recent-content">
            <div class="recent-header">
              <span class="recent-type">{{ getTypeLabel(demande.type) }}</span>
              <span class="recent-badge" :class="demande.statut">{{ demande.statut_display || demande.statut }}</span>
            </div>
            <p class="recent-detail">{{ getDemandeDetail(demande) }}</p>
            <p class="recent-meta">
              <span v-if="selectedView !== 'me'" class="recent-user">
                <i class="bi bi-person"></i> {{ demande.utilisateur_details?.display_name }}
              </span>
              <span class="recent-date">{{ formatRelative(demande.date_creation) }}</span>
            </p>
          </div>
          <button class="btn-small" @click="goToModule(demande.type, demande.id)">Voir</button>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION MANAGER/ADMIN - Stats équipe         -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher && selectedView !== 'me'" class="dashboard-section">
      <h2>
        <i class="bi bi-graph-up"></i>
        Aperçu de l'équipe : {{ currentViewLabel }}
      </h2>
      
      <div class="team-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">Membres</span>
            <span class="stat-value">{{ currentScopeMembres.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Absents aujourd'hui</span>
            <span class="stat-value">{{ absentsAujourdhui }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">En retard</span>
            <span class="stat-value">{{ retardsAujourdhui }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Taux d'absentéisme</span>
            <span class="stat-value">{{ tauxAbsenteisme }}%</span>
          </div>
        </div>
      </div>

      <!-- Top retardataires -->
      <div v-if="topRetardataires.length > 0" class="top-list">
        <h3>⏰ Top des retardataires ({{ currentViewLabel }})</h3>
        <div class="top-items">
          <div v-for="(item, index) in topRetardataires" :key="item.userId" class="top-item">
            <span class="top-rank">{{ index + 1 }}</span>
            <span class="top-name">{{ item.name }}</span>
            <span class="top-equipe">{{ item.equipe }}</span>
            <span class="top-value">{{ item.total.toFixed(2) }}h</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION SUPER ADMIN - Stats globales         -->
    <!-- ============================================ -->
    <div v-if="isSuperAdmin" class="dashboard-section">
      <h2>
        <i class="bi bi-bar-chart"></i>
        Statistiques globales
      </h2>
      
      <div class="global-stats">
        <div class="stats-grid">
          <div class="stats-card">
            <h4>Répartition des absences (année {{ currentYear }})</h4>
            <div class="pie-chart-container">
              <canvas ref="pieChartRef"></canvas>
            </div>
            <div class="chart-legend">
              <div><span class="dot conges"></span> Congés: {{ globalStats.conges }}</div>
              <div><span class="dot ostie"></span> OSTIE: {{ globalStats.ostie }}</div>
              <div><span class="dot permissions"></span> Permissions: {{ globalStats.permissions }}</div>
              <div><span class="dot repos"></span> Repos: {{ globalStats.repos }}</div>
              <div><span class="dot retards"></span> Retards: {{ globalStats.retards }}</div>
            </div>
          </div>
          
          <div class="stats-card">
            <h4>Évolution mensuelle ({{ currentYear }})</h4>
            <div class="bar-chart-container">
              <canvas ref="barChartRef"></canvas>
            </div>
            <div class="chart-data-info" v-if="monthlyData.length > 0">
              <p><i class="bi bi-info-circle"></i> Données réelles de la base de données</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION ADMIN/STAFF - Alertes système        -->
    <!-- ============================================ -->
    <div v-if="isStaff" class="dashboard-section">
      <h2>
        <i class="bi bi-exclamation-triangle"></i>
        Alertes système
      </h2>
      
      <div class="alerts-list">
        <div v-if="!hasTypesRetard" class="alert-item warning">
          <i class="bi bi-exclamation-circle"></i>
          Aucun type de retard configuré
        </div>
        <div v-if="!hasTypesConge" class="alert-item warning">
          <i class="bi bi-exclamation-circle"></i>
          Aucun type de congé configuré
        </div>
        <div v-if="!hasDroits" class="alert-item info">
          <i class="bi bi-info-circle"></i>
          Aucun droit de congé configuré
        </div>
        <div v-if="hasTypesRetard && hasTypesConge && hasDroits" class="alert-item success">
          <i class="bi bi-check-circle"></i>
          Tous les systèmes sont opérationnels
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useRetardsStore } from '@/store/retards'
import { useFiltersStore } from '@/store/filters'
import { useEquipesStore } from '@/store/equipes'
import { format, parseISO, formatDistanceToNow, getYear, startOfYear, endOfYear, isWithinInterval, parse } from 'date-fns'
import { fr } from 'date-fns/locale/fr'
import Chart from 'chart.js/auto'

// ========== ROUTER ==========
const router = useRouter()

// ========== STORES ==========
const authStore = useAuthStore()
const congesStore = useCongesStore()
const ostieStore = useOstieStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const retardsStore = useRetardsStore()
const filtersStore = useFiltersStore()
const equipesStore = useEquipesStore()

// ========== STATE ==========
const loading = ref(false)
const selectedView = ref('me') // 'me', 'equipe-X', 'membre-X'
const memberSearchQuery = ref('')
const pieChartRef = ref<HTMLCanvasElement | null>(null)
const barChartRef = ref<HTMLCanvasElement | null>(null)
let pieChart: Chart | null = null
let barChart: Chart | null = null

// ========== COMPUTED - RÔLES ==========
const userRole = computed(() => {
  if (!authStore.user) return 'Utilisateur'
  if (authStore.user.is_superuser) return 'Super Administrateur'
  if (authStore.user.is_staff) return 'Administrateur'
  if (congesStore.isManagerOrAdmin) return 'Manager'
  return 'Utilisateur'
})

const userRoleClass = computed(() => {
  if (authStore.user?.is_superuser) return 'role-superadmin'
  if (authStore.user?.is_staff) return 'role-admin'
  if (congesStore.isManagerOrAdmin) return 'role-manager'
  return 'role-user'
})

const isManagerOrHigher = computed(() => {
  return congesStore.isManagerOrAdmin || congesStore.isSuperAdmin || authStore.user?.is_staff || false
})

const isSuperAdmin = computed(() => authStore.user?.is_superuser || false)
const isStaff = computed(() => authStore.user?.is_staff || false)

const canViewDetails = (module: string) => true

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'Utilisateur'
})

const currentDate = computed(() => {
  return format(new Date(), 'EEEE d MMMM yyyy', { locale: fr })
})

const currentYear = computed(() => getYear(new Date()))

// ========== GESTION DES ÉQUIPES HIÉRARCHIQUES ==========

// Récupérer les équipes gérées par l'utilisateur connecté
const managedEquipes = computed(() => {
  if (!authStore.user) return []
  
  const userId = authStore.user.id
  const equipes: any[] = []
  
  // Fonction récursive pour chercher dans toute l'arborescence
  const findManagedEquipes = (equipeList: any[]) => {
    for (const equipe of equipeList) {
      // Vérifier si l'utilisateur est manager ou co-manager
      const isManager = equipe.manager === userId
      const isCoManager = equipe.co_managers?.includes(userId)
      
      if (isManager || isCoManager) {
        equipes.push(equipe)
      }
      
      // Chercher récursivement dans les sous-équipes
      if (equipe.sous_equipes?.length) {
        findManagedEquipes(equipe.sous_equipes)
      }
    }
  }
  
  findManagedEquipes(equipesStore.arbreEquipes || [])
  return equipes
})

// Compter les sous-équipes récursivement
const countSubEquipes = (equipe: any): number => {
  let count = 0
  if (equipe.sous_equipes?.length) {
    count += equipe.sous_equipes.length
    for (const sub of equipe.sous_equipes) {
      count += countSubEquipes(sub)
    }
  }
  return count
}

// Récupérer tous les IDs d'équipes dans la portée (équipe + sous-équipes)
const getEquipeScopeIds = (equipeId: number): number[] => {
  const ids = [equipeId]
  
  const findEquipe = (list: any[]): any | null => {
    for (const eq of list) {
      if (eq.id === equipeId) return eq
      if (eq.sous_equipes?.length) {
        const found = findEquipe(eq.sous_equipes)
        if (found) return found
      }
    }
    return null
  }
  
  const equipe = findEquipe(equipesStore.arbreEquipes || [])
  if (equipe?.sous_equipes?.length) {
    const addSubIds = (subs: any[]) => {
      for (const sub of subs) {
        ids.push(sub.id)
        if (sub.sous_equipes?.length) {
          addSubIds(sub.sous_equipes)
        }
      }
    }
    addSubIds(equipe.sous_equipes)
  }
  
  return ids
}

// IDs des équipes dans la portée actuelle
const currentScopeEquipeIds = computed(() => {
  if (selectedView.value.startsWith('equipe-')) {
    const equipeId = parseInt(selectedView.value.replace('equipe-', ''))
    return getEquipeScopeIds(equipeId)
  }
  return []
})

// Membres dans la portée actuelle
const currentScopeMembres = computed(() => {
  if (selectedView.value === 'me') {
    return authStore.user ? [authStore.user] : []
  }
  
  if (selectedView.value.startsWith('membre-')) {
    const membreId = parseInt(selectedView.value.replace('membre-', ''))
    const membre = managedMembres.value.find(m => m.id === membreId)
    return membre ? [membre] : []
  }
  
  if (selectedView.value.startsWith('equipe-')) {
    // Collecter tous les membres des équipes dans la portée
    const membres: any[] = []
    const seenIds = new Set<number>()
    
    const collectMembres = (equipeList: any[]) => {
      for (const equipe of equipeList) {
        if (currentScopeEquipeIds.value.includes(equipe.id)) {
          // Ajouter les membres de cette équipe
          if (equipe.membres?.length) {
            for (const membre of equipe.membres) {
              if (!seenIds.has(membre.id)) {
                seenIds.add(membre.id)
                membres.push(membre)
              }
            }
          }
        }
        
        // Chercher récursivement
        if (equipe.sous_equipes?.length) {
          collectMembres(equipe.sous_equipes)
        }
      }
    }
    
    collectMembres(equipesStore.arbreEquipes || [])
    return membres
  }
  
  return []
})

// Tous les membres gérés (pour le sélecteur)
const managedMembres = computed(() => {
  const membres: any[] = []
  const seenIds = new Set<number>()
  
  const collectFromEquipe = (equipe: any) => {
    if (equipe.membres?.length) {
      for (const membre of equipe.membres) {
        if (!seenIds.has(membre.id) && membre.id !== authStore.user?.id) {
          seenIds.add(membre.id)
          membres.push({
            ...membre,
            equipe_nom: equipe.nom,
            equipe_id: equipe.id
          })
        }
      }
    }
    
    if (equipe.sous_equipes?.length) {
      for (const sub of equipe.sous_equipes) {
        collectFromEquipe(sub)
      }
    }
  }
  
  for (const equipe of managedEquipes.value) {
    collectFromEquipe(equipe)
  }
  
  return membres.sort((a, b) => a.display_name?.localeCompare(b.display_name))
})

const filteredManagedMembres = computed(() => {
  if (!memberSearchQuery.value) return managedMembres.value.slice(0, 10)
  
  const query = memberSearchQuery.value.toLowerCase()
  return managedMembres.value.filter(m => 
    m.display_name?.toLowerCase().includes(query) ||
    m.username?.toLowerCase().includes(query) ||
    m.equipe_nom?.toLowerCase().includes(query)
  ).slice(0, 15)
})

// Label de la vue actuelle
const currentViewLabel = computed(() => {
  if (selectedView.value === 'me') return 'Ma vue personnelle'
  
  if (selectedView.value.startsWith('equipe-')) {
    const equipeId = parseInt(selectedView.value.replace('equipe-', ''))
    const equipe = findEquipeById(equipeId)
    return equipe ? `Équipe: ${equipe.nom}` : 'Équipe sélectionnée'
  }
  
  if (selectedView.value.startsWith('membre-')) {
    const membreId = parseInt(selectedView.value.replace('membre-', ''))
    const membre = managedMembres.value.find(m => m.id === membreId)
    return membre ? `Membre: ${membre.display_name}` : 'Membre sélectionné'
  }
  
  return 'Vue personnelle'
})

const findEquipeById = (id: number): any | null => {
  const search = (list: any[]): any | null => {
    for (const eq of list) {
      if (eq.id === id) return eq
      if (eq.sous_equipes?.length) {
        const found = search(eq.sous_equipes)
        if (found) return found
      }
    }
    return null
  }
  return search(equipesStore.arbreEquipes || [])
}

// ========== FILTRE PAR PORTÉE ==========

const isInCurrentScope = (item: any): boolean => {
  if (selectedView.value === 'me') {
    return item.utilisateur === authStore.user?.id
  }
  
  if (selectedView.value.startsWith('membre-')) {
    const membreId = parseInt(selectedView.value.replace('membre-', ''))
    return item.utilisateur === membreId
  }
  
  if (selectedView.value.startsWith('equipe-')) {
    // Vérifier si l'utilisateur de l'item est dans la portée des équipes
    const userEquipeId = item.utilisateur_details?.equipe
    return currentScopeEquipeIds.value.includes(userEquipeId)
  }
  
  return true
}

// ========== KPI CONGÉS ==========
const congesKPI = computed(() => {
  let conges = congesStore.conges || []
  
  // Filtrer selon la vue
  if (selectedView.value !== 'me') {
    conges = conges.filter(isInCurrentScope)
  }
  
  const approuves = conges.filter((c: any) => c.statut === 'approuve').length
  const enAttente = conges.filter((c: any) => c.statut === 'en_attente').length
  const refuses = conges.filter((c: any) => c.statut === 'refuse').length
  const annules = conges.filter((c: any) => c.statut === 'annule').length
  
  // Solde : pour "me" on prend le solde auth, sinon on compte les jours approuvés consommés
  let solde = '0'
  if (selectedView.value === 'me') {
    solde = String(authStore.soldeConge?.actuelle || 0)
  } else {
    // Calculer le solde approximatif (approuvés - consommés)
    const totalJours = conges.reduce((acc: number, c: any) => {
      if (c.statut === 'approuve') return acc + (c.jours_deduits || 0)
      return acc
    }, 0)
    solde = String(Math.max(0, 25 - totalJours)) // Hypothèse: solde de base 25j
  }
  
  return {
    solde,
    approuves,
    enAttente,
    refuses,
    annules
  }
})

// ========== KPI OSTIE ==========
const ostieKPI = computed(() => {
  let osties = ostieStore.osties || []
  
  if (selectedView.value !== 'me') {
    osties = osties.filter(isInCurrentScope)
  }
  
  return {
    total: osties.length,
    enAttente: osties.filter((o: any) => o.statut === 'en_attente').length,
    approuves: osties.filter((o: any) => o.statut === 'approuve').length,
    transformes: osties.filter((o: any) => o.statut === 'transforme').length,
    annules: osties.filter((o: any) => o.statut === 'annule').length
  }
})

// ========== KPI PERMISSIONS ==========
const permissionsKPI = computed(() => {
  let perms = permissionsStore.permissions || []
  
  if (selectedView.value !== 'me') {
    perms = perms.filter(isInCurrentScope)
  }
  
  const heures = perms.reduce((acc: number, p: any) => acc + (parseFloat(p.heures_a_rattraper) || 0), 0)
  
  return {
    heures: heures.toFixed(2),
    rattrapage: perms.filter((p: any) => p.statut === 'rattrapage').length,
    retournees: perms.filter((p: any) => p.statut === 'retourne').length,
    approuves: perms.filter((p: any) => p.statut === 'approuve').length,
    annules: perms.filter((p: any) => p.statut === 'annule').length
  }
})

// ========== KPI REPOS ==========
const reposKPI = computed(() => {
  let repos = reposStore.reposMedicaux || []
  
  if (selectedView.value !== 'me') {
    repos = repos.filter(isInCurrentScope)
  }
  
  const heures = repos.reduce((acc: number, r: any) => acc + (parseFloat(r.duree_heures) || 0), 0)
  
  return {
    heures: heures.toFixed(2),
    enAttente: repos.filter((r: any) => r.statut === 'en_attente').length,
    approuves: repos.filter((r: any) => r.statut === 'approuve').length,
    transformes: repos.filter((r: any) => r.statut === 'transforme').length,
    annules: repos.filter((r: any) => r.statut === 'annule').length
  }
})

// ========== KPI RETARDS ==========
const retardsKPI = computed(() => {
  let retards = retardsStore.retards || []
  
  if (selectedView.value !== 'me') {
    retards = retards.filter(isInCurrentScope)
  }
  
  const heures = retards.reduce((acc: number, r: any) => {
    const h = typeof r.heures_a_rattraper === 'number' ? r.heures_a_rattraper : parseFloat(r.heures_a_rattraper) || 0
    return acc + h
  }, 0)
  
  return {
    heures: heures.toFixed(2),
    enCours: retards.filter((r: any) => r.statut === 'en_cours').length,
    rattrapes: retards.filter((r: any) => r.statut === 'approuve').length,
    annules: retards.filter((r: any) => r.statut === 'annule').length
  }
})

// ========== DEMANDES EN ATTENTE ==========
const congesEnAttenteList = computed(() => {
  if (!congesStore.conges || !isManagerOrHigher.value) return []
  return congesStore.conges.filter((c: any) => 
    c.statut === 'en_attente' && isInCurrentScope(c)
  )
})

const ostieEnAttenteList = computed(() => {
  if (!ostieStore.osties || !isManagerOrHigher.value) return []
  return ostieStore.osties.filter((o: any) => 
    o.statut === 'en_attente' && isInCurrentScope(o)
  )
})

const permissionsEnAttenteList = computed(() => {
  if (!permissionsStore.permissions || !isManagerOrHigher.value) return []
  return permissionsStore.permissions.filter((p: any) => 
    p.statut === 'en_attente' && isInCurrentScope(p)
  )
})

const reposEnAttenteList = computed(() => {
  if (!reposStore.reposMedicaux || !isManagerOrHigher.value) return []
  return reposStore.reposMedicaux.filter((r: any) => 
    r.statut === 'en_attente' && isInCurrentScope(r)
  )
})

const retardsEnAttenteList = computed(() => {
  if (!retardsStore.retards || !isManagerOrHigher.value) return []
  return retardsStore.retards.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && isInCurrentScope(r)
  )
})

const totalEnAttente = computed(() => 
  congesEnAttenteList.value.length +
  ostieEnAttenteList.value.length +
  permissionsEnAttenteList.value.length +
  reposEnAttenteList.value.length +
  retardsEnAttenteList.value.length
)

// ========== MES DEMANDES RÉCENTES ==========
const mesDemandes = computed(() => {
  const demandes: any[] = []
  
  // Congés
  if (congesStore.conges) {
    congesStore.conges.filter(isInCurrentScope).forEach((c: any) => {
      demandes.push({
        ...c,
        type: 'conges',
        type_label: 'Congé',
        icon: 'bi-calendar-check',
        color: '#1976d2'
      })
    })
  }

  // OSTIE
  if (ostieStore.osties) {
    ostieStore.osties.filter(isInCurrentScope).forEach((o: any) => {
      demandes.push({
        ...o,
        type: 'ostie',
        type_label: 'OSTIE',
        icon: 'bi-heart-pulse',
        color: '#f57c00'
      })
    })
  }

  // Permissions
  if (permissionsStore.permissions) {
    permissionsStore.permissions.filter(isInCurrentScope).forEach((p: any) => {
      demandes.push({
        ...p,
        type: 'permissions',
        type_label: 'Permission',
        icon: 'bi-door-open',
        color: '#388e3c'
      })
    })
  }

  // Repos médicaux
  if (reposStore.reposMedicaux) {
    reposStore.reposMedicaux.filter(isInCurrentScope).forEach((r: any) => {
      demandes.push({
        ...r,
        type: 'repos',
        type_label: 'Repos médical',
        icon: 'bi-hospital',
        color: '#7b1fa2'
      })
    })
  }

  // Retards
  if (retardsStore.retards) {
    retardsStore.retards.filter(isInCurrentScope).forEach((r: any) => {
      demandes.push({
        ...r,
        type: 'retards',
        type_label: 'Retard',
        icon: 'bi-clock-history',
        color: '#c62828'
      })
    })
  }

  return demandes
    .sort((a, b) => new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime())
    .slice(0, 10)
})

// ========== STATS ÉQUIPE ==========
const absentsAujourdhui = computed(() => {
  if (!isManagerOrHigher.value) return 0
  const today = format(new Date(), 'yyyy-MM-dd')
  let count = 0
  
  const membres = currentScopeMembres.value
  const membreIds = new Set(membres.map(m => m.id))
  
  // Congés aujourd'hui
  if (congesStore.conges) {
    count += congesStore.conges.filter((c: any) => 
      c.statut === 'approuve' && 
      c.date_debut <= today && 
      c.date_fin >= today &&
      membreIds.has(c.utilisateur)
    ).length
  }
  
  // OSTIE aujourd'hui
  if (ostieStore.osties) {
    count += ostieStore.osties.filter((o: any) => 
      (o.statut === 'approuve' || o.statut === 'transforme') && 
      o.date === today &&
      membreIds.has(o.utilisateur)
    ).length
  }
  
  // Repos médicaux aujourd'hui
  if (reposStore.reposMedicaux) {
    count += reposStore.reposMedicaux.filter((r: any) => 
      r.statut === 'approuve' && 
      r.date === today &&
      membreIds.has(r.utilisateur)
    ).length
  }
  
  return count
})

const retardsAujourdhui = computed(() => {
  if (!isManagerOrHigher.value) return 0
  const today = format(new Date(), 'yyyy-MM-dd')
  
  const membres = currentScopeMembres.value
  const membreIds = new Set(membres.map(m => m.id))
  
  if (!retardsStore.retards) return 0
  return retardsStore.retards.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && 
    r.date === today &&
    membreIds.has(r.utilisateur)
  ).length
})

const tauxAbsenteisme = computed(() => {
  const membres = currentScopeMembres.value
  if (!isManagerOrHigher.value || membres.length === 0) return '0.0'
  return ((absentsAujourdhui.value / membres.length) * 100).toFixed(1)
})

const topRetardataires = computed(() => {
  if (!isManagerOrHigher.value || !retardsStore.retards) return []
  
  const membres = currentScopeMembres.value
  const membreIds = new Set(membres.map(m => m.id))
  
  const stats: Record<number, { name: string; equipe: string; total: number }> = {}
  
  retardsStore.retards.forEach((r: any) => {
    if (!membreIds.has(r.utilisateur)) return
    
    if (r.statut === 'approuve' || r.statut === 'en_cours') {
      const userId = r.utilisateur
      const heures = parseFloat(r.heures_a_rattraper || '0')
      
      if (!stats[userId]) {
        stats[userId] = {
          name: r.utilisateur_details?.display_name || `User ${userId}`,
          equipe: r.utilisateur_details?.equipe_nom || '',
          total: 0
        }
      }
      stats[userId].total += heures
    }
  })
  
  return Object.entries(stats)
    .map(([userId, data]) => ({
      userId: parseInt(userId),
      name: data.name,
      equipe: data.equipe,
      total: data.total
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 5)
})

// ========== STATS GLOBALES (SUPER ADMIN) ==========
const globalStats = computed(() => {
  return {
    conges: congesStore.conges?.length || 0,
    ostie: ostieStore.osties?.length || 0,
    permissions: permissionsStore.permissions?.length || 0,
    repos: reposStore.reposMedicaux?.length || 0,
    retards: retardsStore.retards?.length || 0
  }
})

// Données mensuelles réelles
const monthlyData = computed(() => {
  const data = new Array(12).fill(0)
  const yearStart = startOfYear(new Date())
  const yearEnd = endOfYear(new Date())
  
  // Agréger toutes les demandes par mois
  const allItems = [
    ...(congesStore.conges || []),
    ...(ostieStore.osties || []),
    ...(permissionsStore.permissions || []),
    ...(reposStore.reposMedicaux || []),
    ...(retardsStore.retards || [])
  ]
  
  allItems.forEach((item: any) => {
    const date = item.date_debut || item.date
    if (!date) return
    
    const itemDate = parseISO(date)
    if (isWithinInterval(itemDate, { start: yearStart, end: yearEnd })) {
      const month = itemDate.getMonth() // 0-11
      data[month]++
    }
  })
  
  return data
})

const initCharts = () => {
  if (!isSuperAdmin.value) return
  
  nextTick(() => {
    // Camembert
    if (pieChartRef.value) {
      if (pieChart) pieChart.destroy()
      
      pieChart = new Chart(pieChartRef.value, {
        type: 'doughnut',
        data: {
          labels: ['Congés', 'OSTIE', 'Permissions', 'Repos', 'Retards'],
          datasets: [{
            data: [
              globalStats.value.conges,
              globalStats.value.ostie,
              globalStats.value.permissions,
              globalStats.value.repos,
              globalStats.value.retards
            ],
            backgroundColor: ['#1976d2', '#f57c00', '#388e3c', '#7b1fa2', '#c62828']
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          }
        }
      })
    }
    
    // Barres mensuelles
    if (barChartRef.value) {
      if (barChart) barChart.destroy()
      
      const moisNoms = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Août', 'Sep', 'Oct', 'Nov', 'Déc']
      const data = monthlyData.value
      const maxValue = Math.max(...data, 1)
      
      barChart = new Chart(barChartRef.value, {
        type: 'bar',
        data: {
          labels: moisNoms,
          datasets: [{
            label: 'Demandes',
            data: data,
            backgroundColor: '#1976d2',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              max: Math.ceil(maxValue * 1.2)
            }
          },
          plugins: {
            legend: { display: false }
          }
        }
      })
    }
  })
}

// ========== ALERTES SYSTÈME ==========
const hasTypesRetard = computed(() => retardsStore.typesRetard?.length > 0)
const hasTypesConge = computed(() => congesStore.typesConge?.length > 0)
const hasDroits = computed(() => congesStore.droits?.length > 0)

// ========== METHODS ==========
const resetView = () => {
  selectedView.value = 'me'
  memberSearchQuery.value = ''
}

const getInitials = (name: string | undefined) => {
  if (!name) return '?'
  return name.charAt(0).toUpperCase()
}

const formatDate = (dateStr: string | undefined) => {
  if (!dateStr) return ''
  try {
    return format(parseISO(dateStr), 'dd/MM/yyyy')
  } catch {
    return ''
  }
}

const formatTime = (timeStr: string | undefined) => {
  if (!timeStr) return ''
  return String(timeStr).substring(0, 5)
}

const formatRelative = (dateStr: string | undefined) => {
  if (!dateStr) return ''
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true, locale: fr })
  } catch {
    return ''
  }
}

const getTypeIcon = (type: string) => {
  const icons: Record<string, string> = {
    conges: 'bi-calendar-check',
    ostie: 'bi-heart-pulse',
    permissions: 'bi-door-open',
    repos: 'bi-hospital',
    retards: 'bi-clock-history'
  }
  return icons[type] || 'bi-file-text'
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    conges: 'Congé',
    ostie: 'OSTIE',
    permissions: 'Permission',
    repos: 'Repos médical',
    retards: 'Retard'
  }
  return labels[type] || type
}

const getTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    conges: '#1976d2',
    ostie: '#f57c00',
    permissions: '#388e3c',
    repos: '#7b1fa2',
    retards: '#c62828'
  }
  return colors[type] || '#9e9e9e'
}

const getDemandeDetail = (demande: any) => {
  switch (demande.type) {
    case 'conges':
      return `${formatDate(demande.date_debut)} → ${formatDate(demande.date_fin)} (${demande.jours_deduits || '?'}j)`
    case 'ostie':
      return `${formatDate(demande.date)} à ${formatTime(demande.heure_debut)}`
    case 'permissions':
      return `${formatDate(demande.date)} - Départ ${formatTime(demande.heure_depart)}`
    case 'repos':
      return `${formatDate(demande.date)} - ${demande.duree_heures || '?'}h`
    case 'retards':
      return `${formatDate(demande.date)} - ${demande.minutes_retard || '?'}min`
    default:
      return ''
  }
}

const goToModule = (module: string, id?: number) => {
  const routes: Record<string, string> = {
    conges: '/conges',
    ostie: '/ostie',
    permissions: '/permissions',
    repos: '/repos-medical',
    retards: '/retards'
  }
  
  const path = routes[module]
  if (path) {
    if (id) {
      router.push({ path, query: { open: id.toString() } })
    } else {
      router.push(path)
    }
  }
}

const refreshAllData = async () => {
  loading.value = true
  
  const currentYear = new Date().getFullYear()
  
  await Promise.allSettled([
    equipesStore.fetchArbre(true),
    congesStore.fetchCalendrier({ annee: currentYear }),
    congesStore.fetchMesConges(currentYear),
    ostieStore.fetchCalendrier({ annee: currentYear }),
    ostieStore.fetchMesOsties(currentYear),
    permissionsStore.fetchCalendrier({ annee: currentYear }),
    permissionsStore.fetchMesPermissions(currentYear),
    reposStore.fetchCalendrier({ annee: currentYear }),
    reposStore.fetchMesRepos(currentYear),
    retardsStore.fetchCalendrier({ annee: currentYear }),
    retardsStore.fetchMesRetards(currentYear),
    authStore.refreshSolde()
  ])
  
  loading.value = false
  
  // Réinitialiser les graphiques si SuperAdmin
  if (isSuperAdmin.value) {
    initCharts()
  }
}

// Watch pour mettre à jour les graphiques quand les données changent
watch([globalStats, monthlyData], () => {
  if (isSuperAdmin.value) {
    initCharts()
  }
}, { deep: true })

// ========== LIFECYCLE ==========
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await equipesStore.fetchArbre(true)
  await refreshAllData()
})
</script>

<style scoped>
/* ... (le CSS précédent reste identique, ajouts ci-dessous) ... */

/* ============================================ */
/* SÉLECTEUR DE VUE                             */
/* ============================================ */
.view-selector-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.view-selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.view-selector-header h3 {
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-reset {
  padding: 6px 12px;
  background: #f5f5f5;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: background 0.2s;
}

.btn-reset:hover {
  background: #e0e0e0;
}

.view-options {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.view-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.view-label {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}

.view-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.view-option {
  padding: 10px 16px;
  background: #f5f5f5;
  border: 2px solid transparent;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
  font-size: 14px;
}

.view-option:hover {
  background: #e8e8e8;
}

.view-option.active {
  background: #e3f2fd;
  border-color: #1976d2;
  color: #1976d2;
}

.view-option.member {
  padding: 8px 12px;
}

.member-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #1976d2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.member-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
}

.member-name {
  font-weight: 500;
  font-size: 13px;
}

.member-equipe {
  font-size: 11px;
  color: #666;
}

.sub-count {
  background: #1976d2;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
}

.member-search {
  position: relative;
  margin-bottom: 8px;
}

.member-search i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #666;
}

.member-search-input {
  width: 100%;
  padding: 10px 12px 10px 40px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
}

.members-list {
  max-height: 200px;
  overflow-y: auto;
  padding: 4px;
  background: #fafafa;
  border-radius: 8px;
}

.current-view-indicator {
  margin-top: 15px;
  padding: 12px;
  background: #f0f7ff;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.current-view-indicator strong {
  color: #1976d2;
}

.view-scope {
  font-size: 12px;
  color: #999;
  margin-left: auto;
}

/* ============================================ */
/* BADGES SUPPLÉMENTAIRES                       */
/* ============================================ */
.badge-danger {
  background: #ffebee;
  color: #c62828;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-secondary {
  background: #f5f5f5;
  color: #666;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.kpi-detail.stacked {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 6px;
}

.kpi-detail.stacked span {
  text-align: center;
  padding: 4px;
  font-size: 11px;
}

.kpi-value.small-text {
  font-size: 22px;
}

/* ============================================ */
/* FILTRE DE VUE DANS LES SECTIONS              */
/* ============================================ */
.view-filter-badge {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 12px;
  margin-left: 10px;
  font-weight: normal;
}

.item-equipe {
  font-size: 11px;
  color: #666;
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  margin-top: 4px;
  display: inline-block;
}

.recent-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 4px 0 0 0;
  font-size: 12px;
  color: #999;
}

.recent-user {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #666;
}

/* ============================================ */
/* GRAPHIQUES                                   */
/* ============================================ */
.pie-chart-container,
.bar-chart-container {
  height: 200px;
  margin: 15px 0;
}

.chart-data-info {
  text-align: center;
  font-size: 12px;
  color: #666;
  margin-top: 10px;
}

/* ============================================ */
/* TOP RETARDATAIRES AMÉLIORÉ                   */
/* ============================================ */
.top-equipe {
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

/* Responsive pour le sélecteur */
@media (max-width: 768px) {
  .view-buttons {
    flex-direction: column;
  }
  
  .view-option {
    width: 100%;
    justify-content: flex-start;
  }
  
  .members-list {
    max-height: 150px;
  }
}

/* Styles identiques au précédent, avec ajouts */
.dashboard {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
}

.header-left h1 {
  font-size: 28px;
  margin: 0 0 5px 0;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.role-badge {
  font-size: 14px;
  font-weight: normal;
  padding: 4px 12px;
  border-radius: 20px;
}

.role-superadmin {
  background: #ffd700;
  color: #000;
}

.role-admin {
  background: #1976d2;
  color: white;
}

.role-manager {
  background: #388e3c;
  color: white;
}

.role-user {
  background: #757575;
  color: white;
}

.date-today {
  color: #666;
  font-size: 14px;
  margin: 0;
  text-transform: capitalize;
}

.btn-refresh {
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #f5f5f5;
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Filtres */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.member-filter {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.member-filter label {
  font-weight: 500;
  color: #666;
  display: flex;
  align-items: center;
  gap: 5px;
}

.filter-tabs {
  display: flex;
  gap: 5px;
  background: #f0f0f0;
  padding: 3px;
  border-radius: 8px;
}

.filter-tab {
  padding: 6px 12px;
  border: none;
  background: transparent;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.filter-tab.active {
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.filter-tab:hover {
  background: rgba(255,255,255,0.5);
}

.equipe-selector, .membre-selector {
  flex: 1;
  min-width: 250px;
}

.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.search-wrapper {
  position: relative;
  margin-bottom: 8px;
}

.search-icon {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.search-input {
  width: 100%;
  padding: 8px 12px 8px 35px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
}

.btn-clear-filter {
  padding: 8px 16px;
  border: 1px solid #f44336;
  background: white;
  color: #f44336;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  transition: all 0.2s;
}

.btn-clear-filter:hover {
  background: #f44336;
  color: white;
}

.active-filter {
  margin-top: 10px;
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 6px;
  font-size: 13px;
  color: #1976d2;
  display: flex;
  align-items: center;
  gap: 5px;
}

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.kpi-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  display: flex;
  gap: 15px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.kpi-card.clickable {
  cursor: pointer;
}

.kpi-card.clickable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.kpi-icon {
  width: 50px;
  height: 50px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.kpi-content {
  flex: 1;
}

.kpi-content h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #666;
}

.kpi-value {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 8px;
}

.kpi-detail {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.badge-success {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.badge-warning {
  background: #fff3e0;
  color: #f57c00;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.badge-danger {
  background: #ffebee;
  color: #c62828;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.badge-info {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

.badge-secondary {
  background: #f5f5f5;
  color: #757575;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
}

/* Sections */
.dashboard-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.dashboard-section h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.section-badge {
  background: #f44336;
  color: white;
  padding: 2px 8px;
  border-radius: 20px;
  font-size: 12px;
  margin-left: 10px;
}

/* Demandes en attente */
.pending-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.pending-card {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 15px;
}

.pending-card h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.pending-card.conges h3 { color: #1976d2; }
.pending-card.ostie h3 { color: #f57c00; }
.pending-card.permissions h3 { color: #388e3c; }
.pending-card.repos h3 { color: #7b1fa2; }
.pending-card.retards h3 { color: #c62828; }

.pending-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.pending-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: white;
  border-radius: 8px;
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e0e0e0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #666;
}

.item-content {
  flex: 1;
}

.user-name {
  margin: 0;
  font-weight: 500;
  font-size: 14px;
}

.item-detail {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #666;
}

.btn-small {
  padding: 4px 12px;
  background: #f0f0f0;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  transition: background 0.2s;
}

.btn-small:hover {
  background: #e0e0e0;
}

.more-link {
  text-align: center;
  font-size: 12px;
  color: #1976d2;
  cursor: pointer;
  padding: 8px;
}

.more-link:hover {
  text-decoration: underline;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 10px;
}

/* Mes demandes récentes */
.recent-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  transition: background 0.2s;
}

.recent-item:hover {
  background: #f0f0f0;
}

.recent-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.recent-content {
  flex: 1;
}

.recent-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.recent-type {
  font-weight: 500;
}

.recent-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}

.recent-badge.en_attente {
  background: #fff3e0;
  color: #f57c00;
}

.recent-badge.approuve, .recent-badge.valide {
  background: #e8f5e9;
  color: #2e7d32;
}

.recent-badge.refuse, .recent-badge.annule {
  background: #ffebee;
  color: #c62828;
}

.recent-badge.transforme {
  background: #e3f2fd;
  color: #1976d2;
}

.recent-detail {
  margin: 0 0 2px 0;
  font-size: 13px;
}

.recent-date {
  margin: 0;
  font-size: 11px;
  color: #999;
}

/* Team stats */
.team-stats {
  margin-bottom: 20px;
}

.stat-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

/* Module stats */
.module-stats {
  margin: 20px 0;
}

.module-stats h3 {
  font-size: 16px;
  margin: 0 0 15px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
}

.stat-module {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 15px;
}

.stat-module h4 {
  margin: 0 0 15px 0;
  font-size: 15px;
  color: #333;
}

.stat-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.stat-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 80px;
  font-size: 12px;
  color: #666;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 4px;
}

.bar-value {
  width: 50px;
  font-size: 12px;
  font-weight: 500;
  text-align: right;
}

/* Top list */
.top-list {
  margin-top: 20px;
}

.top-list h3 {
  font-size: 16px;
  margin: 0 0 15px 0;
}

.top-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.top-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f5f5f5;
  border-radius: 6px;
}

.top-rank {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: #1976d2;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
}

.top-name {
  flex: 1;
}

.top-value {
  font-weight: bold;
  color: #c62828;
}

/* Global stats */
.global-stats {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.stats-card {
  background: #f9f9f9;
  border-radius: 10px;
  padding: 15px;
}

.stats-card h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
}

.pie-chart-placeholder {
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-legend {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chart-legend div {
  display: flex;
  align-items: center;
  gap: 8px;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.conges { background: #1976d2; }
.dot.ostie { background: #f57c00; }
.dot.permissions { background: #388e3c; }
.dot.repos { background: #7b1fa2; }
.dot.retards { background: #c62828; }

.bar-chart-placeholder {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.bar-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 35px;
  font-size: 12px;
  color: #666;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.bar {
  height: 100%;
  border-radius: 4px;
}

.bar-value {
  width: 30px;
  font-size: 12px;
  text-align: right;
  color: #666;
}

/* Alertes système */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.alert-item {
  padding: 15px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.alert-item.warning {
  background: #fff3e0;
  color: #f57c00;
  border-left: 4px solid #f57c00;
}

.alert-item.info {
  background: #e3f2fd;
  color: #1976d2;
  border-left: 4px solid #1976d2;
}

.alert-item.success {
  background: #e8f5e9;
  color: #2e7d32;
  border-left: 4px solid #2e7d32;
}

.alert-item i {
  font-size: 20px;
}

/* Utilitaires */
.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .kpi-grid {
    grid-template-columns: 1fr;
  }
  
  .pending-grid {
    grid-template-columns: 1fr;
  }
  
  .stat-row {
    grid-template-columns: 1fr 1fr;
  }
  
  .member-filter {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-tabs {
    justify-content: center;
  }
}
</style>