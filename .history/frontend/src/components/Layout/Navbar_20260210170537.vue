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
        <div class="avatar">
          {{ userInitials }}
        </div>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import { storeToRefs } from 'pinia'

const authStore = useAuthStore()
const { user } = storeToRefs(authStore)

// Nom complet de l'utilisateur
const userFullName = computed(() => {
  if (!user.value) return 'Utilisateur'
  
  if (user.value.pseudo) {
    return user.value.pseudo
  }
  
  const fullName = `${user.value.first_name || ''} ${user.value.last_name || ''} (${user.value.username || ''}) ` .trim()
  return fullName || user.value.username || 'Utilisateur'
})

// Rôle de l'utilisateur
const userRole = computed(() => {
  if (!user.value) return 'Non connecté'
  
  if (user.value.is_superuser) return 'Super Administrateur'
  if (user.value.is_staff) return 'Administrateur'
  return 'Employé'
})

// Initiales pour l'avatar
const userInitials = computed(() => {
  if (!user.value) return '?'
  
  // Utiliser le pseudo si disponible
  if (user.value.pseudo && user.value.pseudo.length > 0) {
    return user.value.pseudo.charAt(0).toUpperCase()
  }
  
  // Sinon utiliser nom + prénom
  const firstName = user.value.first_name || ''
  const lastName = user.value.last_name || ''
  
  if (firstName && lastName) {
    return (firstName.charAt(0) + lastName.charAt(0)).toUpperCase()
  }
  
  // Sinon utiliser le username
  if (user.value.username) {
    return user.value.username.charAt(0).toUpperCase()
  }
  
  return 'U' // Par défaut
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
  display: none; /* Visible uniquement sur mobile */
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
}
</style>