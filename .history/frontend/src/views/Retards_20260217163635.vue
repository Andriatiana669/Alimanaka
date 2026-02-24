<template>
  <!-- Header avec résumé -->
  <div class="page-header">
    <div class="header-left">
      <h1>Gestion des Retards</h1>
      <div v-if="authStore.user" class="retard-badge">
        <span class="heures-restantes">{{ totalHeuresARattraper }}h à rattraper</span>
        <span class="retards-encours">{{ retardsEnCours.length }} en cours</span>
      </div>
    </div>
    
    <div class="header-actions">
      <button v-if="retardsStore.canManageOthers" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i> Ajouter un retard
      </button>
    </div>
  </div>

  <!-- Filtres -->
  <div class="filters-bar">
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
        :class="{ active: statusFilter === 'en_cours' }" 
        @click="setStatusFilter('en_cours')"
      >
        En cours
      </button>
      <button 
        :class="{ active: statusFilter === 'approuve' }" 
        @click="setStatusFilter('approuve')"
      >
        Rattrapés
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

  <!-- Calendrier des retards -->
  <Calendar
    :events="filteredEventsForCalendar"
    :default-view="'month'"
    class="retards-calendar"
    @event-click="onEventClick"
  />

  <!-- Modal Création de retard -->
  <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
    <div class="modal modal-large">
      <div class="modal-header">
        <h3>Ajouter un retard</h3>
        <button class="btn-close" @click="closeCreateModal">×</button>
      </div>

      <div class="modal-body">
        <!-- Sélection de l'utilisateur (pour managers) -->
        <div v-if="retardsStore.canManageOthers" class="form-group">
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

        <!-- Date du retard -->
        <div class="form-group">
          <label>Date du retard <span class="required">*</span></label>
          <input 
            type="date" 
            v-model="form.date"
            :max="today"
            class="form-input"
            @change="onDateChange"
          />
        </div>

        <!-- Heure d'arrivée réelle -->
        <div class="form-group">
          <label>Heure d'arrivée réelle <span class="required">*</span></label>
          <input 
            type="time" 
            v-model="form.heure_arrivee_reelle"
            class="form-input"
            step="60"
          />
          <p class="help-text">
            Heure de début prévue: {{ heureDebutPrevueFormatee }}
          </p>
        </div>

        <!-- Aperçu du retard -->
        <div v-if="form.date && form.heure_arrivee_reelle" class="preview-box" :class="retardTypeClass">
          <p><strong>⏰ {{ minutesRetard }} minutes</strong> de retard</p>
          <p>Type: <strong>{{ retardTypeLabel }}</strong></p>
          <p>À rattraper: <strong>{{ heuresARattraper }}h</strong></p>
          <p class="multiplicateur-info" v-if="multiplicateur > 1">
            (Multiplicateur: {{ multiplicateur }}x)
          </p>
        </div>

        <!-- Motif / Justificatif -->
        <div class="form-group">
          <label>Justificatif / Motif <span class="required">*</span></label>
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
        <button class="btn-secondary" @click="closeCreateModal">Annuler</button>
        <button 
          class="btn-primary" 
          @click="submitForm"
          :disabled="!isFormValid || submitting"
        >
          <i v-if="submitting" class="bi bi-arrow-repeat spin"></i>
          <span v-else>Enregistrer le retard</span>
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Détails du retard -->
  <div v-if="showDetailModal" class="modal-overlay" @click.self="closeDetailModal">
    <div class="modal modal-large">
      <div class="modal-header" :class="'header-' + (selectedRetard?.statut || '')">
        <h3>
          Détails du retard
          <span class="header-badge" :class="selectedRetard?.statut">
            {{ selectedRetard?.statut_display }}
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
            <p class="detail-meta">{{ selectedRetard.utilisateur_details?.username?.toUpperCase() }}</p>
          </div>
        </div>

        <!-- Informations du retard -->
        <div class="detail-grid">
          <div class="detail-item">
            <label>Date</label>
            <span>{{ formatDate(selectedRetard.date) }}</span>
          </div>
          
          <div class="detail-item">
            <label>Heure prévue</label>
            <span>{{ selectedRetard.heure_debut_prevue }}</span>
          </div>

          <div class="detail-item">
            <label>Heure arrivée</label>
            <span>{{ selectedRetard.heure_arrivee_reelle }}</span>
          </div>

          <div class="detail-item">
            <label>Minutes de retard</label>
            <span class="detail-minutes" :class="'type-' + (selectedRetard.type_retard || 'leger')">
              {{ selectedRetard.minutes_retard }}min
            </span>
          </div>

          <div class="detail-item">
            <label>À rattraper</label>
            <span class="detail-heures">{{ selectedRetard.heures_a_rattraper }}h</span>
          </div>

          <div class="detail-item">
            <label>Restant</label>
            <span class="detail-heures-restantes">{{ selectedRetard.heures_restantes }}h</span>
          </div>

          <div class="detail-item full-width" v-if="selectedRetard.motif_retard">
            <label>Justificatif</label>
            <p class="detail-motif">{{ selectedRetard.motif_retard }}</p>
          </div>
        </div>

        <!-- Rattrapages effectués -->
        <div v-if="selectedRetard.rattrapages?.length" class="rattrapages-section">
          <h4>Rattrapages effectués</h4>
          <div v-for="rattrapage in selectedRetard.rattrapages" :key="rattrapage.id" class="rattrapage-item">
            <div class="rattrapage-info">
              <span class="rattrapage-date">{{ formatDate(rattrapage.date_rattrapage) }}</span>
              <span class="rattrapage-heures">{{ rattrapage.heures_rattrapees }}h</span>
              <span class="rattrapage-horaires">
                {{ rattrapage.heure_debut }} - {{ rattrapage.heure_fin }}
              </span>
            </div>
            <p v-if="rattrapage.commentaire" class="rattrapage-commentaire">
              {{ rattrapage.commentaire }}
            </p>
          </div>
        </div>

        <!-- Info validation/annulation -->
        <div v-if="selectedRetard.statut === 'approuve' && selectedRetard.approuve_par_details" 
            class="validation-box approved-box">
          <h5>✓ Rattrapé et approuvé par</h5>
          <p><strong>{{ selectedRetard.approuve_par_details.display_name }}</strong></p>
          <p class="detail-meta">Le {{ formatDateTime(selectedRetard.date_approbation || '') }}</p>
        </div>

        <div v-if="selectedRetard.statut === 'annule' && selectedRetard.annule_par_details" 
            class="validation-box cancelled-box">
          <h5>✗ Annulé par</h5>
          <p><strong>{{ selectedRetard.annule_par_details.display_name }}</strong></p>
          <p class="detail-meta">Le {{ formatDateTime(selectedRetard.date_annulation || '') }}</p>
          <p v-if="selectedRetard.commentaire_annulation" class="cancelled-comment">
            {{ selectedRetard.commentaire_annulation }}
          </p>
        </div>
      </div>

      <div class="modal-actions">
        <button class="btn-secondary" @click="closeDetailModal">Fermer</button>
        
        <!-- Bouton ajouter rattrapage -->
        <button 
          v-if="canAddRattrapage(selectedRetard)"
          class="btn-success"
          @click="openRattrapageModal"
        >
          <i class="bi bi-plus-circle"></i> Ajouter un rattrapage
        </button>
        
        <!-- Bouton annuler -->
        <button 
          v-if="canCancelRetard(selectedRetard)"
          class="btn-warning"
          @click="cancelSelectedRetard"
        >
          <i class="bi bi-x-circle"></i> Annuler
        </button>
      </div>
    </div>
  </div>

  <!-- Modal Ajout Rattrapage -->
  <div v-if="showRattrapageModal" class="modal-overlay" @click.self="closeRattrapageModal">
    <div class="modal">
      <div class="modal-header">
        <h3>Ajouter un rattrapage</h3>
        <button class="btn-close" @click="closeRattrapageModal">×</button>
      </div>

      <div class="modal-body">
        <div class="info-retard">
          <p>Retard du <strong>{{ formatDate(selectedRetard?.date || '') }}</strong></p>
          <p>Heures restantes à rattraper: <strong>{{ selectedRetard?.heures_restantes }}h</strong></p>
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
</template>


<script setup lang="ts">


</script>


<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.retard-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.heures-restantes {
  background-color: #fff3e0;
  color: #e65100;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.retards-encours {
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
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: #ff9800;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #f57c00;
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
  background: #ff9800;
  color: white;
  border-color: #ff9800;
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

/* Preview box styles */
.preview-box {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid;
}

.preview-box.type-leger {
  background: #e8f5e9;
  border-left-color: #4caf50;
}

.preview-box.type-moyen {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.preview-box.type-important {
  background: #ffebee;
  border-left-color: #f44336;
}

.multiplicateur-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

/* Modal détails */
.detail-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
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

.detail-minutes.type-leger { color: #4caf50; }
.detail-minutes.type-moyen { color: #ff9800; }
.detail-minutes.type-important { color: #f44336; }

.detail-heures {
  color: #2196f3;
  font-weight: bold;
}

.detail-heures-restantes {
  color: #ff9800;
  font-weight: bold;
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

/* Info retard dans modal rattrapage */
.info-retard {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #2196f3;
}

.info-retard p {
  margin: 0.25rem 0;
}

/* Header couleurs selon statut */
.header-en_attente { background: #ff9800; }
.header-en_cours { background: #2196f3; }
.header-approuve { background: #4caf50; }
.header-annule { background: #9e9e9e; }

.header-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.7em;
  margin-left: 10px;
  font-weight: bold;
  background: rgba(255,255,255,0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .rattrapage-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>