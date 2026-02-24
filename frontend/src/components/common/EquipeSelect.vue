<template>
  <div class="equipe-select">
    <label v-if="label" class="form-label">{{ label }}</label>
    <select 
      :value="modelValue" 
      @change="emit('update:modelValue', Number(($event.target as HTMLSelectElement).value) || null)"
      class="form-select"
      :disabled="loading || disabled || equipesFiltrees.length === 0"
    >
      <option :value="null">{{ placeholder }}</option>
      <optgroup 
        v-for="groupe in equipesGroupes" 
        :key="groupe.pole || 'sans-pole'"
        :label="groupe.pole || 'Sans pôle'"
      >
        <option 
          v-for="equipe in groupe.equipes" 
          :key="equipe.id" 
          :value="equipe.id"
        >
          {{ equipe.nom }}
          <span v-if="equipe.manager_details">(Manager: {{ equipe.manager_details.display_name }})</span>
        </option>
      </optgroup>
    </select>
    <div v-if="loading" class="loading-indicator">
      <i class="bi bi-arrow-repeat spin"></i>
    </div>
    <div v-if="filtrePole && equipesFiltrees.length === 0 && !loading" class="text-muted small mt-1">
      Aucune équipe dans ce pôle
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
import { useEquipesStore } from '@/store/equipes'

const props = defineProps<{
  modelValue: number | null
  label?: string
  placeholder?: string
  disabled?: boolean
  filtrePole?: number | null
}>()

// Déclaration explicite des emits
const emit = defineEmits<{
  (e: 'update:modelValue', value: number | null): void
}>()

const equipesStore = useEquipesStore()

const loading = computed(() => equipesStore.loading)

const equipesFiltrees = computed(() => {
  let equipes = equipesStore.equipesActives
  
  if (props.filtrePole !== undefined && props.filtrePole !== null) {
    equipes = equipes.filter(e => e.pole === props.filtrePole)
  }
  
  return equipes
})

const equipesGroupes = computed(() => {
  const grouped = new Map<string | null, { pole: string | null, equipes: typeof equipesFiltrees.value }>()
  
  equipesFiltrees.value.forEach(equipe => {
    const poleNom = equipe.pole_details?.nom || 'Sans pôle'
    
    if (!grouped.has(poleNom)) {
      grouped.set(poleNom, { pole: poleNom, equipes: [] })
    }
    grouped.get(poleNom)!.equipes.push(equipe)
  })
  
  return Array.from(grouped.values())
})

onMounted(() => {
  if (equipesStore.equipes.length === 0) {
    equipesStore.fetchEquipes()
  }
})

watch(() => props.filtrePole, () => {
  if (props.modelValue) {
    const equipeExiste = equipesFiltrees.value.some(e => e.id === props.modelValue)
    if (!equipeExiste) {
      emit('update:modelValue', null)
    }
  }
})
</script>

<style scoped>
.equipe-select {
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-select {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background-color: white;
  font-size: 0.9rem;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16'%3e%3cpath fill='none' stroke='%23343a40' stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M2 5l6 6 6-6'/%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 0.75rem center;
  background-size: 16px 12px;
}

.form-select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-select:disabled {
  background-color: #f8f9fa;
  cursor: not-allowed;
}

.loading-indicator {
  position: absolute;
  right: 2.5rem;
  top: 2.25rem;
  color: #6c757d;
}

.text-muted {
  color: #6c757d;
}

.small {
  font-size: 0.875rem;
}

.mt-1 {
  margin-top: 0.25rem;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}
</style>