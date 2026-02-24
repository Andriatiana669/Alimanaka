<template>
  <div class="demandes-container">
    <!-- Header -->
    <div class="demandes-header">
      <h2>📋 Demandes en attente</h2>
      <div class="header-actions">
        <button class="btn-refresh" @click="refresh" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          Actualiser
        </button>
      </div>
    </div>

    <!-- Filtres rapides -->
    <div class="filters-bar">
      <button 
        v-for="type in eventTypes" 
        :key="type.value"
        class="filter-chip"
        :class="{ active: selectedType === type.value }"
        :style="{ borderColor: type.color }"
        @click="selectedType = type.value === selectedType ? null : type.value"
      >
        <span class="color-dot" :style="{ backgroundColor: type.color }"></span>
        {{ type.label }}
        <span class="count">{{ getCountByType(type.value) }}</span>
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement des demandes...</p>
    </div>

    <!-- Liste des demandes -->
    <div v-else-if="filteredDemandes.length === 0" class="empty-state">
      <i class="bi bi-inbox"></i>
      <h3>Aucune demande en attente</h3>
      <p>Toutes les demandes ont été traitées</p>
    </div>

    <div v-else class="demandes-list">
      <div 
        v-for="demande in filteredDemandes" 
        :key="demande.id"
        class="demande-card"
        :class="demande.type"
        @click="openDemandeDetails(demande)"
      >
        <!-- Icône -->
        <div class="demande-icon" :class="demande.type">
          <i :class="getIcon(demande.type)"></i>
        </div>

        <!-- Contenu -->
        <div class="demande-content">
          <div class="demande-header">
            <div class="demande-title">
              <span class="demande-user">
                <i class="bi bi-person-circle"></i>
                {{ demande.originalEvent?.user_display_name || demande.user_display_name || 'Utilisateur' }}
              </span>
              <span class="demande-type" :class="demande.type">
                {{ getTypeLabel(demande.type) }}
              </span>
            </div>
            <span class="demande-date">
              <i class="bi bi-calendar"></i>
              {{ formatDate(demande.start) }}
            </span>
          </div>

          <div class="demande-details">
            <!-- Détails selon le type - utiliser originalEvent -->
            <template v-if="demande.type === 'conge'">
              <span class="detail-chip">
                <i class="bi bi-calendar-range"></i>
                {{ formatDateRange(demande.originalEvent?.date_debut, demande.originalEvent?.date_fin) }}
              </span>
              <span class="detail-chip">
                <i class="bi bi-hourglass-split"></i>
                {{ demande.originalEvent?.jours_deduits || 0 }}j
              </span>
            </template>

            <template v-else-if="demande.type === 'retard'">
              <span class="detail-chip">
                <i class="bi bi-clock-history"></i>
                {{ demande.originalEvent?.minutes_retard || 0 }}min
              </span>
              <span class="detail-chip">
                <i class="bi bi-arrow-repeat"></i>
                {{ demande.originalEvent?.heures_restantes || 0 }}h restantes
              </span>
            </template>

            <template v-else-if="demande.type === 'permission'">
              <span class="detail-chip">
                <i class="bi bi-clock"></i>
                {{ formatTime(demande.originalEvent?.heure_depart) }} → {{ formatTime(demande.originalEvent?.heure_arrivee_max) }}
              </span>
            </template>

            <template v-else-if="demande.type === 'repos_medical'">
              <span class="detail-chip">
                <i class="bi bi-clock"></i>
                {{ formatTime(demande.originalEvent?.heure_debut) }} → {{ formatTime(demande.originalEvent?.heure_fin) }}
              </span>
              <span class="detail-chip">
                <i class="bi bi-hourglass"></i>
                {{ demande.originalEvent?.duree_heures || 0 }}h
              </span>
            </template>

            <template v-else-if="demande.type === 'ostie'">
              <span class="detail-chip">
                <i class="bi bi-clock"></i>
                Début {{ formatTime(demande.originalEvent?.heure_debut) }}
              </span>
            </template>

            <!-- Motif -->
            <span v-if="demande.originalEvent?.motif" class="detail-chip motif">
              <i class="bi bi-chat-text"></i>
              {{ truncateMotif(demande.originalEvent.motif) }}
            </span>
          </div>

          <!-- Actions rapides -->
          <div class="demande-actions" @click.stop>
            <button 
              v-if="canValidate(demande)"
              class="action-btn success"
              @click="validateDemande(demande)"
              title="Valider"
            >
              <i class="bi bi-check-lg"></i>
            </button>
            <button 
              v-if="canRefuse(demande)"
              class="action-btn danger"
              @click="refuseDemande(demande)"
              title="Refuser"
            >
              <i class="bi bi-x-lg"></i>
            </button>
            <button 
              v-if="canTransform(demande)"
              class="action-btn purple"
              @click="transformDemande(demande)"
              title="Transformer"
            >
              <i class="bi bi-arrow-right-circle"></i>
            </button>
            <button 
              v-if="canCancel(demande)"
              class="action-btn warning"
              @click="cancelDemande(demande)"
              title="Annuler"
            >
              <i class="bi bi-x-circle"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <Teleport to="body">
      <CongeDetailModal
        v-if="showCongeModal && selectedDemande?.type === 'conge'"
        :conge="selectedDemande.originalEvent"
        @close="closeModals"
        @refresh="refresh"
      />
      <RetardDetailModal
        v-if="showRetardModal && selectedDemande?.type === 'retard'"
        :retard="selectedDemande.originalEvent"
        @close="closeModals"
        @refresh="refresh"
      />
      <PermissionDetailModal
        v-if="showPermissionModal && selectedDemande?.type === 'permission'"
        :permission="selectedDemande.originalEvent"
        @close="closeModals"
        @refresh="refresh"
      />
      <ReposMedicalDetailModal
        v-if="showReposModal && selectedDemande?.type === 'repos_medical'"
        :repos="selectedDemande.originalEvent"
        @close="closeModals"
        @refresh="refresh"
      />
      <OstieDetailModal
        v-if="showOstieModal && selectedDemande?.type === 'ostie'"
        :ostie="selectedDemande.originalEvent"
        @close="closeModals"
        @refresh="refresh"
      />
    </Teleport>
  </div>
</template>





<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEventsStore } from '@/store/events'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useRetardsStore } from '@/store/retards'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useOstieStore } from '@/store/ostie'
import { format, parseISO } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// Modals
import CongeDetailModal from '@/components/conges/CongeDetailModal.vue'
import RetardDetailModal from '@/components/retards/RetardDetailModal.vue'
import PermissionDetailModal from '@/components/permissions/PermissionDetailModal.vue'
import ReposMedicalDetailModal from '@/components/reposmedicale/ReposMedicalDetailModal.vue'
import OstieDetailModal from '@/components/ostie/OstieDetailModal.vue'

// ============================================
// Interfaces pour typer les événements
// ============================================

interface OriginalEvent {
  id?: string | number
  user_display_name?: string
  date_debut?: string
  date_fin?: string
  jours_deduits?: number
  minutes_retard?: number
  heures_restantes?: number
  heure_depart?: string
  heure_arrivee_max?: string
  heure_debut?: string
  heure_fin?: string
  duree_heures?: number
  motif?: string
  [key: string]: any
}

interface CalendarEvent {
  id: string
  title: string
  start: Date
  end?: Date
  allDay: boolean
  color: string
  type: string
  user_id?: number
  user_display_name?: string
  statut?: string
  isBlocked?: boolean
  isSystem?: boolean
  originalEvent?: OriginalEvent
}

// Stores
const eventsStore = useEventsStore()
const authStore = useAuthStore()
const congesStore = useCongesStore()
const retardsStore = useRetardsStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const ostieStore = useOstieStore()

// État
const loading = ref(false)
const selectedType = ref<string | null>(null)
const selectedDemande = ref<CalendarEvent | null>(null)

// Modals
const showCongeModal = ref(false)
const showRetardModal = ref(false)
const showPermissionModal = ref(false)
const showReposModal = ref(false)
const showOstieModal = ref(false)

// Types d'événements
const eventTypes = [
  { value: 'conge', label: 'Congés', color: '#3498db' },
  { value: 'retard', label: 'Retards', color: '#f39c12' },
  { value: 'permission', label: 'Permissions', color: '#27ae60' },
  { value: 'repos_medical', label: 'Repos médicaux', color: '#e74c3c' },
  { value: 'ostie', label: 'OSTIES', color: '#9b59b6' }
]

// Demandes en attente (statut = 'en_attente')
const demandesEnAttente = computed<CalendarEvent[]>(() => {
  return eventsStore.eventsForCalendar.filter(e => 
    e.statut === 'en_attente' && 
    e.user_id && 
    ['conge', 'retard', 'permission', 'repos_medical', 'ostie'].includes(e.type as string)
  ) as CalendarEvent[]
})

// Demandes filtrées par type
const filteredDemandes = computed(() => {
  if (!selectedType.value) return demandesEnAttente.value
  return demandesEnAttente.value.filter(d => d.type === selectedType.value)
})

// Compteur par type
const getCountByType = (type: string) => {
  return demandesEnAttente.value.filter(d => d.type === type).length
}

// ============================================
// Utilitaires
// ============================================

const getIcon = (type: string): string => {
  const icons: Record<string, string> = {
    conge: 'bi bi-calendar-check',
    retard: 'bi bi-clock-history',
    permission: 'bi bi-door-open',
    repos_medical: 'bi bi-heart-pulse',
    ostie: 'bi bi-lightning'
  }
  return icons[type] || 'bi bi-question-circle'
}

const getTypeLabel = (type: string): string => {
  const found = eventTypes.find(t => t.value === type)
  return found?.label || type
}

const formatDate = (date: Date | string): string => {
  if (!date) return ''
  const d = typeof date === 'string' ? new Date(date) : date
  return format(d, 'dd/MM/yyyy', { locale: fr })
}

const formatTime = (timeStr: string | undefined): string => {
  if (!timeStr) return '--:--'
  return timeStr.substring(0, 5)
}

const formatDateRange = (start: string | undefined, end: string | undefined): string => {
  if (!start || !end) return ''
  if (start === end) return formatDate(start)
  return `${formatDate(start)} → ${formatDate(end)}`
}

const truncateMotif = (motif: string, maxLength = 50): string => {
  if (!motif) return ''
  if (motif.length <= maxLength) return motif
  return motif.substring(0, maxLength) + '...'
}

// ============================================
// Vérifications des actions
// ============================================

const canManageOthers = computed(() => {
  const user = authStore.user
  return user?.is_superuser || user?.est_chef_equipe
})

const canValidate = (demande: CalendarEvent): boolean => {
  if (!canManageOthers.value) return false
  return demande.statut === 'en_attente' && 
         ['conge', 'repos_medical'].includes(demande.type)
}

const canRefuse = (demande: CalendarEvent): boolean => {
  if (!canManageOthers.value) return false
  return demande.statut === 'en_attente' && 
         ['conge'].includes(demande.type)
}

const canTransform = (demande: CalendarEvent): boolean => {
  if (!canManageOthers.value) return false
  
  const original = demande.originalEvent || {}
  
  if (demande.type === 'permission') {
    return demande.statut === 'retourne' && (original.minutes_depassement || 0) > 0
  }
  if (demande.type === 'repos_medical') {
    return demande.statut === 'en_attente'
  }
  if (demande.type === 'ostie') {
    return demande.statut === 'en_attente'
  }
  return false
}

const canCancel = (demande: CalendarEvent): boolean => {
  if (!canManageOthers.value) return false
  return ['en_attente', 'retourne', 'rattrapage'].includes(demande.statut || '')
}

// ============================================
// Actions
// ============================================

const openDemandeDetails = (demande: CalendarEvent) => {
  selectedDemande.value = demande
  
  switch (demande.type) {
    case 'conge':
      showCongeModal.value = true
      break
    case 'retard':
      showRetardModal.value = true
      break
    case 'permission':
      showPermissionModal.value = true
      break
    case 'repos_medical':
      showReposModal.value = true
      break
    case 'ostie':
      showOstieModal.value = true
      break
  }
}

const closeModals = () => {
  showCongeModal.value = false
  showRetardModal.value = false
  showPermissionModal.value = false
  showReposModal.value = false
  showOstieModal.value = false
  selectedDemande.value = null
}



const getDemandeId = (demande: CalendarEvent): number | null => {
  const original = demande.originalEvent || demande
  if (!original.id) return null
  
  if (typeof original.id === 'string') {
    // Extraire le nombre de l'ID (ex: "conge_123" -> 123)
    const matches = original.id.match(/\d+/)
    return matches ? parseInt(matches[0]) : null
  }
  
  return original.id
}



const validateDemande = async (demande: CalendarEvent) => {
  const id = getDemandeId(demande)
  if (!id) {
    alert('Impossible de valider : ID non trouvé')
    return
  }
  
  if (!confirm(`Valider cette demande de ${getTypeLabel(demande.type)} ?`)) return
  
  try {
    switch (demande.type) {
      case 'conge':
        await congesStore.validerConge(id)
        break
      case 'repos_medical':
        await reposStore.validerReposMedical(id)
        break
      default:
        alert('Type de demande non supporté pour la validation')
        return
    }
    
    await refresh()
    alert('Demande validée avec succès !')
  } catch (err) {
    console.error('Erreur validation:', err)
    alert('Erreur lors de la validation')
  }
}

const refuseDemande = async (demande: CalendarEvent) => {
  const id = getDemandeId(demande)
  if (!id) {
    alert('Impossible de refuser : ID non trouvé')
    return
  }
  
  const commentaire = prompt('Motif du refus (optionnel):')
  if (commentaire === null) return
  
  if (!confirm(`Refuser cette demande de ${getTypeLabel(demande.type)} ?`)) return
  
  try {
    if (demande.type !== 'conge') {
      alert('Seuls les congés peuvent être refusés')
      return
    }
    
    await congesStore.refuserConge(id, commentaire || undefined)
    await refresh()
    alert('Demande refusée avec succès !')
  } catch (err) {
    console.error('Erreur refus:', err)
    alert('Erreur lors du refus')
  }
}


const transformDemande = (demande: CalendarEvent) => {
  const id = getDemandeId(demande)
  if (!id) {
    alert('Impossible de transformer : ID non trouvé')
    return
  }
  openDemandeDetails(demande)
}


const cancelDemande = async (demande: CalendarEvent) => {
  const id = getDemandeId(demande)
  if (!id) {
    alert('Impossible d\'annuler : ID non trouvé')
    return
  }
  
  const commentaire = prompt('Motif de l\'annulation (optionnel):')
  if (commentaire === null) return
  
  if (!confirm(`Annuler cette demande de ${getTypeLabel(demande.type)} ?`)) return
  
  try {
    switch (demande.type) {
      case 'conge':
        await congesStore.annulerConge(id)
        break
      case 'retard':
        await retardsStore.annulerRetard(id, commentaire || undefined)
        break
      case 'permission':
        await permissionsStore.annulerPermission(id, commentaire || undefined)
        break
      case 'repos_medical':
        await reposStore.annulerReposMedical(id, commentaire || undefined)
        break
      case 'ostie':
        await ostieStore.annulerOstie(id, commentaire || undefined)
        break
      default:
        alert('Type de demande non supporté pour l\'annulation')
        return
    }
    
    await refresh()
    alert('Demande annulée avec succès !')
  } catch (err) {
    console.error('Erreur annulation:', err)
    alert('Erreur lors de l\'annulation')
  }
}



const refresh = async () => {
  loading.value = true
  const currentYear = new Date().getFullYear()
  await eventsStore.fetchCalendrier({ annee: currentYear })
  loading.value = false
}

// Initialisation
onMounted(async () => {
  await refresh()
})
</script>


<style scoped>
.demandes-container {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.demandes-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.demandes-header h2 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #e9ecef;
}

.filters-bar {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.8rem;
  background: white;
  border: 1px solid #dee2e6;
  border-radius: 20px;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-chip:hover {
  background: #f8f9fa;
  border-color: #adb5bd;
}

.filter-chip.active {
  background: #e3f2fd;
  border-color: #3498db;
}

.color-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.count {
  background: rgba(0,0,0,0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 12px;
  font-size: 0.7rem;
  margin-left: 0.25rem;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.loading-state i, .empty-state i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.spinner {
  width: 30px;
  height: 30px;
  margin: 0 auto 1rem;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.demandes-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.demande-card {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.demande-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  border-color: #adb5bd;
}

.demande-icon {
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

.demande-icon.conge { background: #3498db; }
.demande-icon.retard { background: #f39c12; }
.demande-icon.permission { background: #27ae60; }
.demande-icon.repos_medical { background: #e74c3c; }
.demande-icon.ostie { background: #9b59b6; }

.demande-content {
  flex: 1;
  min-width: 0;
}

.demande-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.demande-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.demande-user {
  font-weight: 600;
  color: #2c3e50;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.demande-type {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  color: white;
  font-weight: 600;
  text-transform: uppercase;
}

.demande-type.conge { background: #3498db; }
.demande-type.retard { background: #f39c12; }
.demande-type.permission { background: #27ae60; }
.demande-type.repos_medical { background: #e74c3c; }
.demande-type.ostie { background: #9b59b6; }

.demande-date {
  color: #6c757d;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.demande-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.detail-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.6rem;
  background: #f8f9fa;
  border-radius: 16px;
  font-size: 0.75rem;
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

.demande-actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  color: white;
  font-size: 0.9rem;
}

.action-btn.success { background: #27ae60; }
.action-btn.success:hover { background: #219a52; }

.action-btn.danger { background: #e74c3c; }
.action-btn.danger:hover { background: #c0392b; }

.action-btn.purple { background: #9b59b6; }
.action-btn.purple:hover { background: #8e44ad; }

.action-btn.warning { background: #f39c12; }
.action-btn.warning:hover { background: #e67e22; }

@media (max-width: 768px) {
  .demande-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .demande-date {
    align-self: flex-end;
  }
  
  .demande-actions {
    margin-top: 0.5rem;
  }
}
</style>