<!-- frontend/src/components/Layout/Sidebar.vue -->
<template>
  <aside class="sidebar" :class="{ collapsed: isCollapsed }">
    <div class="sidebar-header">
      <!-- Logo visible uniquement si non collapsed -->
      <div class="sidebar-logos" v-if="!isCollapsed">
        <img src="/logo_gauche.svg" alt="Logo Lalamby" class="sidebar-logo left-logo" />
        <img src="/logo_droite.svg" alt="Autre Logo" class="sidebar-logo right-logo" />
      </div>
      
      <!-- Icône seule quand collapsed -->
      <div v-else class="logo-collapsed">
        <img src="/logo_gauche.svg" alt="Logo" class="collapsed-logo" />
      </div>

      <!-- Bouton toggle -->
      <button class="menu-toggle" @click="toggleSidebar">
        {{ isCollapsed ? '☰' : '✕' }}
      </button>
    </div>

    <nav class="sidebar-nav">
      <router-link to="/dashboard" class="nav-item" active-class="active">
        <span class="icon">📊</span>
        <span class="label">Dashboard</span>
      </router-link>

      <router-link to="/users" class="nav-item" active-class="active">
        <span class="icon">👥</span>
        <span class="label">Utilisateurs</span>
      </router-link>

      <router-link to="/profile" class="nav-item" active-class="active">
        <span class="icon">👤</span>
        <span class="label">Mon Profil</span>
      </router-link>

      <!-- Routes futures - À décommenter quand tu les créeras -->
      <!--
      <router-link to="/equipes" class="nav-item" active-class="active">
        <span class="icon">👥</span>
        <span class="label">Équipes</span>
      </router-link>
      
      <router-link to="/conges" class="nav-item" active-class="active">
        <span class="icon">📅</span>
        <span class="label">Congés</span>
      </router-link>

      <router-link to="/retards" class="nav-item" active-class="active">
        <span class="icon">⏰</span>
        <span class="label">Retards</span>
      </router-link>

      <router-link to="/permissions" class="nav-item" active-class="active">
        <span class="icon">🔓</span>
        <span class="label">Permissions</span>
      </router-link>

      <router-link to="/repos-medicaux" class="nav-item" active-class="active">
        <span class="icon">🏥</span>
        <span class="label">Repos Médicaux</span>
      </router-link>

      <router-link to="/ostie" class="nav-item" active-class="active">
        <span class="icon">🏦</span>
        <span class="label">OSTIE</span>
      </router-link>
      -->
    </nav>

    <div class="sidebar-footer">
      <!-- Info utilisateur -->
      <div v-if="!isCollapsed && user" class="user-info">
        <div class="user-avatar">{{ userInitials }}</div>
        <div class="user-details">
          <p class="user-name">{{ userDisplayName }}</p>
          <p class="user-role">{{ userRole }}</p>
        </div>
      </div>
      
      <!-- Bouton déconnexion -->
      <button @click="handleLogout" class="logout-btn">
        <span class="icon">🚪</span>
        <span v-if="!isCollapsed" class="label">Déconnexion</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { user, logout } = useAuth()

const isCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')

// Computed properties
const userInitials = computed(() => {
  if (!user.value) return '?'
  if (user.value.pseudo) {
    return user.value.pseudo.charAt(0).toUpperCase()
  }
  const first = user.value.first_name?.[0] || ''
  const last = user.value.last_name?.[0] || ''
  return (first + last).toUpperCase() || user.value.username?.[0]?.toUpperCase() || '?'
})

const userDisplayName = computed(() => {
  if (!user.value) return 'Utilisateur'
  return user.value.pseudo || user.value.display_name || `${user.value.last_name} ${user.value.first_name}`
})

const userRole = computed(() => {
  if (!user.value) return 'Invité'
  if (user.value.is_superuser) return 'Super Admin'
  if (user.value.is_staff) return 'Administrateur'
  return 'Employé'
})

// Méthodes
const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
  // Émettre un événement pour synchroniser avec Navbar
  const event = new CustomEvent('sidebar-toggle', { 
    detail: { collapsed: isCollapsed.value } 
  })
  window.dispatchEvent(event)
}

const handleLogout = async () => {
  await logout()
}

// Sauvegarder l'état dans localStorage
watch(isCollapsed, (newVal) => {
  localStorage.setItem('sidebar-collapsed', String(newVal))
})

// Écouter les événements du Navbar
onMounted(() => {
  window.addEventListener('toggle-sidebar', (event: any) => {
    isCollapsed.value = event.detail.collapsed
  })
})
</script>

<style scoped>
.sidebar {
  width: 250px;
  height: 100vh;
  background: linear-gradient(180deg, #1A2F59 0%, #0d1a3d 100%);
  color: white;
  position: fixed;
  left: 0;
  top: 0;
  display: flex;
  flex-direction: column;
  box-shadow: 3px 0 15px rgba(0, 0, 0, 0.2);
  transition: width 0.3s ease;
  z-index: 1000;
}

.sidebar.collapsed {
  width: 80px;
}

.sidebar-header {
  height: 70px; /* Même hauteur que la navbar */
  padding: 0 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: relative;
}

.sidebar-logos {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 0.5rem;
}

.sidebar-logo {
  max-height: 40px;
  width: auto;
  transition: opacity 0.3s ease;
}

.left-logo {
  max-width: 60px;
}

.right-logo {
  max-width: 120px;
}

.sidebar.collapsed .sidebar-logos {
  display: none;
}

.logo-collapsed {
  width: 100%;
  display: flex;
  justify-content: center;
}

.collapsed-logo {
  max-height: 40px;
  width: auto;
}

.menu-toggle {
  position: absolute;
  right: -12px;
  top: 50%;
  transform: translateY(-50%);
  background: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-size: 0.9rem;
  color: #1A2F59;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1001;
}

.menu-toggle:hover {
  background: #f8f9fa;
  transform: translateY(-50%) scale(1.1);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.sidebar-nav::-webkit-scrollbar {
  width: 4px;
}

.sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.sidebar-nav::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  transition: all 0.3s ease;
  border-left: 3px solid transparent;
  margin: 0.25rem 0.5rem;
  border-radius: 6px;
}

.nav-item:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: white;
}

.nav-item.active {
  background-color: rgba(52, 152, 219, 0.2);
  color: #3498db;
  border-left-color: #3498db;
  box-shadow: inset 3px 0 10px rgba(52, 152, 219, 0.1);
}

.icon {
  font-size: 1.25rem;
  width: 24px;
  text-align: center;
  flex-shrink: 0;
}

.label {
  white-space: nowrap;
  overflow: hidden;
  font-weight: 500;
  transition: all 0.3s ease;
}

.sidebar.collapsed .label {
  opacity: 0;
  width: 0;
  margin-left: 0;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.05);
}

.user-avatar {
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

.user-details {
  overflow: hidden;
}

.user-name {
  margin: 0;
  font-weight: 600;
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-role {
  margin: 0;
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
}

.sidebar.collapsed .user-info {
  display: none;
}

.logout-btn {
  width: 100%;
  padding: 0.75rem;
  background-color: rgba(231, 76, 60, 0.15);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.3);
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  font-weight: 500;
}

.logout-btn:hover {
  background-color: #e74c3c;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.sidebar.collapsed .logout-btn {
  justify-content: center;
  padding: 0.75rem;
}

.sidebar.collapsed .logout-btn .label {
  display: none;
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
    width: 250px;
  }
  
  .sidebar:not(.collapsed) {
    transform: translateX(0);
  }
  
  .sidebar.collapsed {
    transform: translateX(-100%);
    width: 250px;
  }
  
  .menu-toggle {
    display: none;
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 100%;
  }
}
</style>