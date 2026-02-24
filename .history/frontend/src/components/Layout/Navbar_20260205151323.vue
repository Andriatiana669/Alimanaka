<!-- frontend/src/components/Layout/Navbar.vue -->
<template>
  <nav class="navbar">
    <div class="navbar-left">
      <!-- Bouton toggle sidebar -->
      <button class="menu-toggle" @click="toggleSidebar" aria-label="Toggle sidebar">
        <span class="menu-icon">{{ sidebarCollapsed ? '☰' : '✕' }}</span>
      </button>
      
      <!-- Logo et titre -->
      <div class="navbar-brand">
        <img :src="logoGauche" alt="Logo Alimanaka" class="logo" />
        <h1 class="app-title">Alimanaka</h1>
      </div>
    </div>
    
    <div class="navbar-center">
      <!-- Titre de la page actuelle -->
      <div class="page-title">
        {{ currentPageTitle }}
      </div>
    </div>
    
    <div class="navbar-right">
      <!-- Bouton notifications -->
      <button class="notification-btn" @click="toggleNotifications" aria-label="Notifications">
        <span class="notification-icon">🔔</span>
        <span v-if="unreadCount > 0" class="notification-badge">{{ unreadCount }}</span>
      </button>
      
      <!-- Menu utilisateur -->
      <div class="user-menu" ref="userMenuRef">
        <button class="user-menu-btn" @click="toggleUserMenu">
          <div class="user-avatar-small">
            {{ getUserInitials() }}
          </div>
          <span class="user-name">{{ user?.display_name }}</span>
          <span class="dropdown-icon">{{ userMenuOpen ? '▲' : '▼' }}</span>
        </button>
        
        <!-- Dropdown utilisateur -->
        <div v-if="userMenuOpen" class="user-dropdown">
          <router-link to="/profile" class="dropdown-item" @click="closeUserMenu">
            <span class="dropdown-icon">👤</span>
            <span>Mon profil</span>
          </router-link>
          <div class="dropdown-divider"></div>
          <button @click="handleLogout" class="dropdown-item logout">
            <span class="dropdown-icon">🚪</span>
            <span>Déconnexion</span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Dropdown notifications -->
    <div v-if="notificationsOpen" class="notifications-dropdown" ref="notificationsRef">
      <div class="notifications-header">
        <h3>Notifications</h3>
        <button @click="markAllAsRead" class="mark-read-btn">Tout marquer comme lu</button>
      </div>
      <div class="notifications-list">
        <div v-for="notification in notifications" :key="notification.id" 
             class="notification-item" :class="{ unread: !notification.read }">
          <div class="notification-content">
            <p>{{ notification.message }}</p>
            <span class="notification-time">{{ notification.time }}</span>
          </div>
        </div>
        <div v-if="notifications.length === 0" class="empty-notifications">
          Aucune notification
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import logoGauche from '@/../public/logo_gauche.svg'

const { user, logout } = useAuth()
const route = useRoute()
const router = useRouter()

// États réactifs
const sidebarCollapsed = ref(false)
const userMenuOpen = ref(false)
const notificationsOpen = ref(false)
const unreadCount = ref(3)
const userMenuRef = ref<HTMLElement>()
const notificationsRef = ref<HTMLElement>()

// Notifications simulées
const notifications = ref([
  { id: 1, message: 'Bienvenue dans Alimanaka !', time: 'Il y a 2 heures', read: false },
  { id: 2, message: 'Votre demande de congé a été approuvée', time: 'Hier', read: true },
  { id: 3, message: 'Nouvel événement ajouté au calendrier', time: 'Il y a 3 jours', read: true },
])

// Titres des pages
const pageTitles: Record<string, string> = {
  Dashboard: 'Tableau de bord',
  Users: 'Utilisateurs',
  Profile: 'Mon profil',
  Equipes: 'Équipes',
  Permissions: 'Permissions',
  Conges: 'Congés',
  ReposMedicale: 'Repos médical',
  Retards: 'Retards',
  Calendar: 'Calendrier',
  Events: 'Événements',
  Ostie: 'OSTIE'
}

const currentPageTitle = computed(() => {
  return pageTitles[route.name as string] || 'Alimanaka'
})

// Méthodes
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
  // Émettre un événement personnalisé pour informer le parent
  const event = new CustomEvent('toggle-sidebar', { 
    detail: { collapsed: sidebarCollapsed.value }
  })
  window.dispatchEvent(event)
}

const toggleUserMenu = () => {
  userMenuOpen.value = !userMenuOpen.value
  if (userMenuOpen.value) {
    notificationsOpen.value = false
  }
}

const toggleNotifications = () => {
  notificationsOpen.value = !notificationsOpen.value
  if (notificationsOpen.value) {
    userMenuOpen.value = false
  }
}

const closeUserMenu = () => {
  userMenuOpen.value = false
}

const handleLogout = async () => {
  userMenuOpen.value = false
  await logout()
}

const markAllAsRead = () => {
  notifications.value = notifications.value.map(n => ({ ...n, read: true }))
  unreadCount.value = 0
}

const getUserInitials = (): string => {
  if (!user.value) return '?'
  if (user.value.pseudo) return user.value.pseudo.charAt(0).toUpperCase()
  if (user.value.first_name && user.value.last_name) {
    return (user.value.first_name.charAt(0) + user.value.last_name.charAt(0)).toUpperCase()
  }
  return user.value.username.charAt(0).toUpperCase()
}

// Gestion des clics en dehors des dropdowns
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  
  if (userMenuRef.value && !userMenuRef.value.contains(target)) {
    userMenuOpen.value = false
  }
  
  if (notificationsRef.value && !notificationsRef.value.contains(target)) {
    notificationsOpen.value = false
  }
}

// Mettre à jour le compteur de notifications non lues
const updateUnreadCount = () => {
  unreadCount.value = notifications.value.filter(n => !n.read).length
}

// Lifecycle hooks
onMounted(() => {
  window.addEventListener('click', handleClickOutside)
  updateUnreadCount()
})

onUnmounted(() => {
  window.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.navbar-left,
.navbar-center,
.navbar-right {
  display: flex;
  align-items: center;
  gap: 1rem;
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
}

.menu-toggle:hover {
  background-color: #f8f9fa;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo {
  height: 32px;
  width: auto;
}

.app-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
  margin: 0;
}

.page-title {
  font-size: 1.1rem;
  font-weight: 500;
  color: #34495e;
}

/* Bouton notifications */
.notification-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #7f8c8d;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.notification-btn:hover {
  background-color: #f8f9fa;
}

.notification-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #e74c3c;
  color: white;
  font-size: 0.7rem;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 0.25rem;
}

/* Menu utilisateur */
.user-menu {
  position: relative;
}

.user-menu-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background: none;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu-btn:hover {
  background: #f8f9fa;
  border-color: #dee2e6;
}

.user-avatar-small {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 0.9rem;
  color: white;
}

.user-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 0.7rem;
  color: #7f8c8d;
  transition: transform 0.2s;
}

/* Dropdown utilisateur */
.user-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  min-width: 200px;
  z-index: 1001;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  text-decoration: none;
  color: #2c3e50;
  cursor: pointer;
  transition: background 0.2s;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  font-size: 0.9rem;
}

.dropdown-item:hover {
  background: #f8f9fa;
}

.dropdown-item.logout {
  color: #e74c3c;
}

.dropdown-divider {
  height: 1px;
  background: #e9ecef;
  margin: 0.25rem 0;
}

/* Dropdown notifications */
.notifications-dropdown {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 1rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 350px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1001;
  animation: fadeIn 0.2s ease;
}

.notifications-header {
  padding: 1rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.notifications-header h3 {
  margin: 0;
  font-size: 1rem;
  color: #2c3e50;
}

.mark-read-btn {
  background: none;
  border: none;
  color: #3498db;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0;
  transition: color 0.2s;
}

.mark-read-btn:hover {
  color: #2980b9;
}

.notifications-list {
  padding: 0.5rem;
}

.notification-item {
  padding: 0.75rem;
  border-radius: 6px;
  transition: background 0.2s;
  cursor: pointer;
  margin-bottom: 0.25rem;
}

.notification-item:hover {
  background: #f8f9fa;
}

.notification-item.unread {
  background: #f0f7ff;
  border-left: 3px solid #3498db;
}

.notification-content p {
  margin: 0 0 0.25rem 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.notification-time {
  font-size: 0.75rem;
  color: #7f8c8d;
}

.empty-notifications {
  text-align: center;
  padding: 2rem;
  color: #95a5a6;
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .navbar {
    padding: 0 1rem;
  }
  
  .app-title {
    display: none;
  }
  
  .page-title {
    font-size: 0.9rem;
  }
  
  .user-name {
    display: none;
  }
  
  .notifications-dropdown {
    width: 300px;
    right: 0.5rem;
  }
}

@media (max-width: 480px) {
  .navbar-center {
    display: none;
  }
}
</style>