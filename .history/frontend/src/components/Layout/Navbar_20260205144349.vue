<!-- frontend/src/components/Layout/Navbar.vue -->
<template>
  <header class="navbar">
    <div class="navbar-left">
      <button class="menu-toggle" @click="toggleSidebar">
        ☰
      </button>
      <span class="breadcrumb">Lalamby : Alimanaka</span>
    </div>

    <div class="navbar-right">
      <div class="search-box">
        <input 
          type="text" 
          placeholder="Rechercher..." 
          v-model="searchQuery"
          @keyup.enter="performSearch"
        />
        <span class="search-icon">🔍</span>
      </div>

      <div class="notifications">
        <button class="icon-btn" @click="toggleNotifications">
          <span v-if="unreadNotifications > 0" class="badge">{{ unreadNotifications }}</span>
          <span>🔔</span>
        </button>
      </div>

      <div class="user-menu" @click="toggleUserDropdown">
        <div class="user-info">
          <span class="user-name">{{ userDisplayName.toUpperCase() }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
        <div class="avatar">
          {{ userInitials }}
        </div>
        
        <!-- Dropdown menu -->
        <div v-if="showUserDropdown" class="user-dropdown" @click.stop>
          <div class="dropdown-item" @click="goToProfile">
            <span class="dropdown-icon">👤</span>
            <span>Mon Profil</span>
          </div>
          <div class="dropdown-item" @click="goToSettings">
            <span class="dropdown-icon">⚙️</span>
            <span>Paramètres</span>
          </div>
          <div class="dropdown-divider"></div>
          <div class="dropdown-item logout" @click="logout">
            <span class="dropdown-icon">🚪</span>
            <span>Déconnexion</span>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, isAdmin, logout: authLogout } = useAuth()

// État local
const searchQuery = ref('')
const showUserDropdown = ref(false)
const unreadNotifications = ref(3) // Valeur temporaire
const sidebarCollapsed = ref(false)

// Computed properties
const userDisplayName = computed(() => {
  if (!user.value) return 'Utilisateur'
  return user.value.display_name || user.value.get_full_name || `${user.value.last_name} ${user.value.first_name}`
})

const userInitials = computed(() => {
  if (!user.value) return '?'
  
  if (user.value.pseudo) {
    return user.value.pseudo.charAt(0).toUpperCase()
  }
  
  const first = user.value.first_name?.[0] || ''
  const last = user.value.last_name?.[0] || ''
  return (first + last).toUpperCase() || user.value.username?.[0]?.toUpperCase() || '?'
})

const userRole = computed(() => {
  if (!user.value) return 'Invité'
  if (user.value.is_superuser) return 'Super Admin'
  if (user.value.is_staff) return 'Administrateur'
  return 'Employé'
})

// Méthodes
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  // Émettre un événement pour le parent
  const event = new CustomEvent('toggle-sidebar', { 
    detail: { collapsed: sidebarCollapsed.value } 
  })
  window.dispatchEvent(event)
}

const toggleUserDropdown = () => {
  showUserDropdown.value = !showUserDropdown.value
}

const toggleNotifications = () => {
  // TODO: Implémenter la logique des notifications
  console.log('Afficher les notifications')
}

const performSearch = () => {
  if (searchQuery.value.trim()) {
    console.log('Recherche:', searchQuery.value)
    // TODO: Implémenter la recherche
    searchQuery.value = ''
  }
}

const goToProfile = () => {
  showUserDropdown.value = false
  router.push('/profile')
}

const goToSettings = () => {
  showUserDropdown.value = false
  router.push('/settings') // Tu devras créer cette route si nécessaire
}

const logout = async () => {
  showUserDropdown.value = false
  await authLogout()
}

// Fermer le dropdown en cliquant à l'extérieur
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showUserDropdown.value = false
  }
}

// Gestionnaires d'événements
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  height: 70px;
  background-color: white;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #2c3e50;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: none; /* Caché par défaut, visible sur mobile */
}

.menu-toggle:hover {
  background-color: #f8f9fa;
}

.breadcrumb {
  color: #2c3e50;
  font-weight: 600;
  font-size: 1.1rem;
  letter-spacing: 0.5px;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.search-box {
  position: relative;
}

.search-box input {
  padding: 0.5rem 2.5rem 0.5rem 1rem;
  border: 1px solid #e1e8ed;
  border-radius: 20px;
  width: 250px;
  outline: none;
  transition: all 0.3s;
  font-size: 0.9rem;
  background-color: #f8f9fa;
}

.search-box input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
  background-color: white;
}

.search-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #95a5a6;
  font-size: 0.9rem;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  color: #7f8c8d;
  transition: all 0.3s;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.icon-btn:hover {
  color: #2c3e50;
  background-color: #f8f9fa;
}

.badge {
  position: absolute;
  top: 2px;
  right: 2px;
  background-color: #e74c3c;
  color: white;
  font-size: 0.65rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-menu:hover {
  background-color: #f8f9fa;
}

.user-info {
  text-align: right;
  display: flex;
  flex-direction: column;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.9rem;
  letter-spacing: 0.5px;
}

.user-role {
  font-size: 0.75rem;
  color: #7f8c8d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.avatar {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
  flex-shrink: 0;
}

/* Dropdown menu */
.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1000;
  margin-top: 0.5rem;
  border: 1px solid #e1e8ed;
  overflow: hidden;
}

.dropdown-item {
  padding: 0.75rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: background-color 0.2s;
  color: #2c3e50;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-icon {
  font-size: 1rem;
  width: 20px;
  text-align: center;
}

.dropdown-divider {
  height: 1px;
  background-color: #e1e8ed;
  margin: 0.25rem 0;
}

.dropdown-item.logout {
  color: #e74c3c;
}

.dropdown-item.logout:hover {
  background-color: #fdeaea;
}

/* Responsive */
@media (max-width: 1024px) {
  .search-box input {
    width: 200px;
  }
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
    height: 60px;
  }
  
  .menu-toggle {
    display: block;
  }
  
  .search-box {
    display: none;
  }
  
  .user-info {
    display: none;
  }
  
  .notifications {
    margin-left: auto;
  }
  
  .user-menu {
    padding: 0;
  }
}

@media (max-width: 480px) {
  .breadcrumb {
    font-size: 0.9rem;
  }
  
  .icon-btn {
    width: 36px;
    height: 36px;
  }
  
  .avatar {
    width: 36px;
    height: 36px;
    font-size: 0.9rem;
  }
}
</style>