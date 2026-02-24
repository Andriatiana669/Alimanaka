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
          :disabled="!poleFilter"
        >
          <option value="">Toutes les équipes</option>
          <option 
            v-for="equipe in equipesFiltrees" 
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
            <!-- NOUVELLES COLONNES -->
            <th>Pôle</th>
            <th>Équipe</th>
            <th>Rôle</th>
            <th>Dernière connexion</th>
            <th>Actions</th>
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
            <!-- NOUVELLES CELLULES -->
            <td>
              <span v-if="user.pole_details" class="pole-badge">
                {{ user.pole_details.nom }}
              </span>
              <span v-else class="no-data">-</span>
            </td>
            <td>
              <span v-if="user.equipe_details" class="equipe-badge">
                {{ user.equipe_details.nom }}
              </span>
              <span v-else class="no-data">-</span>
            </td>
            <td>
              <span class="role-badge" :class="getRoleClass(user)">
                {{ getUserRole(user) }}
              </span>
            </td>
            <td>
              <span class="last-login">
                {{ user.last_login ? formatDate(user.last_login) : 'Jamais' }}
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
              <!-- Bouton éditer pour admin seulement -->
              <button 
                v-if="isAdmin" 
                @click="openEditModal(user)" 
                class="btn-action edit"
                title="Modifier pôle/équipe"
              >
                <i class="bi bi-building"></i>
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

    <!-- MODAL ÉDITION PÔLE/ÉQUIPE (Admin uniquement) -->
    <div v-if="showEditModal && editingUser" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal">
        <h3>Modifier l'organisation</h3>
        <p class="user-name">{{ editingUser.first_name }} {{ editingUser.last_name }}</p>
        
        <form @submit.prevent="saveUserOrg">
          <div class="form-group">
            <label>Pôle</label>
            <PoleSelect 
              v-model="editForm.pole_id"
              placeholder="Sélectionner un pôle"
            />
          </div>

          <div class="form-group">
            <label>Équipe</label>
            <EquipeSelect 
              v-model="editForm.equipe_id"
              :filtre-pole="editForm.pole_id"
              placeholder="Sélectionner une équipe"
            />
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeEditModal">Annuler</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
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
import PoleSelect from '@/components/common/PoleSelect.vue'
import EquipeSelect from '@/components/common/EquipeSelect.vue'
import type { User } from '@/types/user'

const router = useRouter()
const { isAdmin } = useAuth()
const polesStore = usePolesStore()
const equipesStore = useEquipesStore()
const { generatePseudo } = useDisplayName()

// État pour la persistance
const USERS_PER_PAGE_KEY = 'users_items_per_page'

// Stockage des données
const allUsers = ref<User[]>([])
const loading = ref(false)
const error = ref<string | null>(null)

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

// Modal édition
const showEditModal = ref(false)
const editingUser = ref<User | null>(null)
const saving = ref(false)
const editForm = ref({
  pole_id: null as number | null,
  equipe_id: null as number | null
})

// Réinitialiser le filtre équipe quand le pôle change
watch(poleFilter, () => {
  equipeFilter.value = ''
  currentPage.value = 1
})

// Filtrer les équipes selon le pôle sélectionné dans le modal
const equipesFiltrees = computed(() => {
  if (!editForm.value.pole_id) return equipesStore.equipesActives
  return equipesStore.equipesActives.filter(e => e.pole === editForm.value.pole_id)
})

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

  // Filtre par pôle (uniquement si une valeur est sélectionnée)
  if (poleFilter.value !== '' && poleFilter.value !== null) {
    users = users.filter(user => user.pole === Number(poleFilter.value))
  }

  // Filtre par équipe (uniquement si une valeur est sélectionnée)
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
    // Charger les données en parallèle
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

const viewProfile = (user: User) => {
  router.push(`/profile/${user.id}`)
}

// MODAL ÉDITION
const openEditModal = (user: User) => {
  editingUser.value = user
  editForm.value = {
    pole_id: user.pole,
    equipe_id: user.equipe
  }
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingUser.value = null
}

const saveUserOrg = async () => {
  if (!editingUser.value) return
  
  saving.value = true
  try {
    await usersApi.updatePoleEquipe({
      user_id: editingUser.value.id,
      pole_id: editForm.value.pole_id || 0,
      equipe_id: editForm.value.equipe_id || 0
    })
    
    // Rafraîchir la liste
    await fetchAllUsers()
    closeEditModal()
  } catch (err: any) {
    alert('Erreur: ' + err.message)
  } finally {
    saving.value = false
  }
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

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

onMounted(() => {
  fetchAllUsers()
})
</script>

<style scoped>
.users-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 1.8rem;
  margin: 0;
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
}

.filter-select:focus {
  outline: none;
  border-color: #3498db;
}

.header-actions .btn-refresh {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.5rem 1rem;
  cursor: pointer;
  color: #6c757d;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #2c3e50;
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

.users-table {
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
}

.sortable:hover {
  background: #e9ecef;
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
  font-size: 0.85rem;
}

/* NOUVEAUX BADGES */
.pole-badge {
  background: #f0f0f0;
  color: #495057;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: 500;
}

.equipe-badge {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.email-link {
  color: #3498db;
  text-decoration: none;
}

.role-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
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

.last-login {
  font-size: 0.85rem;
  color: #6c757d;
  white-space: nowrap;
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
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 400px;
}

.modal h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.user-name {
  color: #6c757d;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

/* Responsive */
@media (max-width: 768px) {
  .users-page {
    padding: 1rem;
  }
  
  .search-bar {
    flex-direction: column;
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
    font-size: 0.8rem;
  }
}
</style>