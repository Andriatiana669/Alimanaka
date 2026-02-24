<template>
  <div class="equipe-node" :style="{ marginLeft: `${niveau * 2}rem` }">
    <div 
      class="node-content" 
      :class="{ 'selected': isSelected, 'inactive': !equipe.est_actif }"
      @click="handleSelect"
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
          <span v-if="equipeManagers.length > 0" class="separator">|</span>
        </span>
      </div>
      
      <!-- Affichage des managers -->
      <div v-if="equipeManagers.length > 0" class="managers-container">
        <span class="manager-label">Manager(s):</span>
        <div class="managers-tags">
          <span 
            v-for="manager in equipeManagers" 
            :key="manager.id"
            class="manager-tag"
            :class="{ 'is-main-manager': manager.id === equipe.manager }"
            :title="getMembreFullName(manager)"
          >
            <i class="bi" :class="manager.id === equipe.manager ? 'bi-person-badge-fill' : 'bi-person-badge'"></i>
            {{ generatePseudo(manager.last_name, manager.pseudo) }}
            <small class="manager-matricule">{{ manager.username.toUpperCase() }}</small>
          </span>
        </div>
      </div>
      <div v-else class="managers-container">
        <span class="manager-label">Manager:</span>
        <span class="no-manager">Non assigné</span>
      </div>
      
      <!-- Bouton membres avec double-clic -->
      <button 
        v-if="canSeeMembers"
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
        <!-- Bouton Toggle active/inactive: visible uniquement si super admin OU (admin ET manager) -->
        <button 
          v-if="canToggleStatus"
          class="btn-status" 
          @click.stop="handleToggleStatus"
          :title="equipe.est_actif ? 'Désactiver' : 'Activer'"
          :class="{ 'active': equipe.est_actif, 'inactive': !equipe.est_actif }"
        >
          <i class="bi" :class="equipe.est_actif ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
          <span class="status-text">{{ equipe.est_actif ? 'Active' : 'Inactive' }}</span>
        </button>
      </div>
    </div>
    
    <!-- Liste des membres (s'affiche sous l'équipe) -->
    <div v-if="showMembres && canSeeMembers" class="membres-section">
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
          :class="{ 'is-manager': membre.id === equipe.manager, 'is-co-manager': isCoManager(membre.id) }"
          :title="getMembreFullName(membre)"
        >
          <div class="membre-avatar" :class="{ 'manager': membre.id === equipe.manager, 'co-manager': isCoManager(membre.id) }">
            <i class="bi" :class="membre.id === equipe.manager ? 'bi-person-badge-fill' : isCoManager(membre.id) ? 'bi-person-badge' : 'bi-person-circle'"></i>
          </div>
          <div class="membre-info">
            <div class="membre-name-row">
              <span class="membre-name">{{ generatePseudo(membre.last_name, membre.pseudo) }}</span>
              <span v-if="membre.id === equipe.manager" class="manager-badge">👑</span>
              <span v-else-if="isCoManager(membre.id)" class="co-manager-badge">🛡️</span>
            </div>
            <span class="membre-matricule"> {{ membre.username.toUpperCase() }}</span>
          </div>
        </div>
      </div>
      
      <div v-else class="empty-membres">
        <i class="bi bi-people"></i>
        <p>Aucun membre dans cette équipe</p>
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
        @refresh="$emit('refresh')"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useDisplayName } from '@/composables/useDisplayName'
import { useAuth } from '@/composables/useAuth'
import { equipesApi } from '@/api/equipes'
import { usersApi } from '@/api/users'
import type { Equipe, EquipeMembre, User } from '@/types/user'

const props = defineProps<{
  equipe: Equipe
  niveau: number
  selectedId?: number
}>()

const emit = defineEmits<{
  select: [equipe: Equipe]
  toggle: [equipe: Equipe]
  refresh: []
}>()

const { user: currentUser } = useAuth()
const expanded = ref(true)
const showMembres = ref(false)
const loadingMembres = ref(false)
const membres = ref<EquipeMembre[]>([])
const { generatePseudo } = useDisplayName()

const STORAGE_KEY = 'equipe_membres_open'

const hasChildren = computed(() => 
  props.equipe.sous_equipes && props.equipe.sous_equipes.length > 0
)

const isSelected = computed(() => props.selectedId === props.equipe.id)

const isSuperAdmin = computed(() => currentUser.value?.is_superuser === true)
const isAdmin = computed(() => currentUser.value?.is_staff === true || isSuperAdmin.value)
const isManager = computed(() => props.equipe.manager === currentUser.value?.id)
const isCoManager = computed(() => props.equipe.co_managers?.includes(currentUser.value?.id || 0) || false)

// Conditions d'affichage
const canSeeMembers = computed(() => {
  // Utilisateur normal ne voit que les membres de ses propres équipes
  if (!isAdmin.value) {
    return isManager.value || isCoManager.value
  }
  // Admin voit tout
  return true
})

const canToggleStatus = computed(() => {
  // Super admin peut toujours toggle
  if (isSuperAdmin.value) return true
  
  // Admin ET manager (pas co-manager) peut toggle
  if (isAdmin.value && isManager.value && !isCoManager.value) return true
  
  return false
})

const getMembreDisplayName = (membre: EquipeMembre | User | any) => {
  if (membre.display_name) return membre.display_name
  if (membre.last_name || membre.pseudo) {
    return generatePseudo(membre.last_name, membre.pseudo)
  }
  return membre.username.toUpperCase()
}

const getMembreFullName = (membre: EquipeMembre | any) => {
  if (membre.first_name && membre.last_name) {
    return `${membre.first_name} ${membre.last_name} (${membre.username.toUpperCase()})`
  }
  return membre.username.toUpperCase()
}


const equipeManagers = computed(() => {
  const managers: EquipeMembre[] = []
  
  if (props.equipe.manager_details) {
    const managerDetails = props.equipe.manager_details
    managers.push({
      id: managerDetails.id,
      username: managerDetails.username,
      first_name: managerDetails.first_name || '',
      last_name: managerDetails.last_name || '',
      pseudo: managerDetails.pseudo || null,
      display_name: managerDetails.display_name || '',
      pole_nom: '',
      is_staff: false,
      date_joined: ''
    } as EquipeMembre)
  }
  
  if (props.equipe.co_managers_details && props.equipe.co_managers_details.length > 0) {
    props.equipe.co_managers_details.forEach(coManager => {
      managers.push({
        id: coManager.id,
        username: coManager.username,
        first_name: coManager.first_name || '',
        last_name: coManager.last_name || '',
        pseudo: coManager.pseudo || null,
        display_name: coManager.display_name || '',
        pole_nom: '',
        is_staff: false,
        date_joined: ''
      } as EquipeMembre)
    })
  }
  
  return managers
})

// Charger l'état sauvegardé
onMounted(async () => {
  const savedState = localStorage.getItem(STORAGE_KEY)
  if (savedState) {
    try {
      const state = JSON.parse(savedState)
      if (state[props.equipe.id]) {
        showMembres.value = state[props.equipe.id]
        if (showMembres.value && canSeeMembers.value) {
          await loadMembres()
        }
      }
    } catch (e) {
      console.error('Erreur de lecture du localStorage:', e)
    }
  }
})

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

const loadMembres = async () => {
  if (loadingMembres.value || !canSeeMembers.value) return
  
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

const refreshMembres = async () => {
  membres.value = []
  await loadMembres()
}

const handleSelect = () => {
  emit('select', props.equipe)
}

const handleToggleStatus = (event: MouseEvent) => {
  event.stopPropagation()
  emit('toggle', props.equipe)
}

const toggleMembres = async () => {
  if (!canSeeMembers.value) return
  
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
  event.stopPropagation()
}

const toggleExpanded = (event: MouseEvent) => {
  event.stopPropagation()
  expanded.value = !expanded.value
}

watch(() => props.equipe.id, () => {
  showMembres.value = false
  membres.value = []
})

// Si l'utilisateur n'a plus accès aux membres, fermer la section
watch(canSeeMembers, (newValue) => {
  if (!newValue) {
    showMembres.value = false
  }
})
</script>




<style scoped>
/* Structure et layout */
.equipe-node {
  margin: 0.25rem 0;
}

.node-content {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.node-content:hover {
  background: #f8f9fa;
  border-color: #e9ecef;
}

.node-content.selected {
  background: #e8f4fc;
  border-color: #3498db;
  box-shadow: 0 2px 4px rgba(52, 152, 219, 0.1);
}

.node-content.inactive {
  opacity: 0.6;
  background: #f9f9f9;
}

.equipe-info {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
}

.equipe-name {
  font-weight: 600;
  color: #2c3e50;
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}

.pole-info {
  font-size: 0.8rem;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.separator {
  color: #dee2e6;
  margin: 0 0.25rem;
}

/* Boutons et interactions */
.expand-btn, .btn-refresh, .btn-edit, .close-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-radius: 4px;
  transition: all 0.2s;
}

.expand-btn:hover, .btn-refresh:hover, .btn-edit:hover, .close-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.expand-placeholder {
  width: 28px;
}

.btn-refresh {
  width: 32px;
  height: 32px;
  border: 1px solid #dee2e6;
  background: white;
}

.btn-edit, .close-btn {
  background: #f8f9fa;
}


.manager-info, .membres-btn, .btn-status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 500;
  white-space: nowrap;
  transition: all 0.2s;
}

.manager-info {
  background: #f8f9fa;
}

.manager-label {
  color: #6c757d;
  font-weight: 500;
  white-space: nowrap;
}

.manager-name {
  color: #495057;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.manager-matricule {
  font-family: monospace;
  color: #3498db;
  font-weight: 600;
  font-size: 0.8rem;
  background: #e8f4fc;
  padding: 0.1rem 0.4rem;
  border-radius: 4px;
  white-space: nowrap;
}

.membres-btn {
  background: #f0f9f0;
  color: #27ae60;
  border: none;
  cursor: pointer;
}

.membres-btn:hover {
  background: #e1f7e1;
  transform: scale(1.05);
}

.membres-btn:active {
  transform: scale(0.95);
}

.membres-btn.active {
  background: #27ae60;
  color: white;
}

.membres-count {
  font-weight: 600;
}

.btn-status {
  border: none;
  cursor: pointer;
}

.btn-status.active {
  background: #f0f9f0;
  color: #27ae60;
}

.btn-status.active:hover {
  background: #e1f7e1;
}

.btn-status.inactive {
  background: #f8f9fa;
  color: #6c757d;
}

.btn-status.inactive:hover {
  background: #e9ecef;
}

.status-text {
  font-size: 0.8rem;
}

/* Liste des membres */
.membres-list, .membres-section {
  margin: 0.5rem 0 0.5rem 2rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease-out;
}

.membres-header, .membres-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.membres-header h4, .membres-list-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
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
  transform: translateY(-2px);
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


/* Animations et états */
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

.loading-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
}

.empty-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
  font-style: italic;
}

.children {
  border-left: 2px solid #e9ecef;
  margin-left: 1rem;
  padding-left: 0.75rem;
}

/* Grilles */
.membres-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .node-content {
    flex-wrap: wrap;
    gap: 0.5rem;
  }

  .manager-info, .membres-btn, .btn-status {
    order: 1;
  }

  .equipe-info {
    width: 100%;
  }

  .membres-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}

@media (max-width: 768px) {
  .node-content {
    padding: 0.5rem;
  }

  .manager-info {
    flex-wrap: wrap;
  }

  .status-text {
    display: none;
  }

  .btn-status {
    padding: 0.35rem;
  }

  .membres-list {
    margin-left: 1rem;
    padding: 0.75rem;
  }

  .membres-grid {
    grid-template-columns: 1fr;
  }
}
</style>