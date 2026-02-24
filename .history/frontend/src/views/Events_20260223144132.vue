<template>
  <div class="events-container">
    <!-- Header avec titre et filtres globaux -->
    <div class="page-header">
      <div class="header-left">
        <h1>📋 Fil d'actualité</h1>
        <p class="header-subtitle">Tous les événements en attente et récents</p>
      </div>
      
      <div class="header-actions">
        <button class="btn-refresh" @click="refreshAll" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          {{ loading ? 'Chargement...' : 'Actualiser' }}
        </button>
      </div>
    </div>

    <!-- Filtres avancés -->
    <div class="filters-section">
      <div class="filters-row">
        <!-- Filtre par type d'événement -->
        <div class="filter-group">
          <label>Type</label>
          <div class="filter-buttons">
            <button 
              v-for="type in eventTypes" 
              :key="type.value"
              class="filter-btn"
              :class="{ 
                active: typeFilters.includes(type.value),
                [type.color]: true
              }"
              @click="toggleTypeFilter(type.value)"
            >
              <i :class="type.icon"></i>
              {{ type.label }}
              <span v-if="getTypeCount(type.value)" class="count-badge">
                {{ getTypeCount(type.value) }}
              </span>
            </button>
          </div>
        </div>

        <!-- Filtre par statut -->
        <div class="filter-group">
          <label>Statut</label>
          <div class="filter-buttons">
            <button 
              v-for="status in statusOptions" 
              :key="status.value"
              class="filter-btn"
              :class="{ active: statusFilters.includes(status.value) }"
              @click="toggleStatusFilter(status.value)"
            >
              <span class="status-dot" :class="status.color"></span>
              {{ status.label }}
            </button>
          </div>
        </div>

        <!-- Filtre par utilisateur (pour managers) -->
        <div v-if="canManageOthers" class="filter-group large">
          <label>Utilisateur</label>
          <div class="user-filter">
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
                :class="{ selected: selectedUserIds.includes(user.id) }"
                @click="toggleUserFilter(user)"
              >
                <div class="user-option-info">
                  <span class="user-option-name">{{ user.display_name }}</span>
                  <span class="user-option-meta">
                    {{ user.username.toUpperCase() }} | {{ user.equipe_nom || 'Sans équipe' }}
                  </span>
                </div>
                <span v-if="selectedUserIds.includes(user.id)" class="check-icon">
                  <i class="bi bi-check-lg"></i>
                </span>
              </div>
            </div>
            <div v-if="selectedUsers.length" class="selected-users">
              <div v-for="user in selectedUsers" :key="user.id" class="selected-user-tag">
                <span class="user-tag-name">{{ user.display_name }}</span>
                <button class="remove-tag" @click="removeUserFilter(user.id)">×</button>
              </div>
              <button v-if="selectedUsers.length" class="clear-tags" @click="clearUserFilters">
                Tout effacer
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Filtres rapides par période -->
      <div class="filters-row">
        <div class="filter-group">
          <label>Période</label>
          <div class="filter-buttons">
            <button 
              v-for="period in periodOptions" 
              :key="period.value"
              class="filter-btn"
              :class="{ active: selectedPeriod === period.value }"
              @click="selectedPeriod = period.value"
            >
              {{ period.label }}
            </button>
          </div>
        </div>

        <!-- Filtre par date personnalisée -->
        <div v-if="selectedPeriod === 'custom'" class="filter-group date-range">
          <input 
            type="date" 
            v-model="dateRange.start" 
            class="form-input small"
            placeholder="Date début"
          />
          <span class="date-separator">→</span>
          <input 
            type="date" 
            v-model="dateRange.end" 
            class="form-input small"
            placeholder="Date fin"
          />
        </div>
      </div>
    </div>

    <!-- Résumé des filtres actifs -->
    <div v-if="hasActiveFilters" class="active-filters">
      <span class="active-filters-label">Filtres actifs :</span>
      <div class="filter-tags">
        <span v-for="type in activeTypeLabels" :key="'type-'+type" class="filter-tag" :class="getTypeClass(type)">
          <i :class="getTypeIcon(type)"></i>
          {{ type }}
          <button class="remove-filter" @click="removeTypeFilter(type)">×</button>
        </span>
        <span v-for="status in activeStatusLabels" :key="'status-'+status" class="filter-tag status-tag">
          <span class="status-dot" :class="getStatusColor(status)"></span>
          {{ status }}
          <button class="remove-filter" @click="removeStatusFilter(status)">×</button>
        </span>
        <span v-for="user in selectedUsers" :key="'user-'+user.id" class="filter-tag user-tag">
          <i class="bi bi-person-circle"></i>
          {{ user.display_name }}
          <button class="remove-filter" @click="removeUserFilter(user.id)">×</button>
        </span>
        <button class="clear-all-filters" @click="clearAllFilters">
          Tout effacer
        </button>
      </div>
    </div>

    <!-- Timeline des événements -->
    <div class="timeline">
      <div v-if="loading && !events.length" class="loading-state">
        <div class="spinner"></div>
        <p>Chargement des événements...</p>
      </div>

      <div v-else-if="filteredEvents.length === 0" class="empty-state">
        <i class="bi bi-calendar-x"></i>
        <h3>Aucun événement trouvé</h3>
        <p>Essayez de modifier vos filtres ou d'actualiser la page.</p>
      </div>

      <div v-else class="events-list">
        <!-- Grouper par date -->
        <div v-for="(group, dateKey) in groupedEvents" :key="dateKey" class="date-group">
          <div class="date-header">
            <span class="date-badge">{{ formatDateHeader(dateKey) }}</span>
            <span class="date-count">{{ group.length }} événement(s)</span>
          </div>
          
          <div class="events-group">
            <TransitionGroup name="event-list">
              <div 
                v-for="event in group" 
                :key="event.id"
                class="event-card"
                :class="[event.type, event.statut]"
                @click="openEventDetails(event)"
              >
                <!-- Icône et type -->
                <div class="event-icon" :class="event.type">
                  <i :class="getEventIcon(event.type)"></i>
                </div>

                <!-- Contenu principal -->
                <div class="event-content">
                  <div class="event-header">
                    <div class="event-title">
                      <span class="event-user">
                        <i class="bi bi-person-circle"></i>
                        {{ event.user_display_name }}
                      </span>
                      <span class="event-type-badge" :class="event.type">
                        {{ getEventTypeLabel(event.type) }}
                      </span>
                      <span class="event-statut-badge" :class="event.statut">
                        {{ getStatusLabel(event.statut, event.type) }}
                      </span>
                    </div>
                    <span class="event-time">
                      <i class="bi bi-clock"></i>
                      {{ formatTime(event.date) }}
                    </span>
                  </div>

                  <div class="event-details">
                    <!-- Détails spécifiques selon le type -->
                    <template v-if="event.type === 'conge'">
                      <span class="detail-chip">
                        <i class="bi bi-calendar-range"></i>
                        {{ formatDateRange(event.date_debut, event.date_fin) }}
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-hourglass-split"></i>
                        {{ event.jours_deduits }}j
                      </span>
                      <span v-if="event.type_conge" class="detail-chip">
                        {{ event.type_conge_display }}
                      </span>
                    </template>

                    <template v-else-if="event.type === 'retard'">
                      <span class="detail-chip">
                        <i class="bi bi-clock-history"></i>
                        {{ event.minutes_retard }}min de retard
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-arrow-repeat"></i>
                        {{ event.heures_restantes }}h restantes
                      </span>
                    </template>

                    <template v-else-if="event.type === 'permission'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        {{ formatTime(event.heure_depart) }} → {{ formatTime(event.heure_arrivee_max) }}
                      </span>
                      <span v-if="event.heures_restantes > 0" class="detail-chip">
                        <i class="bi bi-arrow-repeat"></i>
                        {{ event.heures_restantes }}h restantes
                      </span>
                    </template>

                    <template v-else-if="event.type === 'repos_medical'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        {{ formatTime(event.heure_debut) }} → {{ formatTime(event.heure_fin) }}
                      </span>
                      <span class="detail-chip">
                        <i class="bi bi-hourglass"></i>
                        {{ event.duree_heures }}h
                      </span>
                    </template>

                    <template v-else-if="event.type === 'ostie'">
                      <span class="detail-chip">
                        <i class="bi bi-clock"></i>
                        Début {{ formatTime(event.heure_debut) }}
                      </span>
                      <span v-if="event.heure_fin" class="detail-chip">
                        Fin {{ formatTime(event.heure_fin) }}
                      </span>
                    </template>

                    <!-- Motif si présent -->
                    <span v-if="event.motif" class="detail-chip motif">
                      <i class="bi bi-chat-text"></i>
                      {{ truncateMotif(event.motif) }}
                    </span>
                  </div>

                  <!-- Actions rapides (pour les managers) -->
                  <div v-if="canManageThisEvent(event)" class="event-actions" @click.stop>
                    <button 
                      v-if="canQuickAction(event, 'valider')"
                      class="action-btn success"
                      @click="quickValidate(event)"
                      title="Valider"
                    >
                      <i class="bi bi-check-lg"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'retour')"
                      class="action-btn primary"
                      @click="quickRetour(event)"
                      title="Enregistrer retour"
                    >
                      <i class="bi bi-arrow-return-left"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'rattrapage')"
                      class="action-btn info"
                      @click="quickRattrapage(event)"
                      title="Ajouter rattrapage"
                    >
                      <i class="bi bi-plus-circle"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'transformer')"
                      class="action-btn purple"
                      @click="quickTransform(event)"
                      title="Transformer"
                    >
                      <i class="bi bi-arrow-right-circle"></i>
                    </button>
                    <button 
                      v-if="canQuickAction(event, 'annuler')"
                      class="action-btn warning"
                      @click="quickCancel(event)"
                      title="Annuler"
                    >
                      <i class="bi bi-x-circle"></i>
                    </button>
                  </div>
                </div>

                <!-- Badge d'urgence -->
                <div v-if="isUrgent(event)" class="urgent-badge" title="Urgent (moins d'une semaine)">
                  ⚠️
                </div>
              </div>
            </TransitionGroup>
          </div>
        </div>

        <!-- Bouton "Charger plus" -->
        <div v-if="hasMoreEvents" class="load-more">
          <button class="btn-load-more" @click="loadMore" :disabled="loadingMore">
            <i v-if="loadingMore" class="bi bi-arrow-repeat spin"></i>
            <span v-else>Charger plus d'événements</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Modals réutilisables (importés des composants existants) -->
    <Teleport to="body">
      <!-- Modal Détails Congé -->
      <CongeDetailModal
        v-if="showCongeDetail && selectedEvent?.type === 'conge'"
        :conge="selectedEvent"
        @close="closeDetailModal"
        @refresh="refreshAll"
      />

      <!-- Modal Détails Retard -->
      <RetardDetailModal
        v-if="showRetardDetail && selectedEvent?.type === 'retard'"
        :retard="selectedEvent"
        @close="closeDetailModal"
        @refresh="refreshAll"
      />

      <!-- Modal Détails Permission -->
      <PermissionDetailModal
        v-if="showPermissionDetail && selectedEvent?.type === 'permission'"
        :permission="selectedEvent"
        @close="closeDetailModal"
        @refresh="refreshAll"
      />

      <!-- Modal Détails Repos Medical -->
      <ReposMedicalDetailModal
        v-if="showReposDetail && selectedEvent?.type === 'repos_medical'"
        :repos="selectedEvent"
        @close="closeDetailModal"
        @refresh="refreshAll"
      />

      <!-- Modal Détails OSTIE -->
      <OstieDetailModal
        v-if="showOstieDetail && selectedEvent?.type === 'ostie'"
        :ostie="selectedEvent"
        @close="closeDetailModal"
        @refresh="refreshAll"
      />

      <!-- Modals d'action rapide (réutilisés) -->
      <RetourModal
        v-if="showRetourModal && selectedEvent?.type === 'permission'"
        :permission="selectedEvent"
        @close="closeRetourModal"
        @validated="handleActionValidated"
      />

      <RattrapageModal
        v-if="showRattrapageModal && (selectedEvent?.type === 'permission' || selectedEvent?.type === 'retard')"
        :event="selectedEvent"
        @close="closeRattrapageModal"
        @validated="handleActionValidated"
      />

      <ValidationOstieModal
        v-if="showValidationOstieModal && selectedEvent?.type === 'ostie'"
        :ostie="selectedEvent"
        @close="closeValidationOstieModal"
        @validated="handleActionValidated"
      />

      <TransformationModal
        v-if="showTransformationModal && (selectedEvent?.type === 'permission' || selectedEvent?.type === 'repos_medical')"
        :event="selectedEvent"
        :types-conge="typesConge"
        @close="closeTransformationModal"
        @validated="handleActionValidated"
      />

      <TransformationOstieModal
        v-if="showTransformationOstieModal && selectedEvent?.type === 'ostie'"
        :ostie="selectedEvent"
        @close="closeTransformationOstieModal"
        @validated="handleActionValidated"
      />
    </Teleport>
  </div>
</template>



<style scoped>
.events-container {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-subtitle {
  color: #6c757d;
  margin: 0;
  font-size: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e9ecef;
  border-color: #adb5bd;
}

.filters-section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  margin-bottom: 1rem;
}

.filters-row:last-child {
  margin-bottom: 0;
}

.filter-group {
  flex: 1;
  min-width: 250px;
}

.filter-group.large {
  flex: 2;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.filter-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.filter-btn:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.filter-btn.active {
  background: #3498db;
  color: white;
  border-color: #3498db;
}

.filter-btn.active.blue { background: #3498db; border-color: #3498db; }
.filter-btn.active.orange { background: #f39c12; border-color: #f39c12; }
.filter-btn.active.green { background: #27ae60; border-color: #27ae60; }
.filter-btn.active.red { background: #e74c3c; border-color: #e74c3c; }
.filter-btn.active.purple { background: #9b59b6; border-color: #9b59b6; }

.count-badge {
  background: rgba(0,0,0,0.1);
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.status-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.orange { background: #f39c12; }
.status-dot.blue { background: #3498db; }
.status-dot.purple { background: #9b59b6; }
.status-dot.green { background: #27ae60; }
.status-dot.red { background: #e74c3c; }
.status-dot.gray { background: #95a5a6; }

/* Filtre utilisateur */
.user-filter {
  position: relative;
}

.form-input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.95rem;
}

.form-input.small {
  padding: 0.5rem;
  font-size: 0.9rem;
}

.user-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  max-height: 300px;
  overflow-y: auto;
  z-index: 100;
  margin-top: 0.25rem;
}

.user-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid #f1f3f5;
}

.user-option:hover {
  background: #f8f9fa;
}

.user-option.selected {
  background: #e3f2fd;
}

.user-option-info {
  display: flex;
  flex-direction: column;
}

.user-option-name {
  font-weight: 600;
  color: #2c3e50;
}

.user-option-meta {
  font-size: 0.8rem;
  color: #6c757d;
}

.check-icon {
  color: #27ae60;
}

.selected-users {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.75rem;
}

.selected-user-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #e3f2fd;
  border-radius: 20px;
  font-size: 0.85rem;
}

.remove-tag {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  color: #6c757d;
  padding: 0 0.25rem;
}

.remove-tag:hover {
  color: #e74c3c;
}

.clear-tags {
  background: none;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  cursor: pointer;
}

/* Date range */
.date-range {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.date-separator {
  color: #6c757d;
  font-weight: bold;
}

/* Filtres actifs */
.active-filters {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #dee2e6;
}

.active-filters-label {
  font-weight: 600;
  color: #495057;
  margin-right: 1rem;
}

.filter-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
  margin-top: 0.5rem;
}

.filter-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  background: #f8f9fa;
  border-radius: 20px;
  font-size: 0.85rem;
  border: 1px solid #dee2e6;
}

.filter-tag.blue { border-left: 3px solid #3498db; }
.filter-tag.orange { border-left: 3px solid #f39c12; }
.filter-tag.green { border-left: 3px solid #27ae60; }
.filter-tag.red { border-left: 3px solid #e74c3c; }
.filter-tag.purple { border-left: 3px solid #9b59b6; }

.filter-tag.status-tag {
  border-left: 3px solid;
}

.filter-tag.user-tag {
  background: #e3f2fd;
}

.remove-filter {
  background: none;
  border: none;
  font-size: 1.2rem;
  line-height: 1;
  cursor: pointer;
  color: #6c757d;
  padding: 0 0.25rem;
}

.remove-filter:hover {
  color: #e74c3c;
}

.clear-all-filters {
  background: none;
  border: 1px solid #e74c3c;
  color: #e74c3c;
  border-radius: 20px;
  padding: 0.25rem 0.75rem;
  font-size: 0.8rem;
  cursor: pointer;
  margin-left: 0.5rem;
}

.clear-all-filters:hover {
  background: #e74c3c;
  color: white;
}

/* Timeline */
.timeline {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.loading-state, .empty-state {
  text-align: center;
  padding: 4rem 2rem;
  color: #6c757d;
}

.loading-state i, .empty-state i {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 1rem;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.date-group {
  margin-bottom: 2rem;
}

.date-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #f1f3f5;
}

.date-badge {
  font-weight: 600;
  color: #2c3e50;
  font-size: 1.1rem;
  text-transform: capitalize;
}

.date-count {
  color: #6c757d;
  font-size: 0.9rem;
}

.events-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.event-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

.event-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #adb5bd;
}

/* Bordures colorées selon le type */
.event-card.conge { border-left: 4px solid #3498db; }
.event-card.retard { border-left: 4px solid #f39c12; }
.event-card.permission { border-left: 4px solid #27ae60; }
.event-card.repos_medical { border-left: 4px solid #e74c3c; }
.event-card.ostie { border-left: 4px solid #9b59b6; }

/* Bordures selon le statut (overlay) */
.event-card.en_attente { border-left-color: #f39c12; }
.event-card.retourne { border-left-color: #3498db; }
.event-card.rattrapage { border-left-color: #9b59b6; }
.event-card.en_cours { border-left-color: #3498db; }
.event-card.approuve { border-left-color: #27ae60; }
.event-card.transforme { border-left-color: #9b59b6; }
.event-card.refuse { border-left-color: #e74c3c; }
.event-card.annule { border-left-color: #95a5a6; }

.event-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: white;
  flex-shrink: 0;
}

.event-icon.conge { background: #3498db; }
.event-icon.retard { background: #f39c12; }
.event-icon.permission { background: #27ae60; }
.event-icon.repos_medical { background: #e74c3c; }
.event-icon.ostie { background: #9b59b6; }

.event-content {
  flex: 1;
  min-width: 0;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.event-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.event-user {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.event-type-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  color: white;
}

.event-type-badge.conge { background: #3498db; }
.event-type-badge.retard { background: #f39c12; }
.event-type-badge.permission { background: #27ae60; }
.event-type-badge.repos_medical { background: #e74c3c; }
.event-type-badge.ostie { background: #9b59b6; }

.event-statut-badge {
  padding: 0.2rem 0.6rem;
  border-radius: 16px;
  font-size: 0.7rem;
  font-weight: 600;
  background: #f8f9fa;
  border: 1px solid;
}

.event-statut-badge.en_attente { 
  background: #fff3e0; 
  color: #e67e22; 
  border-color: #f39c12; 
}
.event-statut-badge.retourne { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.event-statut-badge.rattrapage { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.event-statut-badge.en_cours { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.event-statut-badge.approuve { 
  background: #e8f5e9; 
  color: #2e7d32; 
  border-color: #27ae60; 
}
.event-statut-badge.transforme { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.event-statut-badge.refuse { 
  background: #ffebee; 
  color: #c62828; 
  border-color: #e74c3c; 
}
.event-statut-badge.annule { 
  background: #eceff1; 
  color: #455a64; 
  border-color: #95a5a6; 
}

.event-time {
  color: #6c757d;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}

.event-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.6rem;
  background: #f8f9fa;
  border-radius: 16px;
  font-size: 0.8rem;
  color: #495057;
}

.detail-chip.motif {
  background: #e3f2fd;
  color: #1976d2;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.event-actions {
  display: flex;
  gap: 0.25rem;
  margin-top: 0.5rem;
}

.action-btn {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  font-size: 1rem;
}

.action-btn.success { background: #27ae60; }
.action-btn.success:hover { background: #219a52; }

.action-btn.primary { background: #3498db; }
.action-btn.primary:hover { background: #2980b9; }

.action-btn.info { background: #9b59b6; }
.action-btn.info:hover { background: #8e44ad; }

.action-btn.purple { background: #9b59b6; }
.action-btn.purple:hover { background: #8e44ad; }

.action-btn.warning { background: #f39c12; }
.action-btn.warning:hover { background: #e67e22; }

.urgent-badge {
  position: absolute;
  top: -0.5rem;
  right: -0.5rem;
  width: 24px;
  height: 24px;
  background: #e74c3c;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  border: 2px solid white;
}

.load-more {
  text-align: center;
  margin-top: 2rem;
}

.btn-load-more {
  padding: 0.75rem 2rem;
  background: white;
  border: 1px solid #3498db;
  color: #3498db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-load-more:hover {
  background: #3498db;
  color: white;
}

/* Animations */
.event-list-enter-active,
.event-list-leave-active {
  transition: all 0.3s ease;
}

.event-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.event-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.event-list-move {
  transition: transform 0.3s ease;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .events-container {
    padding: 1rem;
  }

  .filters-row {
    flex-direction: column;
    gap: 1rem;
  }

  .filter-group {
    min-width: 100%;
  }

  .filter-buttons {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 0.5rem;
  }

  .filter-btn {
    flex-shrink: 0;
  }

  .event-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .event-title {
    width: 100%;
  }

  .event-time {
    align-self: flex-end;
  }

  .event-actions {
    flex-wrap: wrap;
  }
}
</style>