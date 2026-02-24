<template>
  <!-- Header avec résumé -->
  <div class="page-header">
    <div class="header-left">
      <h1>Gestion des Permissions</h1>
      <div v-if="authStore.user" class="permission-badge">
        <span class="heures-restantes">{{ totalHeuresARattraper }}h à rattraper</span>
        <span class="permissions-encours">{{ permissionsRattrapage.length + permissionsRetournees.length }} en cours</span>
      </div>
    </div>
    
    <div class="header-actions">
      <button v-if="permissionsStore.canManageOthers" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i> Ajouter une permission
      </button>
    </div>
  </div>

  <!-- Filtres avancés pour managers/admins -->
  <div v-if="permissionsStore.isManagerOrAdmin || permissionsStore.isSuperAdmin" class="filters-bar">
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
        :class="{ active: statusFilter === 'retourne' }" 
        @click="setStatusFilter('retourne')"
      >
        Retournés
      </button>
      <button 
        :class="{ active: statusFilter === 'rattrapage' }" 
        @click="setStatusFilter('rattrapage')"
      >
        Rattrapage
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
        :class="{ active: statusFilter === 'retourne' }" 
        @click="setStatusFilter('retourne')"
      >
        Retournés
      </button>
      <button 
        :class="{ active: statusFilter === 'rattrapage' }" 
        @click="setStatusFilter('rattrapage')"
      >
        Rattrapage
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

  <!-- Calendrier des permissions -->
  <Calendar
    :events="filteredEventsForCalendar"
    :blocked-dates="blockedDates"
    :default-view="'month'"
    class="permissions-calendar"
    @event-click="onEventClick"
  />

  <!-- Modal Création de permission -->
  <Teleport to="body">
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>{{ permissionsStore.canManageOthers ? 'Ajouter une permission' : 'Demander une permission' }}</h3>
          <button class="btn-close" @click="closeCreateModal">×</button>
        </div>

        <div class="modal-body">
          <!-- Sélection de l'utilisateur (pour managers) -->
          <div v-if="permissionsStore.canManageOthers" class="form-group">
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

          <!-- Date de la permission -->
          <div class="form-group">
            <label>Date de la permission <span class="required">*</span></label>
            <input 
              type="date" 
              v-model="form.date"
              :min="today"
              class="form-input"
              @change="onDateChange"
            />
          </div>

          <!-- Heure de départ -->
          <div class="form-group">
            <label>Heure de départ <span class="required">*</span></label>
            <input 
              type="time" 
              v-model="form.heure_depart"
              class="form-input"
              step="60"
            />
          </div>

          <!-- Aperçu de l'heure d'arrivée max (calcul automatique) -->
          <div v-if="form.date && form.heure_depart" class="preview-box info-box">
            <p><strong>⏱️ Heure d'arrivée max</strong></p>
            <p>{{ formatTime(heureArriveeMax) }} (départ + 2h)</p>
          </div>

          <!-- Motif -->
          <div class="form-group">
            <label>Motif <span class="required">*</span></label>
            <textarea 
              v-model="form.motif" 
              rows="3" 
              placeholder="Raison de la permission..."
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
          <button class="btn-secondary" @click="closeCreateModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="submitForm"
            :disabled="!isFormValid || submitting"
          >
            <i v-if="submitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Enregistrer la permission</span>
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Détails de la permission -->
  <Teleport to="body">
    <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
      <div class="modal modal-large">
        <div class="modal-header" :class="'header-' + (selectedPermission?.statut || '')">
          <h3>
            Détails de la permission
            <span class="header-badge" :class="selectedPermission?.statut">
              {{ selectedPermission?.statut_display }}
            </span>
          </h3>
          <button class="btn-close" @click="closeDetailModal">×</button>
        </div>

        <div class="modal-body" v-if="selectedPermission">
          <!-- Section utilisateur -->
          <div class="detail-section">
            <div class="detail-avatar">{{ getInitials(selectedPermission.utilisateur_details?.display_name || '') }}</div>
            <div class="detail-user-info">
              <h4>{{ selectedPermission.utilisateur_details?.display_name }}</h4>
              <p class="detail-meta">{{ selectedPermission.utilisateur_details?.username?.toUpperCase() }}</p>
            </div>
          </div>

          <!-- Informations de la permission -->
          <div class="detail-grid">
            <div class="detail-item">
              <label>Date</label>
              <span>{{ formatDate(selectedPermission.date) }}</span>
            </div>
            
            <div class="detail-item">
              <label>Heure départ</label>
              <span>{{ formatTime(selectedPermission.heure_depart) }}</span>
            </div>

            <div class="detail-item">
              <label>Heure max</label>
              <span>{{ formatTime(selectedPermission.heure_arrivee_max) }}</span>
            </div>

            <div v-if="selectedPermission.heure_arrivee_reelle" class="detail-item">
              <label>Heure arrivée</label>
              <span>{{ formatTime(selectedPermission.heure_arrivee_reelle) }}</span>
            </div>

            <div v-if="selectedPermission.minutes_depassement > 0" class="detail-item">
              <label>Dépassement</label>
              <span class="detail-minutes" style="color: #f44336;">
                {{ selectedPermission.minutes_depassement }}min
              </span>
            </div>

            <div v-if="selectedPermission.heures_a_rattraper > 0" class="detail-item">
              <label>À rattraper</label>
              <span class="detail-heures">{{ selectedPermission.heures_a_rattraper }}h</span>
            </div>

            <div v-if="selectedPermission.heures_restantes > 0" class="detail-item">
              <label>Restant</label>
              <span class="detail-heures-restantes">{{ selectedPermission.heures_restantes }}h</span>
            </div>

            <div class="detail-item full-width">
              <label>Motif</label>
              <p class="detail-motif">{{ selectedPermission.motif }}</p>
            </div>
          </div>

          <!-- Lien vers le congé généré (si transformé) -->
          <div v-if="selectedPermission.statut === 'transforme' && selectedPermission.conge_genere_details" 
              class="info-box transformation-box">
            <h5>🔄 Transformé en congé</h5>
            <p>
              <strong>Type:</strong> {{ selectedPermission.conge_genere_details.type_conge }} |
              <strong>Statut:</strong> {{ selectedPermission.conge_genere_details.statut }}
            </p>
            <p class="detail-meta">Voir dans l'onglet Congés</p>
          </div>


          <!-- Rattrapages effectués -->
          <div v-if="selectedPermission.rattrapages?.length" class="rattrapages-section">
            <h4>Rattrapages effectués</h4>
            <div v-for="rattrapage in selectedPermission.rattrapages" :key="rattrapage.id" class="rattrapage-item">
              <div class="rattrapage-info">
                <span class="rattrapage-date">{{ formatDate(rattrapage.date) }}</span>
                <span class="rattrapage-heures">{{ rattrapage.heures }}h</span>
                <span class="rattrapage-horaires">
                  {{ formatTime(rattrapage.heure_debut) }} - {{ formatTime(rattrapage.heure_fin) }}
                </span>
              </div>
              <p v-if="rattrapage.commentaire" class="rattrapage-commentaire">
                {{ rattrapage.commentaire }}
              </p>
            </div>
          </div>

          <!-- Info validation/annulation -->
          <div v-if="selectedPermission.statut === 'approuve' && selectedPermission.valide_par_details" 
              class="validation-box approved-box">
            <h5>✓ Approuvé par</h5>
            <p><strong>{{ selectedPermission.valide_par_details.display_name }} - {{ (selectedPermission.valide_par_details.username).toUpperCase() }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedPermission.date_validation || '') }}</p>
          </div>

          <div v-if="selectedPermission.statut === 'annule' && selectedPermission.annule_par_details" 
              class="validation-box cancelled-box">
            <h5>✗ Annulé par</h5>
            <p><strong>{{ selectedPermission.annule_par_details.display_name }}</strong></p>
            <p class="detail-meta">Le {{ formatDateTime(selectedPermission.date_annulation || '') }}</p>
            <p v-if="selectedPermission.commentaire_annulation" class="cancelled-comment">
              {{ selectedPermission.commentaire_annulation }}
            </p>
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
          
          <!-- Bouton De retour (pour le jour J) -->
          <button 
            v-if="peutRetourner(selectedPermission) && canManageThisPermission(selectedPermission)"
            class="btn-success"
            @click="openRetourModal"
          >
            <i class="bi bi-arrow-return-left"></i> De retour
          </button>
          
          <!-- Bouton ajouter rattrapage -->
          <button 
            v-if="peutAjouterRattrapage(selectedPermission) && canManageThisPermission(selectedPermission)"
            class="btn-success"
            @click="openRattrapageModal"
          >
            <i class="bi bi-plus-circle"></i> Commencer un rattrapage
          </button>
          
          <!-- Bouton transformer en congé -->
          <button 
            v-if="peutTransformerEnConge(selectedPermission) && canManageThisPermission(selectedPermission)"
            class="btn-primary"
            @click="openTransformationModal"
          >
            <i class="bi bi-calendar-plus"></i> Transformer en congé
          </button>
          
          <!-- Bouton annuler -->
          <button 
            v-if="peutAnnuler(selectedPermission) && canManageThisPermission(selectedPermission)"
            class="btn-warning"
            @click="cancelSelectedPermission"
          >
            <i class="bi bi-x-circle"></i> Annuler
          </button>
        </div>
      </div>
    </div>
  </Teleport>

  <!-- Modal Retour (saisie heure d'arrivée) -->
  <Teleport to="body">
    <div v-if="showRetourModal" class="modal-overlay" @click.self="closeRetourModal">
        <div class="modal">
        <div class="modal-header">
            <h3>Enregistrer le retour</h3>
            <button class="btn-close" @click="closeRetourModal">×</button>
        </div>

        <div class="modal-body">
            <div class="info-permission">
            <p>Permission du <strong>{{ formatDate(selectedPermission?.date || '') }}</strong></p>
            <p>Départ à <strong>{{ formatTime(selectedPermission?.heure_depart) }}</strong></p>
            <p>Retour max à <strong>{{ formatTime(selectedPermission?.heure_arrivee_max) }}</strong></p>
            </div>

            <div class="form-group">
            <label>Heure d'arrivée réelle <span class="required">*</span></label>
            <input 
                type="time" 
                v-model="retourForm.heure_arrivee_reelle"
                class="form-input"
                step="60"
            />
            </div>

            <!-- Aperçu du dépassement -->
            <div v-if="retourForm.heure_arrivee_reelle && minutesDepassement > 0" class="preview-box warning-box">
              <div v-if="minutesDepassement > 0" class="calcul-detail">
                <p><strong>⏰ Retard de {{ minutesDepassement }} minutes</strong></p>
                <p>Calcul des heures à rattraper :</p>
                <ul class="calcul-list">
                  <li>Permission de 2h (120 min) <span class="calcul-value">+ 120 min</span></li>
                  <li>Dépassement <span class="calcul-value">+ {{ minutesDepassement }} min</span></li>
                  <li class="calcul-total">Total <span class="calcul-value">{{ (minutesDepassement + 120) / 60 }}h</span></li>
                </ul>
              </div>
            </div>
            <div v-else-if="retourForm.heure_arrivee_reelle && minutesDepassement <= 0" class="preview-box info-box">
              <p>✅ Retour dans les temps !</p>
              <p><strong>⚠️ Rattrapage obligatoire</strong></p>
              <p>Vous devrez effectuer un rattrapage.</p>
            </div>

            <div v-if="retourError" class="alert-error">
            {{ retourError }}
            </div>
        </div>

        <div class="modal-actions">
            <button class="btn-secondary" @click="closeRetourModal">Annuler</button>
            <button 
            class="btn-primary" 
            @click="submitRetour"
            :disabled="!retourForm.heure_arrivee_reelle || retourSubmitting"
            >
            <i v-if="retourSubmitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Valider le retour</span>
            </button>
        </div>
        </div>
    </div>
    </Teleport>

  <!-- Modal Ajout Rattrapage (comme dans retards) -->
  <Teleport to="body">
    <div v-if="showRattrapageModal" class="modal-overlay" @click.self="closeRattrapageModal">
      <div class="modal">
        <div class="modal-header">
          <h3>Ajouter un rattrapage</h3>
          <button class="btn-close" @click="closeRattrapageModal">×</button>
        </div>

        <div class="modal-body">
          <div class="info-permission">
            <p>Permission du <strong>{{ formatDate(selectedPermission?.date || '') }}</strong></p>
            <p>Heures restantes à rattraper: <strong>{{ selectedPermission?.heures_restantes }}h</strong></p>
          </div>

          <div class="form-group">
            <label>Date du rattrapage <span class="required">*</span></label>
            <input 
              type="date" 
              v-model="rattrapageForm.date_rattrapage"
              :max="today"
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

          <!-- Calcul automatique -->
          <div v-if="rattrapageForm.heure_debut && rattrapageForm.heure_fin" class="preview-box">
            <p>Heures rattrapées: <strong>{{ calculateRattrapageHeures }}h</strong></p>
            <p v-if="parseFloat(calculateRattrapageHeures) > (selectedPermission?.heures_restantes || 0)" class="error-text">
              ⚠️ Vous ne pouvez pas rattraper plus que les heures restantes !
            </p>
          </div>

          <div class="form-group">
            <label>Commentaire (facultatif)</label>
            <textarea 
              v-model="rattrapageForm.commentaire" 
              rows="2" 
              class="form-textarea"
              maxlength="300"
            ></textarea>
          </div>

          <div v-if="rattrapageError" class="alert-error">
            {{ rattrapageError }}
          </div>
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeRattrapageModal">Annuler</button>
          <button 
            class="btn-primary" 
            @click="submitRattrapage"
            :disabled="!isRattrapageValid || rattrapageSubmitting"
          >
            <i v-if="rattrapageSubmitting" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Valider le rattrapage</span>
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
            <p><strong>⚠️ Dépassement de {{ selectedPermission?.minutes_depassement }} minutes</strong></p>
            <p>Cette permission pourra se transformée en congé et déduite du solde (si vous le voulez).</p>
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
import { usePermissionsStore } from '@/store/permissions'
import { useCongesStore } from '@/store/conges'
import { useFiltersStore } from '@/store/filters'
import Calendar from '@/components/common/Calendar.vue'
import type { CalendarEvent } from '@/components/common/Calendar.vue'
import type { GerableUserPermission, Permission } from '@/types/permissions'
import { format, parseISO, getYear, differenceInMinutes, addDays, addHours } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Stores
const authStore = useAuthStore()
const permissionsStore = usePermissionsStore()
const congesStore = useCongesStore()
const filtersStore = useFiltersStore()

// Clés localStorage
const STORAGE_KEY_STATUS = 'alimanaka_permissions_status_filter'

// État local
const filters = ref({
  pole: null as number | null,
  equipe: null as number | null
})

const statusFilter = ref<'tous' | 'en_attente' | 'retourne' | 'rattrapage' | 'approuve' | 'transforme' | 'annule'>(
  (localStorage.getItem(STORAGE_KEY_STATUS) as any) || 'tous'
)

const showPoleDropdown = ref(false)
const showEquipeDropdown = ref(false)

const showCreateModal = ref(false)
const showDetailModal = ref(false)
const showRetourModal = ref(false)
const showRattrapageModal = ref(false)
const showTransformationModal = ref(false)

const loading = ref(false)
const submitting = ref(false)
const retourSubmitting = ref(false)
const rattrapageSubmitting = ref(false)
const transformationSubmitting = ref(false)

const formError = ref<string | null>(null)
const retourError = ref<string | null>(null)
const rattrapageError = ref<string | null>(null)
const transformationError = ref<string | null>(null)

// Sélection utilisateur (pour managers)
const userSearchQuery = ref('')
const showUserDropdown = ref(false)
const selectedUser = ref<GerableUserPermission | null>(null)

// Permission sélectionnée
const selectedPermission = ref<Permission | null>(null)

// Formulaire principal
const form = ref({
  date: '',
  heure_depart: '',
  motif: ''
})

// Formulaire retour
const retourForm = ref({
  heure_arrivee_reelle: ''
})

// Formulaire rattrapage
const rattrapageForm = ref({
  date_rattrapage: '',
  heure_debut: '',
  heure_fin: '',
  commentaire: ''
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

const typesConge = computed(() => permissionsStore.typesConge)

const selectedType = computed(() => {
  return typesConge.value.find(t => t.type_conge === transformationForm.value.type_conge)
})

// Heure d'arrivée max = départ + 2h
const heureArriveeMax = computed(() => {
  if (!form.value.date || !form.value.heure_depart) return ''
  
  const depart = parseTime(form.value.heure_depart)
  const date = new Date(form.value.date)
  date.setHours(depart.hours, depart.minutes, 0)
  
  const arriveeMax = addHours(date, 2)
  return format(arriveeMax, 'HH:mm')
})

// Calcul des minutes de dépassement pour le retour
const minutesDepassement = computed(() => {
  if (!selectedPermission.value || !retourForm.value.heure_arrivee_reelle) return 0
  
  const arrivee = parseTime(retourForm.value.heure_arrivee_reelle)
  const max = parseTime(selectedPermission.value.heure_arrivee_max)
  const depart = parseTime(selectedPermission.value.heure_depart)
  
  const arriveeDate = new Date(selectedPermission.value.date)
  arriveeDate.setHours(arrivee.hours, arrivee.minutes, 0)
  
  const maxDate = new Date(selectedPermission.value.date)
  maxDate.setHours(max.hours, max.minutes, 0)
  
  const departDate = new Date(selectedPermission.value.date)
  departDate.setHours(depart.hours, depart.minutes, 0)
  
  // Calcul du dépassement (si retour après max)
  const depassement = Math.max(0, differenceInMinutes(arriveeDate, maxDate))
  return depassement
})

const heuresARattraperRetour = computed(() => {
  if (!selectedPermission.value || !retourForm.value.heure_arrivee_reelle) return '0.00'
  
  const arrivee = parseTime(retourForm.value.heure_arrivee_reelle)
  const max = parseTime(selectedPermission.value.heure_arrivee_max)
  const depart = parseTime(selectedPermission.value.heure_depart)
  
  const arriveeDate = new Date(selectedPermission.value.date)
  arriveeDate.setHours(arrivee.hours, arrivee.minutes, 0)
  
  const maxDate = new Date(selectedPermission.value.date)
  maxDate.setHours(max.hours, max.minutes, 0)
  
  const departDate = new Date(selectedPermission.value.date)
  departDate.setHours(depart.hours, depart.minutes, 0)
  
  let minutesARattraper = 0
  
  if (arriveeDate > maxDate) {
    // CAS 1: Retour APRÈS l'heure max
    // Total = (heure_max - départ) + (arrivée - heure_max)
    // (heure_max - départ) = toujours 120 minutes (2h)
    const depassement = differenceInMinutes(arriveeDate, maxDate)
    minutesARattraper = 120 + depassement
  } else {
    // CAS 2: Retour AVANT l'heure max
    // Total = durée réelle de l'absence (arrivée - départ)
    const dureeAbsence = differenceInMinutes(arriveeDate, departDate)
    
    // Comparer avec le forfait (30 min par défaut)
    const forfaitMinutes = 30 // À récupérer depuis la config si disponible
    minutesARattraper = Math.max(dureeAbsence, forfaitMinutes)
  }
  
  return (minutesARattraper / 60).toFixed(2)
})

// Calcul des heures de rattrapage
const calculateRattrapageHeures = computed(() => {
  if (!rattrapageForm.value.heure_debut || !rattrapageForm.value.heure_fin) return '0.00'
  
  const debut = parseTime(rattrapageForm.value.heure_debut)
  const fin = parseTime(rattrapageForm.value.heure_fin)
  
  const debutDate = new Date(rattrapageForm.value.date_rattrapage || new Date())
  debutDate.setHours(debut.hours, debut.minutes, 0)
  
  const finDate = new Date(rattrapageForm.value.date_rattrapage || new Date())
  finDate.setHours(fin.hours, fin.minutes, 0)
  
  const minutes = differenceInMinutes(finDate, debutDate)
  return (minutes / 60).toFixed(2)
})

// Événements filtrés pour le calendrier
const filteredEventsForCalendar = computed<CalendarEvent[]>(() => {
  return permissionsStore.eventsForCalendar
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

// Total des heures à rattraper
const totalHeuresARattraper = computed(() => {
  return permissionsStore.totalHeuresARattraper.toFixed(2)
})

const permissionsRattrapage = computed(() => permissionsStore.permissionsRattrapage)
const permissionsRetournees = computed(() => permissionsStore.permissionsRetournees)

// Initials pour l'avatar
const userInitials = computed(() => {
  const name = authStore.user?.display_name || authStore.user?.username || '?'
  return name.charAt(0).toUpperCase()
})

// Date aujourd'hui
const today = computed(() => format(new Date(), 'yyyy-MM-dd'))

// Utilisateurs filtrés pour le dropdown
const filteredUsers = computed(() => {
  if (!userSearchQuery.value) return permissionsStore.utilisateursGerables
  
  const query = userSearchQuery.value.toLowerCase()
  return permissionsStore.utilisateursGerables.filter(u => 
    u.display_name.toLowerCase().includes(query) ||
    u.username.toLowerCase().includes(query) ||
    (u.equipe_nom && u.equipe_nom.toLowerCase().includes(query))
  )
})

// Validation du formulaire
const isFormValid = computed(() => {
  const baseValid = form.value.date && 
                   form.value.heure_depart && 
                   form.value.motif && 
                   form.value.motif.trim().length > 0
  
  if (permissionsStore.canManageOthers && !selectedUser.value) {
    return false
  }
  
  return baseValid
})

// Validation du formulaire de rattrapage
const isRattrapageValid = computed(() => {
  if (!rattrapageForm.value.date_rattrapage || 
      !rattrapageForm.value.heure_debut || 
      !rattrapageForm.value.heure_fin) {
    return false
  }
  
  const heures = parseFloat(calculateRattrapageHeures.value)
  return heures > 0 && heures <= (selectedPermission.value?.heures_restantes || 0)
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

const setStatusFilter = (filter: 'tous' | 'en_attente' | 'retourne' | 'rattrapage' | 'approuve' | 'transforme' | 'annule') => {
  statusFilter.value = filter
  localStorage.setItem(STORAGE_KEY_STATUS, filter)
  refreshData()
}

const onUserSearch = () => {
  showUserDropdown.value = true
}

const selectUser = (user: GerableUserPermission) => {
  selectedUser.value = user
  showUserDropdown.value = false
  userSearchQuery.value = ''
}

const onDateChange = () => {
  if (form.value.date < today.value) {
    formError.value = "La date de permission ne peut pas être dans le passé"
    form.value.date = ''
  } else {
    formError.value = null
  }
}

// Création
const openCreateModal = async () => {
  formError.value = null
  form.value = {
    date: '',
    heure_depart: '',
    motif: ''
  }
  selectedUser.value = null
  userSearchQuery.value = ''
  
  try {
    if (permissionsStore.typesConge.length === 0) {
      await permissionsStore.fetchTypesConge()
    }
    
    if (permissionsStore.canManageOthers) {
      await permissionsStore.fetchUtilisateursGerables()
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
    const payload: any = {
      date: form.value.date,
      heure_depart: form.value.heure_depart,
      motif: form.value.motif
    }
    
    if (permissionsStore.canManageOthers && selectedUser.value) {
      payload.user_id = selectedUser.value.id
    }
    
    await permissionsStore.createPermission(payload)
    
    closeCreateModal()
    alert('Permission enregistrée avec succès !')
    await refreshData()
    
  } catch (err: any) {
    formError.value = err.response?.data?.error || err.response?.data?.detail || 'Erreur lors de l\'enregistrement'
  } finally {
    submitting.value = false
  }
}

// Détails
const onEventClick = (event: CalendarEvent) => {
  const permId = parseInt(String(event.id).replace('perm_', ''))
  loadPermissionDetails(permId)
}

const loadPermissionDetails = async (id: number) => {
  try {
    selectedPermission.value = await permissionsStore.getPermissionDetails(id)
    showDetailModal.value = true
  } catch (e) {
    console.error('Erreur chargement détails:', e)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedPermission.value = null
}

// Retour
const openRetourModal = () => {
  retourError.value = null
  retourForm.value = {
    heure_arrivee_reelle: ''
  }
  showRetourModal.value = true
}

const closeRetourModal = () => {
  showRetourModal.value = false
}

const submitRetour = async () => {
  if (!selectedPermission.value || !retourForm.value.heure_arrivee_reelle) return
  
  retourSubmitting.value = true
  retourError.value = null
  
  try {
    await permissionsStore.enregistrerRetour(
      selectedPermission.value.id, 
      retourForm.value.heure_arrivee_reelle
    )
    
    closeRetourModal()
    closeDetailModal()
    alert('Retour enregistré avec succès !')
    await refreshData()
    
  } catch (err: any) {
    retourError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    retourSubmitting.value = false
  }
}

// Rattrapage
const openRattrapageModal = () => {
  rattrapageError.value = null
  rattrapageForm.value = {
    date_rattrapage: '',
    heure_debut: '',
    heure_fin: '',
    commentaire: ''
  }
  showRattrapageModal.value = true
}

const closeRattrapageModal = () => {
  showRattrapageModal.value = false
}

const submitRattrapage = async () => {
  if (!isRattrapageValid.value || !selectedPermission.value) return
  
  rattrapageSubmitting.value = true
  rattrapageError.value = null
  
  try {
    await permissionsStore.ajouterRattrapage(selectedPermission.value.id, rattrapageForm.value)
    
    closeRattrapageModal()
    closeDetailModal()
    alert('Rattrapage ajouté avec succès !')
    await refreshData()
    
  } catch (err: any) {
    rattrapageError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    rattrapageSubmitting.value = false
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
  if (!selectedPermission.value || !transformationForm.value.type_conge) return
  
  transformationSubmitting.value = true
  transformationError.value = null
  
  try {
    await permissionsStore.transformerEnConge(
      selectedPermission.value.id, 
      transformationForm.value.type_conge
    )
    
    closeTransformationModal()
    closeDetailModal()
    alert('Permission transformée en congé avec succès !')
    await refreshData()
    
  } catch (err: any) {
    transformationError.value = err.response?.data?.error || err.message || 'Erreur'
  } finally {
    transformationSubmitting.value = false
  }
}

// Annulation
const peutAnnuler = (permission: Permission | null): boolean => {
  if (!permission) return false
  return ['en_attente', 'retourne', 'rattrapage'].includes(permission.statut)
}

const peutRetourner = (permission: Permission | null): boolean => {
  if (!permission) return false
  return permissionsStore.peutRetourner(permission)
}

const peutAjouterRattrapage = (permission: Permission | null): boolean => {
  if (!permission) return false
  return permissionsStore.peutAjouterRattrapage(permission)
}

const peutTransformerEnConge = (permission: Permission | null): boolean => {
  if (!permission) return false
  return permissionsStore.peutTransformerEnConge(permission)
}

const canManageThisPermission = (permission: Permission | null): boolean => {
  if (!permission) return false
  return permissionsStore.canManageThisPermission(permission)
}

const cancelSelectedPermission = async () => {
  if (!selectedPermission.value) return
  
  const commentaire = prompt('Motif de l\'annulation (optionnel):')
  if (commentaire === null) return
  
  if (confirm('Voulez-vous vraiment annuler cette permission ?')) {
    await permissionsStore.annulerPermission(selectedPermission.value.id, commentaire || undefined)
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
    permissionsStore.fetchCalendrier(params),
    permissionsStore.fetchMesPermissions(currentYear),
    congesStore.fetchCalendrier({ annee: currentYear })
  ])
  
  loading.value = false
}

// Cycle de vie
onMounted(async () => {
  await authStore.checkAuth()
  await filtersStore.fetchPoles()
  if (permissionsStore.typesConge.length === 0) {
    await permissionsStore.fetchTypesConge()
  }
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

.permission-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.heures-restantes {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.permissions-encours {
  background-color: #e3f2fd;
  color: #0d47a1;
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

.filter-tabs button.active:hover:not(.disabled) {
  background: linear-gradient(90deg, rgb(36,59,107) 0%, rgb(181,9,1) 100%);
  color: white;
  border-color: linear-gradient(90deg, rgb(36,59,107) 0%, rgb(181,9,1) 100%);
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

.permissions-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
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

.char-count {
  display: block;
  text-align: right;
  color: #6c757d;
  font-size: 0.8rem;
  margin-top: 0.25rem;
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

.alert-warning {
  background: #fff3cd;
  color: #856404;
  padding: 0.75rem;
  border-radius: 6px;
  border-left: 4px solid #ffc107;
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

.success-box {
  background: #e8f5e9;
  border-left-color: #4caf50;
}

.transformation-box {
  background: #f3e5f5;
  border-left-color: #9c27b0;
  margin-top: 1rem;
  padding: 1rem;
  border-radius: 8px;
}

.multiplicateur-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

/* Info permission */

.info-text {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px dashed #ccc;
}


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

/* Detail styles (comme dans retards) */
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

.detail-minutes {
  font-weight: bold;
}

.detail-heures {
  color: #2196f3;
  font-weight: bold;
}

.detail-heures-restantes {
  color: #ff9800;
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

/* Rattrapages */
.rattrapages-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.rattrapages-section h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.rattrapage-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid #4caf50;
}

.rattrapage-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.rattrapage-date {
  font-weight: 600;
  color: #2c3e50;
  min-width: 100px;
}

.rattrapage-heures {
  background: #4caf50;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.rattrapage-horaires {
  color: #6c757d;
  font-size: 0.9rem;
}

.rattrapage-commentaire {
  margin: 0.5rem 0 0 0;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  font-style: italic;
  color: #495057;
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
.header-retourne { background: #2196f3 !important; }
.header-rattrapage { background: #9c27b0 !important; }
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
  
  .rattrapage-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
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