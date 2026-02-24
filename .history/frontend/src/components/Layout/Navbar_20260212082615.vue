<template>
  <header class="navbar">
    <div class="navbar-left">
      <span class="breadcrumb">Lalamby : Alimanaka</span>
    </div>

    <div class="navbar-right">
      <!-- Notifications -->
      <div class="notifications">
        <button class="icon-btn">
          <span class="badge">3</span>
          <span>🔔</span>
        </button>
      </div>

      <!-- Zone utilisateur cliquable (nom + avatar) -->
      <div class="user-menu" @click="toggleDropdown" ref="userMenuContainer">
        <div class="user-info">
          <span class="user-name">{{ userFullName.toUpperCase() }} {{ currentuser?.username }}</span>
          <span class="user-role">{{ userRole }}</span>
        </div>
        
        <div class="avatar">
          {{ userInitials }}
        </div>

        <!-- Menu déroulant -->
        <div v-if="showDropdown" class="dropdown-menu">
          <!-- Lien Mon profil -->
          <router-link to="/profile" class="dropdown-item" @click="closeDropdown">
            <!-- <span class="dropdown-icon"><i class="bi bi-person-circle"></i></span> -->
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
              <!-- <span class="dropdown-icon"><i class="bi bi-gear-wide-connected"></i></span> -->
              <span class="dropdown-label">Admin / Groupe</span>
              <span class="admin-badge super">Super Admin</span>
            </a>
            
            <!-- Admin Alimanaka (Staff) -->
            <a 
              v-if="isStaff" 
              :href="alimanakaAdminUrl" 
              target="_blank" 
              class="dropdown-item admin-item"
              @click="closeDropdown"
            >
              <!-- <span class="dropdown-icon"><i class="bi bi-palette"></i></span> -->
              <span class="dropdown-label">Admin Alimanaka</span>
              <span class="admin-badge staff">Admin / Staff</span>
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
  </header>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'
import Users from '@/views/Users.vue'

const router = useRouter()
const authStore = useAuthStore()
const { user: authUser } = storeToRefs(authStore)

// Refs
const showDropdown = ref(false)
const userMenuContainer = ref<HTMLElement | null>(null)
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)

// URLs admin
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
const backendAdminUrl = `${backendUrl}/admin/`
const alimanakaAdminUrl = `${backendUrl}/alimanaka-admin/`

// Récupération de l'utilisateur courant
const fetchCurrentUser = async () => {
  loadingUser.value = true
  try {
    currentUser.value = await usersApi.getCurrentUser()
  } catch (err: any) {
    console.error('Erreur récupération user:', err)
    currentUser.value = authUser.value
  } finally {
    loadingUser.value = false
  }
}

// Computed
const userFullName = computed(() => {
  if (!currentUser.value) return 'Utilisateur'
  if (currentUser.value.pseudo) return currentUser.value.pseudo
  const fullName = `${currentUser.value.first_name || ''} ${currentUser.value.last_name || ''}`.trim()
  return fullName || currentUser.value.username || 'Utilisateur'
})

const userRole = computed(() => {
  if (!currentUser.value) return 'Non connecté'
  if (currentUser.value.is_superuser) return 'Super Administrateur'
  if (currentUser.value.is_staff) return 'Administrateur / Staff'
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
  if (currentUser.value.pseudo && currentUser.value.pseudo.length > 0) {
    return currentUser.value.pseudo.charAt(0).toUpperCase()
  }
  const first = currentUser.value.first_name?.charAt(0) || ''
  const last = currentUser.value.last_name?.charAt(0) || ''
  if (first && last) return (first + last).toUpperCase()
  if (currentUser.value.username) return currentUser.value.username.charAt(0).toUpperCase()
  return 'U'
})

const isSuperAdmin = computed(() => currentUser.value?.is_superuser === true)
const isStaff = computed(() => currentUser.value?.is_staff === true || isSuperAdmin.value)
const showAdminSection = computed(() => isSuperAdmin.value || isStaff.value)

// Méthodes
const toggleDropdown = (e: Event) => {
  // Empêche la propagation si on clique sur un lien/bouton à l'intérieur
  if ((e.target as HTMLElement).closest('a, button')) return
  showDropdown.value = !showDropdown.value
}

const closeDropdown = () => {
  showDropdown.value = false
}

const handleLogout = () => {
  closeDropdown()
  authStore.logout()
}

const handleClickOutside = (event: MouseEvent) => {
  if (userMenuContainer.value && !userMenuContainer.value.contains(event.target as Node)) {
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

.icon-btn {
  background: none;
  border: none;
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0.5rem;
  color: #7f8c8d;
  position: relative;
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  background: #e74c3c;
  color: white;
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 10px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  transition: background 0.2s;
  position: relative;
}

.user-menu:hover {
  background-color: #f8f9fa;
}

.user-info {
  text-align: right;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
  display: block;
}

.user-role {
  font-size: 0.8rem;
  color: #7f8c8d;
  display: block;
}

.avatar {
  width: 42px;
  height: 42px;
  background-color: #3498db;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.avatar:hover {
  background-color: #2980b9;
}

/* Dropdown */
.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.15);
  border: 1px solid #e1e8ed;
  z-index: 1000;
  overflow: hidden;
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
  display: block;
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