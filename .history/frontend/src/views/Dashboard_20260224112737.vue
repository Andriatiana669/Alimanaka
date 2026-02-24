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

    <!-- FILTRE PAR MEMBRE (pour managers et +) -->
    <div v-if="isManagerOrHigher" class="filters-section">
      <div class="member-filter">
        <label>
          <i class="bi bi-funnel"></i>
          Filtrer par :
        </label>
        <div class="filter-tabs">
          <button 
            class="filter-tab" 
            :class="{ active: filterType === 'moi' }"
            @click="setFilterMoi"
          >
            <i class="bi bi-person-circle"></i> Moi
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: filterType === 'equipe' }"
            @click="filterType = 'equipe'"
          >
            <i class="bi bi-diagram-3"></i> Équipe
          </button>
          <button 
            class="filter-tab" 
            :class="{ active: filterType === 'membre' }"
            @click="filterType = 'membre'"
          >
            <i class="bi bi-person"></i> Membre
          </button>
        </div>

        <!-- Sélecteur d'équipe avec hiérarchie complète -->
        <div v-if="filterType === 'equipe'" class="equipe-selector">
          <select v-model="selectedEquipeId" @change="onEquipeChange" class="form-select">
            <option value="">Toutes les équipes que je gère</option>
            <template v-for="equipe in equipesGerablesHierarchiques" :key="equipe.id">
              <option :value="equipe.id" :style="{ paddingLeft: (equipe.niveau * 20) + 'px' }">
                {{ getEquipeIcon(equipe) }} {{ getEquipeDisplay(equipe) }}
              </option>
              <template v-if="equipe.sous_equipes && equipe.sous_equipes.length">
                <option 
                  v-for="sousEquipe in getAllSousEquipes(equipe)" 
                  :key="sousEquipe.id" 
                  :value="sousEquipe.id"
                  :style="{ paddingLeft: ((sousEquipe.niveau || 0) * 20) + 'px' }"
                >
                  {{ getEquipeIcon(sousEquipe) }} {{ getEquipeDisplay(sousEquipe) }}
                </option>
              </template>
            </template>
          </select>
          <div v-if="equipesGerablesHierarchiques.length === 0" class="help-text">
            <i class="bi bi-info-circle"></i> Aucune équipe à gérer
          </div>
        </div>

        <!-- Sélecteur de membre -->
        <div v-else-if="filterType === 'membre'" class="membre-selector">
          <div class="search-wrapper">
            <i class="bi bi-search search-icon"></i>
            <input
              type="text"
              v-model="membreSearch"
              placeholder="Rechercher un membre..."
              class="search-input"
              @input="onMembreSearch"
            />
            <button v-if="membreSearch" @click="membreSearch = ''" class="clear-search">
              <i class="bi bi-x"></i>
            </button>
          </div>
          
          <select v-model="selectedMembreId" @change="onMembreChange" class="form-select" :disabled="membresFiltres.length === 0">
            <option value="">Sélectionner un membre</option>
            <option v-for="membre in membresFiltres" :key="membre.id" :value="membre.id">
              {{ membre.display_name }} ({{ membre.username.toUpperCase() }}) - {{ membre.equipe_path || membre.equipe_nom || 'Sans équipe' }}
            </option>
          </select>
        </div>

        <button v-if="filterType !== 'moi' && (selectedEquipeId || selectedMembreId)" class="btn-clear-filter" @click="clearFilter">
          <i class="bi bi-x"></i> Effacer
        </button>
      </div>

      <div v-if="filterLabel" class="active-filter">
        <i class="bi bi-filter-left"></i>
        Filtre actif : <strong>{{ filterLabel }}</strong>
      </div>
    </div>

    <!-- KPI CARDS -->
    <div class="kpi-grid">
      <!-- Carte Congés -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('conges') }" @click="goToModule('conges')">
        <div class="kpi-icon" style="background: #e3f2fd; color: #1976d2">
          <i class="bi bi-calendar-check"></i>
        </div>
        <div class="kpi-content">
          <h3>Congés</h3>
          <div class="kpi-value">{{ congesSolde }}j</div>
          <div class="kpi-detail">
            <span class="badge-success">{{ congesApprouves }} approuvés</span>
            <span class="badge-warning">{{ congesEnAttente }} en attente</span>
            <span class="badge-danger">{{ congesRefuses }} refusés</span>
            <span class="badge-secondary">{{ congesAnnules }} annulés</span>
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
          <div class="kpi-value">{{ ostieTotal }}</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ ostieEnAttente }} en attente</span>
            <span class="badge-info">{{ ostieTransformes }} transformés</span>
            <span class="badge-secondary">{{ ostieAnnules }} annulés</span>
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
          <div class="kpi-value">{{ permissionsHeures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ permissionsRattrapage.length }} à rattraper</span>
            <span class="badge-info">{{ permissionsRetournees.length }} retournées</span>
            <span class="badge-secondary">{{ permissionsAnnulees }} annulées</span>
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
          <div class="kpi-value">{{ reposHeures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ reposEnAttente.length }} en attente</span>
            <span class="badge-info">{{ reposApprouves }} approuvés</span>
            <span class="badge-secondary">{{ reposAnnules }} annulés</span>
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
          <div class="kpi-value">{{ retardsHeures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ retardsEnCours.length }} en cours</span>
            <span class="badge-success">{{ retardsRattrapes }} rattrapés</span>
            <span class="badge-secondary">{{ retardsAnnules }} annulés</span>
          </div>
        </div>
      </div>
    </div>

    <!-- DEMANDES EN ATTENTE AVEC FILTRE PAR STATUT -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <div class="section-header-with-filter">
        <h2>
          <i class="bi bi-bell"></i>
          Demandes en attente de validation
          <span class="section-badge">{{ totalDemandesFiltrees }}</span>
        </h2>
        
        <!-- Filtre par statut pour les demandes en attente -->
        <div class="status-filter">
          <select v-model="pendingStatusFilter" class="form-select small">
            <option value="en_attente">En attente uniquement</option>
            <option value="approuve">Approuvés</option>
            <option value="refuse">Refusés</option>
            <option value="transforme">Transformés</option>
            <option value="annule">Annulés</option>
            <option value="tous">Tous les statuts</option>
          </select>
        </div>
      </div>
      
      <div v-if="totalDemandesFiltrees === 0" class="empty-state">
        <i class="bi bi-check2-circle"></i>
        <p>Aucune demande{{ filterLabel ? ' pour ce filtre' : '' }}</p>
      </div>

      <div v-else class="pending-grid">
        <!-- Congés -->
        <div v-if="congesFiltresParStatut.length > 0" class="pending-card conges">
          <h3><i class="bi bi-calendar-check"></i> Congés ({{ congesFiltresParStatut.length }})</h3>
          <div class="pending-list">
            <div v-for="conge in congesFiltresParStatut.slice(0, 3)" :key="conge.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(conge.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ conge.utilisateur_details?.display_name }} - {{ conge.utilisateur_details?.username?.toUpperCase() }}</p>
                <p class="item-detail">{{ formatDate(conge.date_debut) }} → {{ formatDate(conge.date_fin) }} <span class="status-badge-small" :class="conge.statut">{{ conge.statut }}</span></p>
              </div>
              <button class="btn-small" @click="goToModule('conges', conge.id)">Voir</button>
            </div>
            <div v-if="congesFiltresParStatut.length > 3" class="more-link" @click="goToModule('conges')">
              + {{ congesFiltresParStatut.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- OSTIE -->
        <div v-if="ostieFiltresParStatut.length > 0" class="pending-card ostie">
          <h3><i class="bi bi-heart-pulse"></i> OSTIE ({{ ostieFiltresParStatut.length }})</h3>
          <div class="pending-list">
            <div v-for="ostie in ostieFiltresParStatut.slice(0, 3)" :key="ostie.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(ostie.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ ostie.utilisateur_details?.display_name }} - {{ ostie.utilisateur_details?.username?.toUpperCase() }}</p>
                <p class="item-detail">{{ formatDate(ostie.date) }} à {{ formatTime(ostie.heure_debut) }} <span class="status-badge-small" :class="ostie.statut">{{ ostie.statut }}</span></p>
              </div>
              <button class="btn-small" @click="goToModule('ostie', ostie.id)">Voir</button>
            </div>
            <div v-if="ostieFiltresParStatut.length > 3" class="more-link" @click="goToModule('ostie')">
              + {{ ostieFiltresParStatut.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Permissions -->
        <div v-if="permissionsFiltresParStatut.length > 0" class="pending-card permissions">
          <h3><i class="bi bi-door-open"></i> Permissions ({{ permissionsFiltresParStatut.length }})</h3>
          <div class="pending-list">
            <div v-for="perm in permissionsFiltresParStatut.slice(0, 3)" :key="perm.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(perm.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ perm.utilisateur_details?.display_name }} - {{ perm.utilisateur_details?.username?.toUpperCase() }}</p>
                <p class="item-detail">{{ formatDate(perm.date) }} - {{ formatTime(perm.heure_depart) }} <span class="status-badge-small" :class="perm.statut">{{ perm.statut }}</span></p>
              </div>
              <button class="btn-small" @click="goToModule('permissions', perm.id)">Voir</button>
            </div>
            <div v-if="permissionsFiltresParStatut.length > 3" class="more-link" @click="goToModule('permissions')">
              + {{ permissionsFiltresParStatut.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Repos médicaux -->
        <div v-if="reposFiltresParStatut.length > 0" class="pending-card repos">
          <h3><i class="bi bi-hospital"></i> Repos médicaux ({{ reposFiltresParStatut.length }})</h3>
          <div class="pending-list">
            <div v-for="repos in reposFiltresParStatut.slice(0, 3)" :key="repos.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(repos.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ repos.utilisateur_details?.display_name }} - {{ repos.utilisateur_details?.username?.toUpperCase() }}</p>
                <p class="item-detail">{{ formatDate(repos.date) }} - {{ repos.duree_heures }}h <span class="status-badge-small" :class="repos.statut">{{ repos.statut }}</span></p>
              </div>
              <button class="btn-small" @click="goToModule('repos', repos.id)">Voir</button>
            </div>
            <div v-if="reposFiltresParStatut.length > 3" class="more-link" @click="goToModule('repos')">
              + {{ reposFiltresParStatut.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Retards -->
        <div v-if="retardsFiltresParStatut.length > 0" class="pending-card retards">
          <h3><i class="bi bi-clock-history"></i> Retards ({{ retardsFiltresParStatut.length }})</h3>
          <div class="pending-list">
            <div v-for="retard in retardsFiltresParStatut.slice(0, 3)" :key="retard.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(retard.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ retard.utilisateur_details?.display_name }} - {{ retard.utilisateur_details?.username?.toUpperCase() }}</p>
                <p class="item-detail">{{ formatDate(retard.date) }} - {{ retard.minutes_retard }}min <span class="status-badge-small" :class="retard.statut">{{ retard.statut }}</span></p>
              </div>
              <button class="btn-small" @click="goToModule('retards', retard.id)">Voir</button>
            </div>
            <div v-if="retardsFiltresParStatut.length > 3" class="more-link" @click="goToModule('retards')">
              + {{ retardsFiltresParStatut.length - 3 }} autres...
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- MES DEMANDES RÉCENTES AVEC FILTRE PAR TYPE -->
    <div class="dashboard-section">
      <div class="section-header-with-filter">
        <h2>
          <i class="bi bi-list-ul"></i>
          Mes dernières demandes
        </h2>
        
        <!-- Filtre par type pour mes demandes -->
        <div class="type-filter">
          <select v-model="myDemandesTypeFilter" class="form-select small">
            <option value="tous">Tous les types</option>
            <option value="conges">Congés</option>
            <option value="ostie">OSTIE</option>
            <option value="permissions">Permissions</option>
            <option value="repos">Repos médicaux</option>
            <option value="retards">Retards</option>
          </select>
        </div>
      </div>
      
      <div v-if="mesDemandesFiltrees.length === 0" class="empty-state">
        <i class="bi bi-inbox"></i>
        <p>Aucune demande récente</p>
      </div>

      <div v-else class="recent-list">
        <div v-for="demande in mesDemandesFiltrees" :key="demande.id" class="recent-item" :class="demande.type">
          <div class="recent-icon" :style="{ background: getTypeColor(demande.type) }">
            <i :class="getTypeIcon(demande.type)"></i>
          </div>
          <div class="recent-content">
            <div class="recent-header">
              <span class="recent-type">{{ getTypeLabel(demande.type) }}</span>
              <span class="recent-badge" :class="demande.statut">{{ demande.statut_display || demande.statut }}</span>
            </div>
            <p class="recent-detail">{{ getDemandeDetail(demande) }}</p>
            <p class="recent-date">{{ formatRelative(demande.date_creation) }}</p>
          </div>
          <button class="btn-small" @click="goToModule(demande.type, demande.id)">Voir</button>
        </div>
      </div>
    </div>

    <!-- APERÇU DE L'ÉQUIPE -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-graph-up"></i>
        Aperçu de {{ filterLabel ? filterLabel : "l'équipe" }}
      </h2>
      
      <div class="team-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">Membres</span>
            <span class="stat-value">{{ teamMembersCount }}</span>
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
        <h3>⏰ Top des retardataires de l'équipe</h3>
        <div class="top-items">
          <div v-for="(item, index) in topRetardataires" :key="item.userId" class="top-item">
            <span class="top-rank">{{ index + 1 }}</span>
            <span class="top-name">{{ item.name }}</span>
            <span class="top-value">{{ item.total.toFixed(2) }}h</span>
          </div>
        </div>
        <p v-if="topRetardataires.length === 0" class="no-data-top">
          Aucun retardataire dans l'équipe
        </p>
      </div>
    </div>

    <!-- STATISTIQUES GLOBALES (SUPER ADMIN) AVEC FILTRES -->
    <div v-if="isSuperAdmin" class="dashboard-section">
      <h2>
        <i class="bi bi-bar-chart"></i>
        Statistiques globales
      </h2>
      
      <!-- Filtres pour les stats globales -->
      <div class="global-stats-filters">
        <div class="filter-group">
          <label>Type :</label>
          <select v-model="globalStatsTypeFilter" class="form-select small">
            <option value="tous">Tous les types</option>
            <option value="conges">Congés</option>
            <option value="ostie">OSTIE</option>
            <option value="permissions">Permissions</option>
            <option value="repos">Repos médicaux</option>
            <option value="retards">Retards</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Année :</label>
          <select v-model="globalStatsYearFilter" class="form-select small">
            <option :value="currentYear">{{ currentYear }}</option>
            <option :value="currentYear - 1">{{ currentYear - 1 }}</option>
            <option :value="currentYear - 2">{{ currentYear - 2 }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>Statut :</label>
          <select v-model="globalStatsStatusFilter" class="form-select small">
            <option value="tous">Tous les statuts</option>
            <option value="approuve">Approuvés</option>
            <option value="en_attente">En attente</option>
            <option value="refuse">Refusés</option>
            <option value="transforme">Transformés</option>
            <option value="annule">Annulés</option>
          </select>
        </div>
      </div>
      
      <div class="global-stats">
        <div class="stats-grid">
          <div class="stats-card">
            <h4>Répartition des absences</h4>
            <div class="pie-chart-placeholder">
              <div class="chart-legend">
                <div v-if="shouldShowType('conges')"><span class="dot conges"></span> Congés: {{ filteredGlobalStats.conges }}</div>
                <div v-if="shouldShowType('ostie')"><span class="dot ostie"></span> OSTIE: {{ filteredGlobalStats.ostie }}</div>
                <div v-if="shouldShowType('permissions')"><span class="dot permissions"></span> Permissions: {{ filteredGlobalStats.permissions }}</div>
                <div v-if="shouldShowType('repos')"><span class="dot repos"></span> Repos: {{ filteredGlobalStats.repos }}</div>
                <div v-if="shouldShowType('retards')"><span class="dot retards"></span> Retards: {{ filteredGlobalStats.retards }}</div>
              </div>
            </div>
          </div>
          
          <div class="stats-card">
            <h4>Évolution mensuelle ({{ globalStatsYearFilter }})</h4>
            <div class="bar-chart-placeholder">
              <div v-for="(mois, index) in moisNoms" :key="index" class="bar-item">
                <span class="bar-label">{{ mois.substring(0,3) }}</span>
                <div class="bar-container">
                  <div 
                    class="bar" 
                    :style="{ width: getFilteredMoisPourcentage(index) + '%', background: getMoisCouleur(index) }"
                    :title="`${mois}: ${filteredEvolutionData[index]} demande(s)`"
                  ></div>
                </div>
                <span class="bar-value">{{ filteredEvolutionData[index] }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useRetardsStore } from '@/store/retards'
import { useEquipesStore } from '@/store/equipes'
import { usePolesStore } from '@/store/poles'
import { useFiltersStore } from '@/store/filters'
import { usersApi } from '@/api/users'
import { equipesApi } from '@/api/equipes'
import { format, parseISO, formatDistanceToNow, getYear, getMonth } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// ========== ROUTER ==========
const router = useRouter()

// ========== STORES ==========
const authStore = useAuthStore()
const congesStore = useCongesStore()
const ostieStore = useOstieStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const retardsStore = useRetardsStore()
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const filtersStore = useFiltersStore()

// ========== STATE ==========
const loading = ref(false)
const currentUser = ref<any>(null)
const membresParEquipe = ref<Record<number, any[]>>({})
const allGerablesMembres = ref<any[]>([])

// Filtres
const filterType = ref<'moi' | 'equipe' | 'membre'>('moi') // 'moi' par défaut
const selectedEquipeId = ref<number | ''>('')
const selectedMembreId = ref<number | ''>('')
const membreSearch = ref('')
const searchTimeout = ref<number | null>(null)

// Nouveaux filtres
const pendingStatusFilter = ref<string>('en_attente')
const myDemandesTypeFilter = ref<string>('tous')
const globalStatsTypeFilter = ref<string>('tous')
const globalStatsYearFilter = ref<number>(getYear(new Date()))
const globalStatsStatusFilter = ref<string>('tous')

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

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'Utilisateur'
})

const currentDate = computed(() => {
  return format(new Date(), 'EEEE d MMMM yyyy', { locale: fr })
})

const currentYear = computed(() => getYear(new Date()))

// ========== COMPUTED - ÉQUIPES GÉRABLES AVEC HIÉRARCHIE ==========
const equipesGerablesHierarchiques = computed(() => {
  if (!equipesStore.arbreEquipes || !currentUser.value) return []
  
  const userId = currentUser.value.id
  
  const collectGerables = (equipes: any[], niveau = 0): any[] => {
    let result: any[] = []
    
    for (const equipe of equipes) {
      const isManager = equipe.manager === userId
      const isCoManager = equipe.co_managers?.includes(userId)
      
      if (isManager || isCoManager) {
        result.push({
          ...equipe,
          niveau
        })
      }
      
      if (equipe.sous_equipes && equipe.sous_equipes.length > 0) {
        result = [...result, ...collectGerables(equipe.sous_equipes, niveau + 1)]
      }
    }
    
    return result
  }
  
  return collectGerables(equipesStore.arbreEquipes)
})

// ========== FONCTION POUR OBTENIR TOUTES LES SOUS-ÉQUIPES ==========
const getAllSousEquipes = (equipe: any): any[] => {
  const sousEquipes: any[] = []
  
  const collect = (eq: any, niveau = 1) => {
    if (eq.sous_equipes && eq.sous_equipes.length) {
      eq.sous_equipes.forEach((sousEq: any) => {
        sousEquipes.push({
          ...sousEq,
          niveau: (eq.niveau || 0) + niveau
        })
        collect(sousEq, niveau + 1)
      })
    }
  }
  
  collect(equipe)
  return sousEquipes
}

// ========== FONCTIONS D'AFFICHAGE POUR LES ÉQUIPES ==========
const getEquipeIcon = (equipe: any): string => {
  if (!equipe.est_actif) return '🚫'
  if (equipe.sous_equipes && equipe.sous_equipes.length > 0) return '📂'
  return '📁'
}

const getEquipeDisplay = (equipe: any): string => {
  let display = equipe.nom
  if (equipe.pole_details) {
    display = `[${equipe.pole_details.code}] ${display}`
  }
  if (!equipe.est_actif) {
    display += ' (inactive)'
  }
  return display
}

// ========== CHARGEMENT DES MEMBRES ==========
const loadMembresEquipe = async (equipeId: number) => {
  if (membresParEquipe.value[equipeId]) return
  
  try {
    const membres = await equipesApi.getMembres(equipeId)
    membresParEquipe.value[equipeId] = membres
  } catch (error) {
    console.error(`Erreur chargement membres équipe ${equipeId}:`, error)
    membresParEquipe.value[equipeId] = []
  }
}

const loadAllGerablesMembres = async () => {
  const tousMembres: any[] = []
  
  for (const equipe of equipesGerablesHierarchiques.value) {
    await loadMembresEquipe(equipe.id)
    const membres = membresParEquipe.value[equipe.id] || []
    
    let equipePath = equipe.nom
    if (equipe.pole_details) {
      equipePath = `${equipe.pole_details.nom} > ${equipePath}`
    }
    
    tousMembres.push(...membres.map((m: any) => ({
      ...m,
      equipe_nom: equipe.nom,
      equipe_path: equipePath,
      equipe_id: equipe.id,
      equipe_niveau: equipe.niveau || 0,
      solde_conge_actuelle: m.solde_conge_actuelle || '0'
    })))
  }
  
  allGerablesMembres.value = tousMembres
}

// ========== COMPUTED - MEMBRES FILTRÉS ==========
const membresFiltres = computed(() => {
  const query = membreSearch.value.toLowerCase().trim()
  if (!query) return allGerablesMembres.value
  
  return allGerablesMembres.value.filter((m: any) => 
    m.display_name?.toLowerCase().includes(query) ||
    m.username?.toLowerCase().includes(query) ||
    m.first_name?.toLowerCase().includes(query) ||
    m.last_name?.toLowerCase().includes(query) ||
    m.pseudo?.toLowerCase().includes(query) ||
    m.equipe_nom?.toLowerCase().includes(query) ||
    m.equipe_path?.toLowerCase().includes(query)
  )
})

// ========== COMPUTED - FILTRE LABEL ==========
const filterLabel = computed(() => {
  if (filterType.value === 'moi') {
    return `Moi (${displayName.value})`
  }
  if (selectedMembreId.value) {
    const membre = allGerablesMembres.value.find(m => m.id === selectedMembreId.value)
    return membre ? `${membre.display_name} (${membre.username.toUpperCase()})` : ''
  }
  if (selectedEquipeId.value) {
    const findEquipe = (equipes: any[]): any => {
      for (const eq of equipes) {
        if (eq.id === selectedEquipeId.value) return eq
        if (eq.sous_equipes) {
          const found = findEquipe(eq.sous_equipes)
          if (found) return found
        }
      }
      return null
    }
    
    const equipe = findEquipe(equipesStore.arbreEquipes || [])
    if (equipe) {
      let path = equipe.nom
      if (equipe.pole_details) {
        path = `${equipe.pole_details.nom} - ${path}`
      }
      return path
    }
    return ''
  }
  return ''
})

// ========== FILTRAGE RÉCURSIF DES MEMBRES PAR ÉQUIPE ==========
const getMembresEquipeRecursif = (equipeId: number): number[] => {
  const membres: number[] = []
  
  const membresEquipe = membresParEquipe.value[equipeId] || []
  membres.push(...membresEquipe.map((m: any) => m.id))
  
  const trouverEquipe = (equipes: any[]): any => {
    for (const eq of equipes) {
      if (eq.id === equipeId) return eq
      if (eq.sous_equipes) {
        const found = trouverEquipe(eq.sous_equipes)
        if (found) return found
      }
    }
    return null
  }
  
  const equipe = trouverEquipe(equipesStore.arbreEquipes || [])
  
  if (equipe?.sous_equipes) {
    const collectMembresSousEquipes = (sousEqs: any[]) => {
      sousEqs.forEach((sousEq: any) => {
        const membresSousEq = membresParEquipe.value[sousEq.id] || []
        membres.push(...membresSousEq.map((m: any) => m.id))
        if (sousEq.sous_equipes) {
          collectMembresSousEquipes(sousEq.sous_equipes)
        }
      })
    }
    collectMembresSousEquipes(equipe.sous_equipes)
  }
  
  return [...new Set(membres)]
}

const getMembresEquipeIds = (equipeId: number): number[] => {
  return getMembresEquipeRecursif(equipeId)
}

const getAllGerablesMembresIds = (): number[] => {
  return allGerablesMembres.value.map((m: any) => m.id)
}

// ========== FONCTIONS DE CONVERSION DES DONNÉES DU CALENDRIER ==========
const getCongesFromCalendar = () => {
  if (!congesStore.calendrierEvents) return []
  
  return congesStore.calendrierEvents
    .filter(event => event.type === 'conge')
    .map((event: any) => {
      const membre = allGerablesMembres.value.find((m: any) => m.id === event.user_id)
      
      return {
        id: parseInt(String(event.id).replace('conge_', '')),
        utilisateur: event.user_id,
        date_debut: event.start.split('T')[0],
        date_fin: event.end ? event.end.split('T')[0] : event.start.split('T')[0],
        statut: event.statut,
        utilisateur_details: membre ? {
          display_name: membre.display_name,
          username: membre.username,
          pseudo: membre.pseudo
        } : event.utilisateur_details,
        jours_deduits: event.jours_deduits,
        type_conge: event.type_conge,
        date_creation: event.date_creation
      }
    })
}

const getOstieFromCalendar = () => {
  if (!ostieStore.calendrierEvents) return []
  
  return ostieStore.calendrierEvents
    .filter(event => event.type === 'ostie')
    .map((event: any) => {
      const membre = allGerablesMembres.value.find((m: any) => m.id === event.user_id)
      
      return {
        id: parseInt(String(event.id).replace('ostie_', '')),
        utilisateur: event.user_id,
        date: event.start.split('T')[0],
        heure_debut: event.heure_debut,
        statut: event.statut,
        utilisateur_details: membre ? {
          display_name: membre.display_name,
          username: membre.username,
          pseudo: membre.pseudo
        } : event.utilisateur_details,
        date_creation: event.date_creation
      }
    })
}

const getPermissionsFromCalendar = () => {
  if (!permissionsStore.calendrierEvents) return []
  
  return permissionsStore.calendrierEvents
    .filter(event => event.type === 'permission')
    .map((event: any) => {
      const membre = allGerablesMembres.value.find((m: any) => m.id === event.user_id)
      
      return {
        id: parseInt(String(event.id).replace('perm_', '')),
        utilisateur: event.user_id,
        date: event.start.split('T')[0],
        heure_depart: event.heure_depart,
        statut: event.statut,
        utilisateur_details: membre ? {
          display_name: membre.display_name,
          username: membre.username,
          pseudo: membre.pseudo
        } : event.utilisateur_details,
        heures_a_rattraper: event.heures_restantes,
        heures_restantes: event.heures_restantes,
        date_creation: event.date_creation
      }
    })
}

const getReposFromCalendar = () => {
  if (!reposStore.calendrierEvents) return []
  
  return reposStore.calendrierEvents
    .filter(event => event.type === 'repos_medical')
    .map((event: any) => {
      const membre = allGerablesMembres.value.find((m: any) => m.id === event.user_id)
      
      return {
        id: parseInt(String(event.id).replace('repos_', '')),
        utilisateur: event.user_id,
        date: event.start.split('T')[0],
        duree_heures: event.duree_heures,
        statut: event.statut,
        utilisateur_details: membre ? {
          display_name: membre.display_name,
          username: membre.username,
          pseudo: membre.pseudo
        } : event.utilisateur_details,
        date_creation: event.date_creation
      }
    })
}

const getRetardsFromCalendar = () => {
  if (!retardsStore.calendrierEvents) return []
  
  return retardsStore.calendrierEvents
    .filter(event => event.type === 'retard')
    .map((event: any) => {
      const membre = allGerablesMembres.value.find((m: any) => m.id === event.user_id)
      
      return {
        id: parseInt(String(event.id).replace('retard_', '')),
        utilisateur: event.user_id,
        date: event.start.split('T')[0],
        statut: event.statut,
        minutes_retard: event.minutes_retard,
        heures_a_rattraper: event.heures_restantes,
        heures_restantes: event.heures_restantes,
        utilisateur_details: membre ? {
          display_name: membre.display_name,
          username: membre.username,
          pseudo: membre.pseudo
        } : event.utilisateur_details,
        date_creation: event.date_creation
      }
    })
}

// ========== FILTRAGE DES DONNÉES PAR ÉQUIPE/MEMBRE ==========
const getCurrentFilteredUserIds = (): number[] => {
  if (filterType.value === 'moi' && authStore.user) {
    return [authStore.user.id]
  }
  if (selectedMembreId.value) {
    return [selectedMembreId.value]
  }
  if (selectedEquipeId.value) {
    return getMembresEquipeIds(selectedEquipeId.value)
  }
  if (isManagerOrHigher.value) {
    return getAllGerablesMembresIds()
  }
  return []
}

const congesFiltres = computed(() => {
  let data = getCongesFromCalendar()
  const userIds = getCurrentFilteredUserIds()
  
  if (userIds.length > 0) {
    data = data.filter((c: any) => userIds.includes(c.utilisateur))
  }
  
  return data
})

const ostieFiltres = computed(() => {
  let data = getOstieFromCalendar()
  const userIds = getCurrentFilteredUserIds()
  
  if (userIds.length > 0) {
    data = data.filter((o: any) => userIds.includes(o.utilisateur))
  }
  
  return data
})

const permissionsFiltres = computed(() => {
  let data = getPermissionsFromCalendar()
  const userIds = getCurrentFilteredUserIds()
  
  if (userIds.length > 0) {
    data = data.filter((p: any) => userIds.includes(p.utilisateur))
  }
  
  return data
})

const reposFiltres = computed(() => {
  let data = getReposFromCalendar()
  const userIds = getCurrentFilteredUserIds()
  
  if (userIds.length > 0) {
    data = data.filter((r: any) => userIds.includes(r.utilisateur))
  }
  
  return data
})

const retardsFiltres = computed(() => {
  let data = getRetardsFromCalendar()
  const userIds = getCurrentFilteredUserIds()
  
  if (userIds.length > 0) {
    data = data.filter((r: any) => userIds.includes(r.utilisateur))
  }
  
  return data
})

// ========== FILTRES PAR STATUT POUR LES DEMANDES EN ATTENTE ==========
const congesFiltresParStatut = computed(() => {
  if (pendingStatusFilter.value === 'tous') return congesFiltres.value
  return congesFiltres.value.filter((c: any) => c.statut === pendingStatusFilter.value)
})

const ostieFiltresParStatut = computed(() => {
  if (pendingStatusFilter.value === 'tous') return ostieFiltres.value
  return ostieFiltres.value.filter((o: any) => o.statut === pendingStatusFilter.value)
})

const permissionsFiltresParStatut = computed(() => {
  if (pendingStatusFilter.value === 'tous') return permissionsFiltres.value
  return permissionsFiltres.value.filter((p: any) => p.statut === pendingStatusFilter.value)
})

const reposFiltresParStatut = computed(() => {
  if (pendingStatusFilter.value === 'tous') return reposFiltres.value
  return reposFiltres.value.filter((r: any) => r.statut === pendingStatusFilter.value)
})

const retardsFiltresParStatut = computed(() => {
  if (pendingStatusFilter.value === 'tous') return retardsFiltres.value
  return retardsFiltres.value.filter((r: any) => r.statut === pendingStatusFilter.value)
})

const totalDemandesFiltrees = computed(() => {
  return congesFiltresParStatut.value.length +
         ostieFiltresParStatut.value.length +
         permissionsFiltresParStatut.value.length +
         reposFiltresParStatut.value.length +
         retardsFiltresParStatut.value.length
})

// ========== COMPUTED - STATS ==========
const congesSolde = computed(() => {
  if (selectedMembreId.value) {
    const membre = allGerablesMembres.value.find(m => m.id === selectedMembreId.value)
    return membre?.solde_conge_actuelle || '0'
  }
  if (filterType.value === 'moi') {
    return authStore.soldeConge?.actuelle || '0'
  }
  return authStore.soldeConge?.actuelle || '0'
})

const congesApprouves = computed(() => congesFiltres.value.filter((c: any) => c.statut === 'approuve').length)
const congesEnAttente = computed(() => congesFiltres.value.filter((c: any) => c.statut === 'en_attente').length)
const congesRefuses = computed(() => congesFiltres.value.filter((c: any) => c.statut === 'refuse').length)
const congesAnnules = computed(() => congesFiltres.value.filter((c: any) => c.statut === 'annule').length)

const ostieTotal = computed(() => ostieFiltres.value.length)
const ostieEnAttente = computed(() => ostieFiltres.value.filter((o: any) => o.statut === 'en_attente').length)
const ostieTransformes = computed(() => ostieFiltres.value.filter((o: any) => o.statut === 'transforme').length)
const ostieAnnules = computed(() => ostieFiltres.value.filter((o: any) => o.statut === 'annule').length)

const permissionsHeures = computed(() => {
  const total = permissionsFiltres.value.reduce((acc: number, p: any) => {
    return acc + (parseFloat(p.heures_a_rattraper) || 0)
  }, 0)
  return total.toFixed(2)
})

const permissionsRattrapage = computed(() => permissionsFiltres.value.filter((p: any) => p.statut === 'rattrapage'))
const permissionsRetournees = computed(() => permissionsFiltres.value.filter((p: any) => p.statut === 'retourne'))
const permissionsAnnulees = computed(() => permissionsFiltres.value.filter((p: any) => p.statut === 'annule').length)

const reposHeures = computed(() => {
  const total = reposFiltres.value.reduce((acc: number, r: any) => {
    return acc + (parseFloat(r.duree_heures) || 0)
  }, 0)
  return total.toFixed(2)
})

const reposEnAttente = computed(() => reposFiltres.value.filter((r: any) => r.statut === 'en_attente'))
const reposApprouves = computed(() => reposFiltres.value.filter((r: any) => r.statut === 'approuve').length)
const reposAnnules = computed(() => reposFiltres.value.filter((r: any) => r.statut === 'annule').length)

const retardsHeures = computed(() => {
  const total = retardsFiltres.value.reduce((acc: number, r: any) => {
    return acc + (parseFloat(r.heures_a_rattraper) || 0)
  }, 0)
  return total.toFixed(2)
})

const retardsEnCours = computed(() => retardsFiltres.value.filter((r: any) => r.statut === 'en_attente' || r.statut === 'en_cours'))
const retardsRattrapes = computed(() => retardsFiltres.value.filter((r: any) => r.statut === 'approuve').length)
const retardsAnnules = computed(() => retardsFiltres.value.filter((r: any) => r.statut === 'annule').length)

// ========== STATS ÉQUIPE ==========
const teamMembersCount = computed(() => {
  if (filterType.value === 'moi') return 1
  if (selectedMembreId.value) return 1
  if (selectedEquipeId.value) {
    return getMembresEquipeIds(selectedEquipeId.value).length
  }
  return allGerablesMembres.value.length
})

const absentsAujourdhui = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  const userIds = new Set<number>()
  
  congesFiltres.value
    .filter((c: any) => c.statut === 'approuve' && c.date_debut <= today && c.date_fin >= today)
    .forEach((c: any) => userIds.add(c.utilisateur))
  
  ostieFiltres.value
    .filter((o: any) => (o.statut === 'approuve' || o.statut === 'transforme') && o.date === today)
    .forEach((o: any) => userIds.add(o.utilisateur))
  
  reposFiltres.value
    .filter((r: any) => r.statut === 'approuve' && r.date === today)
    .forEach((r: any) => userIds.add(r.utilisateur))
  
  return userIds.size
})

const retardsAujourdhui = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  return retardsFiltres.value.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && r.date === today
  ).length
})

const tauxAbsenteisme = computed(() => {
  if (teamMembersCount.value === 0) return 0
  return ((absentsAujourdhui.value / teamMembersCount.value) * 100).toFixed(1)
})

// ========== TOP RETARDATAIRES ==========
const topRetardataires = computed(() => {
  if (!isManagerOrHigher.value) return []
  
  const stats: Record<number, { name: string; total: number }> = {}
  
  retardsFiltres.value.forEach((retard: any) => {
    if (retard.statut === 'approuve' || retard.statut === 'en_cours') {
      const userId = retard.utilisateur
      const heures = parseFloat(retard.heures_a_rattraper || '0')
      
      if (heures > 0) {
        if (!stats[userId]) {
          let userName = retard.utilisateur_details?.display_name
          
          if (!userName) {
            const membre = allGerablesMembres.value.find((m: any) => m.id === userId)
            userName = membre?.display_name
          }
          
          stats[userId] = {
            name: userName || `Utilisateur ${userId}`,
            total: 0
          }
        }
        stats[userId].total += heures
      }
    }
  })
  
  return Object.entries(stats)
    .map(([userId, data]) => ({
      userId: parseInt(userId),
      name: data.name,
      total: data.total
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 5)
})

// ========== MES DEMANDES AVEC FILTRE ==========
const mesDemandes = computed(() => {
  const demandes: any[] = []
  const userId = authStore.user?.id

  if (congesStore.conges) {
    congesStore.conges.forEach((c: any) => {
      if (c.utilisateur === userId) {
        demandes.push({ ...c, type: 'conges' })
      }
    })
  }

  if (ostieStore.osties) {
    ostieStore.osties.forEach((o: any) => {
      if (o.utilisateur === userId) {
        demandes.push({ ...o, type: 'ostie' })
      }
    })
  }

  if (permissionsStore.permissions) {
    permissionsStore.permissions.forEach((p: any) => {
      if (p.utilisateur === userId) {
        demandes.push({ ...p, type: 'permissions' })
      }
    })
  }

  if (reposStore.reposMedicaux) {
    reposStore.reposMedicaux.forEach((r: any) => {
      if (r.utilisateur === userId) {
        demandes.push({ ...r, type: 'repos' })
      }
    })
  }

  if (retardsStore.retards) {
    retardsStore.retards.forEach((r: any) => {
      if (r.utilisateur === userId) {
        demandes.push({ ...r, type: 'retards' })
      }
    })
  }

  return demandes
    .sort((a, b) => new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime())
})

const mesDemandesFiltrees = computed(() => {
  if (myDemandesTypeFilter.value === 'tous') return mesDemandes.value.slice(0, 10)
  return mesDemandes.value
    .filter(d => d.type === myDemandesTypeFilter.value)
    .slice(0, 10)
})

// ========== STATS GLOBALES FILTRÉES ==========
const filteredGlobalStats = computed(() => {
  let congesCount = 0
  let ostieCount = 0
  let permissionsCount = 0
  let reposCount = 0
  let retardsCount = 0
  
  // Filtrer les données selon les critères
  const filterByYearAndStatus = (items: any[], type: string) => {
    return items.filter((item: any) => {
      // Filtre par année
      let itemDate
      if (type === 'conges') {
        itemDate = parseISO(item.date_debut)
      } else {
        itemDate = parseISO(item.date || item.date_creation)
      }
      if (getYear(itemDate) !== globalStatsYearFilter.value) return false
      
      // Filtre par statut
      if (globalStatsStatusFilter.value !== 'tous' && item.statut !== globalStatsStatusFilter.value) return false
      
      return true
    })
  }
  
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'conges') {
    congesCount = filterByYearAndStatus(congesStore.conges || [], 'conges').length
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'ostie') {
    ostieCount = filterByYearAndStatus(ostieStore.osties || [], 'ostie').length
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'permissions') {
    permissionsCount = filterByYearAndStatus(permissionsStore.permissions || [], 'permissions').length
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'repos') {
    reposCount = filterByYearAndStatus(reposStore.reposMedicaux || [], 'repos').length
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'retards') {
    retardsCount = filterByYearAndStatus(retardsStore.retards || [], 'retards').length
  }
  
  return {
    conges: congesCount,
    ostie: ostieCount,
    permissions: permissionsCount,
    repos: reposCount,
    retards: retardsCount
  }
})

const filteredEvolutionData = computed(() => {
  const mois = Array(12).fill(0)
  
  let allDemandes: any[] = []
  
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'conges') {
    allDemandes = [...allDemandes, ...(congesStore.conges || [])]
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'ostie') {
    allDemandes = [...allDemandes, ...(ostieStore.osties || [])]
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'permissions') {
    allDemandes = [...allDemandes, ...(permissionsStore.permissions || [])]
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'repos') {
    allDemandes = [...allDemandes, ...(reposStore.reposMedicaux || [])]
  }
  if (globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === 'retards') {
    allDemandes = [...allDemandes, ...(retardsStore.retards || [])]
  }
  
  allDemandes.forEach((d: any) => {
    try {
      // Filtre par année
      const date = parseISO(d.date_creation || d.date || d.date_debut)
      if (getYear(date) !== globalStatsYearFilter.value) return
      
      // Filtre par statut
      if (globalStatsStatusFilter.value !== 'tous' && d.statut !== globalStatsStatusFilter.value) return
      
      const moisIndex = getMonth(date)
      mois[moisIndex]++
    } catch (e) {}
  })
  
  return mois
})


const getFilteredMoisPourcentage = (moisIndex: number) => {
  const max = Math.max(...filteredEvolutionData.value, 1)
  return (filteredEvolutionData.value[moisIndex] / max) * 100
}

const shouldShowType = (type: string): boolean => {
  return globalStatsTypeFilter.value === 'tous' || globalStatsTypeFilter.value === type
}



// ========== GRAPH ==========


// ========== METHODS ==========
const setFilterMoi = () => {
  filterType.value = 'moi'
  selectedEquipeId.value = ''
  selectedMembreId.value = ''
  membreSearch.value = ''
}

const canViewDetails = (module: string) => true

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

// ========== GESTION DES FILTRES ==========
const onMembreSearch = () => {
  if (searchTimeout.value !== null) clearTimeout(searchTimeout.value)
  searchTimeout.value = window.setTimeout(() => {}, 300)
}

const onEquipeChange = () => {
  selectedMembreId.value = ''
  membreSearch.value = ''
  filterType.value = 'equipe'
}

const onMembreChange = () => {
  selectedEquipeId.value = ''
  filterType.value = 'membre'
}

const clearFilter = () => {
  filterType.value = 'equipe'
  selectedEquipeId.value = ''
  selectedMembreId.value = ''
  membreSearch.value = ''
}

// ========== RAFRAÎCHISSEMENT CORRIGÉ ==========
const refreshAllData = async () => {
  loading.value = true
  
  const currentYear = getYear(new Date())
  
  // Paramètres pour charger toutes les données de l'année
  const params = { annee: currentYear }
  
  console.log('=== CHARGEMENT DES DONNÉES POUR TOUTE L\'ÉQUIPE ===')
  
  await Promise.allSettled([
    // Congés - utiliser le calendrier qui contient toutes les données
    congesStore.fetchCalendrier(params),
    congesStore.fetchMesConges(currentYear),
    
    // OSTIE - utiliser le calendrier
    ostieStore.fetchCalendrier(params),
    ostieStore.fetchMesOsties(currentYear),
    
    // Permissions - utiliser le calendrier
    permissionsStore.fetchCalendrier(params),
    permissionsStore.fetchMesPermissions(currentYear),
    
    // Repos médicaux - utiliser le calendrier
    reposStore.fetchCalendrier(params),
    reposStore.fetchMesRepos(currentYear),
    
    // Retards - utiliser le calendrier
    retardsStore.fetchCalendrier(params),
    retardsStore.fetchMesRetards(currentYear),
    
    authStore.refreshSolde(),
    equipesStore.fetchArbre(true)
  ])
  
  console.log('=== DONNÉES CHARGÉES DANS LES STORES ===')
  console.log('Congés (calendrier):', congesStore.calendrierEvents?.length || 0)
  console.log('OSTIE (calendrier):', ostieStore.calendrierEvents?.length || 0)
  console.log('Permissions (calendrier):', permissionsStore.calendrierEvents?.length || 0)
  console.log('Repos (calendrier):', reposStore.calendrierEvents?.length || 0)
  console.log('Retards (calendrier):', retardsStore.calendrierEvents?.length || 0)
  
  // Charger les membres des équipes gérables
  await loadAllGerablesMembres()
  
  loading.value = false
}

const fetchCurrentUser = async () => {
  try {
    currentUser.value = await usersApi.getCurrentUser()
  } catch (err) {
    currentUser.value = authStore.user
  }
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await fetchCurrentUser()
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await equipesStore.fetchArbre(true)
  await refreshAllData()
})

onUnmounted(() => {
  if (searchTimeout.value !== null) clearTimeout(searchTimeout.value)
})
</script>




<style scoped>
/* Tous les styles précédents restent identiques */
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

.role-superadmin { background: #ffd700; color: #000; }
.role-admin { background: #1976d2; color: white; }
.role-manager { background: #388e3c; color: white; }
.role-user { background: #757575; color: white; }

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

.btn-refresh:hover { background: #f5f5f5; }
.btn-refresh:disabled { opacity: 0.5; cursor: not-allowed; }

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

.filter-tab:hover { background: rgba(255,255,255,0.5); }

.equipe-selector, .membre-selector { flex: 1; min-width: 250px; }

.form-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  background: white;
}

.form-select option {
  padding: 4px 8px;
}

.help-text {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 5px;
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

.clear-search {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  padding: 4px;
}

.clear-search:hover { color: #f44336; }

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

.kpi-card.clickable { cursor: pointer; }
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

.kpi-content { flex: 1; }
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

.badge-success { background: #e8f5e9; color: #2e7d32; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.badge-warning { background: #fff3e0; color: #f57c00; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.badge-danger { background: #ffebee; color: #c62828; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.badge-info { background: #e3f2fd; color: #1976d2; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
.badge-secondary { background: #f5f5f5; color: #757575; padding: 2px 6px; border-radius: 4px; font-size: 11px; }

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

.pending-list { display: flex; flex-direction: column; gap: 10px; }

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

.item-content { flex: 1; }
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
.btn-small:hover { background: #e0e0e0; }

.more-link {
  text-align: center;
  font-size: 12px;
  color: #1976d2;
  cursor: pointer;
  padding: 8px;
}
.more-link:hover { text-decoration: underline; }

.empty-state {
  text-align: center;
  padding: 40px;
  color: #999;
}
.empty-state i { font-size: 48px; margin-bottom: 10px; }

/* Mes demandes récentes */
.recent-list { display: flex; flex-direction: column; gap: 10px; }

.recent-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 10px;
  transition: background 0.2s;
}
.recent-item:hover { background: #f0f0f0; }

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

.recent-content { flex: 1; }
.recent-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 4px;
}

.recent-type { font-weight: 500; }

.recent-badge {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 4px;
}
.recent-badge.en_attente { background: #fff3e0; color: #f57c00; }
.recent-badge.approuve, .recent-badge.valide { background: #e8f5e9; color: #2e7d32; }
.recent-badge.refuse, .recent-badge.annule { background: #ffebee; color: #c62828; }
.recent-badge.transforme { background: #e3f2fd; color: #1976d2; }

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
.team-stats { margin-bottom: 20px; }
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

/* Top list */
.top-list { margin-top: 20px; }
.top-list h3 {
  font-size: 16px;
  margin: 0 0 15px 0;
}
.top-items { display: flex; flex-direction: column; gap: 8px; }
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
.top-name { flex: 1; }
.top-value { font-weight: bold; color: #c62828; }
.no-data-top {
  text-align: center;
  color: #999;
  font-size: 14px;
  padding: 10px;
}

/* Global stats */
.global-stats { margin-top: 20px; }
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
.chart-legend { display: flex; flex-direction: column; gap: 10px; }
.chart-legend div { display: flex; align-items: center; gap: 8px; }

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

.bar-chart-placeholder { display: flex; flex-direction: column; gap: 8px; }
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

/* Utilitaires */
.spin { animation: spin 1s linear infinite; }
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .dashboard-header { flex-direction: column; align-items: flex-start; }
  .kpi-grid { grid-template-columns: 1fr; }
  .pending-grid { grid-template-columns: 1fr; }
  .stat-row { grid-template-columns: 1fr 1fr; }
  .member-filter { flex-direction: column; align-items: stretch; }
  .filter-tabs { justify-content: center; }
}
</style>