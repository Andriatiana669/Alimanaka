<template>
  <div class="profile">
    <h1 class="profileh1">Mon Profil</h1>
    
    <div v-if="loading" class="loading">
      Chargement du profil...
    </div>
    
    <div v-else-if="user" class="profile-card">
      <div class="profile-header">
        <div class="avatar">
          <span class="avatar-initials">{{ getInitials(user) }}</span>
        </div>
        <div class="profile-info">
          <h2>{{ displayName }} ({{ user.username.toUpperCase() }})</h2>
          <p class="email">{{ user.email }}</p>
          <span class="user-role">{{ userRole }}</span>
        </div>
      </div>
      
      <div class="profile-details">
        <!-- Section Pseudo Éditable -->
        <div class="detail-section pseudo-section">
          <div class="section-header">
            <h3>Mon Pseudo</h3>
            <button 
              v-if="!isEditingPseudo" 
              @click="startEditingPseudo" 
              class="btn-edit"
            >
              <i class="bi bi-pencil"></i> Modifier
            </button>
          </div>
          
          <div v-if="!isEditingPseudo" class="pseudo-display">
            <div class="pseudo-preview">
              <span class="pseudo-value">{{ displayName }}</span>
              <span class="pseudo-format-badge">{{ formatLabel }}</span>
            </div>
            <p class="pseudo-hint">
              Ce nom est visible par vos collègues dans l'application
            </p>
          </div>
          
          <div v-else class="pseudo-editor">
            <div class="form-group">
              <label>Format du pseudo</label>
              <select v-model="pseudoForm.format" @change="onFormatChange" class="form-select">
                <option v-for="option in formatOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <p class="form-hint">{{ formatDescription }}</p>
            </div>
            
            <div v-if="pseudoForm.format === 'custom'" class="form-group">
              <label>Pseudo personnalisé</label>
              <input 
                v-model="pseudoForm.customValue" 
                type="text" 
                maxlength="100"
                placeholder="Entrez votre pseudo personnalisé"
                class="form-input"
              />
              <span class="char-count">{{ pseudoForm.customValue?.length || 0 }}/100</span>
            </div>
            
            <div class="pseudo-preview-edit">
              <label>Aperçu</label>
              <div class="preview-box">
                <span class="preview-value">{{ previewDisplayName }}</span>
              </div>
            </div>
            
            <div class="form-actions">
              <button 
                @click="savePseudo" 
                :disabled="savingPseudo || !isPseudoValid"
                class="btn-save"
              >
                <i v-if="savingPseudo" class="bi bi-arrow-repeat spin"></i>
                <span v-else>Enregistrer</span>
              </button>
              <button @click="cancelEditingPseudo" class="btn-cancel">
                Annuler
              </button>
            </div>
            
            <div v-if="pseudoError" class="alert-error">
              <i class="bi bi-exclamation-triangle"></i>
              {{ pseudoError }}
            </div>
          </div>
        </div>

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
              <label>Pseudo actuel</label>
              <p>{{ displayName }}</p>
            </div>
            <div class="detail-item">
              <label>Email</label>
              <p>{{ user.email || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Pôle</label>
              <p>{{ user.pole_details?.nom || 'Non défini' }}</p>
            </div>
            <div class="detail-item">
              <label>Équipe</label>
              <p>{{ user.equipe_details?.nom || 'Non défini'}}</p>
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

        <!-- Section Organisation -->
        <div v-if="user.equipe_details || user.pole_details" class="detail-section">
          <h3>Organisation</h3>
          <div class="org-info">
            <div v-if="user.pole_details" class="org-item">
              <i class="bi bi-building"></i>
              <div>
                <label>Pôle</label>
                <p>{{ user.pole_details.nom }} ({{ user.pole_details.code }})</p>
              </div>
            </div>
            <div v-if="user.equipe_details" class="org-item">
              <i class="bi bi-people"></i>
              <div>
                <label>Équipe</label>
                <p>{{ user.equipe_details.nom }}</p>
                <span v-if="user.est_chef_equipe" class="badge-manager">👑 Manager</span>
                <span v-else-if="user.est_co_manager" class="badge-co-manager">🛡️ Co-Manager</span>
                <span v-else class="badge-member">👤 Membre</span>
              </div>
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'
import { useDisplayName } from '@/composables/useDisplayName'
import type { User, UpdatePseudoData } from '@/types/user'

// ========== COMPOSABLES ==========
const { generatePseudo } = useDisplayName()
const { user: authUser } = useAuth()

// ========== STATE ==========
const user = ref<User | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

// Édition du pseudo
const isEditingPseudo = ref(false)
const savingPseudo = ref(false)
const pseudoError = ref<string | null>(null)

const pseudoForm = reactive({
  format: 'first_word',
  customValue: ''
})

// Options de format (correspondent au backend)
const formatOptions = [
  { value: 'first_word', label: 'Premier mot du nom', description: 'Ex: "Rakoto" pour "Rakoto Jean Pierre"' },
  { value: 'second_word', label: 'Deuxième mot du nom', description: 'Ex: "Jean" pour "Rakoto Jean Pierre"' },
  { value: 'third_word', label: 'Troisième mot du nom', description: 'Ex: "Pierre" pour "Rakoto Jean Pierre"' },
  { value: 'first_two', label: 'Premier + Deuxième mots', description: 'Ex: "Rakoto Jean" pour "Rakoto Jean Pierre"' },
  { value: 'last_two', label: 'Deuxième + Troisième mots', description: 'Ex: "Jean Pierre" pour "Rakoto Jean Pierre"' },
  { value: 'all_words', label: 'Tous les mots', description: 'Ex: "Rakoto Jean Pierre"' },
  { value: 'custom', label: 'Personnalisé', description: 'Choisissez votre propre pseudo' }
]

// ========== COMPUTED ==========
const userRole = computed(() => {
  if (!user.value) return 'Non connecté'
  if (user.value.is_superuser) return 'Super Administrateur'
  if (user.value.is_staff) return 'Administrateur / Staff'
  return 'Employé'
})

const displayName = computed(() => {
  if (!user.value) return '-'
  return user.value.display_name || generatePseudo(user.value.last_name, user.value.pseudo)
})

const formatLabel = computed(() => {
  const option = formatOptions.find(opt => opt.value === user.value?.pseudo_format)
  return option?.label || 'Automatique'
})

const formatDescription = computed(() => {
  const option = formatOptions.find(opt => opt.value === pseudoForm.format)
  return option?.description || ''
})

const previewDisplayName = computed(() => {
  if (!user.value) return '-'
  
  if (pseudoForm.format === 'custom') {
    return pseudoForm.customValue.trim() || 'Votre pseudo...'
  }
  
  // Simulation du calcul côté backend
  const fullName = `${user.value.last_name} ${user.value.first_name}`.trim()
  const words = fullName.split(/\s+/).filter(w => w)
  
  switch (pseudoForm.format) {
    case 'first_word': return words[0] || user.value.username
    case 'second_word': return words[1] || words[0] || user.value.username
    case 'third_word': return words[2] || words[0] || user.value.username
    case 'first_two': return words.slice(0, 2).join(' ') || user.value.username
    case 'last_two': return words.slice(1, 3).join(' ') || user.value.username
    case 'all_words': return fullName || user.value.username
    default: return user.value.username
  }
})

const isPseudoValid = computed(() => {
  if (pseudoForm.format === 'custom') {
    return pseudoForm.customValue.trim().length > 0 && pseudoForm.customValue.length <= 100
  }
  return true
})

// ========== METHODS ==========
const loadProfile = async () => {
  loading.value = true
  error.value = null
  
  try {
    const userData = await usersApi.getUserProfile()
    user.value = userData
  } catch (err: any) {
    console.error('Erreur API:', err)
    if (authUser.value) {
      user.value = authUser.value as User
    } else {
      error.value = 'Impossible de charger votre profil'
    }
  } finally {
    loading.value = false
  }
}

const startEditingPseudo = () => {
  if (!user.value) return
  
  pseudoForm.format = user.value.pseudo_format || 'first_word'
  pseudoForm.customValue = user.value.pseudo || ''
  pseudoError.value = null
  isEditingPseudo.value = true
}

const cancelEditingPseudo = () => {
  isEditingPseudo.value = false
  pseudoError.value = null
}

const onFormatChange = () => {
  if (pseudoForm.format !== 'custom') {
    pseudoForm.customValue = ''
  }
}

const savePseudo = async () => {
  if (!isPseudoValid.value || !user.value) return
  
  savingPseudo.value = true
  pseudoError.value = null
  
  try {
    let data: UpdatePseudoData
    
    if (pseudoForm.format === 'custom') {
      data = { 
        pseudo: pseudoForm.customValue.trim(),
        pseudo_format: 'custom'
      }
    } else {
      data = { pseudo_format: pseudoForm.format }
    }
    
    const response = await usersApi.updatePseudo(data)
    
    // Mettre à jour l'utilisateur local
    user.value = {
      ...user.value,
      pseudo: response.pseudo,
      pseudo_format: response.pseudo_format,
      display_name: response.display_name
    }
    
    isEditingPseudo.value = false
    
    // Notification succès (tu peux remplacer par un toast)
    alert('Pseudo mis à jour avec succès !')
    
  } catch (err: any) {
    console.error('Erreur mise à jour pseudo:', err)
    pseudoError.value = err.response?.data?.error || 'Erreur lors de la mise à jour du pseudo'
  } finally {
    savingPseudo.value = false
  }
}

const getInitials = (user: User | null) => {
  if (!user) return '?'
  if (user.pseudo) return user.pseudo.charAt(0).toUpperCase()
  if (user.first_name && user.last_name) 
    return (user.first_name.charAt(0) + user.last_name.charAt(0)).toUpperCase()
  return user.username?.charAt(0)?.toUpperCase() || 'U'
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
  } catch (error) {
    return 'Format invalide'
  }
}

// ========== LIFECYCLE ==========
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile {
  margin-bottom: 2.5rem;
}

.profileh1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
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

.user-role {
  display: inline-block;
  background: #e8f4fc;
  color: #3498db;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.detail-section {
  margin-bottom: 2.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.detail-section h3 {
  color: #34495e;
  margin: 0;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ecf0f1;
}

/* Section Pseudo */
.pseudo-section {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  padding: 1.5rem;
  border-radius: 10px;
  border: 1px solid #dee2e6;
}

.pseudo-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pseudo-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.pseudo-value {
  font-size: 1.5rem;
  font-weight: 600;
  color: #2c3e50;
}

.pseudo-format-badge {
  background: #3498db;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
}

.pseudo-hint {
  color: #6c757d;
  font-size: 0.9rem;
  margin: 0;
}

/* Éditeur de pseudo */
.pseudo-editor {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
}

.form-select, .form-input {
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 6px;
  font-size: 1rem;
  background: white;
}

.form-select:focus, .form-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-hint {
  color: #6c757d;
  font-size: 0.85rem;
  margin: 0;
}

.char-count {
  color: #6c757d;
  font-size: 0.8rem;
  text-align: right;
}

.pseudo-preview-edit {
  background: white;
  padding: 1rem;
  border-radius: 6px;
  border: 2px dashed #3498db;
}

.pseudo-preview-edit label {
  font-size: 0.8rem;
  text-transform: uppercase;
  color: #3498db;
  font-weight: 600;
}

.preview-box {
  margin-top: 0.5rem;
}

.preview-value {
  font-size: 1.3rem;
  font-weight: 600;
  color: #2c3e50;
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.btn-edit {
  background: transparent;
  border: 1px solid #3498db;
  color: #3498db;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #3498db;
  color: white;
}

.btn-save {
  background: #27ae60;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.btn-save:hover:not(:disabled) {
  background: #229954;
}

.btn-save:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-cancel {
  background: transparent;
  border: 1px solid #95a5a6;
  color: #7f8c8d;
  padding: 0.75rem 1.5rem;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: #95a5a6;
  color: white;
}

.alert-error {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #c33;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* Grille d'infos */
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
  font-weight: 500;
}

/* Organisation */
.org-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.org-item {
  background: #f8f9fa;
  padding: 1.2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.org-item i {
  font-size: 1.5rem;
  color: #3498db;
}

.org-item label {
  display: block;
  color: #6c757d;
  font-size: 0.85rem;
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.org-item p {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-weight: 600;
}

.badge-manager, .badge-co-manager, .badge-member {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 500;
}

.badge-manager {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge-co-manager {
  background: #fff3e0;
  color: #ef6c00;
}

.badge-member {
  background: #eceff1;
  color: #546e7a;
}

/* Loading et erreurs */
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>