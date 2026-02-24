<template>
  <div class="profile">
    <h1>Mon Profil</h1>

    <!-- Barre de recherche -->
    <div class="search-bar">
      <div class="search-input">
        <i class="bi bi-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Rechercher par matricule, pseudo, nom, email..." 
          @input="handleSearch"
        />
        <button 
          v-if="searchQuery" 
          @click="clearSearch" 
          class="clear-search"
          title="Effacer la recherche"
        >
          <i class="bi bi-x"></i>
        </button>
      </div>
    </div>

    <!-- Loading / Error -->
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>

    <div v-else-if="filteredUser" class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span class="avatar-initials">{{ getInitials(filteredUser) }}</span>
        </div>
        <div class="profile-info">
          <h2>{{ generatePseudo(filteredUser.last_name, filteredUser.pseudo) }} ({{ filteredUser.username.toUpperCase() }})</h2>
          <p class="email">{{ filteredUser.email }}</p>
          <span v-if="currentUser" class="role-badge-header" :class="getUserRoleClass(currentUser)">
            {{ getRoleLabel(currentUser) }}
          </span>
        </div>
      </div>

      <div class="profile-details">
        <div class="detail-section">
          <h3>Informations personnelles</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>Matricule</label>
              <p>{{ filteredUser.username.toUpperCase() }}</p>
            </div>
            <div class="detail-item">
              <label>Nom</label>
              <p>{{ filteredUser.first_name || '-' }}</p>
            </div>
            <div class="detail-item">
              <label>Prénom</label>
              <p>{{ filteredUser.last_name || '-' }}</p>
            </div>
            <div class="detail-item">
              <label>Pseudo</label>
              <p>{{ filteredUser.last_name.split(' ')[1] || filteredUser.last_name.split(' ')[0] }}</p>
            </div>
            <div class="detail-item">
              <label>Email</label>
              <p>{{ filteredUser.email || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Pôle</label>
              <p>{{ filteredUser.pole_details.nom || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Equipe</label>
              <p>{{ filteredUser.equipe_details.nom || 'Non défini'}}</p>
            </div>
            <div class="detail-item">
              <label>Date d'inscription</label>
              <p>{{ formatDate(filteredUser.date_joined) }}</p>
            </div>
            <div class="detail-item">
              <label>Dernière connexion</label>
              <p>{{ filteredUser.last_login ? formatDate(filteredUser.last_login) : 'Jamais connecté' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error">
      Aucun utilisateur ne correspond à votre recherche.
      <button @click="loadProfile" class="btn-retry">Réessayer</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'
import { useRoles } from '@/composables/useRoles'
import { useDisplayName } from '@/composables/useDisplayName'

const { getRoleLabel } = useRoles()
const currentUser = ref<User | null>(null)
const { generatePseudo } = useDisplayName()
const { user: authUser } = useAuth()
const user = ref<User | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Barre de recherche
const searchQuery = ref('')

const handleSearch = () => {
  // rien de spécial à faire ici, la recherche est reactif via computed
}

const clearSearch = () => {
  searchQuery.value = ''
}

// Filtered user selon la recherche
const filteredUser = computed(() => {
  if (!user.value) return null
  if (!searchQuery.value) return user.value

  const query = searchQuery.value.toLowerCase()
  const u = user.value
  if (
    u.username?.toLowerCase().includes(query) ||
    u.pseudo?.toLowerCase().includes(query) ||
    u.first_name?.toLowerCase().includes(query) ||
    u.last_name?.toLowerCase().includes(query) ||
    u.email?.toLowerCase().includes(query)
  ) {
    return u
  }

  return null
})

// Récupérer les initiales
const getInitials = (u: User | null) => {
  if (!u) return '?'
  if (u.pseudo) return u.pseudo.charAt(0).toUpperCase()
  if (u.first_name && u.last_name) 
    return (u.first_name.charAt(0) + u.last_name.charAt(0)).toUpperCase()
  return u?.username?.charAt(0)?.toUpperCase() || 'U'
}

// Classe rôle
const getUserRoleClass = (u: User | null): string => {
  if (!u) return 'role-user'
  if (u.is_superuser) return 'role-super-admin'
  if (u.is_staff) return 'role-admin'
  return 'role-user'
}

const loadProfile = async () => {
  loading.value = true
  error.value = null
  try {
    const userData = await usersApi.getUserProfile()
    user.value = userData
    currentUser.value = authUser.value
  } catch (err: any) {
    console.error('Erreur API:', err)
    if (authUser.value) {
      user.value = authUser.value
      currentUser.value = authUser.value
    } else {
      error.value = 'Impossible de charger votre profil'
    }
  } finally {
    loading.value = false
  }
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Non disponible'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Date invalide'
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Format invalide'
  }
}

onMounted(() => {
  loadProfile()
})
</script>


<style scoped>
.profile {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.profile-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #f1f3f5;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
}

.avatar-initials {
  text-transform: uppercase;
}

.profile-info h2 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.email {
  color: #7f8c8d;
  margin: 0 0 0.5rem 0;
}

.role {
  display: inline-block;
  background: #e8f4fc;
  color: #3498db;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
}

.detail-section {
  margin-bottom: 2.5rem;
}

.detail-section h3 {
  color: #34495e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ecf0f1;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.detail-item {
  background: #f8fafc;
  padding: 1.2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.detail-item label {
  display: block;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.detail-item p {
  color: #495057;
  margin: 0;
  font-size: 1rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #dee2e6;
}

.error {
  color: #dc3545;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-retry:hover {
  background-color: #0056b3;
}
</style>