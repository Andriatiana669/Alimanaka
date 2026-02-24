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

      <div class="user-menu">
        <div class="user-info">
          <span class="user-name">{{ userFullName.toUpperCase() }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
        
        <!-- Avatar avec menu déroulant -->
        <div class="avatar-container" @click="toggleDropdown" ref="avatarContainer">
          <div class="avatar">
            {{ userInitials }}
          </div>
          
          <!-- Menu déroulant -->
          <div v-if="showDropdown" class="dropdown-menu" :class="{ 'visible': showDropdown }">
            <!-- Section utilisateur -->
            <div class="user-dropdown-info">
              <div class="dropdown-avatar">{{ userInitials }}</div>
              <div class="dropdown-user-details">
                <div class="dropdown-user-name">{{ userFullName }}</div>
                <div class="dropdown-user-email">{{ currentUser?.email || '' }}</div>
                <div class="dropdown-user-role">
                  <span class="role-badge" :class="roleClass">{{ userRole }}</span>
                </div>
              </div>
            </div>
            
            <div class="dropdown-divider"></div>
            
            <!-- Lien Mon profil -->
            <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
              <span class="dropdown-icon"><i class="bi bi-person-circle"></i></span>
              <span class="dropdown-label">Mon profil</span>
            </router-link>
            
            <!-- Section Admin (si autorisé) -->
            <div v-if="showAdminSection" class="dropdown-admin-section">
              <div class="dropdown-section-title">
                <i class="bi bi-shield-lock"></i>
                <span>Administration</span>
              </div>
              
              <!-- Admin Django (Super Admin) -->
              <a 
                v-if="isSuperAdmin" 
                :href="backendAdminUrl" 
                target="_blank" 
                class="dropdown-item admin-item"
                @click="closeDropdown"
              >
                <span class="dropdown-icon"><i class="bi bi-gear-wide-connected"></i></span>
                <span class="dropdown-label">Admin Django</span>
                <span class="admin-badge super">Super</span>
              </a>
              
              <!-- Admin Alimanaka (Staff) -->
              <a 
                v-if="isStaff" 
                :href="alimanakaAdminUrl" 
                target="_blank" 
                class="dropdown-item admin-item"
                @click="closeDropdown"
              >
                <span class="dropdown-icon"><i class="bi bi-palette"></i></span>
                <span class="dropdown-label">Admin Alimanaka</span>
                <span class="admin-badge staff">Staff</span>
              </a>
            </div>
            
            <div class="dropdown-divider"></div>
            
            <!-- Déconnexion -->
            <button class="dropdown-item logout-item" @click="handleLogout">
              <span class="dropdown-icon"><i class="bi bi-box-arrow-right"></i></span>
              <span class="dropdown-label">Déconnexion</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>



<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'

const router = useRouter()
const authStore = useAuthStore()
// CORRECTION : storeToRefs seulement pour le state, pas pour les actions
const { user: authUser } = storeToRefs(authStore)

// Refs
const showDropdown = ref(false)
const avatarContainer = ref<HTMLElement | null>(null)
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)

// URLs
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const backendAdminUrl = `${backendUrl}/admin/`
const alimanakaAdminUrl = `${backendUrl}/alimanaka-admin/`

// Récupérer l'utilisateur courant
const fetchCurrentUser = async () => {
  loadingUser.value = true
  try { 
    currentUser.value = await usersApi.getCurrentUser()
  } 
  catch (err: any) { 
    console.error('Erreur récupération user:', err)
    // Fallback sur l'user du store auth
    currentUser.value = authUser.value
  }
  finally { 
    loadingUser.value = false 
  }
}

// Computed properties
const userFullName = computed(() => {
  if (!currentUser.value) return 'Utilisateur'
  
  if (currentUser.value.pseudo) {
    return currentUser.value.pseudo
  }
  
  const fullName = `${currentUser.value.first_name || ''} ${currentUser.value.last_name || ''}`.trim()
  return fullName || currentUser.value.username || 'Utilisateur'
})

const userRole = computed(() => {
  if (!currentUser.value) return 'Non connecté'
  
  if (currentUser.value.is_superuser) return 'Super Administrateur'
  if (currentUser.value.is_staff) return 'Administrateur'
  return 'Employé'
})

const roleClass = computed(() => {
  if (!currentUser.value) return 'role-employee'
  
  if (currentUser.value.is_superuser) return 'role-superadmin'
  if (currentUser.value.is_staff) return 'role-admin'
  return 'role-employee'
})

const userInitials = computed(() => {
  if (!currentUser.value) return '?'
  
  // Utiliser le pseudo si disponible
  if (currentUser.value.pseudo && currentUser.value.pseudo.length > 0) {
    return currentUser.value.pseudo.charAt(0).toUpperCase()
  }
  
  // Sinon utiliser nom + prénom
  const firstName = currentUser.value.first_name || ''
  const lastName = currentUser.value.last_name || ''
  
  if (firstName && lastName) {
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase()
  }
  
  // Sinon utiliser le username
  if (currentUser.value.username) {
    return currentUser.value.username.charAt(0).toUpperCase()
  }
  
  return 'U'
})

const isSuperAdmin = computed(() => {
  return currentUser.value?.is_superuser === true
})

const isStaff = computed(() => {
  return currentUser.value?.is_staff === true || isSuperAdmin.value
})

const showAdminSection = computed(() => {
  return isSuperAdmin.value || isStaff.value
})

// Méthodes
const toggleDropdown = () => {
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

// CORRECTION : Appel direct à l'action du store
const handleLogout = () => {
  closeDropdown()
  authStore.logout() // ← ICI : appel direct, pas via storeToRefs
}

// Fermer le dropdown en cliquant à l'extérieur
const handleClickOutside = (event: MouseEvent) => {
  if (avatarContainer.value && !avatarContainer.value.contains(event.target as Node)) {
    closeDropdown()
  }
}

// Lifecycle
onMounted(() => {
  fetchCurrentUser()
  document.addEventListener('click', handleClickOutside)
})

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
  position: relative;
  cursor: pointer;
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
  transition: all 0.3s ease;
}

.avatar-container:hover .avatar {
  background-color: #2980b9;
  transform: scale(1.05);
}

/* Dropdown Menu */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  border: 1px solid #e1e8ed;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
  overflow: hidden;
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

/* User info in dropdown */
.user-dropdown-info {
  display: flex;
  align-items: center;
  padding: 20px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 1px solid #e1e8ed;
}

.dropdown-avatar {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.2rem;
  margin-right: 15px;
}

.dropdown-user-details {
  flex: 1;
}

.dropdown-user-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1rem;
  margin-bottom: 4px;
}

.dropdown-user-email {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin-bottom: 8px;
}

.dropdown-user-role .role-badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.role-badge.role-superadmin {
  background: linear-gradient(45deg, #e74c3c, #c0392b);
  color: white;
}

.role-badge.role-admin {
  background: linear-gradient(45deg, #3498db, #2980b9);
  color: white;
}

.role-badge.role-employee {
  background: linear-gradient(45deg, #2ecc71, #27ae60);
  color: white;
}

/* Dropdown items */
.dropdown-divider {
  height: 1px;
  background: #e1e8ed;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: #2c3e50;
  text-decoration: none;
  transition: all 0.2s ease;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
  font-size: 0.95rem;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  color: #3498db;
}

.dropdown-item .dropdown-icon {
  width: 24px;
  font-size: 1.1rem;
  margin-right: 12px;
  color: #7f8c8d;
}

.dropdown-item:hover .dropdown-icon {
  color: #3498db;
}

.dropdown-item .dropdown-label {
  flex: 1;
}

/* Admin section */
.dropdown-admin-section {
  padding: 10px 0;
}

.dropdown-section-title {
  display: flex;
  align-items: center;
  padding: 8px 20px;
  color: #7f8c8d;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.dropdown-section-title i {
  margin-right: 8px;
  font-size: 0.9rem;
}

/* Admin items */
.admin-item {
  position: relative;
}

.admin-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.admin-badge.super {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
  border: 1px solid rgba(231, 76, 60, 0.2);
}

.admin-badge.staff {
  background: rgba(52, 152, 219, 0.1);
  color: #3498db;
  border: 1px solid rgba(52, 152, 219, 0.2);
}

/* Logout item */
.logout-item {
  color: #e74c3c;
}

.logout-item:hover {
  background-color: rgba(231, 76, 60, 0.05);
  color: #c0392b;
}

.logout-item .dropdown-icon {
  color: #e74c3c;
}

/* Responsive */
@media (max-width: 768px) {
  .search-box {
    display: none;
  }
  
  .user-info {
    display: none;
  }
  
  .dropdown-menu {
    width: 280px;
    right: -10px;
  }
}

@media (max-width: 480px) {
  .navbar {
    padding: 0 1rem;
    height: 70px;
  }
  
  .dropdown-menu {
    width: 250px;
  }
}
</style>