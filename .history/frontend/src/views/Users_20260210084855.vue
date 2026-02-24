<template>
  <div class="users-page">
    <!-- En-tête avec titre et boutons -->
    <div class="page-header">
      <h1>Gestion des Utilisateurs</h1>
    </div>

    <!-- Barre de recherche et filtres -->
    <div class="search-bar">
      <div class="search-input">
        <i class="bi bi-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Rechercher par matricule, pseudo, nom, email..." 
          @input="handleSearch"
        />
        <button 
          v-if="searchQuery" 
          @click="clearSearch" 
          class="clear-search"
          title="Effacer la recherche"
        >
          <i class="bi bi-x"></i>
        </button>
      </div>

      <div class="filters">
        <!-- Filtre par rôle -->
        <select v-model="roleFilter" @change="applyFilters" class="filter-select">
          <option value="">Tous les rôles</option>
          <option value="admin">Administrateurs</option>
          <option value="user">Utilisateurs</option>
          <option value="super">Super Admins</option>
        </select>

        <!-- Filtre par pôle -->
        <select v-model="poleFilter" @change="applyFilters" class="filter-select">
          <option value="">Tous les pôles</option>
          <option 
            v-for="pole in polesStore.polesActifs" 
            :key="pole.id" 
            :value="pole.id"
          >
            {{ pole.code }} - {{ pole.nom }}
          </option>
        </select>

        <!-- Filtre par équipe -->
        <select 
          v-model="equipeFilter" 
          @change="applyFilters" 
          class="filter-select"
        >
          <option value="">Toutes les équipes</option>
          <option 
            v-for="equipe in equipesFiltreesPourSelect" 
            :key="equipe.id" 
            :value="equipe.id"
          >
            {{ equipe.nom }}
          </option>
        </select>
      </div>

      <div class="header-actions">
        <button class="btn-refresh" @click="refreshUsers" title="Actualiser">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- Tableau des utilisateurs -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <i class="bi bi-arrow-repeat spin"></i>
        <span>Chargement des utilisateurs...</span>
      </div>
      
      <div v-else-if="error" class="error">
        <i class="bi bi-exclamation-triangle"></i>
        <span>{{ error }}</span>
        <button @click="fetchAllUsers" class="btn-retry">Réessayer</button>
      </div>
      
      <div v-else-if="filteredUsers.length === 0" class="no-data">
        <i class="bi bi-people"></i>
        <span v-if="searchQuery">Aucun utilisateur ne correspond à votre recherche</span>
        <span v-else>Aucun utilisateur trouvé</span>
      </div>
      
      <table v-else class="users-table">
        <thead>
          <tr>
            <th @click="sortBy('username')" class="sortable">
              Matricule
              <i v-if="sortField === 'username'" class="bi" :class="sortIcon"></i>
            </th>
            <th @click="sortBy('pseudo')" class="sortable">
              Pseudo
              <i v-if="sortField === 'pseudo'" class="bi" :class="sortIcon"></i>
            </th>
            <th @click="sortBy('last_name')" class="sortable">
              Nom
              <i v-if="sortField === 'last_name'" class="bi" :class="sortIcon"></i>
            </th>
            <th @click="sortBy('first_name')" class="sortable">
              Prénom
              <i v-if="sortField === 'first_name'" class="bi" :class="sortIcon"></i>
            </th>
            <th @click="sortBy('email')" class="sortable">
              Email
              <i v-if="sortField === 'email'" class="bi" :class="sortIcon"></i>
            </th>
            <th>Pôle</th>
            <th>Équipe</th>
            <th>Rôle</th>
            <th>Dernière connexion</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in paginatedUsers" :key="user.id">
            <td class="matricule">{{ user.username.toUpperCase() }}</td>
            <td>
              <span class="pseudo">{{ generatePseudo(user.last_name, user.pseudo) }}</span>
            </td>
            <td>{{ user.first_name || '-' }}</td>
            <td>{{ user.last_name || '-' }}</td>
            <td>
              <a :href="`mailto:${user.email}`" class="email-link">{{ user.email }}</a>
            </td>
            
            <!-- PÔLE - MENU DÉROULANT INLINE -->
            <td>
              <div class="cell-content">
                <select 
                  v-if="isAdmin && canEditUser(user)"
                  v-model="user.pole" 
                  @change="updateUserPole(user)"
                  class="inline-select"
                  :class="{ 'empty': !user.pole }"
                >
                  <option :value="null">Aucun pôle</option>
                  <option 
                    v-for="pole in polesStore.polesActifs" 
                    :key="pole.id" 
                    :value="pole.id"
                  >
                    {{ pole.code }}
                  </option>
                </select>
                <span v-else class="pole-badge" :class="{ 'empty': !user.pole }">
                  {{ user.pole_details?.nom || 'Aucun' }}
                </span>
                <i v-if="updatingUser === user.id && updatingField === 'pole'" class="bi bi-arrow-repeat spin-small"></i>
              </div>
            </td>
            
            <!-- ÉQUIPE - MENU DÉROULANT INLINE AVEC INDICATION -->
            <td>
              <div class="equipe-cell">
                <select 
                  v-if="isAdmin && canEditUser(user)"
                  v-model="user.equipe" 
                  @change="updateUserEquipe(user)"
                  class="inline-select"
                  :class="{ 
                    'empty': !user.equipe,
                    'has-equipe': user.equipe,
                    'is-manager': user.est_chef_equipe
                  }"
                  :disabled="!user.pole"
                >
                  <option :value="null">
                    {{ user.pole ? 'Aucune équipe' : 'Sélectionnez d\'abord un pôle' }}
                  </option>
                  <option 
                    v-for="equipe in getEquipesForUserPole(user)" 
                    :key="equipe.id" 
                    :value="equipe.id"
                  >
                    {{ equipe.nom }}
                  </option>
                </select>
                <span v-else class="equipe-badge" :class="{ 
                  'empty': !user.equipe,
                  'has-equipe': user.equipe,
                  'has-equipe-no-pole': user.equipe && !user.pole
                }">
                  {{ getEquipeDisplay(user) }}
                  <i v-if="user.equipe && !user.pole" class="bi bi-exclamation-triangle" title="Cette équipe ne correspond à aucun pôle"></i>
                </span>
                
                <!-- INDICATION VISUELLE DU RÔLE DANS L'ÉQUIPE -->
                <span v-if="user.equipe" class="role-indicator" :class="getEquipeRoleClass(user)">
                  <i class="bi" :class="getEquipeRoleIcon(user)"></i>
                  {{ getEquipeRoleLabel(user) }}
                </span>
                <i v-if="updatingUser === user.id && updatingField === 'equipe'" class="bi bi-arrow-repeat spin-small"></i>
              </div>
            </td>
            
            <td>
              <span class="role-badge" :class="getRoleClass(user)">
                {{ getRoleLabel(user) }}
              </span>
            </td>
            <td>
              <span class="last-login">
                {{ user.last_login ? formatDate(user.last_login) : 'Jamais' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div v-if="filteredUsers.length > itemsPerPage" class="pagination">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1" 
        class="page-btn"
      >
        <i class="bi bi-chevron-left"></i>
      </button>
      
      <span class="page-info">
        Page {{ currentPage }} sur {{ totalPages }}
      </span>
      
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages" 
        class="page-btn"
      >
        <i class="bi bi-chevron-right"></i>
      </button>
      
      <select v-model="itemsPerPage" @change="changeItemsPerPage" class="page-select">
        <option value="10">10 par page</option>
        <option value="25">25 par page</option>
        <option value="50">50 par page</option>
        <option value="100">100 par page</option>
      </select>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'
import { usePolesStore } from '@/store/poles'
import { useEquipesStore } from '@/store/equipes'
import { useDisplayName } from '@/composables/useDisplayName'
import type { User, Equipe } from '@/types/user'
import { useRoles } from '@/composables/useRoles'

const { getUserRole, getRoleClass, getRoleLabel } = useRoles()

const router = useRouter()
const { isAdmin, user: currentAuthUser } = useAuth()
const polesStore = usePolesStore()
const equipesStore = useEquipesStore()
const { generatePseudo } = useDisplayName()

// État pour la persistance
const USERS_PER_PAGE_KEY = 'users_items_per_page'

// Stockage des données
const allUsers = ref<User[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const updatingUser = ref<number | null>(null)
const updatingField = ref<string>('')

// Filtres et recherche
const searchQuery = ref('')
const roleFilter = ref('')
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')

// Tri
const sortField = ref<string>('last_name')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Pagination (persistante)
const currentPage = ref(1)
const itemsPerPage = ref(Number(localStorage.getItem(USERS_PER_PAGE_KEY)) || 10)

// Réinitialiser le filtre équipe quand le pôle change
watch(poleFilter, () => {
  equipeFilter.value = ''
  currentPage.value = 1
})

// Filtrer les équipes pour le select global
const equipesFiltreesPourSelect = computed(() => {
  if (!poleFilter.value) return equipesStore.equipesActives
  return equipesStore.equipesActives.filter(e => e.pole === poleFilter.value)
})

// ============================================
// CORRECTION ICI : Autorise l'auto-édition
// ============================================
const canEditUser = (user: User): boolean => {
  // Seuls les admins peuvent éditer, mais ils peuvent s'éditer eux-mêmes
  return isAdmin && !!currentAuthUser.value
}

// Récupérer les équipes disponibles pour un user selon son pôle
const getEquipesForUserPole = (user: User): Equipe[] => {
  if (!user.pole) return []
  return equipesStore.equipesActives.filter(e => e.pole === user.pole)
}

// Afficher l'équipe de manière lisible
const getEquipeDisplay = (user: User): string => {
  if (!user.equipe) return 'Aucune'
  if (user.equipe_details) {
    return user.equipe_details.nom
  }
  return `Équipe #${user.equipe}`
}

// Déterminer le rôle de l'utilisateur dans son équipe
const getEquipeRoleClass = (user: User): string => {
  if (!user.equipe) return 'role-none'
  if (user.est_chef_equipe) return 'role-manager'
  return 'role-membre'
}

const getEquipeRoleIcon = (user: User): string => {
  if (!user.equipe) return 'bi-person-x'
  if (user.est_chef_equipe) return 'bi-person-badge-fill'
  return 'bi-person-fill'
}

const getEquipeRoleLabel = (user: User): string => {
  if (!user.equipe) return ''
  if (user.est_chef_equipe) return 'Chef'
  return 'Membre'
}

// Computed properties
const filteredUsers = computed(() => {
  let users = [...allUsers.value]
  
  // Filtre par recherche texte
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    users = users.filter(user => 
      (user.username?.toLowerCase().includes(query)) ||
      (user.pseudo?.toLowerCase().includes(query)) ||
      (user.first_name?.toLowerCase().includes(query)) ||
      (user.last_name?.toLowerCase().includes(query)) ||
      (user.email?.toLowerCase().includes(query))
    )
  }
  
  // Filtre par rôle
  if (roleFilter.value) {
    users = users.filter(user => {
      if (roleFilter.value === 'admin') return user.is_staff
      if (roleFilter.value === 'super') return user.is_superuser
      if (roleFilter.value === 'user') return !user.is_staff && !user.is_superuser
      return true
    })
  }

  // Filtre par pôle
  if (poleFilter.value !== '' && poleFilter.value !== null) {
    users = users.filter(user => user.pole === Number(poleFilter.value))
  }

  // Filtre par équipe
  if (equipeFilter.value !== '' && equipeFilter.value !== null) {
    users = users.filter(user => user.equipe === Number(equipeFilter.value))
  }
  
  // Tri
  users.sort((a, b) => {
    let aValue = a[sortField.value as keyof User]
    let bValue = b[sortField.value as keyof User]
    
    if (aValue == null) aValue = ''
    if (bValue == null) bValue = ''
    
    if (aValue < bValue) return sortDirection.value === 'asc' ? -1 : 1
    if (aValue > bValue) return sortDirection.value === 'asc' ? 1 : -1
    return 0
  })
  
  return users
})

const paginatedUsers = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return filteredUsers.value.slice(start, end)
})

const totalPages = computed(() => {
  return Math.ceil(filteredUsers.value.length / itemsPerPage.value)
})

const sortIcon = computed(() => {
  return sortDirection.value === 'asc' ? 'bi-chevron-up' : 'bi-chevron-down'
})

const fetchAllUsers = async () => {
  loading.value = true
  error.value = null
  
  try {
    await Promise.all([
      usersApi.getAllUsers().then(users => allUsers.value = users),
      polesStore.fetchPoles(),
      equipesStore.fetchEquipes()
    ])
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement des utilisateurs'
    console.error('Erreur:', err)
  } finally {
    loading.value = false
  }
}

const refreshUsers = () => {
  fetchAllUsers()
}

const handleSearch = () => {
  currentPage.value = 1
}

const clearSearch = () => {
  searchQuery.value = ''
  currentPage.value = 1
}

const applyFilters = () => {
  currentPage.value = 1
}

const sortBy = (field: string) => {
  if (sortField.value === field) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortDirection.value = 'asc'
  }
}

const prevPage = () => {
  if (currentPage.value > 1) currentPage.value--
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) currentPage.value++
}

const changeItemsPerPage = () => {
  localStorage.setItem(USERS_PER_PAGE_KEY, itemsPerPage.value.toString())
  currentPage.value = 1
}

// Mise à jour inline du pôle
const updateUserPole = async (user: User) => {
  if (!canEditUser(user)) return
  
  const originalPole = user.pole
  const newPoleId = user.pole || 0
  
  updatingUser.value = user.id
  updatingField.value = 'pole'
  
  try {
    // Si on change de pôle, on retire l'équipe
    const newEquipeId = (originalPole !== user.pole) ? 0 : (user.equipe || 0)
    
    await usersApi.updatePoleEquipe({
      user_id: user.id,
      pole_id: newPoleId,
      equipe_id: newEquipeId
    })
    
    // Si on a changé de pôle, on réinitialise l'équipe
    if (originalPole !== user.pole) {
      user.equipe = null
    }
    
    // Rafraîchir pour avoir les détails à jour
    await fetchAllUsers()
  } catch (err: any) {
    console.error('Erreur lors de la mise à jour du pôle:', err)
    alert(`Erreur lors de la mise à jour du pôle: ${err.message || 'Erreur inconnue'}`)
    
    // Revenir à la valeur d'origine
    user.pole = originalPole
    await fetchAllUsers()
  } finally {
    updatingUser.value = null
    updatingField.value = ''
  }
}

// Mise à jour inline de l'équipe
const updateUserEquipe = async (user: User) => {
  if (!canEditUser(user)) return
  
  const originalEquipe = user.equipe
  const newEquipeId = user.equipe || 0
  
  updatingUser.value = user.id
  updatingField.value = 'equipe'
  
  try {
    await usersApi.updatePoleEquipe({
      user_id: user.id,
      pole_id: user.pole || 0,
      equipe_id: newEquipeId
    })
    
    // Rafraîchir pour avoir les détails à jour
    await fetchAllUsers()
  } catch (err: any) {
    console.error('Erreur lors de la mise à jour de l\'équipe:', err)
    alert(`Erreur lors de la mise à jour de l'équipe: ${err.message || 'Erreur inconnue'}`)
    
    // Revenir à la valeur d'origine
    user.equipe = originalEquipe
    await fetchAllUsers()
  } finally {
    updatingUser.value = null
    updatingField.value = ''
  }
}

const formatDate = (dateString: string) => {
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Date invalide'
    
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Date invalide'
  }
}

onMounted(() => {
  fetchAllUsers()
})
</script>

<style scoped>
.users-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.75rem;
}

.search-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.search-input {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-input i {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
}

.search-input input {
  width: 100%;
  padding: 0.5rem 2.5rem 0.5rem 2.25rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.9rem;
}

.search-input input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.clear-search {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
}

.filters {
  display: flex;
  gap: 0.75rem;
}

.filter-select {
  padding: 0.5rem 2rem 0.5rem 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
  min-width: 150px;
}

.header-actions {
  margin-left: auto;
}

.btn-refresh {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #f8f9fa;
  color: #495057;
}

.table-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.users-table th,
.users-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.users-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.users-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.users-table th.sortable:hover {
  background: #e9ecef;
}

.users-table tbody tr:hover {
  background: #f8f9fa;
}

.matricule {
  font-family: monospace;
  font-weight: 600;
  color: #3498db;
}

.pseudo {
  color: #2c3e50;
  font-weight: 500;
}

.email-link {
  color: #3498db;
  text-decoration: none;
}

.email-link:hover {
  text-decoration: underline;
}

/* Styles pour les selects inline */
.cell-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inline-select {
  padding: 0.35rem 1.5rem 0.35rem 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  font-size: 0.85rem;
  min-width: 120px;
  cursor: pointer;
  transition: all 0.2s;
}

.inline-select:hover {
  border-color: #3498db;
}

.inline-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.inline-select.empty {
  color: #6c757d;
  font-style: italic;
}

.inline-select.has-equipe {
  border-color: #27ae60;
  background: #f0f9f0;
}

.inline-select.is-manager {
  border-color: #f39c12;
  background: #fff8e1;
}

.inline-select:disabled {
  background: #e9ecef;
  cursor: not-allowed;
  opacity: 0.6;
}

/* Badges pour lecture seule */
.pole-badge,
.equipe-badge {
  padding: 0.35rem 0.75rem;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 0.85rem;
  color: #495057;
}

.pole-badge.empty,
.equipe-badge.empty {
  color: #6c757d;
  font-style: italic;
  background: #f8f9fa;
}

.equipe-badge.has-equipe {
  background: #d4efdf;
  color: #27ae60;
  font-weight: 500;
}

.equipe-badge.has-equipe-no-pole {
  background: #fff3cd;
  color: #856404;
}

/* Cellule équipe avec indicateur de rôle */
.equipe-cell {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.role-indicator {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  width: fit-content;
}

.role-indicator.role-manager {
  background: #fff8e1;
  color: #f39c12;
}

.role-indicator.role-membre {
  background: #e8f4fc;
  color: #3498db;
}

/* Badges de rôle */
.role-badge {
  display: inline-block;
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.role-badge.admin {
  background: #e8f4fc;
  color: #3498db;
}

.role-badge.super {
  background: #f5e6ff;
  color: #9b59b6;
}

.role-badge.user {
  background: #e9ecef;
  color: #6c757d;
}

.last-login {
  font-size: 0.85rem;
  color: #6c757d;
}

/* Animation de chargement */
.spin {
  animation: spin 1s linear infinite;
}

.spin-small {
  animation: spin 1s linear infinite;
  font-size: 0.8rem;
  color: #3498db;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* États de chargement et erreur */
.loading,
.error,
.no-data {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.loading i,
.error i,
.no-data i {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

.error {
  color: #e74c3c;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
}

.page-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #495057;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f8f9fa;
  border-color: #3498db;
  color: #3498db;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.page-select {
  padding: 0.35rem 2rem 0.35rem 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  font-size: 0.85rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input {
    min-width: auto;
  }

  .filters {
    flex-wrap: wrap;
  }

  .header-actions {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .users-page {
    padding: 1rem;
  }

  .users-table {
    font-size: 0.8rem;
  }

  .users-table th,
  .users-table td {
    padding: 0.5rem;
  }

  .inline-select {
    min-width: 100px;
    font-size: 0.8rem;
  }
}
</style>