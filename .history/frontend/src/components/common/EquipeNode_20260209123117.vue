<template>
  <div class="equipe-node" :style="{ marginLeft: `${niveau * 2}rem` }">
    <div 
      class="node-content" 
      :class="{ 'selected': isSelected, 'inactive': !equipe.est_actif }"
      @click="$emit('select', equipe)"
    >
      <button 
        v-if="hasChildren" 
        class="expand-btn"
        @click.stop="toggleExpanded"
      >
        <i class="bi" :class="expanded ? 'bi-chevron-down' : 'bi-chevron-right'"></i>
      </button>
      <span v-else class="expand-placeholder"></span>
      
      <div class="equipe-info">
        <span class="equipe-name">{{ equipe.nom }}</span>
        <span v-if="equipe.pole_details" class="pole-info">
          {{ equipe.pole_details.nom }}
          <span v-if="equipe.manager_details" class="separator">|</span>
        </span>
      </div>
      
      <!-- Manager info -->
      <div v-if="equipe.manager_details" class="manager-info">
        <span class="manager-label">Manager:</span>
        <span class="manager-name">{{ generatePseudo(equipe.manager_details.last_name, equipe.manager_details.pseudo) }}</span>
        <span class="manager-matricule">{{ equipe.manager_details.username.toUpperCase() }}</span>
      </div>
      <div v-else class="manager-info">
        <span class="manager-label">Manager:</span>
        <span class="manager-name">Non assigné</span>
      </div>
      
      <!-- Bouton membres avec double-clic -->
      <button 
        class="membres-btn" 
        @dblclick.stop="toggleMembres"
        @click.stop="handleMembreClick"
        :title="`${equipe.membres_count || 0} membre(s) - Double-clic pour ${showMembres ? 'masquer' : 'afficher'}`"
        :class="{ 'active': showMembres }"
      >
        <i class="bi bi-people"></i>
        <span class="membres-count">{{ equipe.membres_count || 0 }}</span>
      </button>
      
      <div class="actions">
        <!-- Bouton Crayon pour modifier -->
        <button 
          class="btn-edit" 
          @click.stop="openEditModal"
          title="Modifier l'équipe"
        >
          <i class="bi bi-pencil"></i>
        </button>
        
        <button 
          class="btn-status" 
          @click.stop="$emit('toggle', equipe)"
          :title="equipe.est_actif ? 'Désactiver' : 'Activer'"
          :class="{ 'active': equipe.est_actif, 'inactive': !equipe.est_actif }"
        >
          <i class="bi" :class="equipe.est_actif ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
          <span class="status-text">{{ equipe.est_actif ? 'Active' : 'Inactive' }}</span>
        </button>
      </div>
    </div>
    
    <!-- Liste des membres (s'affiche sous l'équipe) -->
    <div v-if="showMembres" class="membres-section">
      <div class="membres-header">
        <h4>Membres ({{ membres.length }})</h4>
        <div class="header-actions">
          <button class="btn-refresh" @click="refreshMembres" title="Actualiser">
            <i class="bi bi-arrow-clockwise"></i>
          </button>
          <button class="close-btn" @click="closeMembres" title="Fermer">
            <i class="bi bi-x"></i>
          </button>
        </div>
      </div>
      
      <div v-if="loadingMembres" class="loading-membres">
        <i class="bi bi-arrow-repeat spin"></i> Chargement...
      </div>
      
      <div v-else-if="membres.length > 0" class="membres-grid">
        <div 
          v-for="membre in membres" 
          :key="membre.id" 
          class="membre-item"
          :class="{ 'is-manager': membre.id === equipe.manager }"
          :title="`${membre.first_name} ${membre.last_name} (${membre.username.toUpperCase()})`"
        >
          <div class="membre-avatar" :class="{ 'manager': membre.id === equipe.manager }">
            <i class="bi" :class="membre.id === equipe.manager ? 'bi-person-badge' : 'bi-person-circle'"></i>
          </div>
          <div class="membre-info">
            <div class="membre-name-row">
              <span class="membre-name">{{ generatePseudo(membre.last_name, membre.pseudo) }}</span>
              <span v-if="membre.id === equipe.manager" class="manager-badge">👑 Manager</span>
            </div>
            <span class="membre-matricule">{{ membre.username.toUpperCase() }}</span>
          </div>
          <div class="membre-actions">
            <button 
              v-if="membre.id !== equipe.manager"
              class="btn-action set-manager"
              @click="setAsManager(membre)"
              title="Définir comme manager"
            >
              <i class="bi bi-person-up"></i>
            </button>
            <button 
              class="btn-action remove"
              @click="removeMembre(membre)"
              title="Retirer de l'équipe"
            >
              <i class="bi bi-person-x"></i>
            </button>
            <button 
              class="btn-action transfer"
              @click="transferMembre(membre)"
              title="Transférer vers une autre équipe"
            >
              <i class="bi bi-arrow-right-circle"></i>
            </button>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-membres">
        <i class="bi bi-people"></i>
        <p>Aucun membre dans cette équipe</p>
      </div>
      
      <div class="add-membre-section">
        <button class="btn-add-membre" @click="openAddMembreModal">
          <i class="bi bi-person-plus"></i>
          Ajouter un membre
        </button>
        <button class="btn-add-sous-equipe" @click="openCreateSousEquipeModal">
          <i class="bi bi-diagram-3"></i>
          Créer sous-équipe
        </button>
      </div>
    </div>
    
    <!-- MODAL ÉDITION ÉQUIPE -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal modal-large">
        <h3>Modifier l'équipe : {{ equipe.nom }}</h3>
        
        <div class="form-group">
          <label>Nom de l'équipe *</label>
          <input v-model="editForm.nom" type="text" required maxlength="100" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </div>
        
        <div class="form-group">
          <label>Manager</label>
          <select v-model="editForm.manager">
            <option :value="null">Aucun manager</option>
            <option v-for="membre in membres" :key="membre.id" :value="membre.id">
              {{ generatePseudo(membre.last_name, membre.pseudo) }} ({{ membre.username.toUpperCase() }})
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeEditModal">Annuler</button>
          <button class="btn-danger" @click="deleteEquipe" v-if="niveau === 0">
            <i class="bi bi-trash"></i> Supprimer
          </button>
          <button class="btn-primary" @click="saveEquipe" :disabled="saving">
            {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- MODAL AJOUT MEMBRE -->
    <div v-if="showAddMembreModal" class="modal-overlay" @click.self="closeAddMembreModal">
      <div class="modal modal-large">
        <h3>Ajouter un membre à : {{ equipe.nom }}</h3>
        
        <div class="form-group">
          <label>Sélectionner un utilisateur *</label>
          <select v-model="newMembreId" class="user-select">
            <option :value="null">Choisir un utilisateur</option>
            <option 
              v-for="user in usersAvailable" 
              :key="user.id" 
              :value="user.id"
            >
              {{ generatePseudo(user.last_name, user.pseudo) }} ({{ user.username.toUpperCase() }}) - {{ user.pole_details?.nom || 'Sans pôle' }}
            </option>
          </select>
        </div>
        
        <div class="user-details" v-if="selectedUser">
          <h4>Informations de l'utilisateur :</h4>
          <div class="details-grid">
            <div class="detail-item">
              <label>Matricule :</label>
              <span>{{ selectedUser.username.toUpperCase() }}</span>
            </div>
            <div class="detail-item">
              <label>Nom complet :</label>
              <span>{{ selectedUser.first_name }} {{ selectedUser.last_name }}</span>
            </div>
            <div class="detail-item">
              <label>Pseudo :</label>
              <span>{{ selectedUser.pseudo || 'Aucun' }}</span>
            </div>
            <div class="detail-item">
              <label>Pôle actuel :</label>
              <span>{{ selectedUser.pole_details?.nom || 'Non assigné' }}</span>
            </div>
            <div class="detail-item">
              <label>Équipe actuelle :</label>
              <span>{{ selectedUser.equipe_details?.nom || 'Aucune' }}</span>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeAddMembreModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="addMembre" 
            :disabled="!newMembreId || addingMembre"
          >
            {{ addingMembre ? 'Ajout...' : 'Ajouter le membre' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- MODAL CRÉATION SOUS-ÉQUIPE -->
    <div v-if="showCreateSousEquipeModal" class="modal-overlay" @click.self="closeCreateSousEquipeModal">
      <div class="modal">
        <h3>Créer une sous-équipe pour : {{ equipe.nom }}</h3>
        
        <div class="form-group">
          <label>Nom de la sous-équipe *</label>
          <input v-model="sousEquipeForm.nom" type="text" required maxlength="100" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="sousEquipeForm.description" rows="2"></textarea>
        </div>
        
        <div class="form-group">
          <label>Manager (optionnel)</label>
          <select v-model="sousEquipeForm.manager">
            <option :value="null">Aucun manager</option>
            <option 
              v-for="membre in membres" 
              :key="membre.id" 
              :value="membre.id"
            >
              {{ generatePseudo(membre.last_name, membre.pseudo) }} ({{ membre.username.toUpperCase() }})
            </option>
          </select>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeCreateSousEquipeModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="createSousEquipe" 
            :disabled="!sousEquipeForm.nom || creatingSousEquipe"
          >
            {{ creatingSousEquipe ? 'Création...' : 'Créer la sous-équipe' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- MODAL TRANSFERT MEMBRE -->
    <div v-if="showTransferModal && membreToTransfer" class="modal-overlay" @click.self="closeTransferModal">
      <div class="modal">
        <h3>Transférer : {{ generatePseudo(membreToTransfer.last_name, membreToTransfer.pseudo) }}</h3>
        
        <div class="form-group">
          <label>Destination *</label>
          <select v-model="transferToEquipeId" class="equipe-select">
            <option :value="null">Choisir une équipe</option>
            <option 
              v-for="eq in equipesAvailableForTransfer" 
              :key="eq.id" 
              :value="eq.id"
              :disabled="eq.id === equipe.id"
            >
              {{ eq.nom }} ({{ eq.pole_details?.nom || 'Sans pôle' }})
            </option>
          </select>
        </div>
        
        <div class="warning-box" v-if="transferToEquipeId === equipe.id">
          <i class="bi bi-exclamation-triangle"></i>
          <span>L'utilisateur est déjà dans cette équipe</span>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeTransferModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="confirmTransfer" 
            :disabled="!transferToEquipeId || transferring"
          >
            {{ transferring ? 'Transfert...' : 'Transférer' }}
          </button>
        </div>
      </div>
    </div>
    
    <div v-if="expanded && hasChildren" class="children">
      <EquipeNode
        v-for="child in equipe.sous_equipes"
        :key="child.id"
        :equipe="child"
        :niveau="niveau + 1"
        :selected-id="selectedId"
        @select="$emit('select', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useDisplayName } from '@/composables/useDisplayName'
import { equipesApi } from '@/api/equipes'
import { usersApi } from '@/api/users'
import type { Equipe, User } from '@/types/user'

const props = defineProps<{
  equipe: Equipe
  niveau: number
  selectedId?: number
}>()

const emit = defineEmits<{
  select: [equipe: Equipe]
  toggle: [equipe: Equipe]
}>()

const expanded = ref(true)
const showMembres = ref(false)
const loadingMembres = ref(false)
const membres = ref<User[]>([])
const { generatePseudo } = useDisplayName()

// États pour les modals
const showEditModal = ref(false)
const showAddMembreModal = ref(false)
const showCreateSousEquipeModal = ref(false)
const showTransferModal = ref(false)

// Formulaires
const editForm = ref({
  nom: '',
  description: '',
  manager: null as number | null
})

const sousEquipeForm = ref({
  nom: '',
  description: '',
  manager: null as number | null
})

// Données pour les modals
const newMembreId = ref<number | null>(null)
const membreToTransfer = ref<User | null>(null)
const transferToEquipeId = ref<number | null>(null)
const allUsers = ref<User[]>([])
const allEquipes = ref<Equipe[]>([])

// États de chargement
const saving = ref(false)
const addingMembre = ref(false)
const creatingSousEquipe = ref(false)
const transferring = ref(false)

// Gestion du localStorage pour persister l'état
const STORAGE_KEY = 'equipe_membres_open'

const hasChildren = computed(() => 
  props.equipe.sous_equipes && props.equipe.sous_equipes.length > 0
)

const isSelected = computed(() => props.selectedId === props.equipe.id)

// Utilisateurs disponibles (même pôle, pas dans l'équipe)
const usersAvailable = computed(() => {
  const currentMembreIds = new Set(membres.value.map(m => m.id))
  return allUsers.value.filter(user => {
    // Même pôle que l'équipe
    if (user.pole !== props.equipe.pole) return false
    
    // Pas déjà dans l'équipe
    if (currentMembreIds.has(user.id)) return false
    
    // Utilisateur actif
    return user.is_active !== false
  })
})

// Équipes disponibles pour transfert (même pôle, différentes de l'équipe actuelle)
const equipesAvailableForTransfer = computed(() => {
  return allEquipes.value.filter(eq => {
    // Même pôle
    if (eq.pole !== props.equipe.pole) return false
    
    // Équipe active
    if (!eq.est_actif) return false
    
    return true
  })
})

// Utilisateur sélectionné dans le modal d'ajout
const selectedUser = computed(() => {
  if (!newMembreId.value) return null
  return allUsers.value.find(u => u.id === newMembreId.value)
})

// Charger l'état depuis le localStorage
onMounted(async () => {
  await loadInitialData()
  
  const savedState = localStorage.getItem(STORAGE_KEY)
  if (savedState) {
    try {
      const state = JSON.parse(savedState)
      if (state[props.equipe.id]) {
        showMembres.value = state[props.equipe.id]
        if (showMembres.value) {
          await loadMembres()
        }
      }
    } catch (e) {
      console.error('Erreur de lecture du localStorage:', e)
    }
  }
})

// Charger les données initiales
const loadInitialData = async () => {
  try {
    // Charger tous les utilisateurs
    const usersResponse = await usersApi.getAll()
    allUsers.value = usersResponse
    
    // Charger toutes les équipes
    const equipesResponse = await equipesApi.getAll()
    allEquipes.value = equipesResponse
  } catch (error) {
    console.error('Erreur chargement données initiales:', error)
  }
}

// Sauvegarder l'état dans le localStorage
const saveState = () => {
  try {
    const savedState = localStorage.getItem(STORAGE_KEY)
    const state = savedState ? JSON.parse(savedState) : {}
    state[props.equipe.id] = showMembres.value
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
  } catch (e) {
    console.error('Erreur de sauvegarde du localStorage:', e)
  }
}

// Charger les membres
const loadMembres = async () => {
  if (loadingMembres.value || membres.value.length > 0) return
  
  loadingMembres.value = true
  try {
    const response = await equipesApi.getMembres(props.equipe.id)
    membres.value = response
  } catch (error) {
    console.error('Erreur chargement membres:', error)
  } finally {
    loadingMembres.value = false
  }
}

// Actualiser les membres
const refreshMembres = async () => {
  membres.value = []
  await loadMembres()
}

// Gestion du double-clic
const toggleMembres = async () => {
  showMembres.value = !showMembres.value
  
  if (showMembres.value && membres.value.length === 0) {
    await loadMembres()
  }
  
  saveState()
}

const closeMembres = () => {
  showMembres.value = false
  saveState()
}

const handleMembreClick = (event: MouseEvent) => {
  event.preventDefault()
}

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

// MODAL ÉDITION
const openEditModal = () => {
  editForm.value = {
    nom: props.equipe.nom,
    description: props.equipe.description || '',
    manager: props.equipe.manager
  }
  showEditModal.value = true
  
  // Charger les membres si pas encore fait
  if (membres.value.length === 0) {
    loadMembres()
  }
}

const closeEditModal = () => {
  showEditModal.value = false
}

const saveEquipe = async () => {
  if (!editForm.value.nom) return
  
  saving.value = true
  try {
    await equipesApi.update(props.equipe.id, {
      nom: editForm.value.nom,
      description: editForm.value.description,
      manager: editForm.value.manager
    })
    
    // Émettre un événement pour rafraîchir l'arbre
    emit('toggle', props.equipe) // Réutilise l'événement toggle pour rafraîchir
    
    closeEditModal()
  } catch (error) {
    console.error('Erreur modification équipe:', error)
    alert('Erreur lors de la modification')
  } finally {
    saving.value = false
  }
}

const deleteEquipe = async () => {
  if (!confirm(`Supprimer l'équipe "${props.equipe.nom}" ? Cette action est irréversible.`)) return
  
  try {
    await equipesApi.delete(props.equipe.id)
    emit('toggle', props.equipe) // Rafraîchir l'arbre
    closeEditModal()
  } catch (error) {
    console.error('Erreur suppression équipe:', error)
    alert('Erreur lors de la suppression')
  }
}

// GESTION MEMBRES
const openAddMembreModal = async () => {
  if (allUsers.value.length === 0) {
    await loadInitialData()
  }
  showAddMembreModal.value = true
}

const closeAddMembreModal = () => {
  showAddMembreModal.value = false
  newMembreId.value = null
}

const addMembre = async () => {
  if (!newMembreId.value) return
  
  addingMembre.value = true
  try {
    // Mettre à jour l'utilisateur pour l'ajouter à l'équipe
    await usersApi.update(newMembreId.value, { equipe: props.equipe.id })
    
    // Rafraîchir la liste des membres
    await refreshMembres()
    
    // Rafraîchir la liste des utilisateurs
    await loadInitialData()
    
    closeAddMembreModal()
  } catch (error) {
    console.error('Erreur ajout membre:', error)
    alert('Erreur lors de l\'ajout du membre')
  } finally {
    addingMembre.value = false
  }
}

const removeMembre = async (membre: User) => {
  if (!confirm(`Retirer ${generatePseudo(membre.last_name, membre.pseudo)} de l'équipe ?`)) return
  
  try {
    // Si c'est le manager, retirer aussi le rôle de manager
    if (membre.id === props.equipe.manager) {
      await equipesApi.update(props.equipe.id, { manager: null })
    }
    
    // Retirer de l'équipe
    await usersApi.update(membre.id, { equipe: null })
    
    // Rafraîchir
    await refreshMembres()
    await loadInitialData()
    
    // Émettre un événement pour rafraîchir l'arbre
    emit('toggle', props.equipe)
  } catch (error) {
    console.error('Erreur retrait membre:', error)
    alert('Erreur lors du retrait du membre')
  }
}

const setAsManager = async (membre: User) => {
  if (!confirm(`Définir ${generatePseudo(membre.last_name, membre.pseudo)} comme manager de l'équipe ?`)) return
  
  try {
    await equipesApi.update(props.equipe.id, { manager: membre.id })
    
    // Rafraîchir l'arbre
    emit('toggle', props.equipe)
    
    // Rafraîchir les membres
    await refreshMembres()
  } catch (error) {
    console.error('Erreur définition manager:', error)
    alert('Erreur lors de la définition du manager')
  }
}

// TRANSFERT
const transferMembre = (membre: User) => {
  membreToTransfer.value = membre
  showTransferModal.value = true
}

const closeTransferModal = () => {
  showTransferModal.value = false
  membreToTransfer.value = null
  transferToEquipeId.value = null
}

const confirmTransfer = async () => {
  if (!membreToTransfer.value || !transferToEquipeId.value) return
  
  transferring.value = true
  try {
    // Transférer vers la nouvelle équipe
    await usersApi.update(membreToTransfer.value.id, { equipe: transferToEquipeId.value })
    
    // Si c'était le manager, retirer le rôle
    if (membreToTransfer.value.id === props.equipe.manager) {
      await equipesApi.update(props.equipe.id, { manager: null })
    }
    
    // Rafraîchir
    await refreshMembres()
    await loadInitialData()
    
    // Rafraîchir l'arbre
    emit('toggle', props.equipe)
    
    closeTransferModal()
  } catch (error) {
    console.error('Erreur transfert:', error)
    alert('Erreur lors du transfert')
  } finally {
    transferring.value = false
  }
}

// CRÉATION SOUS-ÉQUIPE
const openCreateSousEquipeModal = () => {
  sousEquipeForm.value = {
    nom: '',
    description: '',
    manager: null
  }
  showCreateSousEquipeModal.value = true
}

const closeCreateSousEquipeModal = () => {
  showCreateSousEquipeModal.value = false
}

const createSousEquipe = async () => {
  if (!sousEquipeForm.value.nom) return
  
  creatingSousEquipe.value = true
  try {
    await equipesApi.create({
      nom: sousEquipeForm.value.nom,
      description: sousEquipeForm.value.description,
      pole: props.equipe.pole,
      equipe_parente: props.equipe.id,
      manager: sousEquipeForm.value.manager,
      est_actif: true
    })
    
    // Rafraîchir l'arbre
    emit('toggle', props.equipe)
    
    closeCreateSousEquipeModal()
  } catch (error) {
    console.error('Erreur création sous-équipe:', error)
    alert('Erreur lors de la création')
  } finally {
    creatingSousEquipe.value = false
  }
}

// Observer les changements d'équipe
watch(() => props.equipe.id, () => {
  showMembres.value = false
  membres.value = []
})
</script>

<style scoped>
/* Styles existants... */

.membres-btn.active {
  background: #27ae60;
  color: white;
}

.membres-section {
  margin: 0.5rem 0 0.5rem 2rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.membres-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.membres-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-refresh {
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #495057;
}

.membre-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.membre-item:hover {
  background: #e9ecef;
  border-color: #dee2e6;
}

.membre-item.is-manager {
  background: #fff8e1;
  border-color: #ffd54f;
}

.membre-avatar {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #3498db;
  color: white;
  border-radius: 50%;
  font-size: 1.2rem;
}

.membre-avatar.manager {
  background: #f39c12;
}

.membre-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.membre-name-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.15rem;
}

.membre-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.85rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.manager-badge {
  font-size: 0.7rem;
  background: #f39c12;
  color: white;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
}

.membre-matricule {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 600;
}

.membre-actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.membre-item:hover .membre-actions {
  opacity: 1;
}

.btn-action {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-action.set-manager {
  background: #e8f4fc;
  color: #3498db;
}

.btn-action.set-manager:hover {
  background: #d4e6f1;
}

.btn-action.remove {
  background: #fce8e8;
  color: #e74c3c;
}

.btn-action.remove:hover {
  background: #f5c6cb;
}

.btn-action.transfer {
  background: #f0f9f0;
  color: #27ae60;
}

.btn-action.transfer:hover {
  background: #d4efdf;
}

.add-membre-section {
  display: flex;
  gap: 0.75rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
}

.btn-add-membre,
.btn-add-sous-equipe {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-add-membre {
  background: #e8f4fc;
  color: #3498db;
}

.btn-add-membre:hover {
  background: #d4e6f1;
}

.btn-add-sous-equipe {
  background: #f0f9f0;
  color: #27ae60;
}

.btn-add-sous-equipe:hover {
  background: #d4efdf;
}

.btn-edit {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  background: #f8f9fa;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.btn-edit:hover {
  background: #e9ecef;
  color: #495057;
}

/* Modals améliorés */
.modal {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
}

.modal.modal-large {
  max-width: 800px;
}

.user-details {
  margin: 1.5rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.75rem;
  margin-top: 0.75rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
}

.detail-item label {
  font-size: 0.8rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.detail-item span {
  font-weight: 500;
  color: #2c3e50;
}

.warning-box {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 6px;
  color: #856404;
  margin: 1rem 0;
}

.warning-box i {
  font-size: 1.2rem;
}

.btn-danger {
  padding: 0.6rem 1.2rem;
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-danger:hover {
  background: #c0392b;
}

/* Sélecteurs améliorés */
.user-select,
.equipe-select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.9rem;
  background: white;
}

.user-select:focus,
.equipe-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

/* Responsive */
@media (max-width: 768px) {
  .membre-item {
    flex-wrap: wrap;
  }
  
  .membre-actions {
    opacity: 1;
    width: 100%;
    justify-content: flex-end;
    margin-top: 0.5rem;
  }
  
  .add-membre-section {
    flex-direction: column;
  }
  
  .modal {
    padding: 1rem;
    margin: 0.5rem;
  }
}
</style>