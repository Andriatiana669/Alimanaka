<template>
  <div class="dashboard">
    <!-- En-tête -->
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
    <!-- FILTRE PAR ÉQUIPE / MEMBRE (NOUVEAU)        -->
    <!-- ============================================ -->
    <div class="filters-section">
      <h2>
        <i class="bi bi-funnel"></i>
        Filtrer les statistiques
      </h2>
      
      <div class="filters-container">
        <!-- Sélecteur d'équipe hiérarchique -->
        <div class="filter-group equipe-selector">
          <label>Équipe</label>
          <select v-model="selectedEquipeId" @change="onEquipeChange">
            <option value="">Toutes les équipes (vue globale)</option>
            <option v-for="equipe in equipesHierarchiques" :key="equipe.id" :value="equipe.id">
              {{ '—'.repeat(equipe.niveau) }} {{ equipe.nom }}
            </option>
          </select>
        </div>

        <!-- Sélecteur de membre (dépend de l'équipe sélectionnée) -->
        <div class="filter-group membre-selector" v-if="selectedEquipeId">
          <label>Membre</label>
          <select v-model="selectedMembreId" @change="onMembreChange">
            <option value="">Tous les membres de cette équipe</option>
            <option v-for="membre in membresEquipe" :key="membre.id" :value="membre.id">
              {{ membre.display_name }} ({{ membre.username.toUpperCase() }})
            </option>
          </select>
        </div>

        <!-- Bouton reset -->
        <button class="btn-reset" @click="resetFilters" v-if="selectedEquipeId || selectedMembreId">
          <i class="bi bi-x-circle"></i> Réinitialiser
        </button>
      </div>

      <!-- Badge indiquant le filtre actuel -->
      <div v-if="selectedMembreId" class="filter-badge">
        <i class="bi bi-person"></i>
        Membre: {{ membreSelectionne?.display_name }}
      </div>
      <div v-else-if="selectedEquipeId" class="filter-badge">
        <i class="bi bi-people"></i>
        Équipe: {{ equipeSelectionnee?.nom }}
      </div>
    </div>

    <!-- ============================================ -->
    <!-- KPI CARDS - Stats personnelles OU de l'équipe -->
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
            <span class="badge-info">{{ congesPris }} pris</span>
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
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- DEMANDES EN ATTENTE (filtrées par équipe)    -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-bell"></i>
        Demandes en attente de validation
        <span class="section-badge">{{ totalEnAttenteFiltre }}</span>
        <span v-if="selectedEquipeNom" class="filter-context">({{ selectedEquipeNom }})</span>
      </h2>
      
      <div v-if="totalEnAttenteFiltre === 0" class="empty-state">
        <i class="bi bi-check2-circle"></i>
        <p>Aucune demande en attente{{ selectedEquipeNom ? ' pour cette équipe' : '' }}</p>
      </div>

      <div v-else class="pending-grid">
        <!-- Congés en attente -->
        <div v-if="congesEnAttenteFiltre.length > 0" class="pending-card conges">
          <h3>
            <i class="bi bi-calendar-check"></i>
            Congés ({{ congesEnAttenteFiltre.length }})
          </h3>
          <div class="pending-list">
            <div v-for="conge in congesEnAttenteFiltre.slice(0, 3)" :key="conge.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(conge.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ conge.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(conge.date_debut) }} → {{ formatDate(conge.date_fin) }}</p>
              </div>
              <button class="btn-small" @click="goToModule('conges', conge.id)">Voir</button>
            </div>
            <div v-if="congesEnAttenteFiltre.length > 3" class="more-link" @click="goToModule('conges')">
              + {{ congesEnAttenteFiltre.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- OSTIE en attente -->
        <div v-if="ostieEnAttenteFiltre.length > 0" class="pending-card ostie">
          <h3>
            <i class="bi bi-heart-pulse"></i>
            OSTIE ({{ ostieEnAttenteFiltre.length }})
          </h3>
          <div class="pending-list">
            <div v-for="ostie in ostieEnAttenteFiltre.slice(0, 3)" :key="ostie.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(ostie.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ ostie.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(ostie.date) }} à {{ formatTime(ostie.heure_debut) }}</p>
              </div>
              <button class="btn-small" @click="goToModule('ostie', ostie.id)">Voir</button>
            </div>
            <div v-if="ostieEnAttenteFiltre.length > 3" class="more-link" @click="goToModule('ostie')">
              + {{ ostieEnAttenteFiltre.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Permissions en attente -->
        <div v-if="permissionsEnAttenteFiltre.length > 0" class="pending-card permissions">
          <h3>
            <i class="bi bi-door-open"></i>
            Permissions ({{ permissionsEnAttenteFiltre.length }})
          </h3>
          <div class="pending-list">
            <div v-for="perm in permissionsEnAttenteFiltre.slice(0, 3)" :key="perm.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(perm.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ perm.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(perm.date) }} - {{ formatTime(perm.heure_depart) }}</p>
              </div>
              <button class="btn-small" @click="goToModule('permissions', perm.id)">Voir</button>
            </div>
            <div v-if="permissionsEnAttenteFiltre.length > 3" class="more-link" @click="goToModule('permissions')">
              + {{ permissionsEnAttenteFiltre.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Repos médicaux en attente -->
        <div v-if="reposEnAttenteFiltre.length > 0" class="pending-card repos">
          <h3>
            <i class="bi bi-hospital"></i>
            Repos médicaux ({{ reposEnAttenteFiltre.length }})
          </h3>
          <div class="pending-list">
            <div v-for="repos in reposEnAttenteFiltre.slice(0, 3)" :key="repos.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(repos.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ repos.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(repos.date) }} - {{ repos.duree_heures }}h</p>
              </div>
              <button class="btn-small" @click="goToModule('repos', repos.id)">Voir</button>
            </div>
            <div v-if="reposEnAttenteFiltre.length > 3" class="more-link" @click="goToModule('repos')">
              + {{ reposEnAttenteFiltre.length - 3 }} autres...
            </div>
          </div>
        </div>

        <!-- Retards en attente (NOUVEAU) -->
        <div v-if="retardsEnAttenteFiltre.length > 0" class="pending-card retards">
          <h3>
            <i class="bi bi-clock-history"></i>
            Retards ({{ retardsEnAttenteFiltre.length }})
          </h3>
          <div class="pending-list">
            <div v-for="retard in retardsEnAttenteFiltre.slice(0, 3)" :key="retard.id" class="pending-item">
              <div class="user-avatar">{{ getInitials(retard.utilisateur_details?.display_name) }}</div>
              <div class="item-content">
                <p class="user-name">{{ retard.utilisateur_details?.display_name }}</p>
                <p class="item-detail">{{ formatDate(retard.date) }} - {{ retard.minutes_retard }}min</p>
              </div>
              <button class="btn-small" @click="goToModule('retards', retard.id)">Voir</button>
            </div>
            <div v-if="retardsEnAttenteFiltre.length > 3" class="more-link" @click="goToModule('retards')">
              + {{ retardsEnAttenteFiltre.length - 3 }} autres...
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
    <!-- APERÇU DE L'ÉQUIPE (corrigé avec données réelles) -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-graph-up"></i>
        Aperçu de l'équipe
        <span v-if="selectedEquipeNom" class="filter-context">({{ selectedEquipeNom }})</span>
      </h2>
      
      <div class="team-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">Membres</span>
            <span class="stat-value">{{ membresEquipe.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Absents aujourd'hui</span>
            <span class="stat-value">{{ absentsAujourdhuiFiltre }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">En retard</span>
            <span class="stat-value">{{ retardsAujourdhuiFiltre }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Taux d'absentéisme</span>
            <span class="stat-value">{{ tauxAbsenteismeFiltre }}%</span>
          </div>
        </div>
      </div>

      <!-- Top retardataires (filtré par équipe) -->
      <div v-if="topRetardatairesFiltre.length > 0" class="top-list">
        <h3>⏰ Top des retardataires</h3>
        <div class="top-items">
          <div v-for="(item, index) in topRetardatairesFiltre" :key="item.userId" class="top-item">
            <span class="top-rank">{{ index + 1 }}</span>
            <span class="top-name">{{ item.name }}</span>
            <span class="top-value">{{ item.total.toFixed(2) }}h</span>
          </div>
        </div>
      </div>
    </div>

    <!-- ============================================ -->
    <!-- SECTION SUPER ADMIN - Stats globales (avec vraies données) -->
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
            <h4>Évolution mensuelle ({{ anneeActuelle }})</h4>
            <div class="bar-chart-placeholder">
              <div v-for="(mois, index) in moisNoms" :key="index" class="bar-item">
                <span class="bar-label">{{ mois.substring(0,3) }}</span>
                <div class="bar-container">
                  <div class="bar" :style="{ width: evolutionMensuelle[index] + '%', background: getMoisCouleur(index) }"></div>
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
const selectedEquipeId = ref<number | ''>('')
const selectedMembreId = ref<number | ''>('')
const membresEquipe = ref<any[]>([])
const equipesHierarchiques = ref<any[]>([])
const anneeActuelle = ref(getYear(new Date()))

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

// ========== COMPUTED - ÉQUIPES ==========
const equipeSelectionnee = computed(() => {
  if (!selectedEquipeId.value) return null
  return equipesStore.equipes?.find((e: any) => e.id === selectedEquipeId.value)
})

const membreSelectionne = computed(() => {
  if (!selectedMembreId.value) return null
  return membresEquipe.value.find((m: any) => m.id === selectedMembreId.value)
})

const selectedEquipeNom = computed(() => {
  if (selectedMembreId.value && membreSelectionne.value) {
    return `${membreSelectionne.value.display_name} (${equipeSelectionnee.value?.nom})`
  }
  if (selectedEquipeId.value && equipeSelectionnee.value) {
    return equipeSelectionnee.value.nom
  }
  return ''
})

// ========== FILTRES ==========
const filterBySelected = <T extends { utilisateur: number }>(items: T[] | null): T[] => {
  if (!items) return []
  
  if (selectedMembreId.value) {
    return items.filter(item => item.utilisateur === selectedMembreId.value)
  }
  
  if (selectedEquipeId.value && membresEquipe.value.length > 0) {
    const membreIds = membresEquipe.value.map((m: any) => m.id)
    return items.filter(item => membreIds.includes(item.utilisateur))
  }
  
  return items
}

// ========== COMPUTED - STATS CONGÉS ==========
const congesSolde = computed(() => {
  if (selectedMembreId.value && membreSelectionne.value) {
    return membreSelectionne.value.solde_conge_actuelle || '0'
  }
  return authStore.soldeConge?.actuelle || '0'
})

const congesApprouves = computed(() => {
  if (!congesStore.conges) return 0
  const filtered = filterBySelected(congesStore.conges)
  return filtered.filter((c: any) => c.statut === 'approuve').length
})

const congesEnAttente = computed(() => {
  if (!congesStore.conges) return 0
  const filtered = filterBySelected(congesStore.conges)
  return filtered.filter((c: any) => c.statut === 'en_attente').length
})

const congesPris = computed(() => {
  if (!congesStore.conges) return 0
  const filtered = filterBySelected(congesStore.conges)
  const today = format(new Date(), 'yyyy-MM-dd')
  return filtered.filter((c: any) => 
    c.statut === 'approuve' && 
    c.date_debut <= today && 
    c.date_fin >= today
  ).length
})

const congesEnAttenteFiltre = computed(() => {
  if (!congesStore.conges || !isManagerOrHigher.value) return []
  return filterBySelected(congesStore.conges.filter((c: any) => c.statut === 'en_attente'))
})

// ========== COMPUTED - STATS OSTIE ==========
const ostieTotal = computed(() => {
  if (!ostieStore.osties) return 0
  return filterBySelected(ostieStore.osties).length
})

const ostieEnAttente = computed(() => {
  if (!ostieStore.osties) return 0
  return filterBySelected(ostieStore.osties.filter((o: any) => o.statut === 'en_attente')).length
})

const ostieTransformes = computed(() => {
  if (!ostieStore.osties) return 0
  return filterBySelected(ostieStore.osties.filter((o: any) => o.statut === 'transforme')).length
})

const ostieEnAttenteFiltre = computed(() => {
  if (!ostieStore.osties || !isManagerOrHigher.value) return []
  return filterBySelected(ostieStore.osties.filter((o: any) => o.statut === 'en_attente'))
})

// ========== COMPUTED - STATS PERMISSIONS ==========
const permissionsHeures = computed(() => {
  if (!permissionsStore.permissions) return '0.00'
  const filtered = filterBySelected(permissionsStore.permissions)
  const total = filtered.reduce((acc: number, p: any) => acc + (parseFloat(p.heures_a_rattraper) || 0), 0)
  return total.toFixed(2)
})

const permissionsRattrapage = computed(() => {
  if (!permissionsStore.permissionsRattrapage) return []
  return permissionsStore.permissionsRattrapage.filter((p: any) => 
    !selectedEquipeId.value || membresEquipe.value.some((m: any) => m.id === p.utilisateur)
  )
})

const permissionsRetournees = computed(() => {
  if (!permissionsStore.permissionsRetournees) return []
  return permissionsStore.permissionsRetournees.filter((p: any) => 
    !selectedEquipeId.value || membresEquipe.value.some((m: any) => m.id === p.utilisateur)
  )
})

const permissionsEnAttenteFiltre = computed(() => {
  if (!permissionsStore.permissions || !isManagerOrHigher.value) return []
  return filterBySelected(permissionsStore.permissions.filter((p: any) => p.statut === 'en_attente'))
})

// ========== COMPUTED - STATS REPOS ==========
const reposHeures = computed(() => {
  if (!reposStore.reposMedicaux) return '0.00'
  const filtered = filterBySelected(reposStore.reposMedicaux)
  const total = filtered.reduce((acc: number, r: any) => acc + (parseFloat(r.duree_heures) || 0), 0)
  return total.toFixed(2)
})

const reposEnAttente = computed(() => {
  if (!reposStore.reposMedicaux) return []
  return filterBySelected(reposStore.reposMedicaux.filter((r: any) => r.statut === 'en_attente'))
})

const reposApprouves = computed(() => {
  if (!reposStore.reposMedicaux) return 0
  return filterBySelected(reposStore.reposMedicaux.filter((r: any) => r.statut === 'approuve')).length
})

const reposEnAttenteFiltre = computed(() => {
  if (!reposStore.reposMedicaux || !isManagerOrHigher.value) return []
  return filterBySelected(reposStore.reposMedicaux.filter((r: any) => r.statut === 'en_attente'))
})

// ========== COMPUTED - STATS RETARDS ==========
const retardsHeures = computed(() => {
  if (!retardsStore.retards) return '0.00'
  const filtered = filterBySelected(retardsStore.retards)
  const total = filtered.reduce((acc: number, r: any) => acc + (parseFloat(r.heures_a_rattraper) || 0), 0)
  return total.toFixed(2)
})

const retardsEnCours = computed(() => {
  if (!retardsStore.retardsEnCours) return []
  return retardsStore.retardsEnCours.filter((r: any) => 
    !selectedEquipeId.value || membresEquipe.value.some((m: any) => m.id === r.utilisateur)
  )
})

const retardsRattrapes = computed(() => {
  if (!retardsStore.retards) return 0
  return filterBySelected(retardsStore.retards.filter((r: any) => r.statut === 'approuve')).length
})

const retardsEnAttenteFiltre = computed(() => {
  if (!retardsStore.retards || !isManagerOrHigher.value) return []
  return filterBySelected(retardsStore.retards.filter((r: any) => 
    r.statut === 'en_attente' || r.statut === 'en_cours'
  ))
})

// ========== COMPUTED - TOTAL EN ATTENTE FILTRÉ ==========
const totalEnAttenteFiltre = computed(() => {
  return congesEnAttenteFiltre.value.length +
         ostieEnAttenteFiltre.value.length +
         permissionsEnAttenteFiltre.value.length +
         reposEnAttenteFiltre.value.length +
         retardsEnAttenteFiltre.value.length
})

// ========== COMPUTED - APERÇU ÉQUIPE FILTRÉ ==========
const absentsAujourdhuiFiltre = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  let count = 0
  
  const membresIds = selectedEquipeId.value ? membresEquipe.value.map((m: any) => m.id) : []
  
  // Congés aujourd'hui
  if (congesStore.conges) {
    count += congesStore.conges.filter((c: any) => 
      c.statut === 'approuve' && 
      c.date_debut <= today && 
      c.date_fin >= today &&
      (!selectedEquipeId.value || membresIds.includes(c.utilisateur))
    ).length
  }
  
  // OSTIE aujourd'hui
  if (ostieStore.osties) {
    count += ostieStore.osties.filter((o: any) => 
      (o.statut === 'approuve' || o.statut === 'transforme') && 
      o.date === today &&
      (!selectedEquipeId.value || membresIds.includes(o.utilisateur))
    ).length
  }
  
  // Repos médicaux aujourd'hui
  if (reposStore.reposMedicaux) {
    count += reposStore.reposMedicaux.filter((r: any) => 
      r.statut === 'approuve' && 
      r.date === today &&
      (!selectedEquipeId.value || membresIds.includes(r.utilisateur))
    ).length
  }
  
  return count
})

const retardsAujourdhuiFiltre = computed(() => {
  const today = format(new Date(), 'yyyy-MM-dd')
  const membresIds = selectedEquipeId.value ? membresEquipe.value.map((m: any) => m.id) : []
  
  if (!retardsStore.retards) return 0
  return retardsStore.retards.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && 
    r.date === today &&
    (!selectedEquipeId.value || membresIds.includes(r.utilisateur))
  ).length
})

const tauxAbsenteismeFiltre = computed(() => {
  const membresCount = selectedEquipeId.value ? membresEquipe.value.length : 
    (equipesStore.equipes ? equipesStore.equipes.reduce((acc: number, e: any) => acc + (e.membres_count || 0), 0) : 0)
  
  if (membresCount === 0) return 0
  return ((absentsAujourdhuiFiltre.value / membresCount) * 100).toFixed(1)
})

const topRetardatairesFiltre = computed(() => {
  if (!retardsStore.retards) return []
  
  const membresIds = selectedEquipeId.value ? membresEquipe.value.map((m: any) => m.id) : []
  const stats: Record<number, { name: string; total: number }> = {}
  
  retardsStore.retards.forEach((r: any) => {
    if ((r.statut === 'approuve' || r.statut === 'en_cours') &&
        (!selectedEquipeId.value || membresIds.includes(r.utilisateur))) {
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

// ========== COMPUTED - STATS GLOBALES AVEC VRAIES DONNÉES ==========
const globalStats = computed(() => {
  return {
    conges: congesStore.conges?.length || 0,
    ostie: ostieStore.osties?.length || 0,
    permissions: permissionsStore.permissions?.length || 0,
    repos: reposStore.reposMedicaux?.length || 0,
    retards: retardsStore.retards?.length || 0
  }
})

const evolutionMensuelle = computed(() => {
  // Initialiser un tableau de 12 mois avec 0
  const mois = new Array(12).fill(0)
  
  // Compter les demandes par mois
  const compterParMois = (items: any[] | null) => {
    if (!items) return
    items.forEach((item: any) => {
      if (item.date_creation) {
        try {
          const moisIndex = getMonth(parseISO(item.date_creation))
          mois[moisIndex]++
        } catch (e) {
          // Ignorer les dates invalides
        }
      }
    })
  }
  
  compterParMois(congesStore.conges)
  compterParMois(ostieStore.osties)
  compterParMois(permissionsStore.permissions)
  compterParMois(reposStore.reposMedicaux)
  compterParMois(retardsStore.retards)
  
  // Calculer le maximum pour les pourcentages
  const max = Math.max(...mois, 1)
  
  // Retourner les pourcentages
  return mois.map(val => Math.round((val / max) * 100))
})

// ========== COMPUTED - MES DEMANDES ==========
const mesDemandes = computed(() => {
  const demandes: any[] = []
  const userId = authStore.user?.id

  // Congés
  if (congesStore.conges) {
    congesStore.conges.forEach((c: any) => {
      if (c.utilisateur === userId) {
        demandes.push({
          ...c,
          type: 'conges',
          type_label: 'Congé',
          icon: 'bi-calendar-check',
          color: '#1976d2'
        })
      }
    })
  }

  // OSTIE
  if (ostieStore.osties) {
    ostieStore.osties.forEach((o: any) => {
      if (o.utilisateur === userId) {
        demandes.push({
          ...o,
          type: 'ostie',
          type_label: 'OSTIE',
          icon: 'bi-heart-pulse',
          color: '#f57c00'
        })
      }
    })
  }

  // Permissions
  if (permissionsStore.permissions) {
    permissionsStore.permissions.forEach((p: any) => {
      if (p.utilisateur === userId) {
        demandes.push({
          ...p,
          type: 'permissions',
          type_label: 'Permission',
          icon: 'bi-door-open',
          color: '#388e3c'
        })
      }
    })
  }

  // Repos médicaux
  if (reposStore.reposMedicaux) {
    reposStore.reposMedicaux.forEach((r: any) => {
      if (r.utilisateur === userId) {
        demandes.push({
          ...r,
          type: 'repos',
          type_label: 'Repos médical',
          icon: 'bi-hospital',
          color: '#7b1fa2'
        })
      }
    })
  }

  // Retards
  if (retardsStore.retards) {
    retardsStore.retards.forEach((r: any) => {
      if (r.utilisateur === userId) {
        demandes.push({
          ...r,
          type: 'retards',
          type_label: 'Retard',
          icon: 'bi-clock-history',
          color: '#c62828'
        })
      }
    })
  }

  // Trier par date de création (plus récent d'abord)
  return demandes
    .sort((a, b) => new Date(b.date_creation).getTime() - new Date(a.date_creation).getTime())
    .slice(0, 10)
})

// ========== COMPUTED - ALERTES SYSTÈME ==========
const hasTypesRetard = computed(() => retardsStore.typesRetard?.length > 0)
const hasTypesConge = computed(() => congesStore.typesConge?.length > 0)
const hasDroits = computed(() => congesStore.droits?.length > 0)

const moisNoms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const getMoisCouleur = (moisIndex: number) => {
  const couleurs = ['#1976d2', '#f57c00', '#388e3c', '#7b1fa2', '#c62828']
  return couleurs[moisIndex % couleurs.length]
}

// ========== METHODS ==========
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

const canViewDetails = (module: string) => true

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

// ========== FILTRES ==========
const onEquipeChange = async () => {
  selectedMembreId.value = ''
  
  if (selectedEquipeId.value) {
    await loadMembresEquipe(selectedEquipeId.value)
  } else {
    membresEquipe.value = []
  }
}

const onMembreChange = () => {
  // Rien de spécial à faire, les computed se mettront à jour
}

const resetFilters = () => {
  selectedEquipeId.value = ''
  selectedMembreId.value = ''
  membresEquipe.value = []
}

const loadMembresEquipe = async (equipeId: number) => {
  try {
    // Utiliser l'API des équipes pour charger les membres
    // À adapter selon ton API
    const response = await fetch(`/api/equipes/${equipeId}/membres/`)
    if (response.ok) {
      membresEquipe.value = await response.json()
    }
  } catch (error) {
    console.error('Erreur chargement membres:', error)
    membresEquipe.value = []
  }
}

const chargerEquipesHierarchiques = () => {
  if (!equipesStore.equipes) return []
  
  const buildHierarchy = (equipes: any[], niveau: number = 0): any[] => {
    const result: any[] = []
    
    equipes.forEach(equipe => {
      result.push({
        ...equipe,
        niveau
      })
      
      if (equipe.sous_equipes && equipe.sous_equipes.length > 0) {
        result.push(...buildHierarchy(equipe.sous_equipes, niveau + 1))
      }
    })
    
    return result
  }
  
  return buildHierarchy(equipesStore.equipes)
}

// ========== REFRESH ==========
const refreshAllData = async () => {
  loading.value = true
  
  const currentYear = getYear(new Date())
  anneeActuelle.value = currentYear
  
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
    equipesStore.fetchArbre(true)
  ])
  
  equipesHierarchiques.value = chargerEquipesHierarchiques()
  
  if (selectedEquipeId.value) {
    await loadMembresEquipe(selectedEquipeId.value)
  }
  
  loading.value = false
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshAllData()
})
</script>

<style scoped>
/* Garder tout le CSS précédent et ajouter : */

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.filters-section h2 {
  margin: 0 0 15px 0;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #666;
}

.filters-container {
  display: flex;
  gap: 15px;
  align-items: flex-end;
  flex-wrap: wrap;
}

.filter-group {
  flex: 1;
  min-width: 250px;
}

.filter-group label {
  display: block;
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.filter-group select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: white;
  font-size: 14px;
}

.btn-reset {
  padding: 10px 16px;
  background: #f5f5f5;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  white-space: nowrap;
}

.btn-reset:hover {
  background: #e0e0e0;
}

.filter-badge {
  margin-top: 15px;
  padding: 8px 12px;
  background: #e3f2fd;
  border-radius: 20px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #1976d2;
}

.filter-context {
  font-size: 14px;
  font-weight: normal;
  color: #666;
  margin-left: 8px;
}

.pending-card.retards h3 { color: #c62828; }
.pending-card.retards .header-badge { background: #ffebee; color: #c62828; }

.bar-value {
  min-width: 35px;
  font-size: 12px;
  color: #666;
  text-align: right;
}
</style>