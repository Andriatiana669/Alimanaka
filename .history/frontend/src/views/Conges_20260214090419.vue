<template>
  <!-- Header avec solde et actions alignées -->
  <div class="page-header">
    <div class="header-left">
      <h1>Mes Congés</h1>
      <div v-if="authStore.user" class="solde-badge">
        <span class="solde-dispo">🏖️ {{ authStore.soldeConge.actuelle }}j disponibles</span>
        <span class="solde-pris">⛔ {{ authStore.soldeConge.consomme }}j pris</span>
      </div>
    </div>
    
    <div class="header-actions">
      <button class="btn-export" @click="exportMine">
        <i class="bi bi-download"></i> Exporter Seul
      </button>
      <button v-if="congesStore.isSuperAdmin" class="btn-export-all" @click="exportAll">
        <i class="bi bi-download"></i> Exporter Tous
      </button>
      <button class="btn-primary" @click="openRequestModal">
        <i class="bi bi-plus-lg"></i> 
        {{ congesStore.canManageOthers ? 'Ajouter une demande' : 'Nouvelle demande' }}
      </button>
    </div>
  </div>

  <!-- Filtres avancés pour managers/admins -->
  <div v-if="congesStore.isManagerOrAdmin || congesStore.isSuperAdmin" class="filters-bar">
    <div class="filter-tabs">
      <div class="custom-select">
        <button
          class="select-button"
          :class="{ active: filters.pole !== null }"
          @click="togglePoleDropdown"
        >
          {{ filters.pole ? selectedPoleName : 'Tous les pôles' }}
        </button>
        <div v-if="showPoleDropdown" class="select-dropdown">
          <div
            class="select-option"
            @click="selectPole(null)"
          >
            Tous les pôles
          </div>
          <div
            v-for="pole in availablePoles"
            :key="pole.id"
            class="select-option"
            @click="selectPole(pole.id)"
          >
            {{ pole.nom }}
          </div>
        </div>
      </div>
    </div>

    <div class="filter-tabs">
      <div class="custom-select">
        <button
          class="select-button"
          :class="{ active: filters.equipe !== null, disabled: !filters.pole }"
          @click="toggleEquipeDropdown"
          :disabled="!filters.pole"
        >
          {{ filters.equipe ? selectedEquipeName : 'Toutes les équipes' }}
        </button>
        <div v-if="showEquipeDropdown && filters.pole" class="select-dropdown">
          <div
            class="select-option"
            @click="selectEquipe(null)"
          >
            Toutes les équipes
          </div>
          <div
            v-for="equipe in availableEquipes"
            :key="equipe.id"
            class="select-option"
            @click="selectEquipe(equipe.id)"
          >
            {{ equipe.nom }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="filter-tabs">
      <button 
        :class="{ active: statusFilter === 'tous' }" 
        @click="setStatusFilter('tous')"
      >
        Tous
      </button>
      <button 
        :class="{ active: statusFilter === 'approuve' }" 
        @click="setStatusFilter('approuve')"
      >
        Approuvés
      </button>
      <button 
        :class="{ active: statusFilter === 'en_attente' }" 
        @click="setStatusFilter('en_attente')"
      >
        En attente
      </button>

    </div>
    
    <button class="btn-refresh" @click="refreshData" :disabled="loading">
      <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
      {{ loading ? 'Chargement...' : 'Actualiser' }}
    </button>
  </div>

  <!-- Filtres simples pour utilisateurs normaux -->
  <div v-else class="filters-bar">
    <div class="filter-tabs">
      <button 
        :class="{ active: statusFilter === 'tous' }" 
        @click="setStatusFilter('tous')"
      >
        Tous
      </button>
      <button 
        :class="{ active: statusFilter === 'approuve' }" 
        @click="setStatusFilter('approuve')"
      >
        Approuvés
      </button>
      <button 
        :class="{ active: statusFilter === 'en_attente' }" 
        @click="setStatusFilter('en_attente')"
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
    :events="filteredEventsForCalendar"
    :blocked-dates="blockedDates"
    :default-view="'month'"
    class="conges-calendar"
  />

  <!-- Modal Demande de Congé -->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
    <div class="modal modal-large">
      <div class="modal-header">
        <h3>{{ congesStore.canManageOthers ? 'Ajouter un congé (Manager)' : 'Nouvelle demande de congé' }}</h3>
        <button class="btn-close" @click="closeModal">×</button>
      </div>

      <div class="modal-body">
        <!-- Sélection de l'utilisateur (visible seulement pour managers) -->
        <div v-if="congesStore.canManageOthers" class="form-group">
          <label>Utilisateur <span class="required">*</span></label>
          <div class="user-select-container">
            <input
              v-model="userSearchQuery"
              type="text"
              class="form-input"
              placeholder="Rechercher un utilisateur..."
              @focus="showUserDropdown = true"
              @input="onUserSearch"
            />
            
            <!-- Dropdown des utilisateurs -->
            <div v-if="showUserDropdown && filteredUsers.length > 0" class="user-dropdown">
              <div
                v-for="user in filteredUsers"
                :key="user.id"
                class="user-option"
                :class="{ selected: selectedUser?.id === user.id }"
                @click="selectUser(user)"
              >
                <div class="user-option-info">
                  <span class="user-option-name">{{ user.display_name }}</span>
                  <span class="user-option-meta">
                    {{ user.username.toUpperCase() }} | {{ user.equipe_nom || 'Sans équipe' }} | Solde: {{ user.solde_conge_actuelle }}j
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Utilisateur sélectionné -->
            <div v-if="selectedUser && !showUserDropdown" class="selected-user">
              <div class="avatar-small">{{ getInitials(selectedUser.display_name) }}</div>
              <div>
                <p class="user-name">{{ selectedUser.display_name }} ({{ selectedUser.username.toUpperCase() }})</p>
                <p class="user-solde">Solde disponible: <strong>{{ selectedUser.solde_conge_actuelle }}j</strong></p>
              </div>
              <button class="btn-change-user" @click="showUserDropdown = true; userSearchQuery = ''">
                Changer
              </button>
            </div>
          </div>
        </div>

        <!-- Info utilisateur normal (non-manager) -->
        <div v-else-if="authStore.user" class="user-info-form">
          <div class="avatar-small">{{ userInitials }}</div>
          <div>
            <p class="user-name">{{ authStore.user.display_name }} ({{ authStore.user.username.toUpperCase() }})</p>
            <p class="user-solde">Solde disponible: <strong>{{ authStore.soldeConge.actuelle }}j</strong></p>
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
              :min="today"
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
          <!-- Alerte si moins d'1 semaine -->
          <p v-if="isUrgentRequest" class="urgent-text">
            ⚠️ Congé dans moins d'1 semaine - Motif obligatoire !
          </p>
        </div>

        <!-- Motif -->
        <div class="form-group">
          <label>
            Motif 
            <span v-if="isUrgentRequest" class="required">*</span>
            <span v-else>(facultatif)</span>
          </label>
          <textarea 
            v-model="form.motif" 
            rows="3" 
            :placeholder="isUrgentRequest ? 'Motif obligatoire pour un congé urgent...' : 'Raison de votre absence...'"
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import Calendar from '@/components/common/Calendar.vue'
import type { TypeCongeConfig, CalendarEvent, GérableUser } from '@/types/conges'
import { format, addDays, isWeekend, parseISO, getYear, differenceInDays, startOfDay } from 'date-fns'


// Stores
const authStore = useAuthStore()
const congesStore = useCongesStore()

// Clés localStorage
const STORAGE_KEY_STATUS = 'alimanaka_conges_status_filter'

// État local
const filters = ref({
  pole: null as number | null,
  equipe: null as number | null
})
const statusFilter = ref<'tous' | 'approuve' | 'en_attente'>(
  (localStorage.getItem(STORAGE_KEY_STATUS) as 'tous' | 'approuve' | 'en_attente') || 'tous'
)
const showModal = ref(false)
const loading = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)
const dateError = ref<string | null>(null)

// Affichage pôle
const showPoleDropdown = ref(false);
const showEquipeDropdown = ref(false);


// Noms sélectionnés (pour affichage)
const selectedPoleName = computed(() => {
  const pole = availablePoles.value.find(p => p.id === filters.value.pole);
  return pole ? pole.nom : 'Tous les pôles';
});

const selectedEquipeName = computed(() => {
  const equipe = availableEquipes.value.find(e => e.id === filters.value.equipe);
  return equipe ? equipe.nom : 'Toutes les équipes';
});

// Méthodes pour gérer les dropdowns
const togglePoleDropdown = () => {
  showPoleDropdown.value = !showPoleDropdown.value;
  showEquipeDropdown.value = false; // Ferme l'autre dropdown
};

const toggleEquipeDropdown = () => {
  if (!filters.value.pole) return;
  showEquipeDropdown.value = !showEquipeDropdown.value;
  showPoleDropdown.value = false; // Ferme l'autre dropdown
};

const selectPole = (id: number | null) => {
  filters.value.pole = id;
  filters.value.equipe = null; // Réinitialise l'équipe si le pôle change
  showPoleDropdown.value = false;
  onFilterChange();
};

const selectEquipe = (id: number | null) => {
  filters.value.equipe = id;
  showEquipeDropdown.value = false;
  onFilterChange();
};


// Pour le dropdown utilisateur (manager)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUser = ref<GérableUser | null>(null)

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

// Initials pour l'avatar
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

const getInitials = (name: string) => name.charAt(0).toUpperCase()

// Date aujourd'hui (pour min du datepicker)
const today = computed(() => format(new Date(), 'yyyy-MM-dd'))

// Pôles et équipes disponibles pour les filtres (à charger depuis API)
const availablePoles = ref<{id: number, nom: string}[]>([])
const availableEquipes = ref<{id: number, nom: string}[]>([])

// Utilisateurs filtrés pour le dropdown
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return congesStore.utilisateursGérables
  
  const query = userSearchQuery.value.toLowerCase()
  return congesStore.utilisateursGérables.filter(u => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

// Événements filtrés selon le statut sélectionné
const filteredEventsForCalendar = computed<CalendarEvent[]>(() => {
  const allEvents = congesStore.eventsForCalendar
  
  if (statusFilter.value === 'tous') {
    return allEvents
  }
  
  return allEvents.filter(event => {
    if (event.type !== 'conge') return true
    
    const congeId = String(event.id).replace('conge_', '')
    const conge = congesStore.conges.find(c => String(c.id) === congeId)
    
    if (!conge) return true
    
    if (statusFilter.value === 'approuve') {
      return conge.statut === 'approuve'
    } else if (statusFilter.value === 'en_attente') {
      return conge.statut === 'en_attente'
    }
    
    return true
  })
})

// Dates bloquées (jours fériés, exceptionnels, congés annuels - PAS les weekends)
const blockedDates = computed(() => {
  return congesStore.calendrierEvents
    .filter(e => e.isBlocked && e.type !== 'weekend')
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

// Vérifier si congé urgent (moins d'1 semaine)
const isUrgentRequest = computed(() => {
  if (!form.value.date_debut) return false
  
  const startDate = startOfDay(parseISO(form.value.date_debut))
  const now = startOfDay(new Date())
  const daysDiff = differenceInDays(startDate, now)
  
  return daysDiff < 7
})

// Validation du formulaire
const isFormValid = computed(() => {
  const baseValid = form.value.type_conge && 
                   form.value.date_debut && 
                   form.value.date_fin &&
                   form.value.date_fin >= form.value.date_debut
  
  // Si manager, doit sélectionner un utilisateur
  if (congesStore.canManageOthers && !selectedUser.value) {
    return false
  }
  
  // Si urgent, motif obligatoire
  if (isUrgentRequest.value) {
    return baseValid && form.value.motif && form.value.motif.trim().length > 0
  }
  
  return baseValid
})

// Méthodes
const setStatusFilter = (filter: 'tous' | 'approuve' | 'en_attente') => {
  statusFilter.value = filter
  localStorage.setItem(STORAGE_KEY_STATUS, filter)
}

const onFilterChange = () => {
  refreshData()
}

const onUserSearch = () => {
  showUserDropdown.value = true
}

const selectUser = (user: GérableUser) => {
  selectedUser.value = user
  showUserDropdown.value = false
  userSearchQuery.value = ''
}

const openRequestModal = async () => {
  formError.value = null
  dateError.value = null
  form.value = {
    type_conge: 'journee',
    date_debut: '',
    date_fin: '',
    motif: ''
  }
  selectedUser.value = null
  userSearchQuery.value = ''
  
  try {
    if (typesConge.value.length === 0) {
      await congesStore.fetchTypesConge()
      typesConge.value = congesStore.typesConge
    }
    
    // Charger les utilisateurs gérables si manager
    if (congesStore.canManageOthers) {
      await congesStore.fetchUtilisateursGérables()
    }
    
    showModal.value = true
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
  }
}

const closeModal = () => {
  showModal.value = false
  selectedUser.value = null
}

const onDateChange = () => {
  dateError.value = null
  
  if (form.value.date_debut) {
    const selected = parseISO(form.value.date_debut)
    
    const isBlocked = congesStore.calendrierEvents.some(e => {
      if (!e.isBlocked || e.type === 'weekend') return false
      const eventDate = new Date(e.start)
      return format(eventDate, 'yyyy-MM-dd') === form.value.date_debut
    })
    
    if (isBlocked) {
      dateError.value = 'Cette date est indisponible (jour férié ou exceptionnel)'
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
    const payload: any = {
      type_conge: form.value.type_conge,
      date_debut: form.value.date_debut,
      date_fin: form.value.date_fin,
      motif: form.value.motif
    }
    
    // Si manager ajoute pour quelqu'un d'autre
    if (congesStore.canManageOthers && selectedUser.value) {
      payload.user_id = selectedUser.value.id
    }
    
    await congesStore.createConge(payload)
    
    closeModal()
    alert('Demande envoyée !')
    
  } catch (err: any) {
    formError.value = err.response?.data?.error || err.response?.data?.detail || 'Erreur'
  } finally {
    submitting.value = false
  }
}

const refreshData = async () => {
  loading.value = true
  const params: any = { annee: getYear(new Date()) }
  if (filters.value.pole) params.pole = filters.value.pole
  if (filters.value.equipe) params.equipe = filters.value.equipe
  
  await Promise.all([
    congesStore.fetchCalendrier(params),
    congesStore.fetchMesConges(getYear(new Date()))
  ])
  loading.value = false
}

const exportAll = () => congesStore.exportAll()
const exportMine = () => congesStore.exportMine()

const onVisibilityChange = () => {
  if (document.visibilityState === 'visible') {
    authStore.refreshSolde()
  }
}

onMounted(async () => {
  await authStore.checkAuth()
  await refreshData()
  document.addEventListener('visibilitychange', onVisibilityChange)
})

onUnmounted(() => {
  document.removeEventListener('visibilitychange', onVisibilityChange)
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
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.solde-dispo,
.solde-pris {
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.solde-dispo {
  background-color: #d1fae5;
  color: #065f46;
}

.solde-pris {
  background-color: #fee2e2;
  color: #991b1b;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn-export,
.btn-export-all,
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-export {
  background-color: #f3f4f6;
  color: #374151;
}

.btn-export:hover {
  background-color: #e5e7eb;
}

.btn-primary {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background: #2980b9;
}

.btn-primary:disabled {
  background: #95a5a6;
  cursor: not-allowed;
}

.btn-export-all {
  background-color: #dbeafe;
  color: #1e40af;
}

.btn-export-all:hover {
  background-color: #bfdbfe;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.75rem;
  color: #6b7280;
  text-transform: uppercase;
  font-weight: 600;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  background: white;
  min-width: 150px;
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
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  flex-shrink: 0;
}

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
  z-index: 9999;
  padding: 2rem;
  touch-action: none;
}

.modal {
  background: white;
  border-radius: 12px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  overflow-y: auto;
  box-shadow: 0 20px 60px rgba(0,0,0,0.3);
  display: flex;
  flex-direction: column;
  position: relative;
}

.modal-large {
  max-width: 600px;
}

.modal-header {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
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

.urgent-text {
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

/* Dropdown utilisateur */
.user-select-container {
  position: relative;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 0.375rem;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  max-height: 300px;
  overflow-y: auto;
  z-index: 50;
  margin-top: 0.25rem;
}

.user-option {
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f3f4f6;
  transition: background 0.2s;
}

.user-option:hover {
  background: #f9fafb;
}

.user-option.selected {
  background: #eff6ff;
}

.user-option-info {
  display: flex;
  flex-direction: column;
}

.user-option-name {
  font-weight: 600;
  color: #111827;
}

.user-option-meta {
  font-size: 0.75rem;
  color: #6b7280;
}

.selected-user {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 0.375rem;
  margin-top: 0.5rem;
}

.btn-change-user {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  color: #3b82f6;
  background: none;
  border: 1px solid #3b82f6;
  border-radius: 0.25rem;
  cursor: pointer;
}

.btn-change-user:hover {
  background: #eff6ff;
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