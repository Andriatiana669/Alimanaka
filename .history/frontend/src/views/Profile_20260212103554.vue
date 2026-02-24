<template>
  <div class="profile">
    <h1 class="profileh1">Mon Profil</h1>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <span>Chargement du profil...</span>
    </div>
    
    <div v-else-if="user" class="profile-container">
      <!-- Carte principale -->
      <div class="profile-card">
        <div class="profile-header">
          <div class="avatar" :class="{ 'has-pseudo': user.pseudo }">
            <span class="avatar-initials">{{ getInitials(user) }}</span>
            <div v-if="user.pseudo" class="pseudo-badge">@</div>
          </div>
          <div class="profile-info">
            <h2>{{ displayName }} <span class="matricule">({{ user.username.toUpperCase() }})</span></h2>
            <p class="email">{{ user.email }}</p>
            <span class="role-badge" :class="roleClass">
              {{ roleLabel }}
            </span>
          </div>
        </div>
        
        <!-- Section Pseudo Interactive -->
        <div class="pseudo-section" :class="{ 'editing': isEditingPseudo }">
          <div class="section-header">
            <h3><i class="bi bi-person-badge"></i> Mon Pseudo Alimanaka</h3>
            <button 
              v-if="!isEditingPseudo" 
              @click="startEditPseudo" 
              class="btn-edit"
            >
              <i class="bi bi-pencil"></i> Modifier
            </button>
          </div>
          
          <!-- Mode Affichage -->
          <div v-if="!isEditingPseudo" class="pseudo-display">
            <div class="pseudo-preview">
              <span class="current-pseudo">{{ displayName }}</span>
              <span class="format-badge">{{ formatLabel }}</span>
            </div>
            <p class="pseudo-hint">
              Généré selon le format : <strong>{{ formatLabel }}</strong>
            </p>
          </div>
          
          <!-- Mode Édition -->
          <div v-else class="pseudo-edit">
            <div class="form-group">
              <label>Format du pseudo</label>
              <select v-model="pseudoForm.pseudo_format" @change="onFormatChange" class="form-select">
                <option v-for="option in formatOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <small class="help-text">
                {{ getFormatDescription(pseudoForm.pseudo_format) }}
              </small>
            </div>
            
            <div v-if="pseudoForm.pseudo_format === 'custom'" class="form-group">
              <label>Pseudo personnalisé</label>
              <input 
                type="text" 
                v-model="pseudoForm.pseudo" 
                maxlength="100"
                placeholder="Entrez votre pseudo personnalisé"
                class="form-input"
                :class="{ 'error': errors.pseudo }"
              />
              <small v-if="errors.pseudo" class="error-text">{{ errors.pseudo }}</small>
              <small v-else class="help-text">Max 100 caractères</small>
            </div>
            
            <div class="preview-box">
              <label>Aperçu</label>
              <div class="preview-value">{{ previewDisplayName }}</div>
            </div>
            
            <div class="form-actions">
              <button @click="cancelEdit" class="btn-secondary" :disabled="saving">
                <i class="bi bi-x"></i> Annuler
              </button>
              <button @click="savePseudo" class="btn-primary" :disabled="saving || !hasChanges">
                <i class="bi" :class="saving ? 'bi-arrow-repeat spin' : 'bi-check'"></i>
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </div>
        </div>
        
        <!-- Détails du profil -->
        <div class="profile-details">
          <div class="detail-section">
            <h3><i class="bi bi-info-circle"></i> Informations personnelles</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <label><i class="bi bi-person-vcard"></i> Matricule</label>
                <p class="value">{{ user.username.toUpperCase() }}</p>
              </div>
              <div class="detail-item">
                <label><i class="bi bi-person"></i> Nom</label>
                <p class="value">{{ user.last_name || '-' }}</p>
              </div>
              <div class="detail-item">
                <label><i class="bi bi-person"></i> Prénom</label>
                <p class="value">{{ user.first_name || '-' }}</p>
              </div>
              <div class="detail-item">
                <label><i class="bi bi-envelope"></i> Email</label>
                <p class="value">{{ user.email || 'Non défini' }}</p>
              </div>
              <div class="detail-item highlight">
                <label><i class="bi bi-building"></i> Pôle</label>
                <p class="value">
                  <span v-if="user.pole_details" class="tag">
                    {{ user.pole_details.code }} - {{ user.pole_details.nom }}
                  </span>
                  <span v-else class="tag empty">Non assigné</span>
                </p>
              </div>
              <div class="detail-item highlight">
                <label><i class="bi bi-people"></i> Équipe</label>
                <p class="value">
                  <span v-if="user.equipe_details" class="tag">
                    {{ user.equipe_details.nom }}
                    <small v-if="user.est_chef_equipe" class="role-mini">👑 Manager</small>
                    <small v-else-if="user.est_co_manager" class="role-mini">🛡️ Co-Manager</small>
                  </span>
                  <span v-else class="tag empty">Non assignée</span>
                </p>
              </div>
              <div class="detail-item">
                <label><i class="bi bi-calendar-plus"></i> Inscription</label>
                <p class="value">{{ formatDate(user.date_joined) }}</p>
              </div>
              <div class="detail-item">
                <label><i class="bi bi-clock-history"></i> Dernière connexion</label>
                <p class="value">{{ user.last_login ? formatDate(user.last_login) : 'Jamais connecté' }}</p>
              </div>
            </div>
          </div>
          
          <!-- Équipes gérées (si chef/co-manager) -->
          <div v-if="user.equipes_managerisees?.length" class="detail-section">
            <h3><i class="bi bi-stars"></i> Mes responsabilités</h3>
            <div class="managed-teams">
              <div v-for="eq in user.equipes_managerisees" :key="eq.id" class="team-card">
                <span class="team-name">{{ eq.nom }}</span>
                <span class="team-count">{{ eq.membres_count }} membres</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="error-state">
      <i class="bi bi-exclamation-triangle"></i>
      <p>Impossible de charger le profil</p>
      <button @click="loadProfile" class="btn-retry">
        <i class="bi bi-arrow-clockwise"></i> Réessayer
      </button>
    </div>
    
    <!-- Toast notification -->
    <div v-if="notification.show" class="toast" :class="notification.type">
      <i class="bi" :class="notification.type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle'"></i>
      <span>{{ notification.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { usersApi } from '@/api/users'
import type { User, UpdatePseudoData } from '@/types/user'

const { user: authUser, checkAuth } = useAuth()

const user = ref<User | null>(null)
const loading = ref(true)
const saving = ref(false)
const isEditingPseudo = ref(false)

const pseudoForm = reactive({
  pseudo_format: 'first_word',
  pseudo: ''
})

const errors = reactive({
  pseudo: ''
})

const notification = reactive({
  show: false,
  message: '',
  type: 'success' as 'success' | 'error'
})

// Options de format pour le select
const formatOptions = [
  { value: 'first_word', label: 'Premier mot du nom' },
  { value: 'second_word', label: 'Deuxième mot du nom' },
  { value: 'third_word', label: 'Troisième mot du nom' },
  { value: 'first_two', label: 'Premier + Deuxième mots' },
  { value: 'last_two', label: 'Deuxième + Troisième mots' },
  { value: 'all_words', label: 'Tous les mots' },
  { value: 'custom', label: 'Personnalisé (saisie libre)' }
]

const formatDescriptions: Record<string, string> = {
  first_word: 'Ex: "Rakoto" pour "Jean Rakoto"',
  second_word: 'Ex: "Jean" pour "Jean Rakoto"',
  third_word: 'Ex: "Luc" pour "Jean Luc Rakoto"',
  first_two: 'Ex: "Jean Rakoto" pour "Jean Luc Rakoto"',
  last_two: 'Ex: "Luc Rakoto" pour "Jean Luc Rakoto"',
  all_words: 'Ex: "Jean Luc Rakoto"',
  custom: 'Vous choisissez librement votre pseudo'
}

// Computed
const displayName = computed(() => {
  if (!user.value) return '-'
  return user.value.display_name || user.value.full_name || user.value.username
})

const formatLabel = computed(() => {
  if (!user.value?.pseudo_format) return 'Premier mot'
  const option = formatOptions.find(o => o.value === user.value?.pseudo_format)
  return option?.label || 'Personnalisé'
})

const roleLabel = computed(() => {
  if (!user.value) return 'Utilisateur'
  if (user.value.is_superuser) return 'Super Administrateur'
  if (user.value.is_staff) return 'Administrateur'
  if (user.value.est_chef_equipe || user.value.est_co_manager) return 'Chef d\'équipe'
  return 'Utilisateur'
})

const roleClass = computed(() => {
  if (!user.value) return 'role-user'
  if (user.value.is_superuser) return 'role-super-admin'
  if (user.value.is_staff) return 'role-admin'
  if (user.value.est_chef_equipe || user.value.est_co_manager) return 'role-manager'
  return 'role-user'
})

const hasChanges = computed(() => {
  if (!user.value) return false
  return pseudoForm.pseudo_format !== user.value.pseudo_format ||
    (pseudoForm.pseudo_format === 'custom' && pseudoForm.pseudo !== user.value.pseudo)
})

const previewDisplayName = computed(() => {
  if (pseudoForm.pseudo_format === 'custom' && pseudoForm.pseudo) {
    return pseudoForm.pseudo
  }
  
  // Simulation du calcul côté serveur
  const fullName = user.value?.full_name || ''
  const words = fullName.split(/\s+/).filter(w => w)
  
  switch (pseudoForm.pseudo_format) {
    case 'first_word': return words[0] || '-'
    case 'second_word': return words[1] || words[0] || '-'
    case 'third_word': return words[2] || words[1] || words[0] || '-'
    case 'first_two': return words.slice(0, 2).join(' ') || '-'
    case 'last_two': return words.slice(-2).join(' ') || '-'
    case 'all_words': return fullName || '-'
    default: return '-'
  }
})

// Méthodes
const loadProfile = async () => {
  loading.value = true
  
  try {
    const userData = await usersApi.getUserProfile()
    user.value = userData
    console.log('Profil chargé:', userData)
  } catch (err: any) {
    console.error('Erreur API:', err)
    showNotification('Erreur lors du chargement du profil', 'error')
    
    if (authUser.value) {
      user.value = authUser.value
    }
  } finally {
    loading.value = false
  }
}

const startEditPseudo = () => {
  if (!user.value) return
  
  pseudoForm.pseudo_format = user.value.pseudo_format || 'first_word'
  pseudoForm.pseudo = user.value.pseudo || ''
  errors.pseudo = ''
  isEditingPseudo.value = true
}

const cancelEdit = () => {
  isEditingPseudo.value = false
  errors.pseudo = ''
}

const onFormatChange = () => {
  if (pseudoForm.pseudo_format !== 'custom') {
    pseudoForm.pseudo = ''
    errors.pseudo = ''
  }
}

const getFormatDescription = (format: string): string => {
  return formatDescriptions[format] || ''
}

const validateForm = (): boolean => {
  errors.pseudo = ''
  
  if (pseudoForm.pseudo_format === 'custom') {
    const pseudo = pseudoForm.pseudo.trim()
    if (!pseudo) {
      errors.pseudo = 'Le pseudo personnalisé est requis'
      return false
    }
    if (pseudo.length > 100) {
      errors.pseudo = 'Maximum 100 caractères'
      return false
    }
  }
  
  return true
}

const savePseudo = async () => {
  if (!validateForm() || !user.value) return
  
  saving.value = true
  
  try {
    const data: UpdatePseudoData = pseudoForm.pseudo_format === 'custom' 
      ? { pseudo: pseudoForm.pseudo.trim() }
      : { pseudo_format: pseudoForm.pseudo_format }
    
    const response = await usersApi.updatePseudo(data)
    
    // Mettre à jour l'utilisateur local
    user.value.pseudo_format = response.pseudo_format
    user.value.pseudo = response.pseudo
    user.value.display_name = response.display_name
    
    // Rafraîchir le store auth
    await checkAuth()
    
    showNotification('Pseudo mis à jour avec succès !', 'success')
    isEditingPseudo.value = false
  } catch (err: any) {
    console.error('Erreur sauvegarde:', err)
    const message = err.response?.data?.error || 'Erreur lors de la mise à jour'
    showNotification(message, 'error')
  } finally {
    saving.value = false
  }
}

const showNotification = (message: string, type: 'success' | 'error') => {
  notification.message = message
  notification.type = type
  notification.show = true
  setTimeout(() => notification.show = false, 3000)
}

const getInitials = (user: User): string => {
  if (user.pseudo) return user.pseudo.charAt(0).toUpperCase()
  if (user.first_name && user.last_name) {
    return (user.first_name.charAt(0) + user.last_name.charAt(0)).toUpperCase()
  }
  return user.username?.charAt(0)?.toUpperCase() || 'U'
}

const formatDate = (dateString: string | null): string => {
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

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile {
  max-width: 900px;
  margin: 0 auto;
  padding: 2rem;
}

.profileh1 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.profileh1::before {
  content: '👤';
  font-size: 1.5rem;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  color: var(--text-secondary);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.profile-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card {
  background: var(--card-bg, white);
  border-radius: 16px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 2rem;
  background: linear-gradient(135deg, var(--primary-light, #f0f9ff) 0%, var(--card-bg, white) 100%);
  border-bottom: 1px solid var(--border-color, #e5e7eb);
}

.avatar {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color, #3b82f6) 0%, var(--primary-dark, #1d4ed8) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.avatar.has-pseudo {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.pseudo-badge {
  position: absolute;
  bottom: -4px;
  right: -4px;
  width: 28px;
  height: 28px;
  background: #f59e0b;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  border: 3px solid white;
}

.profile-info {
  flex: 1;
}

.profile-info h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary, #1f2937);
  margin-bottom: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.matricule {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
  font-family: monospace;
}

.email {
  color: var(--text-secondary, #6b7280);
  margin-bottom: 0.5rem;
}

.role-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.role-super-admin {
  background: #fef2f2;
  color: #dc2626;
}

.role-admin {
  background: #eff6ff;
  color: #2563eb;
}

.role-manager {
  background: #fff7ed;
  color: #ea580c;
}

.role-user {
  background: #f0fdf4;
  color: #16a34a;
}

/* Section Pseudo */
.pseudo-section {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid var(--border-color, #e5e7eb);
  background: var(--bg-secondary, #f9fafb);
  transition: all 0.3s ease;
}

.pseudo-section.editing {
  background: white;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-edit {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit:hover {
  border-color: var(--primary-color, #3b82f6);
  color: var(--primary-color, #3b82f6);
  background: var(--primary-light, #eff6ff);
}

.pseudo-display {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.pseudo-preview {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.current-pseudo {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--primary-color, #3b82f6);
}

.format-badge {
  padding: 0.25rem 0.625rem;
  background: var(--bg-tertiary, #e5e7eb);
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--text-secondary, #6b7280);
}

.pseudo-hint {
  font-size: 0.875rem;
  color: var(--text-secondary, #6b7280);
}

/* Formulaire d'édition */
.pseudo-edit {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary, #374151);
}

.form-select,
.form-input {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  font-size: 0.9375rem;
  background: white;
  transition: all 0.2s;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: var(--primary-color, #3b82f6);
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #ef4444;
  background: #fef2f2;
}

.help-text {
  font-size: 0.8125rem;
  color: var(--text-secondary, #6b7280);
}

.error-text {
  font-size: 0.8125rem;
  color: #dc2626;
}

.preview-box {
  padding: 1rem;
  background: var(--bg-secondary, #f3f4f6);
  border-radius: 8px;
  border: 2px dashed var(--border-color, #d1d5db);
}

.preview-box label {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary, #6b7280);
  margin-bottom: 0.5rem;
  display: block;
}

.preview-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--primary-color, #3b82f6);
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background: var(--primary-color, #3b82f6);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-dark, #2563eb);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.btn-secondary {
  background: white;
  color: var(--text-secondary, #6b7280);
  border: 1px solid var(--border-color, #d1d5db);
}

.btn-secondary:hover:not(:disabled) {
  background: var(--bg-secondary, #f3f4f6);
  border-color: var(--text-secondary, #9ca3af);
}

.btn-primary:disabled,
.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Détails du profil */
.profile-details {
  padding: 1.5rem 2rem;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section:last-child {
  margin-bottom: 0;
}

.detail-section h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--text-primary, #1f2937);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid var(--border-color, #e5e7eb);
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1.25rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.detail-item.highlight {
  background: var(--bg-secondary, #f9fafb);
  padding: 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--border-color, #e5e7eb);
}

.detail-item label {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--text-secondary, #6b7280);
  text-transform: uppercase;
  letter-spacing: 0.025em;
  display: flex;
  align-items: center;
  gap: 0.375rem;
}

.detail-item .value {
  font-size: 0.9375rem;
  color: var(--text-primary, #1f2937);
  font-weight: 500;
}

.tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  background: var(--primary-light, #dbeafe);
  color: var(--primary-dark, #1e40af);
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
}

.tag.empty {
  background: var(--bg-tertiary, #e5e7eb);
  color: var(--text-secondary, #9ca3af);
}

.role-mini {
  font-size: 0.75rem;
  padding: 0.125rem 0.375rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 4px;
}

/* Équipes gérées */
.managed-teams {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.team-card {
  display: flex;
  flex-direction: column;
  padding: 0.875rem 1rem;
  background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
  border: 1px solid #fed7aa;
  border-radius: 10px;
  min-width: 160px;
}

.team-name {
  font-weight: 600;
  color: #9a3412;
  font-size: 0.9375rem;
}

.team-count {
  font-size: 0.8125rem;
  color: #c2410c;
  margin-top: 0.25rem;
}

/* État d'erreur */
.error-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 3rem;
  text-align: center;
  color: var(--text-secondary, #6b7280);
}

.error-state i {
  font-size: 3rem;
  color: #f59e0b;
}

.btn-retry {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: white;
  border: 1px solid var(--border-color, #d1d5db);
  border-radius: 8px;
  font-weight: 500;
  color: var(--text-primary, #374151);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-retry:hover {
  border-color: var(--primary-color, #3b82f6);
  color: var(--primary-color, #3b82f6);
  background: var(--primary-light, #eff6ff);
}

/* Toast notification */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-radius: 10px;
  font-weight: 500;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.3s ease;
  z-index: 1000;
}

.toast.success {
  background: #dcfce7;
  color: #166534;
  border: 1px solid #86efac;
}

.toast.error {
  background: #fee2e2;
  color: #991b1b;
  border: 1px solid #fca5a5;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Responsive */
@media (max-width: 768px) {
  .profile {
    padding: 1rem;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .btn-primary,
  .btn-secondary {
    justify-content: center;
  }
}
</style>