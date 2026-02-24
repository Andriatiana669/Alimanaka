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

    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-btn">
        <span class="icon"><i class="bi bi-box-arrow-right"></i></span>
        <span class="label">Déconnexion</span>
      </button>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'

// Utiliser le composable auth
const { user, isAdmin, logout } = useAuth()
const isCollapsed = ref(localStorage.getItem('sidebar-collapsed') === 'true')

// Récupérer l'URL du backend depuis les variables d'environnement
const backendUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

// URLs d'administration
const backendAdminUrl = `${backendUrl}/admin/`
const alimanakaAdminUrl = `${backendUrl}/alimanaka-admin/`

// Vérifier les rôles
const isSuperAdmin = computed(() => {
  return user.value?.is_superuser === true
})

const isStaff = computed(() => {
  return user.value?.is_staff === true || isSuperAdmin.value
})

const showAdminSection = computed(() => {
  return isSuperAdmin.value || isStaff.value
})

// Conditions d'accès
const canAccessUsers = computed(() => {
  return isAdmin.value || true // À adapter selon tes besoins
})

const canAccessOSTIE = computed(() => {
  return isAdmin.value // Seulement pour les admins
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
</script>

<style scoped>
/* Styles pour la section admin */
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

.admin-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 15px;
  margin-bottom: 8px;
  border-radius: 8px;
  text-decoration: none;
  transition: all 0.3s ease;
  cursor: pointer;
  border: none;
  width: 100%;
  text-align: left;
  font-size: 0.9rem;
  position: relative;
}

.admin-btn:hover {
  transform: translateX(5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.admin-btn .icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  font-size: 1rem;
}

.admin-btn .label {
  flex: 1;
  font-weight: 500;
}

.admin-btn .badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

/* Bouton Admin Django (Super Admin) */
.django-admin-btn {
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border-left: 4px solid #c0392b;
}

.django-admin-btn:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
}

/* Bouton Admin Alimanaka (Staff) */
.alimanaka-admin-btn {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border-left: 4px solid #2980b9;
}

.alimanaka-admin-btn:hover {
  background: linear-gradient(135deg, #2980b9 0%, #1f639b 100%);
}

/* Style pour sidebar collapsed */
.sidebar.collapsed .admin-section {
  padding: 0 10px;
}

.sidebar.collapsed .admin-btn {
  justify-content: center;
  padding: 10px;
}

.sidebar.collapsed .admin-btn .icon {
  width: auto;
  font-size: 1.2rem;
}

.sidebar.collapsed .admin-btn .label,
.sidebar.collapsed .admin-btn .badge {
  display: none;
}

/* Ajustement pour le footer avec la section admin */
.sidebar-footer {
  margin-top: auto;
}

/* Responsive */
@media (max-height: 700px) {
  .admin-section {
    margin: 10px 0;
    padding-top: 10px;
    padding-bottom: 10px;
  }
  
  .admin-btn {
    padding: 8px 12px;
    margin-bottom: 6px;
  }
}
</style>