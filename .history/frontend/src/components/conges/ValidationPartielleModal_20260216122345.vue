<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <div class="modal-header">
        <h3>Validation partielle</h3>
        <button class="btn-close" @click="$emit('close')">×</button>
      </div>
      
      <div class="modal-body">
        <p>Sélectionnez les jours à valider pour <strong>{{ conge?.utilisateur_details?.display_name }}</strong></p>
        
        <div class="dates-list">
          <div v-for="jour in joursPeriode" :key="jour.date" class="date-item">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="selectedDates" 
                :value="jour.date"
                :disabled="jour.dejaValide"
              />
              <span class="date-text">
                {{ formatDate(jour.date) }}
                <span v-if="jour.dejaValide" class="badge-validated">✓ Déjà validé</span>
                <span class="deduction-preview">-{{ jour.deduction }}j</span>
              </span>
            </label>
          </div>
        </div>
        
        <div class="preview-box">
          <p><strong>{{ selectedDates.length }}</strong> jour(s) sélectionné(s)</p>
          <p>Déduction totale: <strong>{{ deductionTotale }}j</strong></p>
          <p>Solde disponible: <strong>{{ soldeDisponible }}j</strong></p>
          <p v-if="deductionTotale > soldeDisponible" class="error-text">
            ⚠️ Solde insuffisant !
          </p>
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn-secondary" @click="$emit('close')">Annuler</button>
        <button 
          class="btn-success" 
          @click="valider"
          :disabled="selectedDates.length === 0 || deductionTotale > soldeDisponible"
        >
          Valider {{ selectedDates.length }} jour(s)
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

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'valider', dates: string[]): void
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
      const dejaValide = props.conge.jours_valides?.includes(dateStr) || false
      
      // Calculer déduction pour ce jour
      const type = props.typesConge.find(t => t.type_conge === props.conge.type_conge)
      let deduction = type?.deduction_jours || 0
      
      // Règles spéciales (simplifiées)
      if (date.getDay() === 5 && type?.vendredi_deduction) { // Vendredi
        deduction = type.vendredi_deduction
      }
      
      return {
        date: dateStr,
        dejaValide,
        deduction: dejaValide ? 0 : deduction
      }
    })
})

const deductionTotale = computed(() => {
  return selectedDates.value.reduce((total, date) => {
    const jour = joursPeriode.value.find(j => j.date === date)
    return total + (jour?.deduction || 0)
  }, 0)
})

const formatDate = (dateStr: string) => {
  return format(parseISO(dateStr), 'EEEE d MMMM yyyy', { locale: fr })
}

const valider = () => {
  emit('valider', selectedDates.value)
}
</script>


<style scoped>
/* =========================
   OVERLAY & MODAL
   ========================= */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55); /* slate-900 */
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #ffffff;
  width: 100%;
  max-width: 520px;
  border-radius: 16px;
  box-shadow:
    0 20px 40px rgba(0, 0, 0, 0.18),
    0 2px 8px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  animation: modal-enter 0.25s ease-out;
}

@keyframes modal-enter {
  from {
    opacity: 0;
    transform: translateY(16px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

/* =========================
   HEADER
   ========================= */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #2563eb, #1e40af);
  color: #ffffff;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  color: #ffffff;
  cursor: pointer;
  line-height: 1;
  opacity: 0.9;
}

.btn-close:hover {
  opacity: 1;
  transform: scale(1.05);
}

/* =========================
   BODY
   ========================= */
.modal-body {
  padding: 20px;
  color: #1f2937; /* gray-800 */
}

.modal-body p {
  margin-bottom: 12px;
  font-size: 0.95rem;
}

/* =========================
   DATES LIST
   ========================= */
.dates-list {
  max-height: 220px;
  overflow-y: auto;
  margin: 12px 0 16px;
  padding-right: 4px;
}

.date-item {
  margin-bottom: 8px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s ease;
}

.checkbox-label:hover {
  background: #f1f5f9; /* slate-100 */
}

.checkbox-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label input:disabled {
  cursor: not-allowed;
}

.date-text {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
}

/* =========================
   BADGES & INFO
   ========================= */
.badge-validated {
  background: #dcfce7; /* green-100 */
  color: #166534;      /* green-800 */
  font-size: 0.75rem;
  padding: 2px 6px;
  border-radius: 999px;
  font-weight: 500;
}

.deduction-preview {
  margin-left: auto;
  font-size: 0.8rem;
  color: #ef4444; /* red-500 */
  font-weight: 500;
}

/* =========================
   PREVIEW BOX
   ========================= */
.preview-box {
  background: #f8fafc; /* slate-50 */
  border: 1px solid #e5e7eb; /* gray-200 */
  border-radius: 12px;
  padding: 12px 14px;
  font-size: 0.9rem;
}

.preview-box p {
  margin: 4px 0;
}

.error-text {
  color: #dc2626; /* red-600 */
  font-weight: 600;
}

/* =========================
   ACTIONS
   ========================= */
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 16px 20px;
  background: #f9fafb; /* gray-50 */
  border-top: 1px solid #e5e7eb;
}

button {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.15s ease;
}

/* Secondary */
.btn-secondary {
  background: #e5e7eb; /* gray-200 */
  color: #374151; /* gray-700 */
}

.btn-secondary:hover {
  background: #d1d5db;
}

/* Success */
.btn-success {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: #ffffff;
}

.btn-success:hover:not(:disabled) {
  filter: brightness(1.05);
  transform: translateY(-1px);
}

.btn-success:disabled {
  background: #9ca3af; /* gray-400 */
  cursor: not-allowed;
  opacity: 0.8;
}
</style>
