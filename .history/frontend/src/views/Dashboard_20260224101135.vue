<template>
  <!-- En-tête personnalisé selon le rôle -->
  <div class="dashboard-header">
    <div class="header-left">
      <h1>
        Tableau de bord
        <!-- <span class="role-badge" :class="userRoleClass">{{ displayName }} {{ userRole }}</span> -->
      </h1>
      <!-- <p class="date-today">{{ currentDate }}</p> -->
    </div>
    <div class="header-right">
      <button class="btn-refresh" @click="refreshAllData" :disabled="loading">
        <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
        {{ loading ? 'Rafraîchissement...' : 'Actualiser' }}
      </button>
    </div>
  </div>

  <!-- ============================================ -->
  <!-- FILTRE PAR MEMBRE (pour managers et +)       -->
  <!-- ============================================ -->
  <div v-if="isManagerOrHigher" class="filters-section">
    <div class="member-filter">
      <label>
        <i class="bi bi-funnel"></i>
        Filtrer par :
      </label>
      <div class="filter-tabs">
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

      <!-- Sélecteur d'équipe -->
      <!-- Dans la partie template - Sélecteur d'équipe -->
      <div v-if="filterType === 'equipe'" class="equipe-selector">
        <select v-model="selectedEquipeId" @change="onEquipeChange" class="form-select">
          <option value="">Toutes les équipes que je gère</option>
          <!-- Utilisation de la structure hiérarchique -->
          <template v-for="equipe in equipesGerablesHierarchiques" :key="equipe.id">
            <option :value="equipe.id">
              {{ getEquipePath(equipe) }}
            </option>
            <!-- Sous-équipes récursives -->
            <template v-if="equipe.sous_equipes && equipe.sous_equipes.length">
              <option 
                v-for="sousEquipe in getAllSousEquipes(equipe)" 
                :key="sousEquipe.id" 
                :value="sousEquipe.id"
              >
                {{ getEquipePath(sousEquipe) }}
              </option>
            </template>
          </template>
        </select>
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
        </div>
        
        <select v-model="selectedMembreId" @change="onMembreChange" class="form-select" :disabled="membresFiltres.length === 0">
          <option value="">Sélectionner un membre</option>
          <option v-for="membre in membresFiltres" :key="membre.id" :value="membre.id">
            {{ membre.display_name }} ({{ membre.username.toUpperCase() }}) - {{ membre.equipe_nom || 'Sans équipe' }}
          </option>
        </select>
      </div>

      <button v-if="selectedEquipeId || selectedMembreId" class="btn-clear-filter" @click="clearFilter">
        <i class="bi bi-x"></i> Effacer
      </button>
    </div>

    <div v-if="filterLabel" class="active-filter">
      <i class="bi bi-filter-left"></i>
      Filtre actif : <strong>{{ filterLabel }}</strong>
    </div>
  </div>

  <!-- ============================================ -->
  <!-- KPI CARDS -->
  <!-- ============================================ -->
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

  <!-- ============================================ -->
  <!-- DEMANDES EN ATTENTE -->
  <!-- ============================================ -->
  <div v-if="isManagerOrHigher" class="dashboard-section">
    <h2>
      <i class="bi bi-bell"></i>
      Demandes en attente de validation
      <span class="section-badge">{{ totalEnAttente }}</span>
    </h2>
    
    <div v-if="totalEnAttente === 0" class="empty-state">
      <i class="bi bi-check2-circle"></i>
      <p>Aucune demande en attente{{ filterLabel ? ' pour ce filtre' : '' }}</p>
    </div>

    <div v-else class="pending-grid">
      <!-- Congés en attente -->
      <div v-if="congesEnAttenteFiltres.length > 0" class="pending-card conges">
        <h3><i class="bi bi-calendar-check"></i> Congés ({{ congesEnAttenteFiltres.length }})</h3>
        <div class="pending-list">
          <div v-for="conge in congesEnAttenteFiltres.slice(0, 3)" :key="conge.id" class="pending-item">
            <div class="user-avatar">{{ getInitials(conge.utilisateur_details?.display_name) }}</div>
            <div class="item-content">
              <p class="user-name">{{ conge.utilisateur_details?.display_name }}</p>
              <p class="item-detail">{{ formatDate(conge.date_debut) }} → {{ formatDate(conge.date_fin) }}</p>
            </div>
            <button class="btn-small" @click="goToModule('conges', conge.id)">Voir</button>
          </div>
          <div v-if="congesEnAttenteFiltres.length > 3" class="more-link" @click="goToModule('conges')">
            + {{ congesEnAttenteFiltres.length - 3 }} autres...
          </div>
        </div>
      </div>

      <!-- OSTIE en attente -->
      <div v-if="ostieEnAttenteFiltres.length > 0" class="pending-card ostie">
        <h3><i class="bi bi-heart-pulse"></i> OSTIE ({{ ostieEnAttenteFiltres.length }})</h3>
        <div class="pending-list">
          <div v-for="ostie in ostieEnAttenteFiltres.slice(0, 3)" :key="ostie.id" class="pending-item">
            <div class="user-avatar">{{ getInitials(ostie.utilisateur_details?.display_name) }}</div>
            <div class="item-content">
              <p class="user-name">{{ ostie.utilisateur_details?.display_name }}</p>
              <p class="item-detail">{{ formatDate(ostie.date) }} à {{ formatTime(ostie.heure_debut) }}</p>
            </div>
            <button class="btn-small" @click="goToModule('ostie', ostie.id)">Voir</button>
          </div>
          <div v-if="ostieEnAttenteFiltres.length > 3" class="more-link" @click="goToModule('ostie')">
            + {{ ostieEnAttenteFiltres.length - 3 }} autres...
          </div>
        </div>
      </div>

      <!-- Permissions en attente -->
      <div v-if="permissionsEnAttenteFiltres.length > 0" class="pending-card permissions">
        <h3><i class="bi bi-door-open"></i> Permissions ({{ permissionsEnAttenteFiltres.length }})</h3>
        <div class="pending-list">
          <div v-for="perm in permissionsEnAttenteFiltres.slice(0, 3)" :key="perm.id" class="pending-item">
            <div class="user-avatar">{{ getInitials(perm.utilisateur_details?.display_name) }}</div>
            <div class="item-content">
              <p class="user-name">{{ perm.utilisateur_details?.display_name }}</p>
              <p class="item-detail">{{ formatDate(perm.date) }} - {{ formatTime(perm.heure_depart) }}</p>
            </div>
            <button class="btn-small" @click="goToModule('permissions', perm.id)">Voir</button>
          </div>
          <div v-if="permissionsEnAttenteFiltres.length > 3" class="more-link" @click="goToModule('permissions')">
            + {{ permissionsEnAttenteFiltres.length - 3 }} autres...
          </div>
        </div>
      </div>

      <!-- Repos médicaux en attente -->
      <div v-if="reposEnAttenteFiltres.length > 0" class="pending-card repos">
        <h3><i class="bi bi-hospital"></i> Repos médicaux ({{ reposEnAttenteFiltres.length }})</h3>
        <div class="pending-list">
          <div v-for="repos in reposEnAttenteFiltres.slice(0, 3)" :key="repos.id" class="pending-item">
            <div class="user-avatar">{{ getInitials(repos.utilisateur_details?.display_name) }}</div>
            <div class="item-content">
              <p class="user-name">{{ repos.utilisateur_details?.display_name }}</p>
              <p class="item-detail">{{ formatDate(repos.date) }} - {{ repos.duree_heures }}h</p>
            </div>
            <button class="btn-small" @click="goToModule('repos', repos.id)">Voir</button>
          </div>
          <div v-if="reposEnAttenteFiltres.length > 3" class="more-link" @click="goToModule('repos')">
            + {{ reposEnAttenteFiltres.length - 3 }} autres...
          </div>
        </div>
      </div>

      <!-- Retards en attente -->
      <div v-if="retardsEnAttenteFiltres.length > 0" class="pending-card retards">
        <h3><i class="bi bi-clock-history"></i> Retards ({{ retardsEnAttenteFiltres.length }})</h3>
        <div class="pending-list">
          <div v-for="retard in retardsEnAttenteFiltres.slice(0, 3)" :key="retard.id" class="pending-item">
            <div class="user-avatar">{{ getInitials(retard.utilisateur_details?.display_name) }}</div>
            <div class="item-content">
              <p class="user-name">{{ retard.utilisateur_details?.display_name }}</p>
              <p class="item-detail">{{ formatDate(retard.date) }} - {{ retard.minutes_retard }}min</p>
            </div>
            <button class="btn-small" @click="goToModule('retards', retard.id)">Voir</button>
          </div>
          <div v-if="retardsEnAttenteFiltres.length > 3" class="more-link" @click="goToModule('retards')">
            + {{ retardsEnAttenteFiltres.length - 3 }} autres...
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- ============================================ -->
  <!-- MES DEMANDES RÉCENTES -->
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
  <!-- APERÇU DE L'ÉQUIPE -->
  <!-- ============================================ -->
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

    <!-- Top retardataires (corrigé pour afficher toute l'équipe) -->
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

  <!-- ============================================ -->
  <!-- STATISTIQUES GLOBALES (SUPER ADMIN)         -->
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
                  :style="{ width: getMoisPourcentage(index) + '%', background: getMoisCouleur(index) }"
                  :title="`${mois}: ${evolutionData[index]} demande(s)`"
                ></div>
              </div>
              <span class="bar-value">{{ evolutionData[index] }}</span>
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
const filterType = ref<'equipe' | 'membre'>('equipe')
const selectedEquipeId = ref<number | ''>('')
const selectedMembreId = ref<number | ''>('')
const membreSearch = ref('')
const searchTimeout = ref<number | null>(null)

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

// ========== COMPUTED - ÉQUIPES GÉRABLES ==========
const equipesGerables = computed(() => {
  if (!equipesStore.equipes || !currentUser.value) return []
  
  const userId = currentUser.value.id
  
  // Filtrer les équipes où l'utilisateur est manager ou co-manager
  return equipesStore.equipes.filter((equipe: any) => {
    const isManager = equipe.manager === userId
    const isCoManager = equipe.co_managers?.includes(userId)
    return isManager || isCoManager
  })
})

const getEquipePath = (equipe: any): string => {
  // Créer l'indentation basée sur le niveau
  const indent = '  '.repeat(equipe.niveau || 0)
  
  // Construire le chemin complet
  let path = equipe.nom
  
  // Ajouter le pôle si disponible
  if (equipe.pole_details) {
    path = `${equipe.pole_details.nom} > ${path}`
  }
  
  // Ajouter l'indentation et un indicateur visuel
  return indent + '📁 ' + path
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
  
  // Utiliser equipesGerablesHierarchiques au lieu de equipesGerables
  for (const equipe of equipesGerablesHierarchiques.value) {
    await loadMembresEquipe(equipe.id)
    const membres = membresParEquipe.value[equipe.id] || []
    tousMembres.push(...membres.map((m: any) => ({
      ...m,
      equipe_nom: equipe.nom,
      equipe_path: getEquipePath(equipe),
      equipe_id: equipe.id
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
    m.equipe_nom?.toLowerCase().includes(query)
  )
})

// ========== COMPUTED - FILTRE LABEL ==========
const filterLabel = computed(() => {
  if (selectedMembreId.value) {
    const membre = allGerablesMembres.value.find(m => m.id === selectedMembreId.value)
    return membre ? `${membre.display_name} (${membre.username.toUpperCase()})` : ''
  }
  if (selectedEquipeId.value) {
    const equipe = equipesGerables.value.find(e => e.id === selectedEquipeId.value)
    return equipe ? getEquipePath(equipe) : ''
  }
  return ''
})

// ========== FILTRAGE DES DONNÉES ==========
const getMembresEquipeIds = (equipeId: number): number[] => {
  const membres = membresParEquipe.value[equipeId] || []
  return membres.map((m: any) => m.id)
}

const getAllGerablesMembresIds = (): number[] => {
  return allGerablesMembres.value.map((m: any) => m.id)
}

const congesFiltres = computed(() => {
  let data = congesStore.conges || []
  
  if (selectedMembreId.value) {
    data = data.filter((c: any) => c.utilisateur === selectedMembreId.value)
  } else if (selectedEquipeId.value) {
    const membresIds = getMembresEquipeIds(selectedEquipeId.value)
    data = data.filter((c: any) => membresIds.includes(c.utilisateur))
  } else if (isManagerOrHigher.value) {
    const membresIds = getAllGerablesMembresIds()
    data = data.filter((c: any) => membresIds.includes(c.utilisateur))
  }
  
  return data
})

const ostieFiltres = computed(() => {
  let data = ostieStore.osties || []
  
  if (selectedMembreId.value) {
    data = data.filter((o: any) => o.utilisateur === selectedMembreId.value)
  } else if (selectedEquipeId.value) {
    const membresIds = getMembresEquipeIds(selectedEquipeId.value)
    data = data.filter((o: any) => membresIds.includes(o.utilisateur))
  } else if (isManagerOrHigher.value) {
    const membresIds = getAllGerablesMembresIds()
    data = data.filter((o: any) => membresIds.includes(o.utilisateur))
  }
  
  return data
})

const permissionsFiltres = computed(() => {
  let data = permissionsStore.permissions || []
  
  if (selectedMembreId.value) {
    data = data.filter((p: any) => p.utilisateur === selectedMembreId.value)
  } else if (selectedEquipeId.value) {
    const membresIds = getMembresEquipeIds(selectedEquipeId.value)
    data = data.filter((p: any) => membresIds.includes(p.utilisateur))
  } else if (isManagerOrHigher.value) {
    const membresIds = getAllGerablesMembresIds()
    data = data.filter((p: any) => membresIds.includes(p.utilisateur))
  }
  
  return data
})

const reposFiltres = computed(() => {
  let data = reposStore.reposMedicaux || []
  
  if (selectedMembreId.value) {
    data = data.filter((r: any) => r.utilisateur === selectedMembreId.value)
  } else if (selectedEquipeId.value) {
    const membresIds = getMembresEquipeIds(selectedEquipeId.value)
    data = data.filter((r: any) => membresIds.includes(r.utilisateur))
  } else if (isManagerOrHigher.value) {
    const membresIds = getAllGerablesMembresIds()
    data = data.filter((r: any) => membresIds.includes(r.utilisateur))
  }
  
  return data
})

const retardsFiltres = computed(() => {
  let data = retardsStore.retards || []
  
  if (selectedMembreId.value) {
    data = data.filter((r: any) => r.utilisateur === selectedMembreId.value)
  } else if (selectedEquipeId.value) {
    const membresIds = getMembresEquipeIds(selectedEquipeId.value)
    data = data.filter((r: any) => membresIds.includes(r.utilisateur))
  } else if (isManagerOrHigher.value) {
    const membresIds = getAllGerablesMembresIds()
    data = data.filter((r: any) => membresIds.includes(r.utilisateur))
  }
  
  return data
})

// ========== COMPUTED - STATS ==========
const congesSolde = computed(() => {
  if (selectedMembreId.value) {
    const membre = allGerablesMembres.value.find(m => m.id === selectedMembreId.value)
    return membre?.solde_conge_actuelle || '0'
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

const congesEnAttenteFiltres = computed(() => congesFiltres.value.filter((c: any) => c.statut === 'en_attente'))
const ostieEnAttenteFiltres = computed(() => ostieFiltres.value.filter((o: any) => o.statut === 'en_attente'))
const permissionsEnAttenteFiltres = computed(() => permissionsFiltres.value.filter((p: any) => p.statut === 'en_attente'))
const reposEnAttenteFiltres = computed(() => reposFiltres.value.filter((r: any) => r.statut === 'en_attente'))
const retardsEnAttenteFiltres = computed(() => retardsFiltres.value.filter((r: any) => r.statut === 'en_attente'))

const totalEnAttente = computed(() => {
  return congesEnAttenteFiltres.value.length +
         ostieEnAttenteFiltres.value.length +
         permissionsEnAttenteFiltres.value.length +
         reposEnAttenteFiltres.value.length +
         retardsEnAttenteFiltres.value.length
})

// ========== STATS ÉQUIPE ==========
const teamMembersCount = computed(() => {
  if (selectedMembreId.value) return 1
  if (selectedEquipeId.value) {
    return (membresParEquipe.value[selectedEquipeId.value] || []).length
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

// ========== TOP RETARDATAIRES (CORRIGÉ) ==========
const topRetardataires = computed(() => {
  if (!isManagerOrHigher.value) return []
  
  // Utiliser retardsFiltres qui contient déjà les retards de l'équipe
  const stats: Record<number, { name: string; total: number }> = {}
  
  retardsFiltres.value.forEach((r: any) => {
    if (r.statut === 'approuve' || r.statut === 'en_cours') {
      const userId = r.utilisateur
      const heures = parseFloat(r.heures_a_rattraper || '0')
      
      if (!stats[userId]) {
        // Chercher le nom du membre dans allGerablesMembres
        const membre = allGerablesMembres.value.find((m: any) => m.id === userId)
        stats[userId] = {
          name: membre?.display_name || r.utilisateur_details?.display_name || `User ${userId}`,
          total: 0
        }
      }
      stats[userId].total += heures
    }
  })
  
  // Ne garder que ceux qui ont des heures à rattraper
  const result = Object.entries(stats)
    .map(([userId, data]) => ({
      userId: parseInt(userId),
      name: data.name,
      total: data.total
    }))
    .filter(item => item.total > 0) // Exclure ceux qui ont 0 heure
    .sort((a, b) => b.total - a.total)
    .slice(0, 5)
  
  return result
})


// ========== Equipes Be ==========
const equipesGerablesHierarchiques = computed(() => {
  if (!equipesStore.arbreEquipes || !currentUser.value) return []
  
  const userId = currentUser.value.id
  
  // Fonction récursive pour collecter les équipes où l'utilisateur est manager/co-manager
  const collectGerables = (equipes: any[], niveau = 0): any[] => {
    let result: any[] = []
    
    for (const equipe of equipes) {
      // Vérifier si l'utilisateur est manager ou co-manager de cette équipe
      const isManager = equipe.manager === userId
      const isCoManager = equipe.co_managers?.includes(userId)
      
      if (isManager || isCoManager) {
        // Ajouter l'équipe avec son niveau pour l'indentation
        result.push({
          ...equipe,
          niveau
        })
      }
      
      // Ajouter les sous-équipes (même si l'utilisateur n'est pas manager de la parente)
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



const getMembresEquipeRecursif = (equipeId: number): number[] => {
  const membres: number[] = []
  
  // Ajouter les membres de l'équipe elle-même
  const membresEquipe = membresParEquipe.value[equipeId] || []
  membres.push(...membresEquipe.map((m: any) => m.id))
  
  // Trouver l'équipe dans la hiérarchie
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
  
  // Ajouter récursivement les membres des sous-équipes
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
  
  return [...new Set(membres)] // Éliminer les doublons
}

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

// ========== STATS GLOBALES ==========
const globalStats = computed(() => ({
  conges: congesStore.conges?.length || 0,
  ostie: ostieStore.osties?.length || 0,
  permissions: permissionsStore.permissions?.length || 0,
  repos: reposStore.reposMedicaux?.length || 0,
  retards: retardsStore.retards?.length || 0
}))

const evolutionData = computed(() => {
  const mois = Array(12).fill(0)
  
  const allDemandes = [
    ...(congesStore.conges || []),
    ...(ostieStore.osties || []),
    ...(permissionsStore.permissions || []),
    ...(reposStore.reposMedicaux || []),
    ...(retardsStore.retards || [])
  ]
  
  allDemandes.forEach((d: any) => {
    try {
      const date = parseISO(d.date_creation || d.date || d.date_debut)
      const moisIndex = getMonth(date)
      if (getYear(date) === currentYear.value) {
        mois[moisIndex]++
      }
    } catch (e) {}
  })
  
  return mois
})

const getMoisPourcentage = (moisIndex: number) => {
  const max = Math.max(...evolutionData.value, 1)
  return (evolutionData.value[moisIndex] / max) * 100
}

const getMoisCouleur = (moisIndex: number) => {
  const couleurs = ['#1976d2', '#f57c00', '#388e3c', '#7b1fa2', '#c62828']
  return couleurs[moisIndex % couleurs.length]
}

const moisNoms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

// ========== METHODS ==========
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
}

const onMembreChange = () => {
  selectedEquipeId.value = ''
}

const clearFilter = () => {
  selectedEquipeId.value = ''
  selectedMembreId.value = ''
  membreSearch.value = ''
  filterType.value = 'equipe'
}

// ========== RAFRAÎCHISSEMENT ==========
const refreshAllData = async () => {
  loading.value = true
  
  const currentYear = getYear(new Date())
  
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
    authStore.refreshSolde(),
    equipesStore.fetchEquipes()
  ])
  
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
  await equipesStore.fetchEquipes()
  await refreshAllData()
})

onUnmounted(() => {
  if (searchTimeout.value !== null) clearTimeout(searchTimeout.value)
})
</script>

<style scoped>
/* Garder les mêmes styles que précédemment */

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 15px;
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