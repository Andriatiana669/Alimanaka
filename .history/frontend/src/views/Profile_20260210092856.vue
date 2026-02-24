<template>
  <div class="profile">
    <h1>Équipe : {{ teamName || 'Non défini' }}</h1>

    <!-- Barre de recherche -->
    <div class="search-bar">
      <div class="search-input">
        <i class="bi bi-search"></i>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Rechercher par matricule, pseudo, nom, email..." 
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
      Chargement des utilisateurs...
    </div>

    <div v-else-if="filteredUsers.length" class="team-list">
      <div 
        v-for="u in filteredUsers" 
        :key="u.id" 
        class="profile-card"
      >
        <div class="profile-header">
          <div class="avatar">
            <span class="avatar-initials">{{ getInitials(u) }}</span>
          </div>
          <div class="profile-info">
            <h2>{{ generatePseudo(u.last_name, u.pseudo) }} ({{ u.username.toUpperCase() }})</h2>
            <p class="email">{{ u.email }}</p>
            <span class="role-badge-header" :class="getUserRoleClass(u)">
              {{ getRoleLabel(u) }}
            </span>
          </div>
        </div>

        <div class="profile-details">
          <div class="detail-section">
            <h3>Informations personnelles</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label>Matricule</label>
                <p>{{ u.username.toUpperCase() }}</p>
              </div>
              <div class="detail-item">
                <label>Nom</label>
                <p>{{ u.first_name || '-' }}</p>
              </div>
              <div class="detail-item">
                <label>Prénom</label>
                <p>{{ u.last_name || '-' }}</p>
              </div>
              <div class="detail-item">
                <label>Pseudo</label>
                <p>{{ u.last_name.split(' ')[1] || u.last_name.split(' ')[0] }}</p>
              </div>
              <div class="detail-item">
                <label>Email</label>
                <p>{{ u.email || 'Non défini' }}</p>
              </div>
              <div class="detail-item">
                <label>Pôle</label>
                <p>{{ u.pole_details.nom || 'Non défini' }}</p>
              </div>
              <div class="detail-item">
                <label>Equipe</label>
                <p>{{ u.equipe_details.nom || 'Non défini'}}</p>
              </div>
              <div class="detail-item">
                <label>Date d'inscription</label>
                <p>{{ formatDate(u.date_joined) }}</p>
              </div>
              <div class="detail-item">
                <label>Dernière connexion</label>
                <p>{{ u.last_login ? formatDate(u.last_login) : 'Jamais connecté' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="error">
      Aucun utilisateur ne correspond à votre recherche.
      <button @click="loadTeam" class="btn-retry">Réessayer</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usersApi } from '@/api/users'
import type { User } from '@/types/user'
import { useRoles } from '@/composables/useRoles'
import { useDisplayName } from '@/composables/useDisplayName'
import { useAuth } from '@/composables/useAuth'

const { getRoleLabel } = useRoles()
const { generatePseudo } = useDisplayName()
const { user: authUser } = useAuth()

const currentUser = ref<User | null>(null)
const teamUsers = ref<User[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const searchQuery = ref('')

const teamName = ref('')

// Filtrage des utilisateurs selon la recherche
const filteredUsers = computed(() => {
  if (!searchQuery.value) return teamUsers.value
  const query = searchQuery.value.toLowerCase()
  return teamUsers.value.filter(u =>
    u.username?.toLowerCase().includes(query) ||
    u.pseudo?.toLowerCase().includes(query) ||
    u.first_name?.toLowerCase().includes(query) ||
    u.last_name?.toLowerCase().includes(query) ||
    u.email?.toLowerCase().includes(query)
  )
})

const clearSearch = () => {
  searchQuery.value = ''
}

// Récupérer les initiales
const getInitials = (u: User) => {
  if (u.pseudo) return u.pseudo.charAt(0).toUpperCase()
  if (u.first_name && u.last_name)
    return (u.first_name.charAt(0) + u.last_name.charAt(0)).toUpperCase()
  return u.username?.charAt(0)?.toUpperCase() || 'U'
}

// Classe rôle
const getUserRoleClass = (u: User): string => {
  if (!u) return 'role-user'
  if (u.is_superuser) return 'role-super-admin'
  if (u.is_staff) return 'role-admin'
  return 'role-user'
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

// Charger les utilisateurs de la même équipe
const loadTeam = async () => {
  loading.value = true
  error.value = null
  try {
    // Récupérer le user courant
    const authData = authUser.value
    currentUser.value = authData

    if (!authData?.equipe_details?.id) {
      error.value = 'Vous n\'avez pas d\'équipe définie'
      return
    }

    teamName.value = authData.equipe_details.nom

    // API pour récupérer tous les utilisateurs de la même équipe
    const allUsers: User[] = await usersApi.getUsersByTeam(authData.equipe_details.id)
    teamUsers.value = allUsers
  } catch (err: any) {
    console.error('Erreur API:', err)
    error.value = 'Impossible de charger les utilisateurs'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadTeam()
})
</script>

<style scoped>
.search-bar {
  margin-bottom: 1rem;
}
.search-input {
  position: relative;
  display: flex;
  align-items: center;
}
.search-input input {
  flex: 1;
  padding: 0.5rem 2.5rem 0.5rem 2rem;
  border-radius: 4px;
  border: 1px solid #ccc;
}
.search-input i.bi-search {
  position: absolute;
  left: 0.5rem;
  font-size: 1.2rem;
  color: #666;
}
.clear-search {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  cursor: pointer;
}
.profile-card {
  margin-bottom: 1rem;
}
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 0.5rem;
}
.detail-item label {
  font-weight: bold;
}
.role-badge-header {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  color: white;
  font-size: 0.8rem;
}
.role-super-admin { background-color: #d9534f; }
.role-admin { background-color: #f0ad4e; }
.role-user { background-color: #5bc0de; }

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