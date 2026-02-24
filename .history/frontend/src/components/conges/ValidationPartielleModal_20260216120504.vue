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