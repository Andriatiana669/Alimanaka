<template>
  <div class="retards-view">
    <!-- Header -->
    <div class="header-section">
      <h1>Gestion des Retards</h1>
      <div class="actions">
        <button 
          v-if="canCreate"
          class="btn btn-primary"
          @click="openCreateModal"
        >
          <span class="icon">⏰</span>
          Déclarer un retard
        </button>
        <button 
          v-if="isAdmin"
          class="btn btn-secondary"
          @click="exportRetards"
        >
          <span class="icon">📊</span>
          Export Excel
        </button>
      </div>
    </div>

    <!-- Filtres -->
    <div class="filters-section">
      <div class="filter-group">
        <label>Année:</label>
        <select v-model="selectedAnnee" @change="loadRetards">
          <option v-for="annee in anneesDisponibles" :key="annee" :value="annee">
            {{ annee }}
          </option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Statut:</label>
        <select v-model="selectedStatut" @change="loadRetards">
          <option value="">Tous</option>
          <option value="en_attente">En attente</option>
          <option value="approuve">Approuvé</option>
          <option value="annule">Annulé</option>
        </select>
      </div>

      <!-- Filtres admin/manager -->
      <template v-if="isManager || isAdmin">
        <div class="filter-group">
          <label>Pôle:</label>
          <PoleSelect v-model="selectedPole" @change="onPoleChange" />
        </div>
        
        <div class="filter-group">
          <label>Équipe:</label>
          <EquipeSelect 
            v-model="selectedEquipe" 
            :pole-id="selectedPole"
            @change="loadRetards" 
          />
        </div>
      </template>
    </div>

    <!-- Stats rapides -->
    <div class="stats-grid">
      <div class="stat-card warning">
        <div class="stat-value">{{ retardsEnAttente.length }}</div>
        <div class="stat-label">En attente</div>
      </div>
      <div class="stat-card success">
        <div class="stat-value">{{ retardsApprouves.length }}</div>
        <div class="stat-label">Approuvés</div>
      </div>
      <div class="stat-card danger">
        <div class="stat-value">{{ totalHeuresRestantes }}h</div>
        <div class="stat-label">Heures à rattraper</div>
      </div>
    </div>

    <!-- Layout principal: Calendrier + Liste -->
    <div class="main-layout">
      <!-- Calendrier -->
      <div class="calendar-section">
        <Calendar
          :events="calendarEvents"
          :current-year="selectedAnnee"
          @year-change="selectedAnnee = $event; loadRetards()"
          @event-click="onCalendarEventClick"
          @date-click="onCalendarDateClick"
        />
      </div>

      <!-- Liste des retards -->
      <div class="list-section">
        <h2>Mes retards</h2>
        
        <LoadingSpinner v-if="loading" />
        
        <div v-else-if="retards.length === 0" class="empty-state">
          <div class="empty-icon">✅</div>
          <p>Aucun retard enregistré</p>
        </div>
        
        <div v-else class="retards-list">
          <div 
            v-for="retard in retardsFiltres" 
            :key="retard.id"
            class="retard-card"
            :class="`status-${retard.statut}`"
          >
            <div class="retard-header">
              <div class="retard-date">
                <span class="day">{{ formatDay(retard.date) }}</span>
                <span class="month">{{ formatMonth(retard.date) }}</span>
              </div>
              <div class="retard-status" :class="retard.statut">
                {{ retard.statut_display }}
              </div>
            </div>
            
            <div class="retard-body">
              <div class="retard-info">
                <div class="info-row">
                  <span class="label">Arrivée:</span>
                  <span class="value">{{ retard.heure_arrivee_reelle }}</span>
                  <span class="delay">(+{{ retard.minutes_retard }}min)</span>
                </div>
                
                <div class="info-row">
                  <span class="label">À rattraper:</span>
                  <span class="value highlight">{{ retard.heures_a_rattraper }}h</span>
                </div>
                
                <div v-if="parseFloat(retard.heures_restantes) > 0" class="info-row">
                  <span class="label">Reste:</span>
                  <span class="value danger">{{ retard.heures_restantes }}h</span>
                </div>
                
                <div v-if="retard.motif_retard" class="info-row">
                  <span class="label">Justificatif:</span>
                  <span class="value text-small">{{ retard.motif_retard }}</span>
                </div>
              </div>
              
              <!-- Liste des rattrapages -->
              <div v-if="retard.rattrapages?.length > 0" class="rattrapages-list">
                <div class="rattrapages-title">Rattrapages effectués:</div>
                <div 
                  v-for="rattrapage in retard.rattrapages" 
                  :key="rattrapage.id"
                  class="rattrapage-item"
                >
                  <span class="rattrapage-date">{{ formatDate(rattrapage.date_rattrapage) }}</span>
                  <span class="rattrapage-heures">+{{ rattrapage.heures_rattrapees }}h</span>
                </div>
              </div>
            </div>
            
            <div class="retard-actions">
              <!-- Bouton Rattraper (si en attente et heures restantes) -->
              <button 
                v-if="canRattraper(retard)"
                class="btn btn-success btn-small"
                @click="openRattraperModal(retard)"
              >
                Rattraper
              </button>
              
              <!-- Bouton Annuler -->
              <button 
                v-if="canAnnuler(retard)"
                class="btn btn-danger btn-small"
                @click="confirmAnnuler(retard)"
              >
                Annuler
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal: Déclarer un retard -->
    <Modal v-if="showCreateModal" @close="showCreateModal = false">
      <div class="modal-header">
        <h3>Déclarer un retard</h3>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="submitRetard">
          <div class="form-group">
            <label>Date du retard *</label>
            <input 
              v-model="newRetard.date" 
              type="date" 
              required
              :max="today"
            />
          </div>
          
          <div class="form-group">
            <label>Heure d'arrivée réelle *</label>
            <input 
              v-model="newRetard.heure_arrivee_reelle" 
              type="time" 
              required
            />
          </div>
          
          <div class="form-group">
            <label>Justificatif / Motif</label>
            <textarea 
              v-model="newRetard.motif_retard" 
              rows="3"
              placeholder="Expliquez la raison du retard..."
            ></textarea>
          </div>
          
          <ErrorMessage v-if="formError" :message="formError" />
        </form>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showCreateModal = false">
          Annuler
        </button>
        <button 
          class="btn btn-primary" 
          @click="submitRetard"
          :disabled="submitting"
        >
          {{ submitting ? 'Envoi...' : 'Déclarer' }}
        </button>
      </div>
    </Modal>

    <!-- Modal: Rattraper le retard -->
    <Modal v-if="showRattraperModal" @close="showRattraperModal = false">
      <div class="modal-header">
        <h3>Rattraper le retard</h3>
        <p class="modal-subtitle">
          {{ selectedRetard?.heures_restantes }}h restantes à rattraper
        </p>
      </div>
      
      <div class="modal-body">
        <form @submit.prevent="submitRattrapage">
          <div class="form-group">
            <label>Date du rattrapage *</label>
            <input 
              v-model="rattrapageData.date_rattrapage" 
              type="date" 
              required
              :min="today"
            />
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>Heure de début *</label>
              <input 
                v-model="rattrapageData.heure_debut" 
                type="time" 
                required
              />
            </div>
            
            <div class="form-group">
              <label>Heure de fin *</label>
              <input 
                v-model="rattrapageData.heure_fin" 
                type="time" 
                required
              />
            </div>
          </div>
          
          <div class="form-group">
            <label>Commentaire</label>
            <textarea 
              v-model="rattrapageData.commentaire" 
              rows="2"
              placeholder="Détails sur le rattrapage..."
            ></textarea>
          </div>
          
          <div v-if="calculatedHeures" class="calculated-heures">
            Heures rattrapées: <strong>{{ calculatedHeures }}h</strong>
          </div>
          
          <ErrorMessage v-if="formError" :message="formError" />
        </form>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showRattraperModal = false">
          Annuler
        </button>
        <button 
          class="btn btn-success" 
          @click="submitRattrapage"
          :disabled="submitting || !calculatedHeures"
        >
          {{ submitting ? 'Validation...' : 'Valider le rattrapage' }}
        </button>
      </div>
    </Modal>

    <!-- Modal: Confirmation annulation -->
    <Modal v-if="showAnnulerModal" @close="showAnnulerModal = false">
      <div class="modal-header">
        <h3>Confirmer l'annulation</h3>
      </div>
      
      <div class="modal-body">
        <p>Êtes-vous sûr de vouloir annuler ce retard ?</p>
        <div class="form-group">
          <label>Commentaire (optionnel)</label>
          <textarea 
            v-model="annulationCommentaire" 
            rows="2"
          ></textarea>
        </div>
      </div>
      
      <div class="modal-footer">
        <button class="btn btn-secondary" @click="showAnnulerModal = false">
          Non, garder
        </button>
        <button 
          class="btn btn-danger" 
          @click="confirmAnnulation"
          :disabled="submitting"
        >
          {{ submitting ? 'Annulation...' : 'Oui, annuler' }}
        </button>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRetardsStore } from '@/store/retards';
import { useAuthStore } from '@/store/auth';
import { retardsApi } from '@/api/retards';
import Calendar from '@/components/common/Calendar.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import ErrorMessage from '@/components/common/ErrorMessage.vue';
import Modal from '@/components/common/Modal.vue';
import PoleSelect from '@/components/common/PoleSelect.vue';
import EquipeSelect from '@/components/common/EquipeSelect.vue';
import type { Retard, RetardCreateData, RattrapageCreateData } from '@/types/retards';

const store = useRetardsStore();
const authStore = useAuthStore();

// Computed from store
const retards = computed(() => store.retards);
const retardsEnAttente = computed(() => store.retardsEnAttente);
const retardsApprouves = computed(() => store.retardsApprouves);
const loading = computed(() => store.loading);

// Permissions
const canCreate = computed(() => true);
const isAdmin = computed(() => authStore.user?.is_staff || authStore.user?.is_superuser);

// CORRECTION: Utiliser une propriété qui existe sur le type User
const isManager = computed(() => {
  const user = authStore.user as any; // ← CORRECTION: cast en any pour éviter l'erreur TS
  return user?.equipes_gerees?.length > 0 || user?.equipes_co_gerees?.length > 0;
});

// Filtres - CORRECTION: utiliser null au lieu de ""
const selectedAnnee = ref(new Date().getFullYear());
const selectedStatut = ref('');
const selectedPole = ref<number | null>(null);  // ← CORRECTION: null au lieu de ""
const selectedEquipe = ref<number | null>(null); // ← CORRECTION: null au lieu de ""

const anneesDisponibles = computed(() => {
  const current = new Date().getFullYear();
  return [current - 1, current, current + 1];
});

const retardsFiltres = computed(() => {
  let result = retards.value;
  if (selectedStatut.value) {
    result = result.filter(r => r.statut === selectedStatut.value);
  }
  return result.sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
});

const totalHeuresRestantes = computed(() => {
  return retards.value
    .filter(r => r.statut === 'en_attente')
    .reduce((sum, r) => sum + parseFloat(r.heures_restantes || '0'), 0)
    .toFixed(2);
});

// Calendar events
const calendarEvents = ref<any[]>([]);

// Modals state
const showCreateModal = ref(false);
const showRattraperModal = ref(false);
const showAnnulerModal = ref(false);
const submitting = ref(false);
const formError = ref('');
const selectedRetard = ref<Retard | null>(null);
const annulationCommentaire = ref('');

// Form data
const today = new Date().toISOString().split('T')[0];
const newRetard = ref<RetardCreateData>({
  date: today,
  heure_arrivee_reelle: '',
  motif_retard: ''
});

const rattrapageData = ref<RattrapageCreateData>({
  date_rattrapage: today,
  heure_debut: '',
  heure_fin: '',
  commentaire: ''
});

// Calcul des heures de rattrapage
const calculatedHeures = computed(() => {
  if (!rattrapageData.value.heure_debut || !rattrapageData.value.heure_fin) return null;
  
  const debut = new Date(`2000-01-01T${rattrapageData.value.heure_debut}`);
  const fin = new Date(`2000-01-01T${rattrapageData.value.heure_fin}`);
  
  if (fin <= debut) return null;
  
  const diffMs = fin.getTime() - debut.getTime();
  const diffHours = diffMs / (1000 * 60 * 60);
  
  return diffHours.toFixed(2);
});

// Methods
const loadRetards = async () => {
  try {
    const filters = {
      annee: selectedAnnee.value,
      statut: selectedStatut.value || undefined
    };
    
    if (isAdmin.value || isManager.value) {
      await store.fetchAllRetards(filters);
    } else {
      await store.fetchMesRetards(filters);
    }
    
    await loadCalendar();
  } catch (err) {
    console.error('Erreur chargement retards:', err);
  }
};

const loadCalendar = async () => {
  try {
    const events = await store.fetchCalendrier(
      selectedAnnee.value,
      selectedPole.value || undefined,
      selectedEquipe.value || undefined
    );
    calendarEvents.value = events;
  } catch (err) {
    console.error('Erreur chargement calendrier:', err);
  }
};

const onPoleChange = () => {
  selectedEquipe.value = null; // ← CORRECTION: null au lieu de ""
  loadRetards();
};

const openCreateModal = () => {
  newRetard.value = {
    date: today,
    heure_arrivee_reelle: '',
    motif_retard: ''
  };
  formError.value = '';
  showCreateModal.value = true;
};

const submitRetard = async () => {
  submitting.value = true;
  formError.value = '';
  
  try {
    await store.createRetard(newRetard.value);
    showCreateModal.value = false;
    await loadRetards();
  } catch (err: any) {
    formError.value = err.response?.data?.detail || 'Erreur lors de la création';
  } finally {
    submitting.value = false;
  }
};

const canRattraper = (retard: Retard) => {
  return retard.statut === 'en_attente' && parseFloat(retard.heures_restantes) > 0;
};

const canAnnuler = (retard: Retard) => {
  return retard.statut === 'en_attente';
};

const openRattraperModal = (retard: Retard) => {
  selectedRetard.value = retard;
  rattrapageData.value = {
    date_rattrapage: today,
    heure_debut: '',
    heure_fin: '',
    commentaire: ''
  };
  formError.value = '';
  showRattraperModal.value = true;
};

const submitRattrapage = async () => {
  if (!selectedRetard.value || !calculatedHeures.value) return;
  
  submitting.value = true;
  formError.value = '';
  
  try {
    await store.rattraperRetard(selectedRetard.value.id, rattrapageData.value);
    showRattraperModal.value = false;
    await loadRetards();
  } catch (err: any) {
    formError.value = err.response?.data?.error || 'Erreur lors du rattrapage';
  } finally {
    submitting.value = false;
  }
};

const confirmAnnuler = (retard: Retard) => {
  selectedRetard.value = retard;
  annulationCommentaire.value = '';
  showAnnulerModal.value = true;
};

const confirmAnnulation = async () => {
  if (!selectedRetard.value) return;
  
  submitting.value = true;
  
  try {
    await store.annulerRetard(selectedRetard.value.id, annulationCommentaire.value);
    showAnnulerModal.value = false;
    await loadRetards();
  } catch (err) {
    console.error('Erreur annulation:', err);
  } finally {
    submitting.value = false;
  }
};

const onCalendarEventClick = (event: any) => {
  if (event.type === 'retard') {
    const retardId = parseInt(event.id.replace('retard_', ''));
    const retard = retards.value.find(r => r.id === retardId);
    if (retard && canRattraper(retard)) {
      openRattraperModal(retard);
    }
  }
};

const onCalendarDateClick = (date: string) => {
  newRetard.value.date = date;
  openCreateModal();
};

const exportRetards = async () => {
  try {
    const response = await retardsApi.exportRetards(); // ← CORRECTION: utiliser retardsApi directement
    const blob = new Blob([response.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `retards_export_${new Date().toISOString().split('T')[0]}.xlsx`;
    link.click();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    console.error('Erreur export:', err);
  }
};

// Formatters
const formatDay = (dateStr: string) => {
  return new Date(dateStr).getDate();
};

const formatMonth = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('fr-FR', { month: 'short' });
};

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString('fr-FR');
};

// Lifecycle
onMounted(() => {
  loadRetards();
  store.fetchTypesRetard();
});

watch(selectedAnnee, () => {
  loadRetards();
});
</script>

<style scoped>
.retards-view {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.header-section h1 {
  margin: 0;
  color: #2c3e50;
}

.actions {
  display: flex;
  gap: 12px;
}

.filters-section {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.filter-group label {
  font-size: 12px;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
}

.filter-group select,
.filter-group input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 120px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
  border-left: 4px solid;
}

.stat-card.warning { border-left-color: #ff9800; }
.stat-card.success { border-left-color: #4caf50; }
.stat-card.danger { border-left-color: #f44336; }

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #2c3e50;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-top: 4px;
}

.main-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.calendar-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.list-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  max-height: 800px;
  overflow-y: auto;
}

.list-section h2 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #2c3e50;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.retards-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.retard-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.retard-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.retard-card.status-en_attente { border-left: 4px solid #ff9800; }
.retard-card.status-approuve { border-left: 4px solid #4caf50; }
.retard-card.status-annule { border-left: 4px solid #9e9e9e; opacity: 0.7; }

.retard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
}

.retard-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: white;
  padding: 8px 12px;
  border-radius: 4px;
  min-width: 50px;
}

.retard-date .day {
  font-size: 24px;
  font-weight: bold;
  color: #2c3e50;
}

.retard-date .month {
  font-size: 12px;
  text-transform: uppercase;
  color: #666;
}

.retard-status {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.retard-status.en_attente {
  background: #fff3e0;
  color: #e65100;
}

.retard-status.approuve {
  background: #e8f5e9;
  color: #2e7d32;
}

.retard-status.annule {
  background: #eceff1;
  color: #546e7a;
}

.retard-body {
  padding: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.info-row .label {
  font-size: 12px;
  color: #666;
  min-width: 100px;
}

.info-row .value {
  font-weight: 600;
  color: #2c3e50;
}

.info-row .value.highlight {
  color: #ff9800;
}

.info-row .value.danger {
  color: #f44336;
}

.info-row .value.text-small {
  font-size: 12px;
  font-weight: normal;
}

.delay {
  color: #f44336;
  font-weight: 600;
  font-size: 12px;
}

.rattrapages-list {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #ddd;
}

.rattrapages-title {
  font-size: 12px;
  font-weight: 600;
  color: #4caf50;
  margin-bottom: 8px;
}

.rattrapage-item {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
  padding: 4px 0;
  color: #666;
}

.rattrapage-heures {
  color: #4caf50;
  font-weight: 600;
}

.retard-actions {
  display: flex;
  gap: 8px;
  padding: 12px;
  background: #f8f9fa;
  border-top: 1px solid #e0e0e0;
}

/* Modal styles */
.modal-header {
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
}

.modal-subtitle {
  color: #666;
  margin: 8px 0 0 0;
  font-size: 14px;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #2196f3;
  color: white;
}

.btn-primary:hover {
  background: #1976d2;
}

.btn-secondary {
  background: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background: #d0d0d0;
}

.btn-success {
  background: #4caf50;
  color: white;
}

.btn-success:hover {
  background: #388e3c;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #555;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.calculated-heures {
  background: #e8f5e9;
  padding: 12px;
  border-radius: 4px;
  text-align: center;
  margin-top: 16px;
  color: #2e7d32;
}

/* Responsive */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .list-section {
    max-height: none;
  }
}
</style>