<template>
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
                  v-if="user.is_staff && canEditUser(user)"
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
                    {{ pole.code }} - {{ pole.nom }}
                  </option>
                </select>
                <!-- <span v-else class="pole-badge" :class="{ 'empty': !user.pole }">
                  {{ user.pole_details?.nom || 'Aucun' }}
                </span> -->
                <i v-if="updatingUser === user.id && updatingField === 'pole'" class="bi bi-arrow-repeat spin-small"></i>
              </div>
            </td>
            
            <!-- ÉQUIPE - MENU DÉROULANT INLINE AVEC INDICATION -->
            <td>
              <div class="equipe-cell">
                <select 
                  v-if="user.is_staff && canEditUser(user)"
                  v-model="user.equipe" 
                  @change="updateUserEquipe(user)"
                  class="inline-select"
                  :class="{ 
                    'empty': !user.equipe,
                    'is-manager': user.est_chef_equipe,
                    'is-co-manager': user.est_co_manager,
                    'is-member': user.equipe && !user.est_chef_equipe && !user.est_co_manager
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
// CORRECTION ICI : Permet d' autorise l'auto-édition
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
  
  // Vérifier si l'utilisateur est co-manager de son équipe
  const userEquipe = equipesStore.equipesActives.find(e => e.id === user.equipe)
  if (userEquipe?.co_managers?.includes(user.id)) return 'Co-Manager'
  
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

/* Barre de recherche */
.search-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-input {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-input i {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #95a5a6;
}

.search-input input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 3rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.search-input input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.clear-search {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #95a5a6;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.clear-search:hover {
  background-color: #f8f9fa;
  color: #e74c3c;
}

.filters {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
  min-width: 150px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.header-actions .btn-refresh {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.75rem;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #2c3e50;
  transform: rotate(180deg);
}

/* Tableau */
.table-container {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.loading, .error, .no-data {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.spin {
  animation: spin 1s linear infinite;
  font-size: 1.5rem;
}

.error {
  color: #e74c3c;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry:hover {
  background: #2980b9;
}

/* STYLES POUR LES MENUS DÉROULANTS INLINE */
.cell-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.inline-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;

  min-width: 130px;
  max-width: 170px;
  padding: 0.35rem 1.75rem 0.35rem 0.75rem;

  font-family: 'Courier New', monospace;
  font-size: 0.85em;
  font-weight: 500;

  border-radius: 999px; /* effet badge */
  border: 1px solid #dee2e6;

  background-color: #ffffff;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 20 20'%3E%3Cpath fill='%2395a5a6' d='M5 7l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.6rem center;

  cursor: pointer;
  transition: all 0.2s ease;
}

.inline-select:hover:not(:disabled) {
  border-color: #3498db;
  background-color: #f8fbff;
}

.inline-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.12);
}

.inline-select.empty {
  color: #6c757d;
  font-style: italic;
  background-color: #f8f9fa;
  border-style: dashed;
  border-color: #ced4da;
}

.inline-select.empty:hover:not(:disabled) {
  background-color: #f1f3f5;
  border-color: #adb5bd;
}

.inline-select:disabled {
  background-color: #f1f3f5;
  color: #adb5bd;
  border-style: dotted;
  cursor: not-allowed;
  opacity: 1;
  background-image: none;
}

/* RÔLES INLINE SELECT – PRIORITÉ FIXÉE */
.inline-select.is-manager {
  border-color: #E94242;
  background-color: rgba(230, 126, 34, 0.12);
  color: #E94242;
}

.inline-select.is-co-manager {
  border-color: #2ecc71;
  background-color: rgba(46, 204, 113, 0.12);
  color: #2b8a3e;
}

.inline-select.is-member {
  border-color: #3498db;
  background-color: rgba(52, 152, 219, 0.12);
  color: #1d4ed8;
}

/* Icônes */
.inline-select.is-manager::after {
  content: " 👑";
}

.inline-select.is-co-manager::after {
  content: " 🤝";
}

.inline-select.is-member::after {
  content: " 👤";
}

/* Pour forcer la priorité si plusieurs classes sont présentes */
.inline-select.is-co-manager.is-member {
  border-color: #2ecc71 !important;
  background-color: rgba(46, 204, 113, 0.12) !important;
  color: #2b8a3e !important;
}

.spin-small {
  animation: spin 1s linear infinite;
  font-size: 0.8em;
  color: #3498db;
}

/* Cellule équipe */
.equipe-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

/* Badges */
.pole-badge {
  font-family: 'Courier New', monospace;
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background-color: #e9ecef;
  border-radius: 12px;
  font-size: 0.85em;
  color: #495057;
  border: 1px solid #dee2e6;
}

.pole-badge.empty {
  background-color: #f8f9fa;
  color: #6c757d;
  font-style: italic;
}

.equipe-badge {
  font-family: 'Courier New', monospace;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  background-color: #e7f5ff;
  border-radius: 12px;
  font-size: 0.85em;
  color: #1971c2;
  border: 1px solid #a5d8ff;
}

.equipe-badge.has-equipe {
  background-color: #d1f7c4;
  border-color: #8ce99a;
  color: #2b8a3e;
}

.equipe-badge.has-equipe-no-pole {
  background-color: #fff3cd;
  border-color: #ffeaa7;
  color: #856404;
}

.equipe-badge.empty {
  background-color: #f8f9fa;
  color: #6c757d;
  font-style: italic;
  border-color: #dee2e6;
}

/* Indicateur de rôle dans l'équipe */
.role-indicator {
  font-family: 'Courier New', monospace;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.5rem;
  border-radius: 10px;
  font-size: 0.75em;
  font-weight: 500;
  white-space: nowrap;
}

.role-indicator.role-manager {
  background-color: rgba(230, 126, 34, 0.1);
  color: #E94242;
  border: 1px solid rgba(230, 126, 34, 0.2);
}

.role-indicator.role-membre {
  background-color: rgba(52, 152, 219, 0.1);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.role-indicator.role-none {
  display: none;
}

/* Badge rôle principal */
.role-badge {
  font-family: 'Courier New', monospace;
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.role-badge.admin {
  background-color: rgba(52, 152, 219, 0.1);
  color: #1971c2;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

.role-badge.super {
  background-color: rgba(231, 76, 60, 0.1);
  color: #E94242;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.role-badge.user {
  background-color: rgba(46, 204, 113, 0.1);
  color: #27ae60;
  border: 1px solid rgba(46, 204, 113, 0.2);
}

/* Tableau principal */
.users-table {
  font-family: 'Courier New', monospace;
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.users-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  white-space: nowrap;
}

.sortable {
  cursor: pointer;
  transition: background-color 0.2s;
  position: relative;
}

.sortable:hover {
  background: #e9ecef;
}

.sortable i {
  margin-left: 0.5rem;
  font-size: 0.8em;
  opacity: 0.7;
}

.users-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.users-table tr:hover {
  background: #f8fafc;
}

.matricule {
  font-family: 'Courier New', monospace;
  font-weight: 600;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.pseudo {
  font-family: 'Courier New', monospace;
  background: #e8f4fc;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
  font-size: 0.85rem;
}

.email-link {
  font-family: 'Courier New', monospace;
  color: #3498db;
  text-decoration: none;
  transition: color 0.2s;
}

.email-link:hover {
  color: #2980b9;
  text-decoration: underline;
}

.last-login {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #6c757d;
  white-space: nowrap;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  background: white;
  border-top: 1px solid #e9ecef;
  border-radius: 0 0 8px 8px;
}

.page-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-btn:not(:disabled):hover {
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
  min-width: 100px;
  text-align: center;
}

.page-select {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 0.9rem;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto;          /* ← important : permet aux colonnes de s'adapter */
  min-width: 0;                /* ← aide à contrer le débordement */
}

.users-table th,
.users-table td {
  padding: 0.75rem 0.9rem;
  overflow: hidden;            /* ← coupe le texte qui dépasse */
  text-overflow: ellipsis;     /* ← ajoute ... quand ça dépasse */
  white-space: nowrap;         /* garde pour desktop, mais on override en mobile */
}


@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

@media (max-width: 1024px) {
  .users-table th,
  .users-table td {
    padding: 0.6rem 0.7rem;
    font-size: 0.88rem;
  }
  
  .inline-select {
    min-width: 110px;
    max-width: 140px;
    font-size: 0.82rem;
    padding: 0.3rem 1.4rem 0.3rem 0.6rem;
  }
}


@media (max-width: 768px) {
  .search-bar {
    flex-direction: column;
    gap: 1rem;
  }
  
  .filters {
    flex-direction: column;
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
    min-width: unset;
  }
  
  /* Permettre au texte de wrapper quand vraiment trop petit */
  .users-table th,
  .users-table td {
    white-space: normal;       /* ← différence clé */
    min-width: 80px;           /* évite colonnes trop écrasées */
  }
  
  .matricule,
  .pseudo,
  .email-link,
  .last-login {
    white-space: normal;       /* ← le plus important ! */
    word-break: break-all;     /* ou break-word selon préférence */
  }
  
  .equipe-cell {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.4rem;
  }
  
  .role-indicator {
    font-size: 0.7rem;
  }
}


@media (max-width: 992px) {
  .table-container {
    overflow-x: auto;
    -ms-overflow-style: scrollbar;
  }
  
  .users-table {
    min-width: 1100px;   /* force le scroll horizontal au lieu d'écraser */
  }
}

</style>