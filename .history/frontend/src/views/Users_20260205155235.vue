<template>
  <div class="users-page">
    <!-- En-tête avec titre et boutons -->
    <div class="page-header">
      <h1>Gestion des Utilisateurs</h1>
      <div class="header-actions">
        <button v-if="activeTab === 'all'" class="btn-refresh" @click="refreshUsers" title="Actualiser">
          <i class="bi bi-arrow-clockwise"></i>
        </button>
      </div>
    </div>

    <!-- Onglets -->
    <div class="tabs-container">
      <div class="tabs">
        <button 
          class="tab" 
          :class="{ active: activeTab === 'all' }" 
          @click="setActiveTab('all')"
        >
          <i class="bi bi-people-fill"></i>
          <span>Voir Tous</span>
          <span v-if="filteredUsers.length > 0" class="tab-badge">
            {{ filteredUsers.length }}
          </span>
        </button>
        
        <button 
          class="tab" 
          :class="{ active: activeTab === 'me' }" 
          @click="setActiveTab('me')"
        >
          <i class="bi bi-person-fill"></i>
          <span>Voir Moi</span>
        </button>
      </div>
    </div>

    <!-- Contenu de l'onglet "Voir Tous" -->
    <div v-if="activeTab === 'all'" class="tab-content">
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
          <select v-model="roleFilter" @change="applyFilters" class="filter-select">
            <option value="">Tous les rôles</option>
            <option value="admin">Administrateurs</option>
            <option value="user">Utilisateurs</option>
            <option value="super">Super Admins</option>
          </select>
          
          <select v-model="statusFilter" @change="applyFilters" class="filter-select">
            <option value="">Tous les statuts</option>
            <option value="active">Actifs</option>
            <option value="inactive">Inactifs</option>
          </select>
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
              <th>Rôle</th>
              <th>Statut</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in paginatedUsers" :key="user.id">
              <td class="matricule">{{ user.username }}</td>
              <td>
                <span v-if="user.pseudo" class="pseudo">{{ user.pseudo }}</span>
                <span v-else class="no-pseudo">-</span>
              </td>
              <td>{{ user.last_name || '-' }}</td>
              <td>{{ user.first_name || '-' }}</td>
              <td>
                <a :href="`mailto:${user.email}`" class="email-link">{{ user.email }}</a>
              </td>
              <td>
                <span class="role-badge" :class="getRoleClass(user)">
                  {{ getUserRole(user) }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="{ active: user.is_active }">
                  {{ user.is_active ? 'Actif' : 'Inactif' }}
                </span>
              </td>
              <td class="actions">
                <button 
                  @click="viewProfile(user)" 
                  class="btn-action view"
                  title="Voir le profil"
                >
                  <i class="bi bi-eye"></i>
                </button>
                <button 
                  v-if="canEditUser(user)" 
                  @click="editUser(user)" 
                  class="btn-action edit"
                  title="Modifier"
                >
                  <i class="bi bi-pencil"></i>
                </button>
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

    <!-- Contenu de l'onglet "Voir Moi" -->
    <div v-else class="tab-content">
      <div class="my-profile">
        <div v-if="loadingProfile" class="loading">
          <i class="bi bi-arrow-repeat spin"></i>
          <span>Chargement de votre profil...</span>
        </div>
        
        <div v-else-if="profileError" class="error">
          <i class="bi bi-exclamation-triangle"></i>
          <span>{{ profileError }}</span>
          <button @click="loadUserProfile" class="btn-retry">Réessayer</button>
        </div>
        
        <div v-else class="profile-card">
          <!-- Avatar et info de base -->
          <div class="profile-header">
            <div class="avatar-large">
              {{ getUserInitials(currentUser) }}
            </div>
            <div class="profile-info">
              <h2>{{ currentUser.display_name }}</h2>
              <p class="user-role">
                <i class="bi bi-person-badge"></i>
                {{ getUserRole(currentUser) }}
              </p>
              <p class="join-date">
                <i class="bi bi-calendar-plus"></i>
                Membre depuis {{ formatDate(currentUser.date_joined) }}
              </p>
            </div>
          </div>
          
          <!-- Formulaires d'édition -->
          <div class="profile-forms">
            <!-- Formulaire Pseudo -->
            <div class="form-section">
              <h3><i class="bi bi-person-square"></i> Modifier mon pseudo</h3>
              <div class="form-group">
                <label>Pseudo actuel</label>
                <div class="current-value">
                  {{ currentUser.pseudo || 'Aucun pseudo défini' }}
                </div>
              </div>
              <div class="form-group">
                <label for="newPseudo">Nouveau pseudo</label>
                <div class="input-with-button">
                  <input 
                    type="text" 
                    id="newPseudo" 
                    v-model="newPseudo" 
                    placeholder="Entrez votre nouveau pseudo"
                    :disabled="updatingPseudo"
                    maxlength="100"
                  />
                  <button 
                    @click="updatePseudo" 
                    :disabled="!newPseudo || newPseudo === currentUser.pseudo || updatingPseudo"
                    class="btn-save"
                  >
                    <i class="bi" :class="updatingPseudo ? 'bi-arrow-repeat spin' : 'bi-check-circle'"></i>
                    {{ updatingPseudo ? 'Mise à jour...' : 'Mettre à jour' }}
                  </button>
                </div>
                <small class="form-hint">
                  Le pseudo sera utilisé pour vous identifier dans l'application (max 100 caractères)
                </small>
              </div>
            </div>
            
            <!-- Formulaire Email -->
            <div class="form-section">
              <h3><i class="bi bi-envelope"></i> Modifier mon email</h3>
              <div class="form-group">
                <label>Email actuel</label>
                <div class="current-value email-value">
                  {{ currentUser.email }}
                </div>
              </div>
              <div class="form-group">
                <label for="newEmail">Nouvel email</label>
                <div class="input-with-button">
                  <input 
                    type="email" 
                    id="newEmail" 
                    v-model="newEmail" 
                    placeholder="Entrez votre nouvel email"
                    :disabled="updatingEmail"
                  />
                  <button 
                    @click="updateEmail" 
                    :disabled="!isValidEmail || newEmail === currentUser.email || updatingEmail"
                    class="btn-save"
                  >
                    <i class="bi" :class="updatingEmail ? 'bi-arrow-repeat spin' : 'bi-check-circle'"></i>
                    {{ updatingEmail ? 'Mise à jour...' : 'Mettre à jour' }}
                  </button>
                </div>
                <small v-if="newEmail && !isValidEmail" class="form-error">
                  <i class="bi bi-exclamation-circle"></i> Adresse email invalide
                </small>
                <small v-else class="form-hint">
                  Vous recevrez un email de confirmation sur la nouvelle adresse
                </small>
              </div>
            </div>
            
            <!-- Informations non modifiables -->
            <div class="form-section readonly">
              <h3><i class="bi bi-shield-lock"></i> Informations SSO (non modifiables)</h3>
              <div class="readonly-grid">
                <div class="readonly-item">
                  <label>Matricule</label>
                  <div class="readonly-value">{{ currentUser.username }}</div>
                </div>
                <div class="readonly-item">
                  <label>Nom</label>
                  <div class="readonly-value">{{ currentUser.first_name || '-' }}</div>
                </div>
                <div class="readonly-item">
                  <label>Prénom</label>
                  <div class="readonly-value">{{ currentUser.last_name || '-' }}</div>
                </div>
                <div class="readonly-item">
                  <label>Dernière connexion</label>
                  <div class="readonly-value">
                    {{ currentUser.last_login ? formatDate(currentUser.last_login) : 'Jamais' }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'

// État pour la persistance
const ACTIVE_TAB_KEY = 'users_active_tab'
const USERS_PER_PAGE_KEY = 'users_items_per_page'

// Onglet actif (persistant)
const activeTab = ref<string>(localStorage.getItem(ACTIVE_TAB_KEY) || 'all')

// Stockage des données
const allUsers = ref<User[]>([])
const currentUser = ref<User | null>(null)
const loading = ref(false)
const loadingProfile = ref(false)
const error = ref<string | null>(null)
const profileError = ref<string | null>(null)

// Filtres et recherche
const searchQuery = ref('')
const roleFilter = ref('')
const statusFilter = ref('')

// Tri
const sortField = ref<string>('last_name')
const sortDirection = ref<'asc' | 'desc'>('asc')

// Pagination (persistante)
const currentPage = ref(1)
const itemsPerPage = ref(Number(localStorage.getItem(USERS_PER_PAGE_KEY)) || 10)

// Édition
const newPseudo = ref('')
const newEmail = ref('')
const updatingPseudo = ref(false)
const updatingEmail = ref(false)

// Auth
const { user: authUser, isAdmin } = useAuth()

// Computed properties
const filteredUsers = computed(() => {
  let users = [...allUsers.value]
  
  // Filtre par recherche
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
  
  // Filtre par statut
  if (statusFilter.value) {
    users = users.filter(user => {
        const isActive = user.is_active !== false // Si non défini, considérer comme actif
        if (statusFilter.value === 'active') return isActive
        if (statusFilter.value === 'inactive') return !isActive
        return true
    })
  }
  
  // Tri
  users.sort((a, b) => {
    let aValue = a[sortField.value as keyof User]
    let bValue = b[sortField.value as keyof User]
    
    // Gérer les valeurs null/undefined
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

const isValidEmail = computed(() => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(newEmail.value)
})

// Méthodes
const setActiveTab = (tab: string) => {
  activeTab.value = tab
  localStorage.setItem(ACTIVE_TAB_KEY, tab)
  currentPage.value = 1 // Réinitialiser la pagination
}

const fetchAllUsers = async () => {
  if (!isAdmin.value) return
  
  loading.value = true
  error.value = null
  
  try {
    const users = await usersApi.getAllUsers()
    allUsers.value = users
  } catch (err: any) {
    error.value = err.message || 'Erreur lors du chargement des utilisateurs'
    console.error('Erreur:', err)
  } finally {
    loading.value = false
  }
}

const loadUserProfile = async () => {
  loadingProfile.value = true
  profileError.value = null
  
  try {
    const userData = await usersApi.getUserProfile()
    currentUser.value = userData
    newPseudo.value = userData.pseudo || ''
    newEmail.value = userData.email || ''
  } catch (err: any) {
    profileError.value = err.message || 'Erreur lors du chargement du profil'
    console.error('Erreur:', err)
  } finally {
    loadingProfile.value = false
  }
}

const refreshUsers = () => {
  if (activeTab.value === 'all') {
    fetchAllUsers()
  } else {
    loadUserProfile()
  }
}

const handleSearch = () => {
  currentPage.value = 1 // Réinitialiser à la première page
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
  if (currentPage.value > 1) {
    currentPage.value--
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
  }
}

const changeItemsPerPage = () => {
  localStorage.setItem(USERS_PER_PAGE_KEY, itemsPerPage.value.toString())
  currentPage.value = 1
}

const updatePseudo = async () => {
  if (!newPseudo.value.trim() || !currentUser.value) return
  
  updatingPseudo.value = true
  
  try {
    const result = await usersApi.updatePseudo({ pseudo: newPseudo.value })
    
    // Mettre à jour l'utilisateur courant
    if (currentUser.value) {
      currentUser.value.pseudo = newPseudo.value
      currentUser.value.display_name = result.display_name
    }
    
    // Mettre à jour la liste des utilisateurs si admin
    if (isAdmin.value && authUser.value?.id === currentUser.value?.id) {
      const index = allUsers.value.findIndex(u => u.id === currentUser.value?.id)
      if (index !== -1) {
        allUsers.value[index].pseudo = newPseudo.value
      }
    }
    
    // Notification visuelle
    showNotification('Pseudo mis à jour avec succès!', 'success')
    
  } catch (err: any) {
    showNotification(err.message || 'Erreur lors de la mise à jour du pseudo', 'error')
    console.error('Erreur:', err)
  } finally {
    updatingPseudo.value = false
  }
}

const updateEmail = async () => {
  if (!isValidEmail.value || !currentUser.value) return
  
  updatingEmail.value = true
  
  try {
    // À implémenter : appel API pour mettre à jour l'email
    // await usersApi.updateEmail({ email: newEmail.value })
    
    // Simulation temporaire
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    if (currentUser.value) {
      currentUser.value.email = newEmail.value
    }
    
    showNotification('Email mis à jour avec succès!', 'success')
    
  } catch (err: any) {
    showNotification(err.message || 'Erreur lors de la mise à jour de l\'email', 'error')
    console.error('Erreur:', err)
  } finally {
    updatingEmail.value = false
  }
}

const viewProfile = (user: User) => {
  // Rediriger vers la page de profil de l'utilisateur
  console.log('Voir profil:', user.id)
  // router.push(`/profile/${user.id}`)
}

const editUser = (user: User) => {
  // Ouvrir modal d'édition
  console.log('Éditer utilisateur:', user.id)
}

const canEditUser = (user: User) => {
  if (!authUser.value) return false
  return isAdmin.value || authUser.value.id === user.id
}

const getUserRole = (user: User) => {
  if (user.is_superuser) return 'Super Admin'
  if (user.is_staff) return 'Admin'
  return 'Utilisateur'
}

const getRoleClass = (user: User) => {
  if (user.is_superuser) return 'super-admin'
  if (user.is_staff) return 'admin'
  return 'user'
}

const getUserInitials = (user: User) => {
  if (!user) return '?'
  if (user.pseudo) return user.pseudo.charAt(0).toUpperCase()
  if (user.first_name && user.last_name) {
    return (user.first_name.charAt(0) + user.last_name.charAt(0)).toUpperCase()
  }
  return user.username.charAt(0).toUpperCase()
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
  // À remplacer par un système de notification (toast)
  alert(message)
}

// Lifecycle hooks
onMounted(() => {
  // Charger les données en fonction de l'onglet actif
  if (activeTab.value === 'all' && isAdmin.value) {
    fetchAllUsers()
  } else {
    loadUserProfile()
  }
})

// Watchers
watch(activeTab, (newTab) => {
  if (newTab === 'all' && isAdmin.value) {
    fetchAllUsers()
  } else if (newTab === 'me') {
    loadUserProfile()
  }
})
</script>

<style scoped>
.users-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

/* En-tête */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin: 0;
}

.header-actions .btn-refresh {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: #6c757d;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #2c3e50;
}

/* Onglets */
.tabs-container {
  margin-bottom: 2rem;
  border-bottom: 2px solid #e9ecef;
}

.tabs {
  display: flex;
  gap: 0.5rem;
}

.tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: #6c757d;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.tab:hover {
  color: #2c3e50;
  background: #f8f9fa;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
  background: #e8f4fc;
}

.tab-badge {
  background: #3498db;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
  margin-left: 0.25rem;
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
}

.clear-search:hover {
  color: #2c3e50;
}

.filters {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
}

/* Tableau */
.table-container {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.loading, .error, .no-data {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.loading i, .error i, .no-data i {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
}

.btn-retry:hover {
  background: #2980b9;
}

.users-table {
  width: 100%;
  border-collapse: collapse;
}

.users-table thead {
  background: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
}

.users-table th {
  padding: 1rem;
  text-align: left;
  font-weight: 600;
  color: #495057;
  white-space: nowrap;
}

.sortable {
  cursor: pointer;
  user-select: none;
}

.sortable:hover {
  background: #e9ecef;
}

.sortable i {
  margin-left: 0.5rem;
}

.users-table td {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  vertical-align: middle;
}

.users-table tbody tr:hover {
  background: #f8fafc;
}

.matricule {
  font-family: monospace;
  font-weight: 600;
  color: #2c3e50;
}

.pseudo {
  background: #e8f4fc;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-weight: 500;
}

.no-pseudo {
  color: #95a5a6;
  font-style: italic;
}

.email-link {
  color: #3498db;
  text-decoration: none;
}

.email-link:hover {
  text-decoration: underline;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.role-badge.super-admin {
  background: #fce8e8;
  color: #e74c3c;
}

.role-badge.admin {
  background: #e8f4fc;
  color: #3498db;
}

.role-badge.user {
  background: #f0f9f0;
  color: #27ae60;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.status-badge.active {
  background: #f0f9f0;
  color: #27ae60;
}

.status-badge:not(.active) {
  background: #fce8e8;
  color: #e74c3c;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-action.view {
  background: #e8f4fc;
  color: #3498db;
}

.btn-action.view:hover {
  background: #3498db;
  color: white;
}

.btn-action.edit {
  background: #fff3e6;
  color: #f39c12;
}

.btn-action.edit:hover {
  background: #f39c12;
  color: white;
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
}

.page-btn {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #495057;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn:not(:disabled):hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.page-info {
  color: #6c757d;
  font-size: 0.9rem;
}

.page-select {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  color: #495057;
  cursor: pointer;
}

/* Profil */
.my-profile {
  max-width: 800px;
  margin: 0 auto;
}

.profile-card {
  background: white;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  padding: 2rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #f1f3f5;
}

.avatar-large {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: bold;
  color: white;
}

.profile-info h2 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.user-role, .join-date {
  margin: 0.25rem 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.user-role i, .join-date i {
  margin-right: 0.5rem;
}

/* Formulaires */
.profile-forms {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.form-section {
  background: #f8fafc;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
}

.form-section h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-section.readonly {
  background: #f1f3f5;
  border-color: #dee2e6;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.current-value {
  padding: 0.75rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  color: #495057;
}

.email-value {
  color: #3498db;
}

.input-with-button {
  display: flex;
  gap: 0.5rem;
}

.input-with-button input {
  flex: 1;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.input-with-button input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.input-with-button input:disabled {
  background: #f1f3f5;
}

.btn-save {
  padding: 0.75rem 1.5rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-save:hover:not(:disabled) {
  background: #219653;
}

.btn-save:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.form-hint {
  display: block;
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.8rem;
}

.form-error {
  display: block;
  margin-top: 0.5rem;
  color: #e74c3c;
  font-size: 0.8rem;
}

.form-error i {
  margin-right: 0.25rem;
}

/* Grille des informations non modifiables */
.readonly-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.readonly-item label {
  color: #6c757d;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.25rem;
}

.readonly-value {
  padding: 0.75rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  color: #495057;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .users-page {
    padding: 1rem;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }
  
  .search-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    min-width: auto;
  }
  
  .filters {
    width: 100%;
  }
  
  .filter-select {
    flex: 1;
  }
  
  .users-table {
    display: block;
    overflow-x: auto;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
  }
  
  .input-with-button {
    flex-direction: column;
  }
  
  .readonly-grid {
    grid-template-columns: 1fr;
  }
}
</style>