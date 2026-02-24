<template>
  <!-- Header avec solde et actions alignées -->
  <div class="page-header">
    <div class="header-left">
      <h1>Mes Retards</h1>
      <div v-if="authStore.user" class="stats-badge">
        <span class="stat-en-attente">⏰ {{ totalRetardsEnAttente }} en attente</span>
        <span class="stat-heures">⏱️ {{ totalHeuresRestantes }}h à rattraper</span>
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
        <i class="bi bi-plus-lg"></i> 
        {{ canManageOthers ? 'Déclarer un retard (Manager)' : 'Déclarer un retard' }}
      </button>
    </div>
  </div>

  <!-- Filtres avancés pour managers/admins -->
  <div v-if="isManager || isAdmin" class="filters-bar">
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
      <button 
        :class="{ active: statusFilter === 'annule' }" 
        @click="setStatusFilter('annule')"
      >
        Annulés
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
      <button 
        :class="{ active: statusFilter === 'annule' }" 
        @click="setStatusFilter('annule')"
      >
        Annulés
      </button>
    </div>
    
    <button class="btn-refresh" @click="refreshData" :disabled="loading">
      <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
      {{ loading ? 'Chargement...' : 'Actualiser' }}
    </button>
  </div>

  <!-- Modal Détails du Retard -->
  <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
    <div class="modal modal-large">
      <div class="modal-header" :class="{
        'header-validated': selectedRetard?.statut === 'approuve',
        'header-refused': selectedRetard?.statut === 'annule'
      }">
        <h3>
          Détails du retard
          <span v-if="selectedRetard?.statut === 'approuve'" class="header-badge validated">
            ✓ Rattrapé
          </span>
          <span v-if="selectedRetard?.statut === 'annule'" class="header-badge refused">
            ✗ Annulé
          </span>
        </h3>
        <button class="btn-close" @click="closeDetailModal">×</button>
      </div>

      <div class="modal-body" v-if="selectedRetard">
        <!-- Section utilisateur -->
        <div class="detail-section">
          <div class="detail-avatar">{{ getInitials(selectedRetard.utilisateur_details?.display_name || '') }}</div>
          <div class="detail-user-info">
            <h4>{{ selectedRetard.utilisateur_details?.display_name }}</h4>
            <p class="detail-meta">Matricule: {{ selectedRetard.utilisateur_details?.username?.toUpperCase() }}</p>
            <p class="detail-meta">Email: {{ selectedRetard.utilisateur_details?.email || 'Non renseigné' }}</p>
          </div>
        </div>

        <!-- Info rattrapage -->
        <div v-if="selectedRetard.statut === 'approuve'" 
            class="validation-box validated-box">
          <h5>✓ Retard rattrapé</h5>
          <p>Total rattrapé: <strong>{{ selectedRetard.total_rattrape }}h</strong></p>
        </div>

        <div v-if="selectedRetard.statut === 'annule' && selectedRetard.annule_par_details" 
            class="validation-box refused-box">
          <h5>✗ Annulé par</h5>
          <p><strong>{{ selectedRetard.annule_par_details.display_name }}</strong></p>
          <p class="detail-meta">Le {{ formatDateTime(selectedRetard.date_annulation) }}</p>
          <div v-if="selectedRetard.commentaire_annulation" class="refusal-comment">
            <label>Motif :</label>
            <p>{{ selectedRetard.commentaire_annulation }}</p>
          </div>
        </div>

        <!-- Liste des rattrapages -->
        <div v-if="selectedRetard.rattrapages?.length > 0" class="rattrapages-section">
          <h5>Sessions de rattrapage</h5>
          <div v-for="rattrapage in selectedRetard.rattrapages" :key="rattrapage.id" class="rattrapage-detail">
            <div class="rattrapage-info">
              <span class="rattrapage-date">{{ formatDate(rattrapage.date_rattrapage) }}</span>
              <span class="rattrapage-heure">{{ rattrapage.heure_debut }} - {{ rattrapage.heure_fin }}</span>
            </div>
            <span class="rattrapage-duree">+{{ rattrapage.heures_rattrapees }}h</span>
          </div>
        </div>

        <div class="detail-grid">
          <div class="detail-item">
            <label>Date du retard</label>
            <span>{{ formatDate(selectedRetard.date) }}</span>
          </div>
          
          <div class="detail-item">
            <label>Heure d'arrivée</label>
            <span class="detail-badge" :style="{ backgroundColor: getRetardColor(selectedRetard.minutes_retard) }">
              {{ selectedRetard.heure_arrivee_reelle }} (+{{ selectedRetard.minutes_retard }}min)
            </span>
          </div>

          <div class="detail-item">
            <label>Heures à rattraper</label>
            <span class="detail-deduction">{{ selectedRetard.heures_a_rattraper }}h</span>
          </div>

          <div class="detail-item" v-if="parseFloat(selectedRetard.heures_restantes) > 0">
            <label>Reste à rattraper</label>
            <span class="detail-urgent">{{ selectedRetard.heures_restantes }}h</span>
          </div>

          <div class="detail-item">
            <label>Statut</label>
            <span class="detail-badge" :class="'status-' + selectedRetard.statut">
              {{ selectedRetard.statut_display }}
            </span>
          </div>

          <div class="detail-item full-width" v-if="selectedRetard.motif_retard">
            <label>Justificatif</label>
            <p class="detail-motif">{{ selectedRetard.motif_retard }}</p>
          </div>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
        
        <!-- Bouton Rattraper (si en attente et heures restantes) -->
        <template v-if="canManageThisRetard(selectedRetard) && selectedRetard?.statut === 'en_attente' && parseFloat(selectedRetard.heures_restantes) > 0">
          <button 
            class="btn-success"
            @click="openRattraperModal"
          >
            <i class="bi bi-check-lg"></i> Rattraper
          </button>
        </template>
        
        <!-- Bouton annuler -->
        <template v-if="canCancelRetard(selectedRetard)">
          <button class="btn-warning" @click="cancelSelectedRetard">
            <i class="bi bi-x-circle"></i> Annuler
          </button>
        </template>
      </div>
    </div>
  </div>

  <!-- Modal Déclarer un Retard -->
  <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
    <div class="modal modal-large">
      <div class="modal-header">
        <h3>{{ canManageOthers ? 'Déclarer un retard (Manager)' : 'Déclarer un retard' }}</h3>
        <button class="btn-close" @click="closeModal">×</button>
      </div>

      <div class="modal-body">
        <!-- Sélection de l'utilisateur (visible seulement pour managers) -->
        <div v-if="canManageOthers" class="form-group">
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
                    {{ user.username.toUpperCase() }} | {{ user.equipe_nom || 'Sans équipe' }}
                  </span>
                </div>
              </div>
            </div>
            
            <!-- Utilisateur sélectionné -->
            <div v-if="selectedUser && !showUserDropdown" class="selected-user">
              <div class="avatar-small">{{ getInitials(selectedUser.display_name) }}</div>
              <div>
                <p class="user-name">{{ selectedUser.display_name }} ({{ selectedUser.username.toUpperCase() }})</p>
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
          </div>
        </div>

        <!-- Date du retard -->
        <div class="form-row">
          <div class="form-group">
            <label>Date du retard <span class="required">*</span></label>
            <input 
              type="date" 
              v-model="form.date"
              :max="today"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>Heure d'arrivée réelle <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="form.heure_arrivee_reelle"
              class="form-input"
            />
          </div>
        </div>

        <!-- Justificatif -->
        <div class="form-group">
          <label>Justificatif / Motif</label>
          <textarea 
            v-model="form.motif_retard" 
            rows="3" 
            placeholder="Expliquez la raison du retard..."
            class="form-textarea"
            maxlength="500"
          ></textarea>
          <span class="char-count">{{ form.motif_retard?.length || 0 }}/500</span>
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
          <span v-else>Déclarer le retard</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Rattraper le Retard -->
  <div v-if="showRattraperModal" class="modal-overlay" @click.self="closeRattraperModal">
    <div class="modal">
      <div class="modal-header success-header">
        <h3>Rattraper le retard</h3>
        <button class="btn-close" @click="closeRattraperModal">×</button>
      </div>
      
      <div class="modal-body">
        <p v-if="selectedRetard" class="modal-subtitle">
          <strong>{{ selectedRetard.heures_restantes }}h</strong> restantes à rattraper
        </p>
        
        <div class="form-group">
          <label>Date du rattrapage <span class="required">*</span></label>
          <input 
            type="date" 
            v-model="rattrapageForm.date_rattrapage"
            :min="today"
            class="form-input"
          />
        </div>
        
        <div class="form-row">
          <div class="form-group">
            <label>Heure de début <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="rattrapageForm.heure_debut"
              class="form-input"
            />
          </div>
          
          <div class="form-group">
            <label>Heure de fin <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="rattrapageForm.heure_fin"
              class="form-input"
            />
          </div>
        </div>
        
        <div class="form-group">
          <label>Commentaire</label>
          <textarea 
            v-model="rattrapageForm.commentaire" 
            rows="2"
            placeholder="Détails sur le rattrapage..."
            class="form-textarea"
          ></textarea>
        </div>
        
        <div v-if="calculatedHeures" class="preview-box">
          Heures rattrapées: <strong>{{ calculatedHeures }}h</strong>
        </div>
        
        <div v-if="formError" class="alert-error">
          <i class="bi bi-exclamation-triangle"></i>
          {{ formError }}
        </div>
      </div>
      
      <div class="modal-actions">
        <button class="btn-secondary" @click="closeRattraperModal">Annuler</button>
        <button 
          class="btn-success" 
          @click="submitRattrapage"
          :disabled="!calculatedHeures || submitting"
        >
          <i v-if="submitting" class="bi bi-arrow-repeat spin"></i>
          <span v-else>Valider le rattrapage</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Calendrier -->
  <Calendar
    :events="filteredEventsForCalendar"
    :blocked-dates="blockedDates"
    :default-view="'month'"
    class="retards-calendar"
    @event-click="onEventClick"
  />
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useRetardsStore } from '@/store/retards'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import { retardsApi } from '@/api/retards'
import type { Retard, RetardCreateData, RattrapageCreateData, GerableUser } from '@/types/retards'
import { format, parseISO, getYear } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Stores
const authStore = useAuthStore()
const retardsStore = useRetardsStore()
const filtersStore = useFiltersStore()

// État local
const filters = ref({
  pole: null as number | null,
  equipe: null as number | null
})

const statusFilter = ref<'tous' | 'approuve' | 'en_attente' | 'annule'>('tous')

const showModal = ref(false)
const showDetailModal = ref(false)
const showRattraperModal = ref(false)
const loading = ref(false)
const submitting = ref(false)
const formError = ref<string | null>(null)

// Affichage dropdowns
const showPoleDropdown = ref(false)
const showEquipeDropdown = ref(false)

// Dropdown utilisateur (manager)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUser = ref<GerableUser | null>(null)

// Sélection
const selectedRetard = ref<Retard | null>(null)

// Formulaires
const today = format(new Date(), 'yyyy-MM-dd')

const form = ref<RetardCreateData>({
  date: today,
  heure_arrivee_reelle: '',
  motif_retard: ''
})

const rattrapageForm = ref<RattrapageCreateData>({
  date_rattrapage: today,
  heure_debut: '',
  heure_fin: '',
  commentaire: ''
})

// Permissions
const isAdmin = computed(() => authStore.user?.is_staff || authStore.user?.is_superuser)

const isManager = computed(() => {
  const user = authStore.user
  // equipes_managerisees contient les équipes où l'utilisateur est manager ou co-manager
  return (user?.equipes_managerisees?.length ?? 0) > 0
})

const canManageOthers = computed(() => isAdmin.value || isManager.value)

// Stats
const totalRetardsEnAttente = computed(() => 
  retardsStore.retards.filter(r => r.statut === 'en_attente').length
)

const totalHeuresRestantes = computed(() => {
  return retardsStore.retards
    .filter(r => r.statut === 'en_attente')
    .reduce((sum, r) => sum + parseFloat(r.heures_restantes || '0'), 0)
    .toFixed(2)
})

// Filtres affichage
const selectedPoleName = computed(() => {
  const pole = availablePoles.value.find(p => p.id === filters.value.pole)
  return pole ? pole.nom : 'Tous les pôles'
})

const selectedEquipeName = computed(() => {
  const equipe = availableEquipes.value.find(e => e.id === filters.value.equipe)
  return equipe ? equipe.nom : 'Toutes les équipes'
})

const availablePoles = computed(() => filtersStore.poles)
const availableEquipes = computed(() => filtersStore.equipes)

const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return retardsStore.utilisateursGerables
  
  const query = userSearchQuery.value.toLowerCase()
  return retardsStore.utilisateursGerables.filter(u => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

// Événements calendrier
const filteredEventsForCalendar = computed(() => {
  const allEvents = retardsStore.calendarEvents || []
  
  if (statusFilter.value === 'tous') {
    return allEvents
  }
  
  return allEvents.filter((event: any) => {
    if (event.type !== 'retard') return true
    return event.statut === statusFilter.value
  })
})

const blockedDates = computed(() => [])

// Calcul heures rattrapage
const calculatedHeures = computed(() => {
  if (!rattrapageForm.value.heure_debut || !rattrapageForm.value.heure_fin) return null
  
  const debut = new Date(`2000-01-01T${rattrapageForm.value.heure_debut}`)
  const fin = new Date(`2000-01-01T${rattrapageForm.value.heure_fin}`)
  
  if (fin <= debut) return null
  
  const diffMs = fin.getTime() - debut.getTime()
  const diffHours = diffMs / (1000 * 60 * 60)
  
  return diffHours.toFixed(2)
})

// Validation formulaire
const isFormValid = computed(() => {
  const baseValid = form.value.date && form.value.heure_arrivee_reelle
  
  if (canManageOthers.value && !selectedUser.value) {
    return false
  }
  
  return baseValid
})

// Initials
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

const getInitials = (name: string) => name.charAt(0).toUpperCase()

// Méthodes dropdowns
const togglePoleDropdown = () => {
  showPoleDropdown.value = !showPoleDropdown.value
  showEquipeDropdown.value = false
}

const toggleEquipeDropdown = () => {
  if (!filters.value.pole) return
  showEquipeDropdown.value = !showEquipeDropdown.value
  showPoleDropdown.value = false
}

const selectPole = async (id: number | null) => {
  filters.value.pole = id
  filters.value.equipe = null
  showPoleDropdown.value = false
  
  if (id) {
    await filtersStore.fetchEquipesByPole(id)
  } else {
    filtersStore.clearEquipes()
  }
  
  refreshData()
}

const selectEquipe = (id: number | null) => {
  filters.value.equipe = id
  showEquipeDropdown.value = false
  refreshData()
}

// Filtres
const setStatusFilter = (filter: 'tous' | 'approuve' | 'en_attente' | 'annule') => {
  statusFilter.value = filter
  refreshData()
}

// Gestion utilisateurs
const onUserSearch = () => {
  showUserDropdown.value = true
}

const selectUser = (user: GerableUser) => {
  selectedUser.value = user
  showUserDropdown.value = false
  userSearchQuery.value = ''
}

// Modals
const openRequestModal = async () => {
  formError.value = null
  form.value = {
    date: today,
    heure_arrivee_reelle: '',
    motif_retard: ''
  }
  selectedUser.value = null
  userSearchQuery.value = ''
  
  if (canManageOthers.value) {
    await retardsStore.fetchUtilisateursGerables()
  }
  
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  selectedUser.value = null
}

const openRattraperModal = () => {
  if (!selectedRetard.value) return
  
  rattrapageForm.value = {
    date_rattrapage: today,
    heure_debut: '',
    heure_fin: '',
    commentaire: ''
  }
  formError.value = null
  showRattraperModal.value = true
}

const closeRattraperModal = () => {
  showRattraperModal.value = false
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedRetard.value = null
}

// Clic sur événement calendrier
const onEventClick = async (event: any) => {
  if (event.type !== 'retard') return
  
  const retardId = parseInt(String(event.id).replace('retard_', ''))
  let retard = retardsStore.retards.find(r => r.id === retardId)
  
  if (!retard && canManageOthers.value) {
    try {
      const response = await retardsApi.getRetard(retardId)
      retard = response.data
    } catch (e) {
      console.error('Erreur chargement détails:', e)
      return
    }
  }
  
  if (retard) {
    selectedRetard.value = retard
    showDetailModal.value = true
  }
}

// Permissions détaillées
const canManageThisRetard = (retard: Retard | null): boolean => {
  if (!retard) return false
  if (!isManager.value && !isAdmin.value) return false
  if (isAdmin.value) return true
  
  // Vérifier si l'utilisateur du retard est dans une des équipes managerisées
  const userEquipeId = retard.utilisateur_details?.equipe_details?.id
  if (!userEquipeId) return false
  
  return authStore.user?.equipes_managerisees?.some(
    eq => eq.id === userEquipeId
  ) ?? false
}

const canCancelRetard = (retard: Retard | null): boolean => {
  if (!retard) return false
  return retard.statut === 'en_attente'
}

// Soumission formulaires
const submitForm = async () => {
  if (!isFormValid.value) return
  
  submitting.value = true
  formError.value = null
  
  try {
    const payload: any = {
      date: form.value.date,
      heure_arrivee_reelle: form.value.heure_arrivee_reelle,
      motif_retard: form.value.motif_retard
    }
    
    if (canManageOthers.value && selectedUser.value) {
      payload.user_id = selectedUser.value.id
    }
    
    await retardsStore.createRetard(payload)
    closeModal()
    await refreshData()
  } catch (err: any) {
    formError.value = err.response?.data?.error || err.response?.data?.detail || 'Erreur lors de la déclaration'
  } finally {
    submitting.value = false
  }
}

const submitRattrapage = async () => {
  if (!selectedRetard.value || !calculatedHeures.value) return
  
  submitting.value = true
  formError.value = null
  
  try {
    await retardsStore.rattraperRetard(selectedRetard.value.id, rattrapageForm.value)
    closeRattraperModal()
    closeDetailModal()
    await refreshData()
  } catch (err: any) {
    formError.value = err.response?.data?.error || 'Erreur lors du rattrapage'
  } finally {
    submitting.value = false
  }
}

const cancelSelectedRetard = async () => {
  if (!selectedRetard.value) return
  
  if (confirm('Voulez-vous vraiment annuler ce retard ?')) {
    await retardsStore.annulerRetard(selectedRetard.value.id)
    closeDetailModal()
    await refreshData()
  }
}

// Data loading
const refreshData = async () => {
  loading.value = true
  
  const params: any = {
    annee: getYear(new Date()),
    statut: statusFilter.value === 'tous' ? undefined : statusFilter.value
  }
  
  if (filters.value.pole) params.pole = filters.value.pole
  if (filters.value.equipe) params.equipe = filters.value.equipe
  
  await Promise.all([
    retardsStore.fetchCalendrier(getYear(new Date()), filters.value.pole || undefined, filters.value.equipe || undefined),
    retardsStore.fetchMesRetards({ annee: getYear(new Date()), statut: statusFilter.value === 'tous' ? undefined : statusFilter.value })
  ])
  
  loading.value = false
}

// Exports
const exportAll = async () => {
  try {
    const response = await retardsApi.exportRetards()
    downloadExport(response.data, 'retards_export')
  } catch (err) {
    console.error('Erreur export:', err)
  }
}

const exportMine = async () => {
  // TODO: Implémenter export individuel si nécessaire
  alert('Export individuel à implémenter')
}

const downloadExport = (data: Blob, prefix: string) => {
  const blob = new Blob([data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `${prefix}_${format(new Date(), 'yyyyMMdd')}.xlsx`
  link.click()
  window.URL.revokeObjectURL(url)
}

// Formatters
const formatDate = (dateStr: string) => {
  return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: fr })
}

const formatDateTime = (dateStr: string | null) => {
  if (!dateStr) return '-'
  return format(parseISO(dateStr), 'dd/MM/yyyy HH:mm', { locale: fr })
}

const getRetardColor = (minutes: number) => {
  if (minutes < 30) return '#ff9800'
  if (minutes < 60) return '#f44336'
  return '#9c27b0'
}

// Lifecycle
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshData()
})

onUnmounted(() => {
  // Cleanup si nécessaire
})
</script>

<style scoped>
/* Copie exacte des styles de Conges.vue + adaptations */

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

.stats-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.stat-en-attente,
.stat-heures {
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.stat-en-attente {
  background-color: #d1fae5;
  color: #065f46;
}

.stat-heures {
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

.retards-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Custom select */
.custom-select {
  position: relative;
  display: inline-block;
}

.select-button {
  padding: 0.6rem 1.2rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  text-align: left;
  min-width: 150px;
}

.select-button.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.select-button.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.select-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  z-index: 10;
  width: 100%;
  max-height: 200px;
  overflow-y: auto;
}

.select-option {
  padding: 0.5rem 1rem;
  cursor: pointer;
}

.select-option:hover {
  background: #f8f9fa;
}

/* Modal styles */
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

.modal-header.success-header {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
}

.modal-header.header-validated {
  background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
  color: white;
}

.modal-header.header-refused {
  background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
  color: white;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
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

.btn-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: inherit;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.btn-close:hover {
  background: rgba(255,255,255,0.2);
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

.preview-box {
  background: #e8f5e9;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #4caf50;
  color: #2e7d32;
  font-weight: 500;
}

.modal-subtitle {
  margin: 0 0 1.5rem 0;
  color: #666;
}

/* Détails */
.detail-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ff9800 0%, #f44336 100%);
  border-radius: 12px;
  margin-bottom: 1.5rem;
  color: white;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 3px solid white;
}

.detail-user-info h4 {
  margin: 0 0 0.5rem 0;
  font-size: 1.3rem;
}

.detail-meta {
  margin: 0.25rem 0;
  opacity: 0.9;
  font-size: 0.9rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
  font-weight: 600;
}

.detail-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  color: white;
  font-weight: 500;
  font-size: 0.9rem;
  width: fit-content;
}

.detail-deduction {
  color: #e74c3c;
  font-weight: bold;
  font-size: 1.1rem;
}

.detail-urgent {
  color: #f44336;
  font-weight: bold;
  font-size: 1.1rem;
}

.status-en_attente { background: #ff9800; }
.status-approuve { background: #4caf50; }
.status-annule { background: #9e9e9e; }

.detail-motif {
  margin: 0;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #ff9800;
  font-style: italic;
  color: #495057;
}

/* Validation boxes */
.validation-box {
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.validated-box {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.refused-box {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.validation-box h5 {
  margin: 0 0 8px 0;
  font-size: 0.9em;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.refusal-comment {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid rgba(0,0,0,0.1);
}

.refusal-comment label {
  font-weight: 600;
  color: #d32f2f;
  display: block;
  margin-bottom: 5px;
}

.refusal-comment p {
  margin: 0;
  font-style: italic;
  color: #555;
}

/* Rattrapages section */
.rattrapages-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.rattrapages-section h5 {
  margin: 0 0 12px 0;
  color: #4caf50;
  font-size: 0.9em;
  text-transform: uppercase;
}

.rattrapage-detail {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #e0e0e0;
}

.rattrapage-detail:last-child {
  border-bottom: none;
}

.rattrapage-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rattrapage-date {
  font-weight: 500;
  color: #333;
}

.rattrapage-heure {
  font-size: 0.85em;
  color: #666;
}

.rattrapage-duree {
  background: #4caf50;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-weight: 600;
  font-size: 0.9em;
}

/* Header badges */
.header-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.7em;
  margin-left: 10px;
  font-weight: bold;
}

.header-badge.validated {
  background: rgba(255,255,255,0.3);
  border: 1px solid rgba(255,255,255,0.5);
}

.header-badge.refused {
  background: rgba(255,255,255,0.3);
  border: 1px solid rgba(255,255,255,0.5);
}

/* Buttons */
.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn-success {
  padding: 0.75rem 1.5rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-success:hover {
  background: #45a049;
}

.btn-warning {
  padding: 0.75rem 1.5rem;
  background: #ff9800;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.95rem;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-warning:hover {
  background: #f57c00;
}

/* Error styles */
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
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>