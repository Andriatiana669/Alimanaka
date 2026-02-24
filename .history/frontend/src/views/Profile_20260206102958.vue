<template>
  <div class="profile">
    <h1>Mon Profil</h1>
    
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>
    
    <div v-else-if="user" class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span class="avatar-initials">{{ getInitials(user) }}</span>
        </div>
        <div class="profile-info">
          <!-- <h2>{{ user.display_name }}</h2> -->
          <h2>{{ user.last_name.split(' ')[1] || user.last_name.split(' ')[0] }} ({{ user.username }}.toUpercase)</h2>
          <p class="email">{{ user.email }}</p>
          <p class="role">{{ getUserRole(user) }}</p>
        </div>
      </div>
      
      <div class="profile-details">
        <div class="detail-section">
          <h3>Informations personnelles</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <label>Matricule</label>
              <p>{{ user.username }}</p>
            </div>
            <div class="detail-item">
              <label>Nom</label>
              <p>{{ user.first_name || '-' }}</p>
            </div>
            <div class="detail-item">
              <label>Prénom</label>
              <p>{{ user.last_name || '-' }}</p>
            </div>
            <div class="detail-item">
              <label>Pseudo</label>
              <p>{{ user.last_name.split(' ')[1] || user.last_name.split(' ')[0] }}</p>
            </div>
            <div class="detail-item">
              <label>Email</label>
              <p>{{ user.email || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Date d'inscription</label>
              <p>{{ formatDate(user.date_joined) }}</p>
            </div>
            <div class="detail-item">
              <label>Dernière connexion</label>
              <p>{{ user.last_login ? formatDate(user.last_login) : 'Jamais connecté' }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="error">
      Impossible de charger le profil. 
      <button @click="loadProfile" class="btn-retry">Réessayer</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'

const { user: authUser } = useAuth()
const user = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

const loadProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    // Essaie d'abord l'API
    const userData = await usersApi.getUserProfile()
    user.value = userData
  } catch (err: any) {
    console.error('Erreur API:', err)
    
    // Fallback: utiliser les données d'authentification
    if (authUser.value) {
      user.value = authUser.value
    } else {
      error.value = 'Impossible de charger votre profil'
    }
  } finally {
    loading.value = false
  }
}

const getInitials = (user: any) => {
  if (!user) return '?'
  if (user.pseudo) return user.pseudo.charAt(0).toUpperCase()
  if (user.first_name && user.last_name) 
    return (user.first_name.charAt(0) + user.last_name.charAt(0)).toUpperCase()
  return user.username?.charAt(0)?.toUpperCase() || 'U'
}

const getUserRole = (user: any) => {
  if (!user) return 'Inconnu'
  if (user.is_superuser) return 'Super Administrateur'
  if (user.is_staff) return 'Administrateur'
  return 'Utilisateur'
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Non disponible'
  
  try {
    const date = new Date(dateString)
    
    // Vérifier si la date est valide
    if (isNaN(date.getTime())) {
      return 'Date invalide'
    }
    
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    console.error('Erreur format date:', error)
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