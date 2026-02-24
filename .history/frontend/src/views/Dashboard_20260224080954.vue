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
    <!-- KPI CARDS - Commun à tous les rôles         -->
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
    <!-- SECTION MANAGER/ADMIN - Stats équipe         -->
    <!-- ============================================ -->
    <div v-if="isManagerOrHigher" class="dashboard-section">
      <h2>
        <i class="bi bi-graph-up"></i>
        Aperçu de l'équipe
      </h2>
      
      <div class="team-stats">
        <div class="stat-row">
          <div class="stat-item">
            <span class="stat-label">Membres</span>
            <span class="stat-value">{{ teamMembers }}</span>
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

      <!-- Top retardataires (pour managers) -->
      <div v-if="topRetardataires.length > 0" class="top-list">
        <h3>⏰ Top des retardataires</h3>
        <div class="top-items">
          <div v-for="(item, index) in topRetardataires" :key="item.userId" class="top-item">
            <span class="top-rank">{{ index + 1 }}</span>
            <span class="top-name">{{ item.name }}</span>
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
            <h4>Évolution mensuelle</h4>
            <div class="bar-chart-placeholder">
              <div v-for="(mois, index) in moisNoms" :key="index" class="bar-item">
                <span class="bar-label">{{ mois.substring(0,3) }}</span>
                <div class="bar-container">
                  <div class="bar" :style="{ width: getMoisPourcentage(index) + '%', background: getMoisCouleur(index) }"></div>
                </div>
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
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useOstieStore } from '@/store/ostie'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useRetardsStore } from '@/store/retards'
import { useFiltersStore } from '@/store/filters'
import { format, parseISO, formatDistanceToNow, differenceInMinutes } from 'date-fns'
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
const filtersStore = useFiltersStore()

// ========== STATE ==========
const loading = ref(false)

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

const canViewDetails = (module: string) => true // Tous peuvent voir leurs modules

const displayName = computed(() => {
  return authStore.user?.display_name || authStore.user?.username || 'Utilisateur'
})

const currentDate = computed(() => {
  return format(new Date(), 'EEEE d MMMM yyyy', { locale: fr })
})

// ========== COMPUTED - STATS CONGÉS ==========
const congesSolde = computed(() => {
  return authStore.soldeConge?.actuelle || '0'
})

const congesApprouves = computed(() => {
  if (!congesStore.conges) return 0
  return congesStore.conges.filter((c: any) => c.statut === 'approuve').length
})

const congesEnAttente = computed(() => {
  if (!congesStore.conges) return 0
  return congesStore.conges.filter((c: any) => c.statut === 'en_attente').length
})

const congesEnAttenteList = computed(() => {
  if (!congesStore.conges || !isManagerOrHigher.value) return []
  return congesStore.conges.filter((c: any) => c.statut === 'en_attente')
})

// ========== COMPUTED - STATS OSTIE ==========
const ostieTotal = computed(() => ostieStore.totalOsties || 0)
const ostieEnAttente = computed(() => ostieStore.ostiesEnAttente?.length || 0)
const ostieTransformes = computed(() => {
  if (!ostieStore.osties) return 0
  return ostieStore.osties.filter((o: any) => o.statut === 'transforme').length
})

const ostieEnAttenteList = computed(() => {
  if (!ostieStore.osties || !isManagerOrHigher.value) return []
  return ostieStore.osties.filter((o: any) => o.statut === 'en_attente')
})

// ========== COMPUTED - STATS PERMISSIONS ==========
const permissionsHeures = computed(() => {
  return (permissionsStore.totalHeuresARattraper || 0).toFixed(2)
})

const permissionsRattrapage = computed(() => permissionsStore.permissionsRattrapage || [])
const permissionsRetournees = computed(() => permissionsStore.permissionsRetournees || [])

const permissionsEnAttenteList = computed(() => {
  if (!permissionsStore.permissions || !isManagerOrHigher.value) return []
  return permissionsStore.permissions.filter((p: any) => p.statut === 'en_attente')
})

// ========== COMPUTED - STATS REPOS ==========
const reposHeures = computed(() => {
  return (reposStore.totalHeuresRepos || 0).toFixed(2)
})

const reposEnAttente = computed(() => reposStore.reposEnAttente || [])
const reposApprouves = computed(() => {
  if (!reposStore.reposMedicaux) return 0
  return reposStore.reposMedicaux.filter((r: any) => r.statut === 'approuve').length
})

const reposEnAttenteList = computed(() => {
  if (!reposStore.reposMedicaux || !isManagerOrHigher.value) return []
  return reposStore.reposMedicaux.filter((r: any) => r.statut === 'en_attente')
})

// ========== COMPUTED - STATS RETARDS ==========
const retardsHeures = computed(() => {
  const total = retardsStore.totalHeuresARattraper
  return (typeof total === 'number' ? total : parseFloat(String(total)) || 0).toFixed(2)
})

const retardsEnCours = computed(() => retardsStore.retardsEnCours || [])
const retardsRattrapes = computed(() => {
  if (!retardsStore.retards) return 0
  return retardsStore.retards.filter((r: any) => r.statut === 'approuve').length
})

// ========== COMPUTED - TOTAL EN ATTENTE ==========
const totalEnAttente = computed(() => {
  return congesEnAttenteList.value.length +
         ostieEnAttenteList.value.length +
         permissionsEnAttenteList.value.length +
         reposEnAttenteList.value.length
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
    .slice(0, 10) // Garder les 10 plus récents
})

// ========== COMPUTED - STATS ÉQUIPE ==========
const teamMembers = computed(() => {
  if (!isManagerOrHigher.value) return 0
  // Remplacer par la vraie propriété de votre store filters
  return 0 // À ajuster selon votre store
})

const absentsAujourdhui = computed(() => {
  if (!isManagerOrHigher.value) return 0
  const today = format(new Date(), 'yyyy-MM-dd')
  let count = 0
  
  // Congés aujourd'hui
  if (congesStore.conges) {
    count += congesStore.conges.filter((c: any) => 
      c.statut === 'approuve' && 
      c.date_debut <= today && 
      c.date_fin >= today
    ).length
  }
  
  // OSTIE aujourd'hui
  if (ostieStore.osties) {
    count += ostieStore.osties.filter((o: any) => 
      (o.statut === 'approuve' || o.statut === 'transforme') && 
      o.date === today
    ).length
  }
  
  // Repos médicaux aujourd'hui
  if (reposStore.reposMedicaux) {
    count += reposStore.reposMedicaux.filter((r: any) => 
      r.statut === 'approuve' && 
      r.date === today
    ).length
  }
  
  return count
})

const retardsAujourdhui = computed(() => {
  if (!isManagerOrHigher.value) return 0
  const today = format(new Date(), 'yyyy-MM-dd')
  
  if (!retardsStore.retards) return 0
  return retardsStore.retards.filter((r: any) => 
    (r.statut === 'en_attente' || r.statut === 'en_cours') && 
    r.date === today
  ).length
})

const tauxAbsenteisme = computed(() => {
  if (!isManagerOrHigher.value || teamMembers.value === 0) return 0
  return ((absentsAujourdhui.value / teamMembers.value) * 100).toFixed(1)
})

// ========== COMPUTED - TOP RETARDATAIRES ==========
const topRetardataires = computed(() => {
  if (!isManagerOrHigher.value || !retardsStore.retards) return []
  
  const stats: Record<number, { name: string; total: number }> = {}
  
  retardsStore.retards.forEach((r: any) => {
    if (r.statut === 'approuve' || r.statut === 'en_cours') {
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

// ========== COMPUTED - STATS GLOBALES (SUPER ADMIN) ==========
const globalStats = computed(() => {
  return {
    conges: congesStore.conges?.length || 0,
    ostie: ostieStore.osties?.length || 0,
    permissions: permissionsStore.permissions?.length || 0,
    repos: reposStore.reposMedicaux?.length || 0,
    retards: retardsStore.retards?.length || 0
  }
})

const moisNoms = ['Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin', 'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']

const getMoisPourcentage = (moisIndex: number) => {
  // Simulation - à remplacer par de vraies données
  return Math.floor(Math.random() * 80) + 10
}

const getMoisCouleur = (moisIndex: number) => {
  const couleurs = ['#1976d2', '#f57c00', '#388e3c', '#7b1fa2', '#c62828']
  return couleurs[moisIndex % couleurs.length]
}

// ========== COMPUTED - ALERTES SYSTÈME ==========
const hasTypesRetard = computed(() => retardsStore.typesRetard?.length > 0)
const hasTypesConge = computed(() => congesStore.typesConge?.length > 0)
const hasDroits = computed(() => congesStore.droits?.length > 0)

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

const formatDateTime = (dateStr: string | undefined) => {
  if (!dateStr) return ''
  try {
    return format(parseISO(dateStr), 'dd/MM/yyyy HH:mm', { locale: fr })
  } catch {
    return ''
  }
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
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshAllData()
})
</script>




<style scoped>
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

/* KPI Cards */
.kpi-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
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
  gap: 10px;
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
  justify-content:-center;
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
}
</style>