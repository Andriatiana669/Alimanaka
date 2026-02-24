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
      >
        <i class="bi bi-people"></i>
        <span class="membres-count">{{ equipe.membres_count || 0 }}</span>
      </button>
      
      <div class="actions">
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
    <div v-if="showMembres && membres.length > 0" class="membres-list">
      <div class="membres-list-header">
        <h4>Membres ({{ membres.length }})</h4>
        <button class="close-btn" @click="showMembres = false" title="Fermer">
          <i class="bi bi-x"></i>
        </button>
      </div>
      
      <div class="membres-grid">
        <div 
          v-for="membre in membres" 
          :key="membre.id" 
          class="membre-item"
          :title="`${membre.first_name} ${membre.last_name} (${membre.username.toUpperCase()})`"
        >
          <div class="membre-avatar">
            <i class="bi bi-person-circle"></i>
          </div>
          <div class="membre-info">
            <span class="membre-name">{{ generatePseudo(membre.last_name, membre.pseudo) }}</span>
            <span class="membre-matricule">{{ membre.username.toUpperCase() }}</span>
          </div>
        </div>
      </div>
      
      <div v-if="membres.length === 0" class="empty-membres">
        Aucun membre dans cette équipe
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
import { ref, computed, watch, onMounted } from 'vue'
import { useDisplayName } from '@/composables/useDisplayName'
import type { Equipe, User } from '@/types/user'
import { useEquipesStore } from '@/store/equipes'

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

// Gestion du localStorage pour persister l'état
const STORAGE_KEY = 'equipe_membres_state'

const hasChildren = computed(() => 
  props.equipe.sous_equipes && props.equipe.sous_equipes.length > 0
)

const isSelected = computed(() => props.selectedId === props.equipe.id)

// Charger l'état depuis le localStorage
onMounted(() => {
  const savedState = localStorage.getItem(STORAGE_KEY)
  if (savedState) {
    try {
      const state = JSON.parse(savedState)
      if (state[props.equipe.id]) {
        showMembres.value = state[props.equipe.id]
        if (showMembres.value) {
          loadMembres()
        }
      }
    } catch (e) {
      console.error('Erreur de lecture du localStorage:', e)
    }
  }
})

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

// Charger les membres depuis l'API
const loadMembres = async () => {
  if (membres.value.length > 0) return // Déjà chargés
  
  loadingMembres.value = true
  try {
    // Remplace par ton appel API réel
    // const response = await equipesApi.getMembres(props.equipe.id)
    // membres.value = response
    
    // Pour l'instant, simulation

  } catch (error) {
    console.error('Erreur chargement membres:', error)
  } finally {
    loadingMembres.value = false
  }
}

// Gestion du double-clic sur l'icône personnes
const toggleMembres = async () => {
  showMembres.value = !showMembres.value
  
  if (showMembres.value && membres.value.length === 0) {
    await loadMembres()
  }
  
  saveState()
}

// Gestion du clic simple (optionnel)
const handleMembreClick = (event: MouseEvent) => {
  // Empêche le déclenchement du double-clic
  event.preventDefault()
}

const toggleExpanded = () => {
  expanded.value = !expanded.value
}

// Observer les changements d'équipe
watch(() => props.equipe.id, () => {
  // Réinitialiser l'affichage des membres quand l'équipe change
  showMembres.value = false
  membres.value = []
})

</script>

<style scoped>
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

.expand-btn {
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
}

.expand-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.expand-placeholder {
  width: 28px;
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

.manager-info {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #f8f9fa;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-size: 0.85rem;
  min-width: 0;
  flex-shrink: 1;
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

/* Bouton membres */
.membres-btn {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.6rem;
  border: none;
  border-radius: 6px;
  background: #f0f9f0;
  color: #27ae60;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.membres-btn:hover {
  background: #e1f7e1;
  transform: scale(1.05);
}

.membres-btn:active {
  transform: scale(0.95);
}

.membres-count {
  font-weight: 600;
}

/* Liste des membres */
.membres-list {
  margin: 0.5rem 0 0.5rem 2rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.membres-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e9ecef;
}

.membres-list-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 0.9rem;
}

.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: #f8f9fa;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.close-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.membres-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 0.75rem;
}

.membre-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  transition: all 0.2s;
}

.membre-item:hover {
  background: #e9ecef;
  transform: translateY(-2px);
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

.membre-info {
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.membre-name {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.85rem;
  margin-bottom: 0.15rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.membre-matricule {
  font-family: monospace;
  font-size: 0.75rem;
  color: #6c757d;
  font-weight: 600;
}

.empty-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
  font-style: italic;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-status {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.6rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
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

.children {
  border-left: 2px solid #e9ecef;
  margin-left: 1rem;
  padding-left: 0.75rem;
}

/* Loading */
.loading-membres {
  text-align: center;
  padding: 1rem;
  color: #6c757d;
}

/* Responsive */
@media (max-width: 1024px) {
  .node-content {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .manager-info,
  .membres-btn,
  .btn-status {
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