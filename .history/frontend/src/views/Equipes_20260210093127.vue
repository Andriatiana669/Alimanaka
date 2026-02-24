<template>
  <div class="profile-page">
    <h1>Mon Profil</h1>

    <!-- Barre de recherche globale -->
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

    <!-- Profil courant -->
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>
    
    <div v-else-if="user" class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span class="avatar-initials">{{ getInitials(user) }}</span>
        </div>
        <div class="profile-info">
          <h2>{{ generatePseudo(user.last_name, user.pseudo) }} ({{ user.username.toUpperCase() }})</h2>
          <p class="email">{{ user.email }}</p>
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
              <p>{{ user.username.toUpperCase() }}</p>
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
              <label>Pôle</label>
              <p>{{ user.pole_details.nom || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Équipe</label>
              <p>{{ user.equipe_details.nom || 'Non défini'}}</p>
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

    <!-- Liste filtrée des utilisateurs -->
    <div v-if="filteredUsers.length" class="table-container">
      <table class="users-table">
        <thead>
          <tr>
            <th>Matricule</th>
            <th>Pseudo</th>
            <th>Nom</th>
            <th>Prénom</th>
            <th>Email</th>
            <th>Pôle</th>
            <th>Équipe</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="u in filteredUsers" :key="u.id">
            <td>{{ u.username.toUpperCase() }}</td>
            <td>{{ generatePseudo(u.last_name, u.pseudo) }}</td>
            <td>{{ u.first_name || '-' }}</td>
            <td>{{ u.last_name || '-' }}</td>
            <td>{{ u.email }}</td>
            <td>{{ u.pole_details?.nom || '-' }}</td>
            <td>{{ u.equipe_details?.nom || '-' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredUsers.length === 0" class="no-data">
        Aucun utilisateur trouvé pour cette recherche.
      </div>
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

const user = ref<any>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Barre de recherche
const searchQuery = ref('')

// Liste de tous les utilisateurs
const allUsers = ref<User[]>([])

// Chargement du profil courant
const loadProfile = async () => {
  loading.value = true
  error.value = null

  try {
    const userData = await usersApi.getUserProfile()
    user.value = userData
    currentUser.value = userData
  } catch (err: any) {
    console.error('Erreur API:', err)
    if (authUser.value) user.value = authUser.value
    else error.value = 'Impossible de charger votre profil'
  } finally {
    loading.value = false
  }
}

// Chargement de tous les utilisateurs pour la recherche
const loadAllUsers = async () => {
  try {
    const users = await usersApi.getAllUsers()
    allUsers.value = users
  } catch (err) {
    console.error('Erreur chargement utilisateurs:', err)
  }
}

// Computed : utilisateurs filtrés par la recherche
const filteredUsers = computed(() => {
  if (!searchQuery.value) return allUsers.value
  const q = searchQuery.value.toLowerCase()
  return allUsers.value.filter(u =>
    u.username?.toLowerCase().includes(q) ||
    u.pseudo?.toLowerCase().includes(q) ||
    u.first_name?.toLowerCase().includes(q) ||
    u.last_name?.toLowerCase().includes(q) ||
    u.email?.toLowerCase().includes(q)
  )
})

const handleSearch = () => {
  // Reset ou autres effets si besoin
}

const clearSearch = () => {
  searchQuery.value = ''
}

const getInitials = (user: any) => {
  if (!user) return '?'
  if (user.pseudo) return user.pseudo.charAt(0).toUpperCase()
  if (user.first_name && user.last_name)
    return (user.first_name.charAt(0) + user.last_name.charAt(0)).toUpperCase()
  return user.username?.charAt(0)?.toUpperCase() || 'U'
}

const getUserRoleClass = (user: User | null): string => {
  if (!user) return 'role-user'
  if (user.is_superuser) return 'role-super-admin'
  if (user.is_staff) return 'role-admin'
  return 'role-user'
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'Non disponible'
  try {
    const date = new Date(dateString)
    if (isNaN(date.getTime())) return 'Date invalide'
    return date.toLocaleDateString('fr-FR', {
      day: 'numeric', month: 'long', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return 'Format invalide'
  }
}

onMounted(() => {
  loadProfile()
  loadAllUsers()
})
</script>

<style scoped>
/* Tu peux reprendre le CSS du Users.vue pour la search-bar et le tableau */
.search-bar {
  display: flex;
  margin: 1rem 0;
  align-items: center;
  gap: 1rem;
}
.search-input {
  position: relative;
  flex: 1;
}
.search-input input {
  width: 100%;
  padding: 0.5rem 2rem;
  border-radius: 6px;
  border: 1px solid #ccc;
}
.search-input i {
  position: absolute;
  left: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
}
.clear-search {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
}
.users-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}
.users-table th, .users-table td {
  padding: 0.5rem;
  border: 1px solid #ddd;
}





/* BADGES DE RÔLE */
.role-badge-header {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-right: 1rem;
}

.role-super-admin {
  background: #fce8e8;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.role-admin {
  background: #e8f4fc;
  color: #3498db;
  border: 1px solid #3498db;
}

.role-user {
  background: #f0f9f0;
  color: #27ae60;
  border: 1px solid #27ae60;
}

/* PAGE HEADER */
.page-header {
  margin-bottom: 2.5rem;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-left: auto;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #229954;
}

/* FILTRES */
.filters-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
  min-width: 150px;
}


.filter-group:focus {
  outline: none;
  border-color: #3498db;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  min-width: 200px;
}

.btn-refresh {
  width: 38px;
  height: 38px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  margin-left: auto;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #495057;
}

/* TREE VIEW */
.tree-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1rem;
  min-height: 200px;
}

.loading, .empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: #6c757d;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* MODAL */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal.modal-large {
  max-width: 800px;
  width: 90%;
}

.modal h3 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.6rem 1.2rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary:hover {
  background: #5a6268;
}

/* TABLEAU DES MEMBRES */
.membres-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.membres-table th,
.membres-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.membres-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  position: sticky;
  top: 0;
}

.membres-table tbody tr:hover {
  background: #f8f9fa;
}

.pseudo-tag {
  background: #e8f4fc;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.matricule {
  font-family: monospace;
  font-weight: bold;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.total-membres {
  text-align: right;
  font-style: italic;
  color: #6c757d;
  margin-top: 0.5rem;
}

/* ONGLETS */
.tabs {
  display: flex;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.2s;
}

.tab:hover {
  color: #495057;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-content {
  margin-bottom: 1rem;
}

/* FORMULAIRES */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-row select {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

/* BOUTONS ICONES */
.btn-icon.danger {
  color: #e74c3c;
}

.btn-icon.danger:hover {
  background: #fde8e8;
}

.ajout-section,
.membres-liste {
  margin-bottom: 2rem;
}

.ajout-section h4,
.membres-liste h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* RESPONSIVE */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-primary {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .filter-group select {
    width: 100%;
  }
  
  .modal.modal-large {
    width: 95%;
    max-width: 95%;
    padding: 1rem;
  }
  
  .membres-table {
    font-size: 0.8rem;
  }
  
  .membres-table th,
  .membres-table td {
    padding: 0.5rem;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .tab {
    width: 100%;
    text-align: left;
  }
}
</style>