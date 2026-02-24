<template>
  <!-- Header avec résumé -->
  <div class="page-header">
    <div class="header-left">
      <h1>Gestion des OSTIES</h1>
      <div v-if="authStore.user" class="ostie-badge">
        <span class="osties-total">{{ totalOsties }} total</span>
        <span class="osties-encours">{{ ostiesEnAttente.length }} en attente</span>
      </div>
    </div>
    
    <div class="header-actions">
      <button v-if="ostieStore.canManageOthers" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i> Ajouter un OSTIE
      </button>
    </div>
  </div>

  <!-- Filtres avancés pour managers/admins -->
  <div v-if="ostieStore.isManagerOrAdmin || ostieStore.isSuperAdmin" class="filters-bar">
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
        :class="{ active: statusFilter === 'en_attente' }" 
        @click="setStatusFilter('en_attente')"
      >
        En attente
      </button>
      <button 
        :class="{ active: statusFilter === 'approuve' }" 
        @click="setStatusFilter('approuve')"
      >
        Approuvés
      </button>
      <button 
        :class="{ active: statusFilter === 'transforme' }" 
        @click="setStatusFilter('transforme')"
      >
        Transformés
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
        :class="{ active: statusFilter === 'en_attente' }" 
        @click="setStatusFilter('en_attente')"
      >
        En attente
      </button>
      <button 
        :class="{ active: statusFilter === 'approuve' }" 
        @click="setStatusFilter('approuve')"
      >
        Approuvés
      </button>
      <button 
        :class="{ active: statusFilter === 'transforme' }" 
        @click="setStatusFilter('transforme')"
      >
        Transformés
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

  <!-- Calendrier des OSTIES -->
  <Calendar
    :events="filteredEventsForCalendar"
    :blocked-dates="blockedDates"
    :default-view="'month'"
    class="ostie-calendar"
    @event-click="onEventClick"
  />

  <!-- Modal Création d'OSTIE -->
  <Teleport to="body">
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>{{ ostieStore.canManageOthers ? 'Ajouter un OSTIE' : 'Demander un OSTIE' }}</h3>
          <button class="btn-close" @click="closeCreateModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Sélection de l'utilisateur (pour managers) -->
          <div v-if="ostieStore.canManageOthers" class="form-group">
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

          <!-- Info utilisateur normal -->
          <div v-else-if="authStore.user" class="user-info-form">
            <div class="avatar-small">{{ userInitials }}</div>
            <div>
              <p class="user-name">{{ authStore.user.display_name }} ({{ authStore.user.username.toUpperCase() }})</p>
            </div>
          </div>

          <!-- Date de l'OSTIE -->
          <div class="form-group">
            <label>Date de l'OSTIE <span class="required">*</span></label>
            <input 
              type="date" 
              v-model="form.date"
              :min="today"
              class="form-input"
              @change="onDateChange"
            />
          </div>

          <!-- Heure de début -->
          <div class="form-group">
            <label>Heure de début <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="form.heure_debut"
              class="form-input"
              step="60"
            />
          </div>

          <!-- Motif -->
          <div class="form-group">
            <label>Motif (optionnel)</label>
            <input 
              type="text" 
              v-model="form.motif" 
              class="form-input"
              placeholder="Raison de l'OSTIE..."
            />
          </div>

          <!-- Erreur globale -->
          <div v-if="formError" class="alert-error">
            <i class="bi bi-exclamation-triangle"></i>
            {{ formError }}
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeCreateModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="submitForm"
            :disabled="!isFormValid || submitting"
          >
            <i v-if="submitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Enregistrer l'OSTIE</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Détails de l'OSTIE -->
  <Teleport to="body">
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal modal-large">
        <div class="modal-header" :class="'header-' + (selectedOstie?.statut || '')">
          <h3>
            Détails de l'OSTIE
            <span class="header-badge" :class="selectedOstie?.statut">
              {{ selectedOstie?.statut_display }}
            </span>
          </h3>
          <button class="btn-close" @click="closeDetailModal">×</button>
        </div>

        <div class="modal-body" v-if="selectedOstie">
          <!-- Section utilisateur -->
          <div class="detail-section">
            <div class="detail-avatar">{{ getInitials(selectedOstie.utilisateur_details?.display_name || '') }}</div>
            <div class="detail-user-info">
              <h4>{{ selectedOstie.utilisateur_details?.display_name }}</h4>
              <p class="detail-meta">{{ selectedOstie.utilisateur_details?.username?.toUpperCase() }}</p>
            </div>
          </div>

          <!-- Informations de l'OSTIE -->
          <div class="detail-grid">
            <div class="detail-item">
              <label>Date</label>
              <span>{{ formatDate(selectedOstie.date) }}</span>
            </div>
            
            <div class="detail-item">
              <label>Heure début</label>
              <span>{{ formatTime(selectedOstie.heure_debut) }}</span>
            </div>

            <div v-if="selectedOstie.heure_fin" class="detail-item">
              <label>Heure fin</label>
              <span>{{ formatTime(selectedOstie.heure_fin) }}</span>
            </div>

            <div class="detail-item full-width">
              <label>Motif</label>
              <p class="detail-motif">{{ selectedOstie.motif || 'Non spécifié' }}</p>
            </div>
          </div>

          <!-- Lien vers le repos médical généré (si transformé) -->
          <div v-if="selectedOstie.statut === 'transforme' && selectedOstie.repos_genere_details" 
              class="info-box transformation-box">
            <h5>🔄 Transformé en Repos Médical</h5>
            <p>
              <strong>Date:</strong> {{ formatDate(selectedOstie.repos_genere_details.date) }} |
              <strong>Heures:</strong> {{ selectedOstie.repos_genere_details.heure_debut }} - {{ selectedOstie.repos_genere_details.heure_fin }}
            </p>
            <p class="detail-meta">Voir dans l'onglet Repos Médical</p>
          </div>

          <!-- Info validation -->
          <div v-if="selectedOstie.statut === 'approuve' && selectedOstie.valide_par_details" 
              class="validation-box approved-box">
            <h5>✓ Approuvé par</h5>
            <p><strong>{{ selectedOstie.valide_par_details.display_name }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedOstie.date_validation || '') }}</p>
          </div>

          <!-- Info annulation -->
          <div v-if="selectedOstie.statut === 'annule' && selectedOstie.annule_par_details" 
              class="validation-box cancelled-box">
            <h5>✗ Annulé par</h5>
            <p><strong>{{ selectedOstie.annule_par_details.display_name }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedOstie.date_annulation || '') }}</p>
            <p v-if="selectedOstie.commentaire_annulation" class="cancelled-comment">
              {{ selectedOstie.commentaire_annulation }}
            </p>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
          
          <!-- Bouton Valider (avec saisie heure de fin) -->
          <button 
            v-if="peutValider(selectedOstie) && canManageThisOstie(selectedOstie)"
            class="btn-success"
            @click="openValidationModal"
          >
            <i class="bi bi-check-circle"></i> Valider
          </button>
          
          <!-- Bouton transformer en repos médical -->
          <button 
            v-if="peutTransformerEnRepos(selectedOstie) && canManageThisOstie(selectedOstie)"
            class="btn-primary"
            @click="openTransformationModal"
          >
            <i class="bi bi-arrow-right-circle"></i> Transformer en Repos Médical
          </button>
          
          <!-- Bouton annuler -->
          <button 
            v-if="peutAnnuler(selectedOstie) && canManageThisOstie(selectedOstie)"
            class="btn-warning"
            @click="cancelSelectedOstie"
          >
            <i class="bi bi-x-circle"></i> Annuler
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Validation (saisie heure de fin) -->
  <Teleport to="body">
    <div v-if="showValidationModal" class="modal-overlay" @click.self="closeValidationModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Valider l'OSTIE</h3>
          <button class="btn-close" @click="closeValidationModal">×</button>
        </div>

        <div class="modal-body">
          <div class="info-permission">
            <p>OSTIE du <strong>{{ formatDate(selectedOstie?.date || '') }}</strong></p>
            <p>Début à <strong>{{ formatTime(selectedOstie?.heure_debut) }}</strong></p>
          </div>

          <div class="form-group">
            <label>Heure de fin <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="validationForm.heure_fin"
              class="form-input"
              step="60"
              @change="validateHeureFin"
            />
          </div>

          <!-- Aperçu de la durée -->
          <div v-if="validationForm.heure_fin" class="preview-box info-box">
            <p><strong>⏱️ Durée totale</strong></p>
            <p>{{ calculateDuree }} heures</p>
          </div>

          <div v-if="validationError" class="alert-error">
            {{ validationError }}
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeValidationModal">Annuler</button>
          <button 
            class="btn-success" 
            @click="submitValidation"
            :disabled="!validationForm.heure_fin || validationSubmitting"
          >
            <i v-if="validationSubmitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Valider l'OSTIE</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Transformation en Repos Médical -->
  <Teleport to="body">
    <div v-if="showTransformationModal" class="modal-overlay" @click.self="closeTransformationModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Transformer en Repos Médical</h3>
          <button class="btn-close" @click="closeTransformationModal">×</button>
        </div>

        <div class="modal-body">
          <div class="info-permission warning-box">
            <p>OSTIE du <strong>{{ formatDate(selectedOstie?.date || '') }}</strong></p>
            <p>Début à <strong>{{ formatTime(selectedOstie?.heure_debut) }}</strong></p>
            <p class="info-text">Ce repos médical sera créé avec le statut "En attente"</p>
          </div>

          <div class="form-group">
            <label>Heure de fin de l'OSTIE <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="transformationForm.heure_fin_ostie"
              class="form-input"
              step="60"
              @change="validateTransformation"
            />
          </div>

          <div class="form-group">
            <label>Heure de fin du Repos Médical <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="transformationForm.heure_fin_repos"
              class="form-input"
              step="60"
              @change="validateTransformation"
            />
            <span class="help-text">Le repos médical commencera à {{ transformationForm.heure_fin_ostie }} et finira à cette heure</span>
          </div>

          <!-- Aperçu des durées -->
          <div v-if="transformationForm.heure_fin_ostie && transformationForm.heure_fin_repos" 
               class="preview-box" 
               :class="transformationValid ? 'info-box' : 'warning-box'">
            <p><strong>📊 Récapitulatif</strong></p>
            <p>OSTIE : {{ formatTime(selectedOstie?.heure_debut) }} → {{ transformationForm.heure_fin_ostie }} 
               ({{ calculateDureeOstie }}h)</p>
            <p>Repos Médical : {{ transformationForm.heure_fin_ostie }} → {{ transformationForm.heure_fin_repos }} 
               ({{ calculateDureeRepos }}h)</p>
            <p v-if="!transformationValid" class="error-text">
              ⚠️ L'heure de fin du repos doit être après l'heure de fin de l'OSTIE
            </p>
          </div>

          <div v-if="transformationError" class="alert-error">
            {{ transformationError }}
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeTransformationModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="submitTransformation"
            :disabled="!isTransformationValid || transformationSubmitting"
          >
            <i v-if="transformationSubmitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Confirmer la transformation</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useOstieStore } from '@/store/ostie'
import { useCongesStore } from '@/store/conges'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { GerableUserOstie, Ostie } from '@/types/ostie'
import { format, parseISO, getYear, differenceInMinutes, addDays } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Stores
const authStore = useAuthStore()
const ostieStore = useOstieStore()
const congesStore = useCongesStore()
const filtersStore = useFiltersStore()

// Clés localStorage
const STORAGE_KEY_STATUS = 'alimanaka_ostie_status_filter'

// État local
const filters = ref({
  pole: null as number | null,
  equipe: null as number | null
})

const statusFilter = ref<'tous' | 'en_attente' | 'approuve' | 'transforme' | 'annule'>(
  (localStorage.getItem(STORAGE_KEY_STATUS) as any) || 'tous'
)

const showPoleDropdown = ref(false)
const showEquipeDropdown = ref(false)

const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showValidationModal = ref(false)
const showTransformationModal = ref(false)

const loading = ref(false)
const submitting = ref(false)
const validationSubmitting = ref(false)
const transformationSubmitting = ref(false)

const formError = ref<string | null>(null)
const validationError = ref<string | null>(null)
const transformationError = ref<string | null>(null)

// Sélection utilisateur (pour managers)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUser = ref<GerableUserOstie | null>(null)

// OSTIE sélectionné
const selectedOstie = ref<Ostie | null>(null)

// Formulaire principal
const form = ref({
  date: '',
  heure_debut: '',
  motif: ''
})

// Formulaire validation
const validationForm = ref({
  heure_fin: ''
})

// Formulaire transformation
const transformationForm = ref({
  heure_fin_ostie: '',
  heure_fin_repos: ''
})

// ============================================
// Computed pour les filtres
// ============================================

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

// ============================================
// Fonctions utilitaires
// ============================================

const parseTime = (timeStr: string | undefined): { hours: number; minutes: number } => {
  if (!timeStr) return { hours: 0, minutes: 0 }
  const parts = timeStr.split(':')
  return {
    hours: parts[0] ? parseInt(parts[0]) || 0 : 0,
    minutes: parts[1] ? parseInt(parts[1]) || 0 : 0
  }
}

const formatTime = (timeStr: string | undefined): string => {
  if (!timeStr) return '--:--'
  return String(timeStr).substring(0, 5)
}

// ============================================
// Méthodes de filtrage
// ============================================

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

// ============================================
// Computed
// ============================================

// Calcul de la durée pour validation
const calculateDuree = computed(() => {
  if (!selectedOstie.value || !validationForm.value.heure_fin) return '0.00'
  
  const debut = parseTime(selectedOstie.value.heure_debut)
  const fin = parseTime(validationForm.value.heure_fin)
  
  const debutDate = new Date(selectedOstie.value.date)
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date(selectedOstie.value.date)
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  const minutes = differenceInMinutes(finDate, debutDate)
  return (minutes / 60).toFixed(2)
})

// Calcul de la durée de l'OSTIE pour transformation
const calculateDureeOstie = computed(() => {
  if (!selectedOstie.value || !transformationForm.value.heure_fin_ostie) return '0.00'
  
  const debut = parseTime(selectedOstie.value.heure_debut)
  const fin = parseTime(transformationForm.value.heure_fin_ostie)
  
  const debutDate = new Date(selectedOstie.value.date)
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date(selectedOstie.value.date)
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  const minutes = differenceInMinutes(finDate, debutDate)
  return (minutes / 60).toFixed(2)
})

// Calcul de la durée du repos pour transformation
const calculateDureeRepos = computed(() => {
  if (!selectedOstie.value || 
      !transformationForm.value.heure_fin_ostie || 
      !transformationForm.value.heure_fin_repos) return '0.00'
  
  const debut = parseTime(transformationForm.value.heure_fin_ostie)
  const fin = parseTime(transformationForm.value.heure_fin_repos)
  
  const debutDate = new Date(selectedOstie.value.date)
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date(selectedOstie.value.date)
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  const minutes = differenceInMinutes(finDate, debutDate)
  return (minutes / 60).toFixed(2)
})

// Validation du formulaire de transformation
const transformationValid = computed(() => {
  if (!transformationForm.value.heure_fin_ostie || !transformationForm.value.heure_fin_repos) return false
  
  const finOstie = parseTime(transformationForm.value.heure_fin_ostie)
  const finRepos = parseTime(transformationForm.value.heure_fin_repos)
  
  const finOstieDate = new Date()
  finOstieDate.setHours(finOstie.hours, finOstie.minutes, 0)
  
  const finReposDate = new Date()
  finReposDate.setHours(finRepos.hours, finRepos.minutes, 0)
  
  return finReposDate > finOstieDate
})

const isTransformationValid = computed(() => {
  return transformationForm.value.heure_fin_ostie && 
         transformationForm.value.heure_fin_repos && 
         transformationValid.value
})

// Événements filtrés pour le calendrier
const filteredEventsForCalendar = computed<CalendarEvent[]>(() => {
  return ostieStore.eventsForCalendar
})

// Dates bloquées
const blockedDates = computed(() => {
  const congesEvents = congesStore.calendrierEvents
  
  return congesEvents
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

// Totaux
const totalOsties = computed(() => ostieStore.totalOsties)
const ostiesEnAttente = computed(() => ostieStore.ostiesEnAttente)

// Initials pour l'avatar
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

// Date aujourd'hui
const today = computed(() => format(new Date(), 'yyyy-MM-dd'))

// Utilisateurs filtrés pour le dropdown
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return ostieStore.utilisateursGerables
  
  const query = userSearchQuery.value.toLowerCase()
  return ostieStore.utilisateursGerables.filter(u => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

// Validation du formulaire
const isFormValid = computed(() => {
  const baseValid = form.value.date && form.value.heure_debut
  
  if (ostieStore.canManageOthers && !selectedUser.value) {
    return false
  }
  
  return baseValid
})

// ============================================
// Méthodes
// ============================================

const getInitials = (name: string) => name.charAt(0).toUpperCase()

const formatDate = (dateStr: string): string => {
  if (!dateStr) return ''
  return format(parseISO(dateStr), 'dd/MM/yyyy', { locale: fr })
}

const formatDateTime = (dateStr: string): string => {
  if (!dateStr) return ''
  return format(parseISO(dateStr), 'dd/MM/yyyy HH:mm', { locale: fr })
}

const setStatusFilter = (filter: 'tous' | 'en_attente' | 'approuve' | 'transforme' | 'annule') => {
  statusFilter.value = filter
  localStorage.setItem(STORAGE_KEY_STATUS, filter)
  refreshData()
}

const onUserSearch = () => {
  showUserDropdown.value = true
}

const selectUser = (user: GerableUserOstie) => {
  selectedUser.value = user
  showUserDropdown.value = false
  userSearchQuery.value = ''
}

const onDateChange = () => {
  if (form.value.date < today.value) {
    formError.value = "La date de l'OSTIE ne peut pas être dans le passé"
    form.value.date = ''
  } else {
    formError.value = null
  }
}

// Validation des heures
const validateHeureFin = () => {
  if (!validationForm.value.heure_fin || !selectedOstie.value) return
  
  const debut = parseTime(selectedOstie.value.heure_debut)
  const fin = parseTime(validationForm.value.heure_fin)
  
  const debutDate = new Date()
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date()
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  if (finDate <= debutDate) {
    validationError.value = "L'heure de fin doit être après l'heure de début"
  } else {
    validationError.value = null
  }
}

const validateTransformation = () => {
  if (!transformationForm.value.heure_fin_ostie || !transformationForm.value.heure_fin_repos) return
  
  const finOstie = parseTime(transformationForm.value.heure_fin_ostie)
  const finRepos = parseTime(transformationForm.value.heure_fin_repos)
  
  const finOstieDate = new Date()
  finOstieDate.setHours(finOstie.hours, finOstie.minutes, 0)
  
  const finReposDate = new Date()
  finReposDate.setHours(finRepos.hours, finRepos.minutes, 0)
  
  if (finReposDate <= finOstieDate) {
    transformationError.value = "L'heure de fin du repos médical doit être après l'heure de fin de l'OSTIE"
  } else {
    transformationError.value = null
  }
}

// Création
const openCreateModal = async () => {
  formError.value = null
  form.value = {
    date: '',
    heure_debut: '',
    motif: ''
  }
  selectedUser.value = null
  userSearchQuery.value = ''
  
  try {
    if (ostieStore.canManageOthers) {
      await ostieStore.fetchUtilisateursGerables()
    }
    
    showCreateModal.value = true
    
  } catch (error) {
    console.error('Erreur lors du chargement:', error)
    formError.value = "Erreur lors du chargement des données"
  }
}

const closeCreateModal = () => {
  showCreateModal.value = false
  selectedUser.value = null
  formError.value = null
}

const submitForm = async () => {
  if (!isFormValid.value) return
  
  submitting.value = true
  formError.value = null
  
  try {
    const payload = {
      date: form.value.date,
      heure_debut: form.value.heure_debut,
      motif: form.value.motif
    }
    
    const userId = selectedUser.value?.id
    
    await ostieStore.createOstie(payload, userId)
    
    closeCreateModal()
    alert('OSTIE enregistré avec succès !')
    await refreshData()
    
  } catch (err: any) {
    formError.value = err.response?.data?.error || err.response?.data?.detail || 'Erreur lors de l\'enregistrement'
  } finally {
    submitting.value = false
  }
}

// Détails
const onEventClick = (event: CalendarEvent) => {
  const ostieId = parseInt(String(event.id).replace('ostie_', ''))
  loadOstieDetails(ostieId)
}

const loadOstieDetails = async (id: number) => {
  try {
    selectedOstie.value = await ostieStore.getOstieDetails(id)
    showDetailModal.value = true
  } catch (e) {
    console.error('Erreur chargement détails:', e)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedOstie.value = null
}

// Validation
const openValidationModal = () => {
  validationError.value = null
  validationForm.value = {
    heure_fin: ''
  }
  showValidationModal.value = true
}

const closeValidationModal = () => {
  showValidationModal.value = false
}

const submitValidation = async () => {
  if (!selectedOstie.value || !validationForm.value.heure_fin) return
  if (validationError.value) return
  
  validationSubmitting.value = true
  
  try {
    await ostieStore.validerOstie(selectedOstie.value.id, {
      heure_fin: validationForm.value.heure_fin
    })
    
    closeValidationModal()
    closeDetailModal()
    alert('OSTIE validé avec succès !')
    await refreshData()
    
  } catch (err: any) {
    validationError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    validationSubmitting.value = false
  }
}

// Transformation
const openTransformationModal = () => {
  transformationError.value = null
  transformationForm.value = {
    heure_fin_ostie: '',
    heure_fin_repos: ''
  }
  showTransformationModal.value = true
}

const closeTransformationModal = () => {
  showTransformationModal.value = false
}

const submitTransformation = async () => {
  if (!selectedOstie.value || !isTransformationValid.value) return
  if (transformationError.value) return
  
  transformationSubmitting.value = true
  
  try {
    await ostieStore.transformerEnRepos(selectedOstie.value.id, {
      heure_fin_ostie: transformationForm.value.heure_fin_ostie,
      heure_fin_repos: transformationForm.value.heure_fin_repos
    })
    
    closeTransformationModal()
    closeDetailModal()
    alert('OSTIE transformé en repos médical avec succès !')
    await refreshData()
    
  } catch (err: any) {
    transformationError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    transformationSubmitting.value = false
  }
}

// Annulation
const peutValider = (ostie: Ostie | null): boolean => {
  return ostieStore.peutValider(ostie)
}

const peutTransformerEnRepos = (ostie: Ostie | null): boolean => {
  return ostieStore.peutTransformerEnRepos(ostie)
}

const peutAnnuler = (ostie: Ostie | null): boolean => {
  return ostieStore.peutAnnuler(ostie)
}

const canManageThisOstie = (ostie: Ostie | null): boolean => {
  return ostieStore.canManageThisOstie(ostie)
}

const cancelSelectedOstie = async () => {
  if (!selectedOstie.value) return
  
  const commentaire = prompt('Motif de l\'annulation (optionnel):')
  if (commentaire === null) return
  
  if (confirm('Voulez-vous vraiment annuler cet OSTIE ?')) {
    await ostieStore.annulerOstie(selectedOstie.value.id, commentaire || undefined)
    closeDetailModal()
    await refreshData()
  }
}

// Rafraîchissement
const refreshData = async () => {
  loading.value = true
  
  const currentYear = getYear(new Date())
  const params: any = { 
    annee: currentYear,
    statut: statusFilter.value === 'tous' ? undefined : statusFilter.value
  }
  
  if (filters.value.pole) params.pole = filters.value.pole
  if (filters.value.equipe) params.equipe = filters.value.equipe
  
  await Promise.all([
    ostieStore.fetchCalendrier(params),
    ostieStore.fetchMesOsties(currentYear),
    congesStore.fetchCalendrier({ annee: currentYear })
  ])
  
  loading.value = false
}

// Cycle de vie
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  await refreshData()
})
</script>

<style scoped>
/* Mêmes styles que Permissions.vue et ReposMedicale.vue */
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

.ostie-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.osties-total {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.osties-encours {
  background-color: #fef3c7;
  color: #92400e;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: linear-gradient(90deg, rgb(25,169,203) 0%, rgb(43,122,186) 100%);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(90deg, rgb(36,59,107) 0%, rgb(181,9,1) 100%);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  flex-wrap: wrap;
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
  background: linear-gradient(90deg, rgb(25,169,203) 0%, rgb(43,122,186) 100%);
  color: white;
  border-color: transparent;
}

.filter-tabs button:hover:not(.active) {
  background: #f8f9fa;
  border-color: #3498db;
}

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

.ostie-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Modal styles - identiques aux autres modules */
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
  max-width: 700px;
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.btn-close {
  background: rgba(255,255,255,0.2);
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
}

.btn-close:hover {
  background: rgba(255,255,255,0.3);
  transform: rotate(90deg);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.modal-actions {
  padding: 1.25rem 1.5rem;
  border-top: 1px solid #e9ecef;
  background: #f8f9fa;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-shrink: 0;
}

/* Form styles */
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

.help-text {
  margin-top: 0.5rem;
  color: #6c757d;
  font-size: 0.9rem;
}

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

/* Buttons */
.btn-secondary {
  padding: 0.625rem 1.25rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #5a6268;
}

.btn-success {
  padding: 0.625rem 1.5rem;
  background: #28a745;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-success:hover {
  background: #218838;
}

.btn-warning {
  padding: 0.625rem 1.5rem;
  background: #ffc107;
  color: #212529;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.btn-warning:hover {
  background: #e0a800;
}

/* User selection */
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
  border-radius: 6px;
  box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
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
  border-radius: 6px;
  margin-top: 0.5rem;
}

.avatar-small {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: bold;
}

.user-name {
  font-weight: 600;
  margin: 0;
}

.btn-change-user {
  margin-left: auto;
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
  color: #3b82f6;
  background: none;
  border: 1px solid #3b82f6;
  border-radius: 4px;
  cursor: pointer;
}

.btn-change-user:hover {
  background: #eff6ff;
}

.user-info-form {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

/* Preview boxes */
.preview-box {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid;
}

.info-box {
  background: #e3f2fd;
  border-left-color: #2196f3;
}

.warning-box {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.transformation-box {
  background: #f3e5f5;
  border-left-color: #9c27b0;
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
}

/* Info permission */
.info-permission {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #2196f3;
}

.info-permission p {
  margin: 0.25rem 0;
}

/* Detail styles */
.detail-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
  margin-bottom: 1.5rem;
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

.detail-motif {
  margin: 0;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #3498db;
  font-style: italic;
}

/* Validation boxes */
.validation-box {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.approved-box {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.cancelled-box {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.cancelled-comment {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
  font-style: italic;
}

/* Header variants */
.header-en_attente { background: #ff9800 !important; }
.header-approuve { background: #4caf50 !important; }
.header-transforme { background: #9c27b0 !important; }
.header-annule { background: #9e9e9e !important; }

.header-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.7em;
  margin-left: 10px;
  font-weight: bold;
  background: rgba(255,255,255,0.3);
}

/* Spin animation */
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
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .modal {
    width: 95%;
    max-height: 95vh;
  }
  
  .filter-tabs {
    width: 100%;
  }
  
  .filter-tabs button {
    flex: 1;
    min-width: 0;
    padding: 0.5rem;
    font-size: 0.8rem;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>