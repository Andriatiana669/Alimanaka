<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <!-- Logo visible uniquement si non collapsed -->
      <div class="sidebar-logos" v-if="!isCollapsed">
        <img src="@/assets/images/Logo_lalamby_1.svg" alt="Logo Lalamby" class="sidebar-logo left-logo" />
        <img src="@/assets/images/Logo_lalamby_2.svg" alt="Autre Logo" class="sidebar-logo right-logo" />
      </div>

      <!-- Bouton toggle -->
      <button class="menu-toggle" @click="toggleSidebar">
        <i class="bi bi-list"></i>
      </button>
    </div>

    <nav class="sidebar-nav">
      <!-- Dashboard -->
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-bar-chart-fill"></i></span>
        <span class="label">Dashboard</span>
      </router-link>

      <!-- Utilisateurs - condition d'affichage basée sur le rôle -->
      <router-link 
        v-if="canAccessUsers" 
        to="/users" 
        class="nav-item" 
        active-class="active"
      >
        <span class="icon"><i class="bi bi-person"></i></span>
        <span class="label">Utilisateurs</span>
      </router-link>

      <!-- Équipes -->
      <router-link to="/equipes" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-people"></i></span>
        <span class="label">Équipes</span>
      </router-link>

      <!-- Pôles -->
      <router-link to="/poles" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-house"></i></span>
        <span class="label">Pôles</span>
      </router-link>

      
      <!-- Congés -->
      <router-link to="/conges" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-calendar-event"></i></span>
        <span class="label">Congés</span>
      </router-link>

      <!-- Retards -->
      <router-link to="/retards" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-alarm"></i></span>
        <span class="label">Retards</span>
      </router-link>

      <!-- Permissions -->
      <router-link to="/permissions" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-unlock"></i></span>
        <span class="label">Permissions</span>
      </router-link>

      <!-- Repos Médicaux -->
      <router-link to="/repos-medicale" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-hospital"></i></span>
        <span class="label">Repos Médicaux</span>
      </router-link>

      <!-- OSTIE - condition d'affichage basée sur le rôle -->
      <router-link 
        v-if="canAccessOSTIE" 
        to="/ostie" 
        class="nav-item" 
        active-class="active"
      >
        <span class="icon"><i class="bi bi-bank"></i></span>
        <span class="label">OSTIE</span>
      </router-link>

      <!-- Calendrier -->
      <router-link to="/calendar" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-calendar-week"></i></span>
        <span class="label">Calendrier</span>
      </router-link>

      <!-- Événements -->
      <router-link to="/events" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-calendar-check"></i></span>
        <span class="label">Événements</span>
      </router-link>

      <!-- Mon profil -->
      <router-link to="/profile" class="nav-item" active-class="active">
        <span class="icon"><i class="bi bi-person-circle"></i></span>
        <span class="label">Mon profil</span>
      </router-link>
    </nav>

    <!-- Section Admin (uniquement visible pour les admins) -->
    <div v-if="showAdminSection" class="admin-section">
      <div class="section-title" v-if="!isCollapsed">
        <i class="bi bi-shield-lock"></i>
        <span class="label">Administration</span>
      </div>
      
      <!-- Bouton Admin Django Standard (Super Admin) -->
      <a 
        v-if="isSuperAdmin" 
        :href="backendAdminUrl" 
        target="_blank" 
        class="admin-btn django-admin-btn"
        :title="isCollapsed ? 'Admin Django (Super Admin)' : ''"
      >
        <span class="icon"><i class="bi bi-gear-wide-connected"></i></span>
        <span class="label" v-if="!isCollapsed">Admin Django</span>
        <span v-if="!isCollapsed" class="badge">Super</span>
      </a>
      
      <!-- Bouton Admin Alimanaka (Staff) -->
      <a 
        v-if="isStaff" 
        :href="alimanakaAdminUrl" 
        target="_blank" 
        class="admin-btn alimanaka-admin-btn"
        :title="isCollapsed ? 'Admin Alimanaka (Staff)' : ''"
      >
        <span class="icon"><i class="bi bi-palette"></i></span>
        <span class="label" v-if="!isCollapsed">Admin Alimanaka</span>
        <span v-if="!isCollapsed" class="badge">Staff</span>
      </a>
    </div>

    <!-- DEBUG TEMPORAIRE -->
    <div v-if="currentUser" class="debug-info">
      <p><strong>Debug:</strong> Super Admin: {{ currentUser.is_superuser }}, Staff: {{ currentUser.is_staff }}</p>
    </div>

    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-btn">
        <span class="icon"><i class="bi bi-box-arrow-right"></i></span>
        <span class="label">Déconnexion</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'  // Import de l'API users
import type { User } from '@/types/user'

const { logout } = useAuth()

// État pour l'utilisateur courant
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)
const isCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')

// Récupérer l'URL du backend depuis les variables d'environnement
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// URLs d'administration
const backendAdminUrl = `${backendUrl}/admin/`
const alimanakaAdminUrl = `${backendUrl}/alimanaka-admin/`

// Fonction pour récupérer l'utilisateur courant
const fetchCurrentUser = async () => {
  loadingUser.value = true
  try { 
    const userData = await usersApi.getCurrentUser()
    currentUser.value = userData
    console.log('Sidebar - User chargé:', {
      id: userData.id,
      username: userData.username,
      is_superuser: userData.is_superuser,
      is_staff: userData.is_staff,
      display_name: userData.display_name
    })
  } 
  catch (err: any) { 
    console.error('Erreur récupération user dans sidebar:', err)
    currentUser.value = null
  }
  finally { 
    loadingUser.value = false 
  }
}

// Computed properties pour les rôles
const isSuperAdmin = computed(() => {
  return currentUser.value?.is_superuser === true
})

const isStaff = computed(() => {
  return currentUser.value?.is_staff === true || isSuperAdmin.value
})

const showAdminSection = computed(() => {
  return isSuperAdmin.value || isStaff.value
})

// Conditions d'accès
const canAccessUsers = computed(() => {
  return isStaff.value || true // À adapter selon tes besoins
})

const canAccessOSTIE = computed(() => {
  return isStaff.value // Seulement pour les admins
})

// Méthodes
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const handleLogout = () => {
  logout()
}

// Watcher pour sauvegarder l'état
watch(isCollapsed, (newVal) => {
  localStorage.setItem('sidebar-collapsed', String(newVal))
})

// Charger l'utilisateur au montage
onMounted(() => {
  fetchCurrentUser()
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

.role-badge-header {
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-badge-header.role-super-admin {
  background: #f5e6ff;
  color: #9b59b6;
}

.role-badge-header.role-admin {
  background: #e8f4fc;
  color: #3498db;
}

.role-badge-header.role-user {
  background: #e9ecef;
  color: #6c757d;
}

.filters-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

/* Wrapper pour la barre de recherche */
.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 350px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding-left: 2.25rem !important;
  padding-right: 2.5rem !important;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.filter-group {
  padding: 0.5rem 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.filter-group:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
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
/* Barre toogle */
.toggle-inactives {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.toggle-inactives:hover {
  background: #e9ecef;
}

.toggle-inactives input {
  display: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: #495057;
}

.stats-bar {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.stat.active {
  color: #27ae60;
}

.stat.inactive {
  color: #e74c3c;
}


/* Indicateur de recherche */
.search-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #e8f4fc;
  border: 1px solid #3498db;
  border-radius: 6px;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.btn-clear-search {
  padding: 0.35rem 0.75rem;
  background: white;
  border: 1px solid #3498db;
  border-radius: 4px;
  color: #3498db;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-clear-search:hover {
  background: #3498db;
  color: white;
}

/* Vue en arbre */
.tree-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  min-height: 400px;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6c757d;
  text-align: center;
}

.loading i,
.empty i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

.empty .hint {
  font-size: 0.9rem;
  color: #adb5bd;
  margin-top: 0.5rem;
}

.spin {
  animation: spin 1s linear infinite;
}



@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    min-width: auto;
  }

  .filter-group {
    width: 100%;
  }
}
</style>