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
        class="admin-btn"
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
        class="admin-btn"
        :title="isCollapsed ? 'Admin Alimanaka (Staff)' : ''"
      >
        <span class="icon"><i class="bi bi-palette"></i></span>
        <span class="label" v-if="!isCollapsed">Admin Alimanaka</span>
        <span v-if="!isCollapsed" class="badge">Staff</span>
      </a>
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
.sidebar {
  width: 250px;
  height: 100vh;
  background-color: #1A2F59;
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
  transition: width 0.3s ease;
  z-index: 40;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  height: 100px;
  padding: 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.sidebar-logos {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.sidebar-logo {
  max-width: 100px;
  height: auto;
  transition: opacity 0.3s ease;
}

.sidebar.collapsed .sidebar-logo {
  opacity: 0;
}

.left-logo {
  max-width: 60px;
}

.right-logo {
  max-width: 120px;
  margin-right: 10px;
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 1);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
  color: white;
}

.nav-item.active {
  background-color: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border-left-color: #3498db;
}

.icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
}

.label {
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 0.4s ease, width 0.4s ease, margin 0.4s ease;
}

.sidebar.collapsed .label {
  opacity: 0;
  width: 0;
  margin: 0;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.logout-btn, .admin-btn {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  margin-bottom: 0.5rem;
}

.logout-btn {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
}

.logout-btn:hover {
  background-color: #e74c3c;
  color: white;
}

.admin-btn {
  background-color: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border-color: rgba(52, 152, 219, 0.3);
}

.admin-btn:hover {
  background-color: #3498db;
  color: white;
}

.admin-btn.django-admin-btn {
  background-color: rgba(231, 76, 60, 0.2);
  color: #e74c3c;
  border-color: rgba(231, 76, 60, 0.3);
}

.admin-btn.django-admin-btn:hover {
  background-color: #e74c3c;
  color: white;
}

.admin-btn.alimanaka-admin-btn {
  background-color: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border-color: rgba(52, 152, 219, 0.3);
}

.admin-btn.alimanaka-admin-btn:hover {
  background-color: #3498db;
  color: white;
}

.menu-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
}

.sidebar.collapsed .menu-toggle {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.admin-section {
  margin: 20px 0;
  padding: 0 15px;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 15px;
  padding-bottom: 15px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  color: #bdc3c7;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section-title .bi {
  font-size: 1rem;
}

.admin-btn .badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.sidebar.collapsed .admin-section {
  padding: 0 10px;
}

.sidebar.collapsed .admin-btn {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .admin-btn .label,
.sidebar.collapsed .admin-btn .badge {
  display: none;
}

.sidebar-footer {
  margin-top: auto;
}

@media (max-height: 700px) {
  .admin-section {
    margin: 10px 0;
    padding-top: 10px;
    padding-bottom: 10px;
  }
}


</style>