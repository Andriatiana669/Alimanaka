<!-- frontend/src/components/conges/ValidationPartielleModal.vue -->
<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>Validation partielle</h3>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <p>TEST - Modal fonctionnel !</p>
        <p>Congé: {{ conge?.id }}</p>
        <p>Jours: {{ joursPeriode.length }}</p>
        
        <div v-for="jour in joursPeriode" :key="jour.date" class="date-item">
          <label>
            <input type="checkbox" v-model="selectedDates" :value="jour.date" />
            {{ formatDate(jour.date) }} ({{ jour.deduction }}j)
          </label>
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn-secondary" @click="$emit('close')">Annuler</button>
        <button class="btn-success" @click="valider" :disabled="selectedDates.length === 0">
          Valider {{ selectedDates.length }} jour(s)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { parseISO, format, eachDayOfInterval } from 'date-fns'
import { fr } from 'date-fns/locale'

const props = defineProps<{
  conge: any
  typesConge: any[]
  soldeDisponible: number
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'valider', dates: string[]): void
}>()

const selectedDates = ref<string[]>([])

const joursPeriode = computed(() => {
  if (!props.conge) return []
  
  const start = parseISO(props.conge.date_debut)
  const end = parseISO(props.conge.date_fin)
  
  return eachDayOfInterval({ start, end }).map(date => ({
    date: format(date, 'yyyy-MM-dd'),
    deduction: 1 // Valeur simplifiée pour test
  }))
})

const formatDate = (dateStr: string) => {
  return format(parseISO(dateStr), 'EEEE d MMMM', { locale: fr })
}

const valider = () => {
  emit('valider', selectedDates.value)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.modal-actions {
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
}

.date-item {
  padding: 0.5rem;
  border-bottom: 1px solid #f0f0f0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

.btn-secondary {
  padding: 0.5rem 1rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
}

.btn-success {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
}

.btn-success:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>