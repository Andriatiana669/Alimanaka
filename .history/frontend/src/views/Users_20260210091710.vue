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

</style>