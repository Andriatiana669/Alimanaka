<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>Annulation partielle</h3>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <p>Sélectionnez les jours à annuler pour <strong>{{ conge?.utilisateur_details?.display_name }}</strong></p>
        
        <div class="info-box warning">
          <i class="bi bi-exclamation-triangle-fill"></i>
          <span>L'annulation remboursera les jours sélectionnés ({{ remboursementTotal }}j)</span>
        </div>
        
        <div class="dates-list">
          <div v-for="jour in joursPeriode" :key="jour.date" class="date-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="selectedDates" 
                :value="jour.date"
                :disabled="!jour.peutAnnuler"
              />
              <span class="date-text">
                {{ formatDate(jour.date) }}
                <span v-if="!jour.peutAnnuler" class="badge-disabled">⛔ Non annulable</span>
                <span v-else class="deduction-preview">+{{ jour.remboursement }}j</span>
              </span>
            </label>
          </div>
        </div>
        
        <div class="preview-box warning">
          <p><strong>{{ selectedDates.length }}</strong> jour(s) sélectionné(s)</p>
          <p>Remboursement total: <strong class="refund-amount">+{{ remboursementTotal }}j</strong></p>
          <p>Nouveau solde après annulation: <strong>{{ soldeApresAnnulation }}j</strong></p>
          <p class="info-text">
            <i class="bi bi-info-circle"></i>
            Ces jours seront remboursés et le congé sera fractionné automatiquement
          </p>
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn-secondary" @click="$emit('close')">Annuler</button>
        <button 
          class="btn-warning" 
          @click="annuler"
          :disabled="selectedDates.length === 0"
        >
          Annuler {{ selectedDates.length }} jour(s)
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { parseISO, format, eachDayOfInterval, isWeekend } from 'date-fns'
import { fr } from 'date-fns/locale'
import type { Conge } from '@/types/conges'
import { useCongesStore } from '@/store/conges'

const props = defineProps<{
  conge: Conge
  typesConge: any[]
  soldeDisponible: number
}>()

console.log('DEBUG - Congé reçu:', props.conge)
console.log('DEBUG - jours_valides:', props.conge.jours_valides)

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'annuler', dates: string[]): void
}>()

const congesStore = useCongesStore()
const selectedDates = ref<string[]>([])

// Générer tous les jours de la période
const joursPeriode = computed(() => {
  const start = parseISO(props.conge.date_debut)
  const end = parseISO(props.conge.date_fin)
  
  return eachDayOfInterval({ start, end })
    .filter(date => !isWeekend(date) && !congesStore.isDateBlocked(date))
    .map(date => {
      const dateStr = format(date, 'yyyy-MM-dd')
      const joursValides = props.conge.jours_valides || []
      const estValide = joursValides.includes(dateStr)
      
      // Calculer le remboursement pour ce jour
      const type = props.typesConge.find(t => t.type_conge === props.conge.type_conge)
      let remboursement = 0
      
      if (estValide) {
        remboursement = type?.deduction_jours || 0
        // Règles spéciales pour vendredi
        if (date.getDay() === 5 && type?.vendredi_deduction) {
          remboursement = type.vendredi_deduction
        }
      }
      
      return {
        date: dateStr,
        peutAnnuler: estValide,  // On ne peut annuler que les jours déjà validés
        remboursement
      }
    })
})

const remboursementTotal = computed(() => {
  return selectedDates.value.reduce((total, date) => {
    const jour = joursPeriode.value.find(j => j.date === date)
    return total + (jour?.remboursement || 0)
  }, 0)
})

const soldeApresAnnulation = computed(() => {
  return props.soldeDisponible + remboursementTotal.value
})

const formatDate = (dateStr: string) => {
  return format(parseISO(dateStr), 'EEEE d MMMM yyyy', { locale: fr })
}

const annuler = () => {
  emit('annuler', selectedDates.value)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 1rem;
  animation: fadeIn 0.2s ease;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 550px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: 1.5rem 1.5rem 1rem 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #f97316 0%, #dc2626 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: white;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
  line-height: 1;
  padding: 0;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  background: #f8fafc;
}

.modal-body p {
  margin-top: 0;
  margin-bottom: 1.25rem;
  color: #2d3748;
  font-size: 0.95rem;
}

.modal-body strong {
  color: #f97316;
  font-weight: 600;
}

.info-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.25rem;
  font-size: 0.95rem;
}

.info-box.warning {
  background: #fffbeb;
  border-left: 4px solid #f97316;
  color: #9a3412;
}

.info-box i {
  font-size: 1.25rem;
  color: #f97316;
}

.dates-list {
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  margin-bottom: 1.25rem;
  max-height: 300px;
  overflow-y: auto;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
}

.date-item {
  border-bottom: 1px solid #edf2f7;
  transition: background-color 0.2s;
}

.date-item:last-child {
  border-bottom: none;
}

.date-item:hover {
  background-color: #f7fafc;
}

.checkbox-label {
  display: flex;
  align-items: center;
  padding: 0.875rem 1rem;
  cursor: pointer;
  width: 100%;
}

.checkbox-label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  margin-right: 1rem;
  accent-color: #f97316;
  cursor: pointer;
  flex-shrink: 0;
}

.checkbox-label input[type="checkbox"]:disabled {
  accent-color: #cbd5e0;
  cursor: not-allowed;
  opacity: 0.6;
}

.date-text {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.95rem;
  color: #2d3748;
  text-transform: capitalize;
}

.badge-disabled {
  background: #e2e8f0;
  color: #64748b;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  margin-left: 0.75rem;
  white-space: nowrap;
  letter-spacing: 0.3px;
}

.deduction-preview {
  background: #c6f6d5;
  color: #22543d;
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 20px;
  margin-left: 0.5rem;
  white-space: nowrap;
}

.preview-box {
  background: linear-gradient(135deg, #f6f9fc 0%, #edf2f7 100%);
  padding: 1.25rem;
  border-radius: 12px;
  border-left: 4px solid;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-box.warning {
  border-left-color: #f97316;
}

.preview-box p {
  margin: 0.5rem 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.95rem;
  color: #2d3748;
}

.preview-box p:first-child {
  margin-top: 0;
}

.preview-box p:last-child {
  margin-bottom: 0;
}

.preview-box strong {
  color: #2d3748;
  font-size: 1.1rem;
  background: white;
  padding: 0.2rem 0.8rem;
  border-radius: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.refund-amount {
  color: #16a34a !important;
  font-weight: 700;
}

.info-text {
  color: #64748b !important;
  font-size: 0.85rem !important;
  margin-top: 0.75rem !important;
  padding-top: 0.75rem !important;
  border-top: 1px dashed #cbd5e0;
}

.info-text i {
  color: #94a3b8;
  margin-right: 0.25rem;
}

.modal-actions {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background: white;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #edf2f7;
  color: #4a5568;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #e2e8f0;
  color: #2d3748;
  transform: translateY(-1px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
}

.btn-secondary:active {
  transform: translateY(0);
}

.btn-warning {
  padding: 0.625rem 1.5rem;
  background: linear-gradient(135deg, #f97316 0%, #dc2626 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px rgba(249, 115, 22, 0.25);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-warning:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 12px rgba(249, 115, 22, 0.35);
}

.btn-warning:active:not(:disabled) {
  transform: translateY(0);
}

.btn-warning:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: #a0aec0;
  box-shadow: none;
}

/* Scrollbar personnalisée */
.dates-list::-webkit-scrollbar {
  width: 8px;
}

.dates-list::-webkit-scrollbar-track {
  background: #edf2f7;
}

.dates-list::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 4px;
}

.dates-list::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .modal {
    width: 95%;
    max-height: 90vh;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-actions {
    padding: 1rem;
    flex-direction: column-reverse;
  }
  
  .btn-warning, .btn-secondary {
    width: 100%;
    justify-content: center;
  }
  
  .date-text {
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .badge-disabled, .deduction-preview {
    margin-left: 0;
  }
}
</style>