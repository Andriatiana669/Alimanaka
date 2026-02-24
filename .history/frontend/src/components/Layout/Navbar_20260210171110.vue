<template>
  <header class="navbar">
    <div class="navbar-left">
      <span class="breadcrumb">Lalamby : Alimanaka</span>
    </div>

    <div class="navbar-right">
      <div class="search-box">
        <input type="text" placeholder="Rechercher..." />
        <span class="search-icon">🔍</span>
      </div>

      <div class="notifications">
        <button class="icon-btn">
          <span class="badge">3</span>
          <span>🔔</span>
        </button>
      </div>

      <div class="user-menu" @click="toggleDropdown">
        <div class="user-info">
          <span class="user-name">{{ userFullName.toUpperCase() }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
        <div class="avatar-container">
          <div class="avatar">
            {{ userInitials }}
          </div>
          <i class="bi bi-chevron-down dropdown-arrow" :class="{ 'rotated': showDropdown }"></i>
        </div>
        
        <!-- Dropdown Menu -->
        <div v-if="showDropdown" class="dropdown-menu" @click.stop>
          <!-- Mon profil -->
          <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
            <i class="bi bi-person-circle"></i>
            <span>Mon profil</span>
          </router-link>
          
          <!-- Admin Django (Super Admin seulement) -->
          <a 
            v-if="isSuperAdmin" 
            :href="backendAdminUrl" 
            target="_blank" 
            class="dropdown-item admin-item super-admin"
            @click="closeDropdown"
          >
            <i class="bi bi-gear-wide-connected"></i>
            <span>Admin Django</span>
            <span class="admin-badge super">Super</span>
          </a>
          
          <!-- Admin Alimanaka (Staff et Super Admin) -->
          <a 
            v-if="isStaff" 
            :href="alimanakaAdminUrl" 
            target="_blank" 
            class="dropdown-item admin-item staff-admin"
            @click="closeDropdown"
          >
            <i class="bi bi-palette"></i>
            <span>Admin Alimanaka</span>
            <span class="admin-badge staff">Staff</span>
          </a>
          
          <!-- Déconnexion -->
          <button class="dropdown-item logout-item" @click="handleLogout">
            <i class="bi bi-box-arrow-right"></i>
            <span>Déconnexion</span>
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'

const authStore = useAuthStore()
const { user: authUser, logout } = useAuthStore()
const { user } = storeToRefs(authStore)

// État pour le dropdown
const showDropdown = ref(false)
const currentUser = ref<User | null>(null)

// URLs d'administration
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const backendAdminUrl = `${backendUrl}/admin/`
const alimanakaAdminUrl = `${backendUrl}/alimanaka-admin/`

// Récupérer l'utilisateur complet
const fetchCurrentUser = async () => {
  try { 
    const userData = await usersApi.getCurrentUser()
    currentUser.value = userData
  } 
  catch (err: any) { 
    console.error('Erreur récupération user:', err)
    currentUser.value = authUser
  }
}

// Computed properties
const userFullName = computed(() => {
  if (!user.value) return 'Utilisateur'
  
  if (user.value.pseudo) {
    return user.value.pseudo
  }
  
  const fullName = `${user.value.first_name || ''} ${user.value.last_name || ''} (${user.value.username || ''}) ` .trim()
  return fullName || user.value.username || 'Utilisateur'
})

const userRole = computed(() => {
  if (!user.value) return 'Non connecté'
  
  if (user.value.is_superuser) return 'Super Administrateur'
  if (user.value.is_staff) return 'Administrateur'
  return 'Employé'
})

const userInitials = computed(() => {
  if (!user.value) return '?'
  
  if (user.value.pseudo && user.value.pseudo.length > 0) {
    return user.value.pseudo.charAt(0).toUpperCase()
  }
  
  const firstName = user.value.first_name || ''
  const lastName = user.value.last_name || ''
  
  if (firstName && lastName) {
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase()
  }
  
  if (user.value.username) {
    return user.value.username.charAt(0).toUpperCase()
  }
  
  return 'U'
})

const isSuperAdmin = computed(() => {
  return currentUser.value?.is_superuser === true
})

const isStaff = computed(() => {
  return currentUser.value?.is_staff === true || isSuperAdmin.value
})

// Méthodes
const toggleDropdown = (event: MouseEvent) => {
  event.stopPropagation()
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const handleLogout = () => {
  closeDropdown()
  logout()
}

// Fermer le dropdown si on clique en dehors
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.user-menu')) {
    showDropdown.value = false
  }
}

// Charger l'utilisateur au montage
onMounted(() => {
  fetchCurrentUser()
  document.addEventListener('click', handleClickOutside)
})

// Nettoyer l'event listener
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.navbar {
  height: 100px;
  background-color: white;
  border-bottom: 1px solid #e1e8ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 2rem;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.menu-toggle {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  color: #7f8c8d;
  display: none;
}

.breadcrumb {
  color: #2c3e50;
  font-weight: 500;
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
}

.search-box input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.search-icon {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #95a5a6;
}

.icon-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  color: #7f8c8d;
  transition: color 0.3s;
}

.icon-btn:hover {
  color: #2c3e50;
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #e74c3c;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 600;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  position: relative;
  cursor: pointer;
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
}

.user-role {
  font-size: 0.75rem;
  color: #7f8c8d;
}

.avatar-container {
  display: flex;
  align-items: center;
  gap: 8px;
}

.avatar {
  width: 40px;
  height: 40px;
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1rem;
}

.dropdown-arrow {
  font-size: 0.9rem;
  color: #7f8c8d;
  transition: transform 0.3s ease;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  background-color: white;
  border: 1px solid #e1e8ed;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  min-width: 220px;
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: #2c3e50;
  background: none;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.dropdown-item i {
  font-size: 1.1rem;
  width: 20px;
  color: #7f8c8d;
}

.dropdown-item span {
  flex: 1;
}

/* Items admin spécifiques */
.admin-item {
  border-top: 1px solid #e1e8ed;
}

.admin-badge {
  font-size: 0.7rem;
  padding: 2px 8px;
  border-radius: 10px;
  font-weight: 600;
  text-transform: uppercase;
}

.admin-badge.super {
  background-color: #e74c3c;
  color: white;
}

.admin-badge.staff {
  background-color: #3498db;
  color: white;
}

.super-admin i {
  color: #e74c3c;
}

.staff-admin i {
  color: #3498db;
}

/* Item déconnexion */
.logout-item {
  border-top: 1px solid #e1e8ed;
  color: #e74c3c;
}

.logout-item i {
  color: #e74c3c;
}

.logout-item:hover {
  background-color: #fdf2f2;
}

@media (max-width: 768px) {
  .menu-toggle {
    display: block;
  }
  
  .search-box {
    display: none;
  }
  
  .user-info {
    display: none;
  }
  
  .dropdown-menu {
    min-width: 200px;
    right: -10px;
  }
}
</style>