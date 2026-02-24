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
      
      <span class="equipe-name">{{ equipe.nom }} {{ equipe.pole_details }}</span>
      
      <span v-if="equipe.manager_details" class="manager-badge">
        👤 {{ equipe.manager_details.display_name }}
      </span>
      
      <span class="membres-badge">
        {{ equipe.membres_count || 0 }} membre(s)
      </span>
      
      <div class="actions">
        <button class="btn-icon" @click.stop="$emit('edit', equipe)" title="Modifier">
          <i class="bi bi-pencil"></i>
        </button>
        <button 
          class="btn-icon" 
          @click.stop="$emit('toggle', equipe)"
          :title="equipe.est_actif ? 'Désactiver' : 'Activer'"
        >
          <i class="bi" :class="equipe.est_actif ? 'bi-pause' : 'bi-play'"></i>
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
        @edit="$emit('edit', $event)"
        @toggle="$emit('toggle', $event)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Equipe } from '@/types/user'

const props = defineProps<{
  equipe: Equipe
  niveau: number
  selectedId?: number
}>()

defineEmits<{
  select: [equipe: Equipe]
  edit: [equipe: Equipe]
  toggle: [equipe: Equipe]
}>()

const expanded = ref(true)

const hasChildren = computed(() => 
  props.equipe.sous_equipes && props.equipe.sous_equipes.length > 0
)

const isSelected = computed(() => props.selectedId === props.equipe.id)
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
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.node-content:hover {
  background: #f8f9fa;
}

.node-content.selected {
  background: #e8f4fc;
  border: 1px solid #3498db;
}

.node-content.inactive {
  opacity: 0.6;
}

.expand-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
}

.expand-placeholder {
  width: 24px;
}

.equipe-name {
  font-weight: 500;
  color: #2c3e50;
  flex: 1;
}

.manager-badge {
  font-size: 0.85rem;
  color: #6c757d;
  background: #f8f9fa;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.membres-badge {
  font-size: 0.85rem;
  color: #3498db;
  background: #e8f4fc;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
}

.actions {
  display: flex;
  gap: 0.25rem;
  opacity: 0;
  transition: opacity 0.2s;
}

.node-content:hover .actions {
  opacity: 1;
}

.btn-icon {
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon:hover {
  background: #e9ecef;
  color: #2c3e50;
}

.children {
  border-left: 2px solid #e9ecef;
  margin-left: 0.75rem;
  padding-left: 0.5rem;
}
</style>