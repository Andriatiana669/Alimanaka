<template>
  <!-- Header avec résumé -->
  <div class="page-header">
    <div class="header-left">
      <h1>Gestion des Repos Médicaux</h1>
      <div v-if="authStore.user" class="repos-badge">
        <span class="heures-total">{{ totalHeuresRepos.toFixed(2) }}h total</span>
        <span class="repos-encours">{{ reposEnAttente.length }} en attente</span>
      </div>
    </div>
    
    <div class="header-actions">
      <button v-if="reposStore.canManageOthers" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i> Ajouter un repos médical
      </button>
    </div>
  </div>

  <!-- Filtres avancés pour managers/admins -->
  <div v-if="reposStore.isManagerOrAdmin || reposStore.isSuperAdmin" class="filters-bar">
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

  <!-- Calendrier des repos médicaux -->
  <Calendar
    :events="filteredEventsForCalendar"
    :blocked-dates="blockedDates"
    :default-view="'month'"
    class="repos-calendar"
    @event-click="onEventClick"
  />

  <!-- Modal Création de repos médical -->
  <Teleport to="body">
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>{{ reposStore.canManageOthers ? 'Ajouter un repos médical' : 'Demander un repos médical' }}</h3>
          <button class="btn-close" @click="closeCreateModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Sélection de l'utilisateur (pour managers) -->
          <div v-if="reposStore.canManageOthers" class="form-group">
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

          <!-- Date du repos -->
          <div class="form-group">
            <label>Date du repos <span class="required">*</span></label>
            <input 
              type="date" 
              v-model="form.date"
              :min="today"
              class="form-input"
              @change="onDateChange"
            />
          </div>

          <!-- Heures -->
          <div class="form-row">
            <div class="form-group">
              <label>Heure de début <span class="required">*</span></label>
              <input 
                type="time" 
                v-model="form.heure_debut"
                class="form-input"
                step="60"
                @change="validateHeures"
              />
            </div>

            <div class="form-group">
              <label>Heure de fin <span class="required">*</span></label>
              <input 
                type="time" 
                v-model="form.heure_fin"
                class="form-input"
                step="60"
                @change="validateHeures"
              />
            </div>
          </div>

          <!-- Aperçu de la durée -->
          <div v-if="form.date && form.heure_debut && form.heure_fin" class="preview-box info-box">
            <p><strong>⏱️ Durée du repos</strong></p>
            <p>{{ calculateDuree }} heures</p>
            <p v-if="dureeError" class="error-text">{{ dureeError }}</p>
          </div>

          <!-- Motif -->
          <div class="form-group">
            <label>Motif</label>
            <input 
              type="text" 
              v-model="form.motif" 
              class="form-input"
              placeholder="Malade (par défaut)"
            />
            <span class="help-text">Par défaut: "Malade"</span>
          </div>

          <!-- Avertissement -->
          <div class="form-group">
            <label>Avertissement</label>
            <textarea 
              v-model="form.avertissement" 
              rows="2" 
              class="form-textarea"
              placeholder="N'oublie pas d'apporter ton justificatif médical (PJ)"
            ></textarea>
            <span class="help-text">Message affiché à l'utilisateur</span>
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
            <span v-else>Enregistrer le repos médical</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Détails du repos médical -->
  <Teleport to="body">
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal modal-large">
        <div class="modal-header" :class="'header-' + (selectedRepos?.statut || '')">
          <h3>
            Détails du repos médical
            <span class="header-badge" :class="selectedRepos?.statut">
              {{ selectedRepos?.statut_display }}
            </span>
          </h3>
          <button class="btn-close" @click="closeDetailModal">×</button>
        </div>

        <div class="modal-body" v-if="selectedRepos">
          <!-- Section utilisateur -->
          <div class="detail-section">
            <div class="detail-avatar">{{ getInitials(selectedRepos.utilisateur_details?.display_name || '') }}</div>
            <div class="detail-user-info">
              <h4>{{ selectedRepos.utilisateur_details?.display_name }}</h4>
              <p class="detail-meta">{{ selectedRepos.utilisateur_details?.username?.toUpperCase() }}</p>
            </div>
          </div>

          <!-- Informations du repos -->
          <div class="detail-grid">
            <div class="detail-item">
              <label>Date</label>
              <span>{{ formatDate(selectedRepos.date) }}</span>
            </div>
            
            <div class="detail-item">
              <label>Heure début</label>
              <span>{{ formatTime(selectedRepos.heure_debut) }}</span>
            </div>

            <div class="detail-item">
              <label>Heure fin</label>
              <span>{{ formatTime(selectedRepos.heure_fin) }}</span>
            </div>

            <div class="detail-item">
              <label>Durée</label>
              <span class="detail-duree">{{ selectedRepos.duree_heures }}h</span>
            </div>

            <div class="detail-item full-width">
              <label>Motif</label>
              <p class="detail-motif">{{ selectedRepos.motif || 'Malade' }}</p>
            </div>

            <div v-if="selectedRepos.avertissement" class="detail-item full-width">
              <label>Avertissement</label>
              <p class="detail-avertissement">
                <i class="bi bi-exclamation-triangle"></i>
                {{ selectedRepos.avertissement }}
              </p>
            </div>
          </div>

          <!-- Lien vers le congé généré (si transformé) -->
          <div v-if="selectedRepos.statut === 'transforme' && selectedRepos.conge_genere_details" 
              class="info-box transformation-box">
            <h5>🔄 Transformé en congé</h5>
            <p>
              <strong>Type:</strong> {{ selectedRepos.conge_genere_details.type_conge }} |
              <strong>Statut:</strong> {{ selectedRepos.conge_genere_details.statut }}
            </p>
            <p class="detail-meta">Voir dans l'onglet Congés</p>
          </div>

          <!-- Info validation -->
          <div v-if="selectedRepos.statut === 'approuve' && selectedRepos.valide_par_details" 
              class="validation-box approved-box">
            <h5>✓ Approuvé par</h5>
            <p><strong>{{ selectedRepos.valide_par_details.display_name }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedRepos.date_validation || '') }}</p>
          </div>

          <!-- Info annulation -->
          <div v-if="selectedRepos.statut === 'annule' && selectedRepos.annule_par_details" 
              class="validation-box cancelled-box">
            <h5>✗ Annulé par</h5>
            <p><strong>{{ selectedRepos.annule_par_details.display_name }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedRepos.date_annulation || '') }}</p>
            <p v-if="selectedRepos.commentaire_annulation" class="cancelled-comment">
              {{ selectedRepos.commentaire_annulation }}
            </p>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
          
          <!-- Bouton Valider -->
          <button 
            v-if="peutValider(selectedRepos) && canManageThisRepos(selectedRepos)"
            class="btn-success"
            @click="validerSelectedRepos"
          >
            <i class="bi bi-check-circle"></i> Valider
          </button>
          
          <!-- Bouton transformer en congé -->
          <button 
            v-if="peutTransformerEnConge(selectedRepos) && canManageThisRepos(selectedRepos)"
            class="btn-primary"
            @click="openTransformationModal"
          >
            <i class="bi bi-calendar-plus"></i> Transformer en congé
          </button>
          
          <!-- Bouton annuler -->
          <button 
            v-if="peutAnnuler(selectedRepos) && canManageThisRepos(selectedRepos)"
            class="btn-warning"
            @click="cancelSelectedRepos"
          >
            <i class="bi bi-x-circle"></i> Annuler
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Transformation en congé -->
  <Teleport to="body">
    <div v-if="showTransformationModal" class="modal-overlay" @click.self="closeTransformationModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Transformer en congé</h3>
          <button class="btn-close" @click="closeTransformationModal">×</button>
        </div>

        <div class="modal-body">
          <div class="info-permission warning-box">
            <p><strong>⚠️ Repos médical de {{ selectedRepos?.duree_heures }} heures</strong></p>
            <p>Ce repos médical sera transformé en congé et déduit du solde.</p>
          </div>

          <div class="form-group">
            <label>Type de congé <span class="required">*</span></label>
            <div class="type-options">
              <label 
                v-for="type in typesConge" 
                :key="type.type_conge"
                class="type-option"
                :class="{ selected: transformationForm.type_conge === type.type_conge }"
              >
                <input 
                  type="radio" 
                  :value="type.type_conge"
                  v-model="transformationForm.type_conge"
                />
                <span class="type-label">{{ getTypeLabel(type.type_conge) }}</span>
                <span class="type-time">{{ type.heure_debut }} - {{ type.heure_fin }}</span>
                <span class="type-deduction">-{{ type.deduction_jours }}j</span>
              </label>
            </div>
          </div>

          <!-- Aperçu de la déduction -->
          <div v-if="transformationForm.type_conge && selectedType" class="preview-box info-box">
            <p>Déduction estimée: <strong>{{ selectedType.deduction_jours }} jour(s)</strong></p>
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
            :disabled="!transformationForm.type_conge || transformationSubmitting"
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
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useCongesStore } from '@/store/conges'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { GerableUserReposMedical, ReposMedical } from '@/types/reposmedicale'
import { format, parseISO, getYear, differenceInMinutes, addDays } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Stores
const authStore = useAuthStore()
const reposStore = useReposMedicaleStore()
const congesStore = useCongesStore()
const filtersStore = useFiltersStore()

// Clés localStorage
const STORAGE_KEY_STATUS = 'alimanaka_reposmedicale_status_filter'

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
const showTransformationModal = ref(false)

const loading = ref(false)
const submitting = ref(false)
const transformationSubmitting = ref(false)

const formError = ref<string | null>(null)
const transformationError = ref<string | null>(null)
const dureeError = ref<string | null>(null)

// Sélection utilisateur (pour managers)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUser = ref<GerableUserReposMedical | null>(null)

// Repos sélectionné
const selectedRepos = ref<ReposMedical | null>(null)

// Formulaire principal
const form = ref({
  date: '',
  heure_debut: '',
  heure_fin: '',
  motif: '',
  avertissement: "N'oublie pas d'apporter ton justificatif médical (PJ)"
})

// Formulaire transformation
const transformationForm = ref({
  type_conge: '' as 'matin' | 'midi' | 'journee' | ''
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

const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    matin: 'Matin',
    midi: 'Midi',
    journee: 'Journée'
  }
  return labels[type] || type
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

const typesConge = computed(() => reposStore.typesConge)

const selectedType = computed(() => {
  return typesConge.value.find(t => t.type_conge === transformationForm.value.type_conge)
})

// Calcul de la durée
const calculateDuree = computed(() => {
  if (!form.value.date || !form.value.heure_debut || !form.value.heure_fin) return '0.00'
  
  const debut = parseTime(form.value.heure_debut)
  const fin = parseTime(form.value.heure_fin)
  
  const debutDate = new Date(form.value.date)
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date(form.value.date)
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  const minutes = differenceInMinutes(finDate, debutDate)
  return (minutes / 60).toFixed(2)
})

// Validation des heures
const validateHeures = () => {
  if (!form.value.heure_debut || !form.value.heure_fin) return
  
  const debut = parseTime(form.value.heure_debut)
  const fin = parseTime(form.value.heure_fin)
  
  const debutDate = new Date()
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date()
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  if (finDate <= debutDate) {
    dureeError.value = "L'heure de fin doit être après l'heure de début"
  } else {
    dureeError.value = null
  }
}

// Événements filtrés pour le calendrier
const filteredEventsForCalendar = computed<CalendarEvent[]>(() => {
  return reposStore.eventsForCalendar
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

// Total des heures de repos
const totalHeuresRepos = computed(() => {
  return reposStore.totalHeuresRepos
})

const reposEnAttente = computed(() => reposStore.reposEnAttente)

// Initials pour l'avatar
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

// Date aujourd'hui
const today = computed(() => format(new Date(), 'yyyy-MM-dd'))

// Utilisateurs filtrés pour le dropdown
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return reposStore.utilisateursGerables
  
  const query = userSearchQuery.value.toLowerCase()
  return reposStore.utilisateursGerables.filter(u => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

// Validation du formulaire
const isFormValid = computed(() => {
  const baseValid = form.value.date && 
                   form.value.heure_debut && 
                   form.value.heure_fin && 
                   !dureeError.value
  
  if (reposStore.canManageOthers && !selectedUser.value) {
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

const selectUser = (user: GerableUserReposMedical) => {
  selectedUser.value = user
  showUserDropdown.value = false
  userSearchQuery.value = ''
}

const onDateChange = () => {
  if (form.value.date < today.value) {
    formError.value = "La date du repos médical ne peut pas être dans le passé"
    form.value.date = ''
  } else {
    formError.value = null
  }
}

// Création
const openCreateModal = async () => {
  formError.value = null
  dureeError.value = null
  form.value = {
    date: '',
    heure_debut: '',
    heure_fin: '',
    motif: '',
    avertissement: "N'oublie pas d'apporter ton justificatif médical (PJ)"
  }
  selectedUser.value = null
  userSearchQuery.value = ''
  
  try {
    if (reposStore.typesConge.length === 0) {
      await reposStore.fetchTypesConge()
    }
    
    if (reposStore.canManageOthers) {
      await reposStore.fetchUtilisateursGerables()
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
  dureeError.value = null
}

const submitForm = async () => {
  if (!isFormValid.value) return
  
  submitting.value = true
  formError.value = null
  
  try {
    const payload = {
      date: form.value.date,
      heure_debut: form.value.heure_debut,
      heure_fin: form.value.heure_fin,
      motif: form.value.motif || 'Malade',
      avertissement: form.value.avertissement
    }
    
    const userId = selectedUser.value?.id
    
    await reposStore.createReposMedical(payload, userId)
    
    closeCreateModal()
    alert('Repos médical enregistré avec succès !')
    await refreshData()
    
  } catch (err: any) {
    formError.value = err.response?.data?.error || err.response?.data?.detail || 'Erreur lors de l\'enregistrement'
  } finally {
    submitting.value = false
  }
}

// Détails
const onEventClick = (event: CalendarEvent) => {
  const reposId = parseInt(String(event.id).replace('repos_', ''))
  loadReposDetails(reposId)
}

const loadReposDetails = async (id: number) => {
  try {
    selectedRepos.value = await reposStore.getReposMedicalDetails(id)
    showDetailModal.value = true
  } catch (e) {
    console.error('Erreur chargement détails:', e)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedRepos.value = null
}

// Validation
const validerSelectedRepos = async () => {
  if (!selectedRepos.value) return
  
  if (confirm('Voulez-vous valider ce repos médical ?')) {
    await reposStore.validerReposMedical(selectedRepos.value.id)
    closeDetailModal()
    await refreshData()
  }
}

// Transformation
const openTransformationModal = () => {
  transformationError.value = null
  transformationForm.value = {
    type_conge: ''
  }
  showTransformationModal.value = true
}

const closeTransformationModal = () => {
  showTransformationModal.value = false
}

const submitTransformation = async () => {
  if (!selectedRepos.value || !transformationForm.value.type_conge) return
  
  transformationSubmitting.value = true
  transformationError.value = null
  
  try {
    await reposStore.transformerEnConge(
      selectedRepos.value.id, 
      transformationForm.value.type_conge
    )
    
    closeTransformationModal()
    closeDetailModal()
    alert('Repos médical transformé en congé avec succès !')
    await refreshData()
    
  } catch (err: any) {
    transformationError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    transformationSubmitting.value = false
  }
}

// Annulation
const peutValider = (repos: ReposMedical | null): boolean => {
  return reposStore.peutValider(repos)
}

const peutTransformerEnConge = (repos: ReposMedical | null): boolean => {
  return reposStore.peutTransformerEnConge(repos)
}

const peutAnnuler = (repos: ReposMedical | null): boolean => {
  return reposStore.peutAnnuler(repos)
}

const canManageThisRepos = (repos: ReposMedical | null): boolean => {
  return reposStore.canManageThisRepos(repos)
}

const cancelSelectedRepos = async () => {
  if (!selectedRepos.value) return
  
  const commentaire = prompt('Motif de l\'annulation (optionnel):')
  if (commentaire === null) return
  
  if (confirm('Voulez-vous vraiment annuler ce repos médical ?')) {
    await reposStore.annulerReposMedical(selectedRepos.value.id, commentaire || undefined)
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
    reposStore.fetchCalendrier(params),
    reposStore.fetchMesRepos(currentYear),
    congesStore.fetchCalendrier({ annee: currentYear })
  ])
  
  loading.value = false
}

// Cycle de vie
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  if (reposStore.typesConge.length === 0) {
    await reposStore.fetchTypesConge()
  }
  await refreshData()
})
</script>

<style scoped>
/* Mêmes styles que Permissions.vue */
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

.repos-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.heures-total {
  background-color: #e0f2fe;
  color: #0369a1;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.repos-encours {
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

.repos-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Modal styles - identiques à Permissions */
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

.form-textarea {
  resize: vertical;
  min-height: 80px;
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

.detail-duree {
  color: #2196f3;
  font-weight: bold;
}

.detail-motif {
  margin: 0;
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  border-left: 3px solid #3498db;
  font-style: italic;
}

.detail-avertissement {
  margin: 0;
  padding: 0.75rem;
  background: #fff3e0;
  border-radius: 6px;
  border-left: 3px solid #ff9800;
  color: #e65100;
}

.detail-avertissement i {
  margin-right: 0.5rem;
}

/* Type options (pour transformation) */
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
  
  .type-option {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .type-deduction {
    margin-left: 0;
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