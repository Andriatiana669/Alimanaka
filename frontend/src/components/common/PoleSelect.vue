<template>
  <div class="pole-select">
    <label v-if="label" class="form-label">{{ label }}</label>
    <select 
      :value="modelValue" 
      @change="$emit('update:modelValue', Number(($event.target as HTMLSelectElement).value) || null)"
      class="form-select"
      :disabled="loading || disabled"
    >
      <option :value="null">{{ placeholder }}</option>
      <option 
        v-for="pole in polesActifs" 
        :key="pole.id" 
        :value="pole.id"
      >
        {{ pole.code }} - {{ pole.nom }}
      </option>
    </select>
    <div v-if="loading" class="loading-indicator">
      <i class="bi bi-arrow-repeat spin"></i>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { usePolesStore } from '@/store/poles'

const props = defineProps<{
  modelValue: number | null
  label?: string
  placeholder?: string
  disabled?: boolean
}>()

defineEmits<{
  'update:modelValue': [value: number | null]
}>()

const polesStore = usePolesStore()

const polesActifs = computed(() => polesStore.polesActifs)
const loading = computed(() => polesStore.loading)

onMounted(() => {
  if (polesStore.poles.length === 0) {
    polesStore.fetchPoles()
  }
})
</script>

<style scoped>
.pole-select {
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

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.spin {
  animation: spin 1s linear infinite;
}
</style>