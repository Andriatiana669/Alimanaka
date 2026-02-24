<template>
    <!-- Header avec solde -->
    <div class="page-header">
      <div class="header-left">
        <h1>Mes Congés</h1>
        <div v-if="authStore.user" class="solde-badge">
          <span class="solde-dispo">🏖️ {{ (authStore.user as any).solde_conge_actuelle || 0 }}j disponibles</span>
          <span class="solde-pris">⛔ {{ authStore.user.solde_conge_consomme || 0 }}j pris</span>
        </div>
      </div>
      
      <div class="header-actions">
        <button class="btn-export" @click="exportMine">
          <i class="bi bi-download"></i> Exporter Seul
        </button>
        <button v-if="isAdmin" class="btn-export-all" @click="exportAll">
          <i class="bi bi-download"></i> Exporter Tous
        </button>
        <button class="btn-primary" @click="openRequestModal">
          <i class="bi bi-plus-lg"></i> Ajouter une demande
        </button>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      
      <div class="filter-tabs">
        <button 
          :class="{ active: statusFilter === 'tous' }" 
          @click="statusFilter = 'tous'"
        >
          Tous
        </button>
        <button 
          :class="{ active: statusFilter === 'approuve' }" 
          @click="statusFilter = 'approuve'"
        >
          Approuvés
        </button>
        <button 
          :class="{ active: statusFilter === 'en_attente' }" 
          @click="statusFilter = 'en_attente'"
        >
          En attente
        </button>
      </div>
      
      <button class="btn-refresh" @click="refreshData" :disabled="loading">
        <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
        {{ loading ? 'Chargement...' : 'Actualiser' }}
      </button>
    </div>

    <!-- Calendrier -->
    <Calendar
      :events="eventsForCalendar"
      :blocked-dates="blockedDates"
      :default-view="'month'"
      class="conges-calendar"
    />

    <!-- Modal Demande de Congé -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>Nouvelle demande de congé</h3>
          <button class="btn-close" @click="closeModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Info utilisateur -->
          <div class="user-info-form" v-if="authStore.user">
            <div class="avatar-small">{{ userInitials }}</div>
            <div>
              <p class="user-name">{{ authStore.user.display_name }} ({{ authStore.user.username.toUpperCase() }})</p>
              <p class="user-solde">Solde disponible: <strong>{{ authStore.user.solde_conge_actuelle || 0 }}j</strong></p>
            </div>
          </div>

          <!-- Type de congé -->
          <div class="form-group">
            <label>Type de congé <span class="required">*</span></label>
            <div class="type-options">
              <label 
                v-for="type in typesConge" 
                :key="type.type_conge"
                class="type-option"
                :class="{ selected: form.type_conge === type.type_conge }"
              >
                <input 
                  type="radio" 
                  v-model="form.type_conge" 
                  :value="type.type_conge"
                />
                <span class="type-label">{{ typeLabels[type.type_conge] }}</span>
                <span class="type-time">{{ type.heure_debut }} - {{ type.heure_fin }}</span>
                <span class="type-deduction">-{{ type.deduction_jours }}j</span>
              </label>
            </div>
          </div>

          <!-- Dates -->
          <div class="form-row">
            <div class="form-group">
              <label>Date de début <span class="required">*</span></label>
              <input 
                type="date" 
                v-model="form.date_debut"
                :min="minDate"
                class="form-input"
                @change="onDateChange"
              />
              <p v-if="dateError" class="error-text">{{ dateError }}</p>
            </div>
            
            <div class="form-group">
              <label>Date de fin <span class="required">*</span></label>
              <input 
                type="date" 
                v-model="form.date_fin"
                :min="form.date_debut"
                :disabled="!form.date_debut"
                class="form-input"
              />
            </div>
          </div>

          <!-- Aperçu des jours -->
          <div v-if="form.date_debut && form.date_fin" class="preview-box">
            <p>
              <strong>{{ calculateDays }} jour(s)</strong> demandé(s)
              <span v-if="deductionPreview > 0">(déduction: <strong>{{ deductionPreview }}j</strong>)</span>
            </p>
            <p v-if="deductionPreview > (authStore.user?.solde_conge_actuelle || 0)" class="warning-text">
              ⚠️ Solde insuffisant !
            </p>
          </div>

          <!-- Motif -->
          <div class="form-group">
            <label>Motif (facultatif)</label>
            <textarea 
              v-model="form.motif" 
              rows="3" 
              placeholder="Raison de votre absence..."
              class="form-textarea"
              maxlength="500"
            ></textarea>
            <span class="char-count">{{ form.motif?.length || 0 }}/500</span>
          </div>

          <!-- Erreur globale -->
          <div v-if="formError" class="alert-error">
            <i class="bi bi-exclamation-triangle"></i>
            {{ formError }}
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="submitForm"
            :disabled="!isFormValid || submitting"
          >
            <i v-if="submitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Envoyer la demande</span>
          </button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import Calendar from '@/components/common/Calendar.vue'
import type { TypeCongeConfig } from '@/types/conges'
import { format, addDays, isWeekend, parseISO } from 'date-fns'

// Stores
const authStore = useAuthStore()
const congesStore = useCongesStore()

// État local
const yearFilter = ref(new Date().getFullYear())
const statusFilter = ref<'tous' | 'approuve' | 'en_attente'>('tous')
const showModal = ref(false)
const loading = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const dateError = ref<string | null>(null)

const typesConge = ref<TypeCongeConfig[]>([])

const form = ref({
  type_conge: 'journee' as 'matin' | 'midi' | 'journee',
  date_debut: '',
  date_fin: '',
  motif: ''
})

// Labels pour les types
const typeLabels: Record<string, string> = {
  matin: 'Matin',
  midi: 'Midi',
  journee: 'Une journée'
}

// Années disponibles
const years = computed(() => {
  const current = new Date().getFullYear()
  return [current - 1, current, current + 1, current + 2]
})

// Admin check
const isAdmin = computed(() => authStore.isAdmin)

// Initials pour l'avatar
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

// Date minimum (demain)
const minDate = computed(() => {
  const tomorrow = addDays(new Date(), 1)
  return format(tomorrow, 'yyyy-MM-dd')
})

// Événements filtrés pour le calendrier
const eventsForCalendar = computed(() => congesStore.eventsForCalendar)

// Dates bloquées pour le calendrier
const blockedDates = computed(() => {
  return congesStore.calendrierEvents
    .filter(e => e.isBlocked)
    .flatMap(e => {
      const dates: Date[] = []
      const start = new Date(e.start)
      const end = e.end ? new Date(e.end) : start
      let current = new Date(start)
      while (current <= end) {
        dates.push(new Date(current))
        current = addDays(current, 1)
      }
      return dates
    })
})

// Calcul des jours
const calculateDays = computed(() => {
  if (!form.value.date_debut || !form.value.date_fin) return 0
  
  const start = parseISO(form.value.date_debut)
  const end = parseISO(form.value.date_fin)
  
  let count = 0
  let current = new Date(start)
  
  while (current <= end) {
    // Skip weekends et jours bloqués
    if (!isWeekend(current) && !congesStore.isDateBlocked(current)) {
      count++
    }
    current = addDays(current, 1)
  }
  
  return count
})

// Aperçu de la déduction
const deductionPreview = computed(() => {
  const type = typesConge.value.find(t => t.type_conge === form.value.type_conge)
  if (!type) return 0
  
  const days = calculateDays.value
  let deduction = 0
  
  // Calcul simplifié
  const start = form.value.date_debut ? parseISO(form.value.date_debut) : null
  
  if (start) {
    for (let i = 0; i < days; i++) {
      const current = addDays(start, i)
      const dayOfWeek = current.getDay()
      
      if (dayOfWeek === 5 && type.vendredi_deduction) {
        deduction += type.vendredi_deduction
      } else if (dayOfWeek === 4 && type.jeudi_deduction) {
        const vendredi = addDays(current, 1)
        if (congesStore.isDateBlocked(vendredi)) {
          deduction += type.jeudi_deduction
        } else {
          deduction += type.deduction_jours
        }
      } else {
        deduction += type.deduction_jours
      }
    }
  }
  
  return deduction
})

// Validation du formulaire
const isFormValid = computed(() => {
  const solde = authStore.user?.solde_conge_actuelle || 0
  return form.value.type_conge && 
         form.value.date_debut && 
         form.value.date_fin &&
         form.value.date_fin >= form.value.date_debut &&
         deductionPreview.value <= solde
})

// Méthodes
const openRequestModal = async () => {
  formError.value = null
  dateError.value = null
  form.value = {
    type_conge: 'journee',
    date_debut: '',
    date_fin: '',
    motif: ''
  }
  
  if (typesConge.value.length === 0) {
    await congesStore.fetchTypesConge()
    typesConge.value = congesStore.typesConge
  }
  
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const onDateChange = () => {
  dateError.value = null
  
  if (form.value.date_debut) {
    const selected = parseISO(form.value.date_debut)
    
    if (congesStore.isDateBlocked(selected)) {
      dateError.value = 'Cette date est indisponible'
      form.value.date_debut = ''
      return
    }
    
    if (!form.value.date_fin || form.value.date_fin < form.value.date_debut) {
      form.value.date_fin = form.value.date_debut
    }
  }
}

const submitForm = async () => {
  if (!isFormValid.value) return
  
  submitting.value = true
  formError.value = null
  
  try {
    await congesStore.createConge({
      type_conge: form.value.type_conge,
      date_debut: form.value.date_debut,
      date_fin: form.value.date_fin,
      motif: form.value.motif
    })
    
    await authStore.checkAuth()
    closeModal()
    alert('Demande envoyée !')
    
  } catch (err: any) {
    formError.value = err.response?.data?.error || 'Erreur'
  } finally {
    submitting.value = false
  }
}

const refreshData = async () => {
  loading.value = true
  await Promise.all([
    congesStore.fetchCalendrier(yearFilter.value),
    congesStore.fetchMesConges(yearFilter.value)
  ])
  loading.value = false
}

const exportAll = () => congesStore.exportAll()
const exportMine = () => congesStore.exportMine()

// Lifecycle
onMounted(async () => {
  // Attendre que l'auth soit chargée d'abord
  await authStore.checkAuth()
  console.log('User après auth:', authStore.user)
  console.log('Solde:', authStore.user?.solde_conge_actuelle)
  
  // Puis charger les congés
  await refreshData()
})
</script>



<style scoped>

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.solde-badge {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.solde-dispo {
  background: #d4edda;
  color: #155724;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.solde-pris {
  background: #f8d7da;
  color: #721c24;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-export, .btn-export-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.2rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-export-all {
  background: #e3f2fd;
  border-color: #90caf9;
  color: #1976d2;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}



.filter-tabs {
  display: flex;
  gap: 0.5rem;
}

.filter-tabs button {
  padding: 0.6rem 1.2rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.filter-tabs button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  margin-left: auto;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.conges-calendar {
  height: calc(100vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
}

.modal-large {
  max-width: 700px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-close:hover {
  background: #f8f9fa;
  color: #e74c3c;
}

.modal-body {
  padding: 1.5rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}

/* Formulaire */
.user-info-form {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.avatar-small {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
  font-size: 1.2rem;
}

.user-name {
  font-weight: 600;
  color: #2c3e50;
  margin: 0 0 0.25rem 0;
}

.user-solde {
  color: #6c757d;
  margin: 0;
  font-size: 0.9rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.required {
  color: #e74c3c;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Options de type */
.type-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.type-option {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-option:hover {
  border-color: #3498db;
  background: #f8f9fa;
}

.type-option.selected {
  border-color: #3498db;
  background: #e3f2fd;
}

.type-option input {
  display: none;
}

.type-label {
  font-weight: 600;
  color: #2c3e50;
  min-width: 100px;
}

.type-time {
  color: #6c757d;
  font-size: 0.9rem;
}

.type-deduction {
  margin-left: auto;
  background: #e74c3c;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Preview box */
.preview-box {
  background: #e8f5e9;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #4caf50;
}

.preview-box p {
  margin: 0;
  color: #2e7d32;
}

.warning-text {
  color: #e65100 !important;
  font-weight: 500;
  margin-top: 0.5rem !important;
}

/* Error styles */
.error-text {
  color: #e74c3c;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}

.alert-error {
  background: #fee;
  color: #c33;
  padding: 1rem;
  border-radius: 6px;
  border-left: 4px solid #c33;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.char-count {
  display: block;
  text-align: right;
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
  
  .filter-tabs {
    order: 3;
    width: 100%;
  }
}
</style>