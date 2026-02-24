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
        @click.stop="expanded = !expanded"
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
      
      <!-- Manager info avec generatePseudo -->
      <div v-if="equipe.manager_details" class="manager-info">
        <span class="manager-label">Manager:</span>
        <span class="manager-name">{{ generatePseudo(equipe.manager_details.last_name, equipe.manager_details.pseudo) }}</span>
        <span class="manager-matricule">{{ equipe.manager_details.username.toUpperCase() }}</span>
      </div>
      <div v-else class="manager-info">
        <span class="manager-label">Manager:</span>
        <span class="manager-name">Non assigné</span>
      </div>
      
      <span class="membres-badge">
        <i class="bi bi-people"></i>
        {{ equipe.membres_count || 0 }}
      </span>
      
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
import { ref, computed } from 'vue'
import { useDisplayName } from '@/composables/useDisplayName'
import type { Equipe } from '@/types/user'

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
const { generatePseudo } = useDisplayName()

const hasChildren = computed(() => 
  props.equipe.sous_equipes && props.equipe.sous_equipes.length > 0
)

const isSelected = computed(() => props.selectedId === props.equipe.id)
</script>

<style scoped>
/* Garde le même CSS que précédemment */
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

.membres-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #27ae60;
  background: #f0f9f0;
  padding: 0.35rem 0.6rem;
  border-radius: 6px;
  font-weight: 500;
  white-space: nowrap;
}

.membres-badge i {
  font-size: 0.8rem;
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

/* Responsive */
@media (max-width: 1024px) {
  .node-content {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .manager-info,
  .membres-badge,
  .btn-status {
    order: 1;
  }
  
  .equipe-info {
    width: 100%;
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
}
</style>