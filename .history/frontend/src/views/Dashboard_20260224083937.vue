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
    <!-- FILTRES PAR ÉQUIPE/MEMBRE (Manager+)         -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="filters-section">
      <div class="filters-header">
        <h3>
          <i class="bi bi-funnel"></i>
          Filtrer les statistiques
        </h3>
        <button v-if="selectedUser || selectedEquipe" class="btn-clear-filters" @click="clearFilters">
          <i class="bi bi-x-circle"></i> Effacer les filtres
        </button>
      </div>
      
      <div class="filters-grid">
        <!-- Sélection d'équipe (arbre) -->
        <div class="filter-group">
          <label>Équipe</label>
          <div class="team-selector">
            <button class="select-button" @click="showTeamDropdown = !showTeamDropdown">
              <span>{{ selectedEquipeNom || 'Toutes les équipes' }}</span>
              <i class="bi" :class="showTeamDropdown ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
            </button>
            
            <div v-if="showTeamDropdown" class="team-dropdown">
              <div class="dropdown-header">
                <input 
                  v-model="teamSearch" 
                  placeholder="Rechercher une équipe..."
                  class="search-input"
                  @click.stop
                />
              </div>
              <div class="dropdown-tree">
                <div 
                  v-for="equipe in filteredTeamTree" 
                  :key="equipe.id"
                  class="team-node"
                  :style="{ marginLeft: `${equipe._level * 20}px` }"
                >
                  <button 
                    class="team-option"
                    :class="{ selected: selectedEquipeId === equipe.id }"
                    @click="selectEquipe(equipe)"
                  >
                    <i class="bi" :class="equipe.sous_equipes?.length ? 'bi-folder' : 'bi-folder2'"></i>
                    {{ equipe.nom }}
                    <span class="team-count">({{ getMembresCount(equipe) }})</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Sélection de membre -->
        <div class="filter-group">
          <label>Membre</label>
          <div class="member-selector">
            <button class="select-button" @click="showMemberDropdown = !showMemberDropdown" :disabled="!selectedEquipe">
              <span>{{ selectedMemberNom || 'Tous les membres' }}</span>
              <i class="bi" :class="showMemberDropdown ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
            </button>
            
            <div v-if="showMemberDropdown && selectedEquipe" class="member-dropdown">
              <div class="dropdown-header">
                <input 
                  v-model="memberSearch" 
                  placeholder="Rechercher un membre..."
                  class="search-input"
                  @click.stop
                />
              </div>
              <div class="dropdown-list">
                <button 
                  class="member-option"
                  :class="{ selected: !selectedMemberId }"
                  @click="selectMember(null)"
                >
                  <i class="bi bi-people"></i>
                  Tous les membres
                </button>
                <div v-if="loadingMembres" class="loading-small">
                  <i class="bi bi-arrow-repeat spin"></i> Chargement...
                </div>
                <button 
                  v-for="membre in filteredMembres" 
                  :key="membre.id"
                  class="member-option"
                  :class="{ selected: selectedMemberId === membre.id }"
                  @click="selectMember(membre)"
                >
                  <i class="bi bi-person-circle"></i>
                  {{ getMembreDisplayName(membre) }}
                  <span class="member-matricule">{{ membre.username.toUpperCase() }}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Badge actif -->
      <div v-if="selectedMemberObj || selectedEquipeObj" class="active-filter-badge">
        <i class="bi bi-funnel-fill"></i>
        {{ filterDescription }}
      </div>
    </div>

    <!-- ============================================ -->
    <!-- KPI CARDS (adaptés au filtre)               -->
    <!-- ============================================ -->
    <div class="kpi-grid">
      <!-- Carte Congés -->
      <div class="kpi-card" :class="{ 'clickable': canViewDetails('conges') }" @click="goToModule('conges')">
        <div class="kpi-icon" style="background: #e3f2fd; color: #1976d2">
          <i class="bi bi-calendar-check"></i>
        </div>
        <div class="kpi-content">
          <h3>Congés</h3>
          <div class="kpi-value">{{ filteredStats.conges.solde }}j</div>
          <div class="kpi-detail">
            <span class="badge-success">{{ filteredStats.conges.approuves }} approuvés</span>
            <span class="badge-warning">{{ filteredStats.conges.enAttente }} en attente</span>
            <span class="badge-danger">{{ filteredStats.conges.refuses }} refusés</span>
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
          <div class="kpi-value">{{ filteredStats.ostie.total }}</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ filteredStats.ostie.enAttente }} en attente</span>
            <span class="badge-info">{{ filteredStats.ostie.transformes }} transformés</span>
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
          <div class="kpi-value">{{ filteredStats.permissions.heures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ filteredStats.permissions.aRattraper }} à rattraper</span>
            <span class="badge-info">{{ filteredStats.permissions.retournees }} retournées</span>
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
          <div class="kpi-value">{{ filteredStats.repos.heures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ filteredStats.repos.enAttente }} en attente</span>
            <span class="badge-info">{{ filteredStats.repos.approuves }} approuvés</span>
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
          <div class="kpi-value">{{ filteredStats.retards.heures }}h</div>
          <div class="kpi-detail">
            <span class="badge-warning">{{ filteredStats.retards.enCours }} en cours</span>
            <span class="badge-success">{{ filteredStats.retards.rattrapes }} rattrapés</span>
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
      </h2>
      
      <div v-if="totalEnAttente === 0" class="empty-state">
        <i class="bi bi-check2-circle"></i>
        <p>Aucune demande en attente</p>
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
        Mes dernières demandes
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
            <p class="recent-date">{{ formatRelative(demande.date_creation) }}</p>
          </div>
          <button class="btn-small" @click="goToModule(demande.type, demande.id)">Voir</button>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION MANAGER/ADMIN - Stats équipe réelle  -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-graph-up"></i>
        Aperçu de l'équipe {{ selectedEquipeNom ? `- ${selectedEquipeNom}` : '' }}
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

      <!-- Top retardataires de l'équipe -->
      <div v-if="topRetardatairesEquipe.length > 0" class="top-list">
        <h3>⏰ Top des retardataires de l'équipe</h3>
        <div class="top-items">
          <div v-for="(item, index) in topRetardatairesEquipe" :key="item.userId" class="top-item">
            <span class="top-rank">{{ index + 1 }}</span>
            <span class="top-name">{{ item.name }}</span>
            <span class="top-value">{{ item.total.toFixed(2) }}h</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION SUPER ADMIN - Stats globales RÉELLES -->
    <!-- ============================================ -->
    <div v-if="isSuperAdmin" class="dashboard-section">
      <h2>
        <i class="bi bi-bar-chart"></i>
        Statistiques globales
      </h2>
      
      <div class="global-stats">
        <div class="stats-grid">
          <div class="stats-card">
            <h4>Répartition des absences</h4>
            <div class="pie-chart-placeholder">
              <div class="chart-legend">
                <div><span class="dot conges"></span> Congés: {{ globalStats.conges }}</div>
                <div><span class="dot ostie"></span> OSTIE: {{ globalStats.ostie }}</div>
                <div><span class="dot permissions"></span> Permissions: {{ globalStats.permissions }}</div>
                <div><span class="dot repos"></span> Repos: {{ globalStats.repos }}</div>
                <div><span class="dot retards"></span> Retards: {{ globalStats.retards }}</div>
              </div>
            </div>
          </div>
          
          <div class="stats-card">
            <h4>Évolution mensuelle ({{ currentYear }})</h4>
            <div class="bar-chart-placeholder">
              <div v-for="(mois, index) in moisNoms" :key="index" class="bar-item">
                <span class="bar-label">{{ mois.substring(0,3) }}</span>
                <div class="bar-container">
                  <div 
                    class="bar" 
                    :style="{ 
                      width: getMoisPourcentage(index) + '%', 
                      background: getMoisCouleur(index) 
                    }"
                  ></div>
                </div>
                <span class="bar-value">{{ evolutionMensuelle[index] }}</span>
              </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useRetardsStore } from '@/store/retards'
import { useEquipesStore } from '@/store/equipes'
import { useFiltersStore } from '@/store/filters'
import { format, parseISO, formatDistanceToNow, differenceInMinutes, getYear, getMonth } from 'date-fns'
import { fr } from 'date-fns/locale/fr'
import type { Equipe } from '@/types/user'

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
const filtersStore = useFiltersStore()

// ========== STATE ==========
const loading = ref(false)

// Filtres équipe/membre
const showTeamDropdown = ref(false)
const showMemberDropdown = ref(false)
const teamSearch = ref('')
const memberSearch = ref('')
const selectedEquipeId = ref<number | null>(null)
const selectedEquipeObj = ref<Equipe | null>(null)
const selectedMemberId = ref<number | null>(null)
const selectedMemberObj = ref<any | null>(null)
const loadingMembres = ref(false)
const membresEquipe = ref<any[]>([])

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

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'Utilisateur'
})

const currentDate = computed(() => {
  return format(new Date(), 'EEEE d MMMM yyyy', { locale: fr })
})

// ========== FILTRES ÉQUIPE/MEMBRE ==========
const selectedEquipeNom = computed(() => {
  if (!selectedEquipeObj.value) return null
  return selectedEquipeObj.value.nom
})

const selectedMemberNom = computed(() => {
  if (!selectedMemberObj.value) return null
  return getMembreDisplayName(selectedMemberObj.value)
})

const filterDescription = computed(() => {
  if (selectedMemberObj.value) {
    return `Membre: ${selectedMemberNom.value}`
  }
  if (selectedEquipeObj.value) {
    return `Équipe: ${selectedEquipeNom.value}`
  }
  return ''
})

const canViewDetails = (module: string) => true

// Arbre des équipes avec niveau pour l'affichage
const teamTreeWithLevel = computed(() => {
  const addLevel = (equipes: any[], level = 0): any[] => {
    return equipes.map(e => ({
      ...e,
      _level: level,
      sous_equipes: e.sous_equipes ? addLevel(e.sous_equipes, level + 1) : []
    }))
  }
  return addLevel(equipesStore.arbreEquipes || [])
})

const filteredTeamTree = computed(() => {
  if (!teamSearch.value) return teamTreeWithLevel.value
  
  const searchLower = teamSearch.value.toLowerCase()
  const filterTree = (nodes: any[]): any[] => {
    return nodes.filter(node => {
      const match = node.nom.toLowerCase().includes(searchLower)
      const childrenMatch = node.sous_equipes?.length ? filterTree(node.sous_equipes).length > 0 : false
      return match || childrenMatch
    }).map(node => ({
      ...node,
      sous_equipes: node.sous_equipes ? filterTree(node.sous_equipes) : []
    }))
  }
  
  return filterTree(teamTreeWithLevel.value)
})

const filteredMembres = computed(() => {
  if (!membresEquipe.value.length) return []
  if (!memberSearch.value) return membresEquipe.value
  
  const searchLower = memberSearch.value.toLowerCase()
  return membresEquipe.value.filter(m => 
    m.display_name?.toLowerCase().includes(searchLower) ||
    m.username?.toLowerCase().includes(searchLower) ||
    m.first_name?.toLowerCase().includes(searchLower) ||
    m.last_name?.toLowerCase().includes(searchLower)
  )
})

// ========== STATS FILTRÉES ==========
const filteredStats = computed(() => {
  const userId = selectedMemberId.value
  const equipeId = selectedEquipeId.value
  
  // Fonction pour filtrer par équipe (inclut les sous-équipes)
  const isInEquipe = (item: any): boolean => {
    if (!equipeId) return true
    // Implémentez la logique pour vérifier si l'utilisateur est dans l'équipe
    // Ceci est un placeholder - à adapter selon votre structure de données
    return true
  }
  
  // Fonction pour filtrer par utilisateur
  const isForUser = (item: any): boolean => {
    if (!userId) return true
    return item.utilisateur === userId
  }
  
  // Filtrer les données selon les critères
  const filterItems = (items: any[]) => {
    return items.filter(item => {
      if (userId && item.utilisateur !== userId) return false
      if (equipeId && !isInEquipe(item)) return false
      return true
    })
  }
  
  // Congés
  const congesFiltres = filterItems(congesStore.conges || [])
  const congesApprouves = congesFiltres.filter((c: any) => c.statut === 'approuve')
  const congesEnAttente = congesFiltres.filter((c: any) => c.statut === 'en_attente')
  const congesRefuses = congesFiltres.filter((c: any) => c.statut === 'refuse')
  
  // OSTIE
  const ostieFiltres = filterItems(ostieStore.osties || [])
  const ostieEnAttente = ostieFiltres.filter((o: any) => o.statut === 'en_attente')
  const ostieTransformes = ostieFiltres.filter((o: any) => o.statut === 'transforme')
  
  // Permissions
  const permissionsFiltrees = filterItems(permissionsStore.permissions || [])
  const permissionsRattrapage = permissionsFiltrees.filter((p: any) => p.statut === 'rattrapage')
  const permissionsRetournees = permissionsFiltrees.filter((p: any) => p.statut === 'retourne')
  const heuresRattrapage = permissionsFiltrees.reduce((sum, p) => sum + (parseFloat(p.heures_a_rattraper) || 0), 0)
  
  // Repos
  const reposFiltres = filterItems(reposStore.reposMedicaux || [])
  const reposEnAttente = reposFiltres.filter((r: any) => r.statut === 'en_attente')
  const reposApprouves = reposFiltres.filter((r: any) => r.statut === 'approuve')
  const heuresRepos = reposFiltres.reduce((sum, r) => sum + (parseFloat(r.duree_heures) || 0), 0)
  
  // Retards
  const retardsFiltres = filterItems(retardsStore.retards || [])
  const retardsEnCours = retardsFiltres.filter((r: any) => r.statut === 'en_cours')
  const retardsRattrapes = retardsFiltres.filter((r: any) => r.statut === 'approuve')
  const heuresRetards = retardsFiltres.reduce((sum, r) => sum + (parseFloat(r.heures_a_rattraper) || 0), 0)
  
  return {
    conges: {
      solde: userId ? 'N/A' : (authStore.soldeConge?.actuelle || '0'),
      approuves: congesApprouves.length,
      enAttente: congesEnAttente.length,
      refuses: congesRefuses.length
    },
    ostie: {
      total: ostieFiltres.length,
      enAttente: ostieEnAttente.length,
      transformes: ostieTransformes.length
    },
    permissions: {
      heures: heuresRattrapage.toFixed(2),
      aRattraper: permissionsRattrapage.length,
      retournees: permissionsRetournees.length
    },
    repos: {
      heures: heuresRepos.toFixed(2),
      enAttente: reposEnAttente.length,
      approuves: reposApprouves.length
    },
    retards: {
      heures: heuresRetards.toFixed(2),
      enCours: retardsEnCours.length,
      rattrapes: retardsRattrapes.length
    }
  }
})

// ========== DEMANDES EN ATTENTE ==========
const congesEnAttenteList = computed(() => {
  if (!congesStore.conges || !isManagerOrHigher.value) return []
  
  // Filtrer par équipe si sélectionnée
  let filtered = congesStore.conges.filter((c: any) => c.statut === 'en_attente')
  
  if (selectedEquipeId.value) {
    // Filtrer pour ne garder que les membres de l'équipe
    // À adapter selon votre structure
  }
  
  return filtered
})

const ostieEnAttenteList = computed(() => {
  if (!ostieStore.osties || !isManagerOrHigher.value) return []
  
  let filtered = ostieStore.osties.filter((o: any) => o.statut === 'en_attente')
  
  if (selectedEquipeId.value) {
    // Filtrer par équipe
  }
  
  return filtered
})

const permissionsEnAttenteList = computed(() => {
  if (!permissionsStore.permissions || !isManagerOrHigher.value) return []
  
  let filtered = permissionsStore.permissions.filter((p: any) => p.statut === 'en_attente')
  
  if (selectedEquipeId.value) {
    // Filtrer par équipe
  }
  
  return filtered
})

const reposEnAttenteList = computed(() => {
  if (!reposStore.reposMedicaux || !isManagerOrHigher.value) return []
  
  let filtered = reposStore.reposMedicaux.filter((r: any) => r.statut === 'en_attente')
  
  if (selectedEquipeId.value) {
    // Filtrer par équipe
  }
  
  return filtered
})

const retardsEnAttenteList = computed(() => {
  if (!retardsStore.retards || !isManagerOrHigher.value) return []
  
  let filtered = retardsStore.retards.filter((r: any) => 
    r.statut === 'en_attente' || r.statut === 'en_cours'
  )
  
  if (selectedEquipeId.value) {
    // Filtrer par équipe
  }
  
  return filtered
})

const totalEnAttente = computed(() => {
  return congesEnAttenteList.value.length +
         ostieEnAttenteList.value.length +
         permissionsEnAttenteList.value.length +
         reposEnAttenteList.value.length +
         retardsEnAttenteList.value.length
})

// ========== MES DEMANDES ==========
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
    .slice(0, 10)
})

// ========== STATS ÉQUIPE RÉELLES ==========
const teamMembersCount = computed(() => {
  if (!selectedEquipeObj.value) {
    // Si aucune équipe sélectionnée, compter tous les membres de toutes les équipes
    // À adapter selon votre store
    return equipesStore.equipesActives?.reduce((acc: number, eq: any) => acc + (eq.membres_count || 0), 0) || 0
  }
  
  // Membres de l'équipe sélectionnée
  return selectedEquipeObj.value.membres_count || 0
})

const absentsAujourdhui = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  let count = 0
  
  // Fonction pour vérifier si un utilisateur est dans l'équipe
  const isInSelectedTeam = (userId: number): boolean => {
    if (!selectedEquipeId.value) return true
    // À adapter
    return true
  }
  
  if (congesStore.conges) {
    count += congesStore.conges.filter((c: any) => 
      c.statut === 'approuve' && 
      c.date_debut <= today && 
      c.date_fin >= today &&
      isInSelectedTeam(c.utilisateur)
    ).length
  }
  
  if (ostieStore.osties) {
    count += ostieStore.osties.filter((o: any) => 
      (o.statut === 'approuve' || o.statut === 'transforme') && 
      o.date === today &&
      isInSelectedTeam(o.utilisateur)
    ).length
  }
  
  if (reposStore.reposMedicaux) {
    count += reposStore.reposMedicaux.filter((r: any) => 
      r.statut === 'approuve' && 
      r.date === today &&
      isInSelectedTeam(r.utilisateur)
    ).length
  }
  
  return count
})

const retardsAujourdhui = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  
  if (!retardsStore.retards) return 0
  
  const isInSelectedTeam = (userId: number): boolean => {
    if (!selectedEquipeId.value) return true
    // À adapter
    return true
  }
  
  return retardsStore.retards.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && 
    r.date === today &&
    isInSelectedTeam(r.utilisateur)
  ).length
})

const tauxAbsenteisme = computed(() => {
  if (teamMembersCount.value === 0) return 0
  return ((absentsAujourdhui.value / teamMembersCount.value) * 100).toFixed(1)
})

const topRetardatairesEquipe = computed(() => {
  if (!retardsStore.retards) return []
  
  const isInSelectedTeam = (userId: number): boolean => {
    if (!selectedEquipeId.value) return true
    // À adapter
    return true
  }
  
  const stats: Record<number, { name: string; total: number }> = {}
  
  retardsStore.retards.forEach((r: any) => {
    if ((r.statut === 'approuve' || r.statut === 'en_cours') && isInSelectedTeam(r.utilisateur)) {
      const userId = r.utilisateur
      const heures = parseFloat(r.heures_a_rattraper || '0')
      
      if (!stats[userId]) {
        stats[userId] = {
          name: r.utilisateur_details?.display_name || `User ${userId}`,
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
      total: data.total
    }))
    .sort((a, b) => b.total - a.total)
    .slice(0, 5)
})

// ========== STATS GLOBALES RÉELLES ==========
const currentYear = getYear(new Date())

const evolutionMensuelle = computed(() => {
  // Initialiser un tableau de 12 mois avec des compteurs
  const mois: number[] = Array(12).fill(0)
  
  // Compter toutes les absences par mois
  const compterMois = (dateStr: string) => {
    try {
      const date = parseISO(dateStr)
      const moisIndex = getMonth(date)
      if (moisIndex >= 0 && moisIndex < 12) {
        mois[moisIndex]++
      }
    } catch (e) {
      // Ignorer les dates invalides
    }
  }
  
  // Congés
  congesStore.conges?.forEach((c: any) => {
    if (c.statut === 'approuve') {
      compterMois(c.date_debut)
      if (c.date_fin !== c.date_debut) {
        // Pour les congés multi-jours, compter chaque jour
        // Simplifié ici
      }
    }
  })
  
  // OSTIE
  ostieStore.osties?.forEach((o: any) => {
    if (o.statut === 'approuve' || o.statut === 'transforme') {
      compterMois(o.date)
    }
  })
  
  // Permissions (uniquement celles avec dépassement transformé)
  permissionsStore.permissions?.forEach((p: any) => {
    if (p.statut === 'transforme') {
      compterMois(p.date)
    }
  })
  
  // Repos
  reposStore.reposMedicaux?.forEach((r: any) => {
    if (r.statut === 'approuve') {
      compterMois(r.date)
    }
  })
  
  // Retards
  retardsStore.retards?.forEach((r: any) => {
    if (r.statut === 'approuve') {
      compterMois(r.date)
    }
  })
  
  return mois
})

const maxMois = computed(() => Math.max(...evolutionMensuelle.value, 1))

const getMoisPourcentage = (index: number) => {
  const valeur = evolutionMensuelle.value[index] || 0 // ← Ajouter || 0 pour éviter undefined
  if (maxMois.value === 0) return 0
  return (valeur / maxMois.value) * 100
}

const globalStats = computed(() => ({
  conges: congesStore.conges?.filter((c: any) => c.statut === 'approuve').length || 0,
  ostie: ostieStore.osties?.filter((o: any) => o.statut === 'approuve' || o.statut === 'transforme').length || 0,
  permissions: permissionsStore.permissions?.filter((p: any) => p.statut === 'transforme').length || 0,
  repos: reposStore.reposMedicaux?.filter((r: any) => r.statut === 'approuve').length || 0,
  retards: retardsStore.retards?.filter((r: any) => r.statut === 'approuve').length || 0
}))

// ========== ALERTES SYSTÈME ==========
const hasTypesRetard = computed(() => retardsStore.typesRetard?.length > 0)
const hasTypesConge = computed(() => congesStore.typesConge?.length > 0)
const hasDroits = computed(() => congesStore.droits?.length > 0)

// ========== MÉTHODES UTILITAIRES ==========
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

const getMembreDisplayName = (membre: any) => {
  if (membre.display_name) return membre.display_name
  if (membre.first_name && membre.last_name) {
    return `${membre.first_name} ${membre.last_name}`
  }
  return membre.username?.toUpperCase() || 'Membre'
}

const getMembresCount = (equipe: any): number => {
  return equipe.membres_count || 0
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

const moisNoms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const getMoisCouleur = (moisIndex: number) => {
  const couleurs = ['#1976d2', '#f57c00', '#388e3c', '#7b1fa2', '#c62828']
  return couleurs[moisIndex % couleurs.length]
}

// ========== MÉTHODES DE FILTRAGE ==========
const selectEquipe = async (equipe: any) => {
  selectedEquipeId.value = equipe.id
  selectedEquipeObj.value = equipe
  selectedMemberId.value = null
  selectedMemberObj.value = null
  showTeamDropdown.value = false
  
  // Charger les membres de l'équipe
  await loadMembresEquipe(equipe.id)
}

const selectMember = (membre: any | null) => {
  if (membre) {
    selectedMemberId.value = membre.id
    selectedMemberObj.value = membre
  } else {
    selectedMemberId.value = null
    selectedMemberObj.value = null
  }
  showMemberDropdown.value = false
}

const loadMembresEquipe = async (equipeId: number) => {
  loadingMembres.value = true
  try {
    // À implémenter selon votre API
    // const response = await equipesApi.getMembres(equipeId)
    // membresEquipe.value = response
    membresEquipe.value = []
  } catch (error) {
    console.error('Erreur chargement membres:', error)
  } finally {
    loadingMembres.value = false
  }
}

const clearFilters = () => {
  selectedEquipeId.value = null
  selectedEquipeObj.value = null
  selectedMemberId.value = null
  selectedMemberObj.value = null
  membresEquipe.value = []
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
    equipesStore.fetchArbre(true),
    authStore.refreshSolde()
  ])
  
  loading.value = false
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshAllData()
})

// Watch pour fermer les dropdowns quand on clique ailleurs
watch(showTeamDropdown, (val) => {
  if (val) showMemberDropdown.value = false
})

watch(showMemberDropdown, (val) => {
  if (val) showTeamDropdown.value = false
})
</script>

<style scoped>
/* Ajouter les nouveaux styles pour les filtres */
.filters-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filters-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filters-header h3 {
  margin: 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #333;
}

.btn-clear-filters {
  padding: 6px 12px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: all 0.2s;
}

.btn-clear-filters:hover {
  background: #e0e0e0;
}

.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.team-selector, .member-selector {
  position: relative;
}

.select-button {
  width: 100%;
  padding: 10px 12px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  transition: border-color 0.2s;
}

.select-button:hover {
  border-color: #1976d2;
}

.select-button:disabled {
  background: #f5f5f5;
  cursor: not-allowed;
  opacity: 0.6;
}

.team-dropdown, .member-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-top: 5px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.dropdown-header {
  padding: 10px;
  border-bottom: 1px solid #eee;
  position: sticky;
  top: 0;
  background: white;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 13px;
}

.dropdown-tree {
  padding: 8px;
}

.team-node {
  margin: 2px 0;
}

.team-option, .member-option {
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  text-align: left;
  cursor: pointer;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  transition: background 0.2s;
}

.team-option:hover, .member-option:hover {
  background: #f5f5f5;
}

.team-option.selected, .member-option.selected {
  background: #e3f2fd;
  color: #1976d2;
}

.team-option i {
  color: #f57c00;
}

.team-count {
  margin-left: auto;
  color: #999;
  font-size: 11px;
}

.member-option i {
  color: #666;
}

.member-matricule {
  margin-left: auto;
  color: #999;
  font-size: 10px;
}

.active-filter-badge {
  margin-top: 15px;
  padding: 8px 12px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 6px;
  font-size: 13px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading-small {
  padding: 20px;
  text-align: center;
  color: #999;
  font-size: 13px;
}

.loading-small i {
  margin-right: 5px;
}

.badge-danger {
  background: #ffebee;
  color: #c62828;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* Rendre les cartes conges plus grandes pour accueillir le nouveau badge */
.kpi-detail {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.pending-card.retards h3 {
  color: #c62828;
}

/* Le reste du CSS est identique à la version précédente */
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

.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
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
  gap: 8px;
  flex-wrap: wrap;
}

.badge-success {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-warning {
  background: #fff3e0;
  color: #f57c00;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-info {
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.badge-danger {
  background: #ffebee;
  color: #c62828;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

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
  min-width: 35px;
  font-size: 12px;
  font-weight: 500;
  color: #1976d2;
}

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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
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
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>