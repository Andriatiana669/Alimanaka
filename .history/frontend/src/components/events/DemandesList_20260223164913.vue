<template>
  <div class="demandes-container">
    <!-- Header -->
    <div class="demandes-header">
      <h2>📋 Toutes les demandes</h2>
      <div class="header-actions">
        <button class="btn-refresh" @click="loadAllData" :disabled="loading">
          <i class="bi" :class="loading ? 'bi-arrow-repeat spin' : 'bi-arrow-clockwise'"></i>
          Actualiser
        </button>
      </div>
    </div>

    <!-- Filtres rapides -->
    <div class="filters-bar">
      <!-- Filtre par type -->
      <div class="filter-group">
        <label>Type</label>
        <div class="filter-buttons">
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
      </div>

      <!-- Filtre par statut -->
      <div class="filter-group">
        <label>Statut</label>
        <div class="filter-buttons">
          <button 
            v-for="status in allStatusOptions" 
            :key="status.value"
            class="filter-chip status-chip"
            :class="{ active: selectedStatus === status.value }"
            @click="selectedStatus = status.value === selectedStatus ? null : status.value"
          >
            <span class="status-dot" :class="status.color"></span>
            {{ status.label }}
            <span class="count">{{ getCountByStatus(status.value) }}</span>
          </button>
        </div>
      </div>

      <!-- Filtre par année -->
      <div class="filter-group small">
        <label>Année</label>
        <select v-model="selectedYear" class="form-select">
          <option v-for="year in availableYears" :key="year" :value="year">
            {{ year }}
          </option>
        </select>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="loading-state">
      <div class="spinner"></div>
      <p>Chargement des demandes...</p>
    </div>

    <!-- Liste des demandes -->
    <div v-else-if="filteredDemandes.length === 0" class="empty-state">
      <i class="bi bi-inbox"></i>
      <h3>Aucune demande trouvée</h3>
      <p>Essayez de modifier vos filtres</p>
    </div>

    <div v-else class="demandes-list">
      <div 
        v-for="demande in filteredDemandes" 
        :key="demande.id"
        class="demande-card"
        :class="[demande.type, demande.statut]"
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
                {{ getUserDisplayName(demande) }}
              </span>
              <span class="demande-type" :class="demande.type">
                {{ getTypeLabel(demande.type) }}
              </span>
              <span class="demande-status" :class="demande.statut">
                {{ getStatusLabel(demande.statut, demande.type) }}
              </span>
            </div>
            <span class="demande-date">
              <i class="bi bi-calendar"></i>
              {{ formatDate(demande.start) }}
            </span>
          </div>

          <div class="demande-details">
            <!-- Détails selon le type -->
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
              <span v-if="demande.originalEvent?.heures_restantes" class="detail-chip">
                <i class="bi bi-arrow-repeat"></i>
                {{ demande.originalEvent.heures_restantes }}h restantes
              </span>
            </template>

            <template v-else-if="demande.type === 'permission'">
              <span class="detail-chip">
                <i class="bi bi-clock"></i>
                {{ formatTime(demande.originalEvent?.heure_depart) }} → {{ formatTime(demande.originalEvent?.heure_arrivee_max) }}
              </span>
              <span v-if="demande.originalEvent?.heures_restantes" class="detail-chip">
                <i class="bi bi-arrow-repeat"></i>
                {{ demande.originalEvent.heures_restantes }}h restantes
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
              <span v-if="demande.originalEvent?.heure_fin" class="detail-chip">
                Fin {{ formatTime(demande.originalEvent.heure_fin) }}
              </span>
            </template>

            <!-- Motif -->
            <span v-if="demande.originalEvent?.motif" class="detail-chip motif">
              <i class="bi bi-chat-text"></i>
              {{ truncateMotif(demande.originalEvent.motif) }}
            </span>
          </div>

          <!-- Actions rapides -->
          <div v-if="canManageThisDemande(demande)" class="demande-actions" @click.stop>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useAuthStore } from '@/store/auth'
import { useCongesStore } from '@/store/conges'
import { useRetardsStore } from '@/store/retards'
import { usePermissionsStore } from '@/store/permissions'
import { useReposMedicaleStore } from '@/store/reposmedicale'
import { useOstieStore } from '@/store/ostie'
import { format, parseISO, getYear } from 'date-fns'
import { fr } from 'date-fns/locale/fr'

// ============================================
// Interfaces
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
  minutes_depassement?: number
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
const authStore = useAuthStore()
const congesStore = useCongesStore()
const retardsStore = useRetardsStore()
const permissionsStore = usePermissionsStore()
const reposStore = useReposMedicaleStore()
const ostieStore = useOstieStore()

// ============================================
// Options de statut
// ============================================
const allStatusOptions = [
  // Congés
  { value: 'en_attente', label: 'En attente', color: 'orange', types: ['conge', 'retard', 'permission', 'repos_medical', 'ostie'] },
  { value: 'approuve', label: 'Approuvé', color: 'green', types: ['conge', 'permission', 'repos_medical', 'ostie'] },
  { value: 'refuse', label: 'Refusé', color: 'red', types: ['conge'] },
  { value: 'annule', label: 'Annulé', color: 'gray', types: ['conge', 'retard', 'permission', 'repos_medical', 'ostie'] },
  
  // Permissions
  { value: 'retourne', label: 'Retourné', color: 'blue', types: ['permission'] },
  { value: 'rattrapage', label: 'Rattrapage', color: 'purple', types: ['permission'] },
  { value: 'transforme', label: 'Transformé', color: 'purple', types: ['permission', 'repos_medical', 'ostie'] },
  
  // Retards
  { value: 'en_cours', label: 'En cours', color: 'blue', types: ['retard'] },
  { value: 'remplace', label: 'Remplacé', color: 'teal', types: ['retard'] }
]

// Types d'événements
const eventTypes = [
  { value: 'conge', label: 'Congés', color: '#3498db' },
  { value: 'retard', label: 'Retards', color: '#f39c12' },
  { value: 'permission', label: 'Permissions', color: '#27ae60' },
  { value: 'repos_medical', label: 'Repos médicaux', color: '#e74c3c' },
  { value: 'ostie', label: 'OSTIES', color: '#9b59b6' }
]


// ============================================
// DisplayName
// ============================================

const getUserDisplayName = (demande: CalendarEvent): string => {
  // Essayer de récupérer depuis originalEvent d'abord
  if (demande.originalEvent?.user_display_name) {
    return demande.originalEvent.user_display_name
  }
  
  // Sinon utiliser user_display_name du demande
  if (demande.user_display_name) {
    return demande.user_display_name
  }
  
  // Chercher dans tous les stores pour trouver l'utilisateur
  const userId = demande.user_id
  if (userId) {
    // Chercher dans congesStore
    const congesUser = congesStore.utilisateursGerables?.find(u => u.id === userId)
    if (congesUser) return congesUser.display_name
    
    // Chercher dans retardsStore
    const retardsUser = retardsStore.utilisateursGerables?.find(u => u.id === userId)
    if (retardsUser) return retardsUser.display_name
    
    // Chercher dans permissionsStore
    const permissionsUser = permissionsStore.utilisateursGerables?.find(u => u.id === userId)
    if (permissionsUser) return permissionsUser.display_name
    
    // Chercher dans reposStore
    const reposUser = reposStore.utilisateursGerables?.find(u => u.id === userId)
    if (reposUser) return reposUser.display_name
    
    // Chercher dans ostieStore
    const ostieUser = ostieStore.utilisateursGerables?.find(u => u.id === userId)
    if (ostieUser) return ostieUser.display_name
  }
  
  return 'Utilisateur inconnu'
}



// ============================================
// État
// ============================================
const loading = ref(false)
const selectedType = ref<string | null>(null)
const selectedStatus = ref<string | null>(null)
const selectedYear = ref(getYear(new Date()))
const selectedDemande = ref<CalendarEvent | null>(null)

// Années disponibles
const availableYears = computed(() => {
  const current = getYear(new Date())
  return [current - 2, current - 1, current, current + 1]
})

// ============================================
// Fusion de toutes les demandes depuis les stores existants
// ============================================
const allDemandes = computed<CalendarEvent[]>(() => {
  const demandes: CalendarEvent[] = []
  
  // Congés
  if (congesStore.calendrierEvents) {
    congesStore.calendrierEvents.forEach((e: any) => {
      if (e.user_id) {
        demandes.push({
          id: String(e.id),
          title: e.title || 'Congé',
          start: new Date(e.start),
          type: 'conge',
          user_id: e.user_id,
          user_display_name: e.user_display_name,
          statut: e.statut,
          color: e.color || '#3498db',
          allDay: true,
          originalEvent: e
        })
      }
    })
  }
  
  // Retards
  if (retardsStore.calendrierEvents) {
    retardsStore.calendrierEvents.forEach((e: any) => {
      if (e.user_id) {
        demandes.push({
          id: String(e.id),
          title: e.title || 'Retard',
          start: new Date(e.start),
          type: 'retard',
          user_id: e.user_id,
          user_display_name: e.user_display_name,
          statut: e.statut,
          color: e.color || '#f39c12',
          allDay: true,
          originalEvent: e
        })
      }
    })
  }
  
  // Permissions
  if (permissionsStore.calendrierEvents) {
    permissionsStore.calendrierEvents.forEach((e: any) => {
      if (e.user_id) {
        demandes.push({
          id: String(e.id),
          title: e.title || 'Permission',
          start: new Date(e.start),
          type: 'permission',
          user_id: e.user_id,
          user_display_name: e.user_display_name,
          statut: e.statut,
          color: e.color || '#27ae60',
          allDay: true,
          originalEvent: e
        })
      }
    })
  }
  
  // Repos médicaux
  if (reposStore.calendrierEvents) {
    reposStore.calendrierEvents.forEach((e: any) => {
      if (e.user_id) {
        demandes.push({
          id: String(e.id),
          title: e.title || 'Repos médical',
          start: new Date(e.start),
          type: 'repos_medical',
          user_id: e.user_id,
          user_display_name: e.user_display_name,
          statut: e.statut,
          color: e.color || '#e74c3c',
          allDay: true,
          originalEvent: e
        })
      }
    })
  }
  
  // OSTIES
  if (ostieStore.calendrierEvents) {
    ostieStore.calendrierEvents.forEach((e: any) => {
      if (e.user_id) {
        demandes.push({
          id: String(e.id),
          title: e.title || 'OSTIE',
          start: new Date(e.start),
          type: 'ostie',
          user_id: e.user_id,
          user_display_name: e.user_display_name,
          statut: e.statut,
          color: e.color || '#9b59b6',
          allDay: true,
          originalEvent: e
        })
      }
    })
  }
  
  return demandes
})

// Demandes filtrées
const filteredDemandes = computed(() => {
  let demandes = allDemandes.value

  // Filtre par année
  demandes = demandes.filter(d => {
    const year = d.start.getFullYear()
    return year === selectedYear.value
  })

  // Filtre par type
  if (selectedType.value) {
    demandes = demandes.filter(d => d.type === selectedType.value)
  }

  // Filtre par statut
  if (selectedStatus.value) {
    demandes = demandes.filter(d => d.statut === selectedStatus.value)
  }

  // Trier par date (plus récent d'abord)
  return demandes.sort((a, b) => b.start.getTime() - a.start.getTime())
})

// Compteurs
const getCountByType = (type: string) => {
  return allDemandes.value.filter(d => d.type === type).length
}

const getCountByStatus = (status: string) => {
  return allDemandes.value.filter(d => d.statut === status).length
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

const getStatusLabel = (statut: string | undefined, type?: string): string => {
  if (!statut) return 'Inconnu'
  
  // Cas spéciaux pour permissions
  if (type === 'permission') {
    const labels: Record<string, string> = {
      en_attente: 'En attente',
      retourne: 'Retourné',
      rattrapage: 'Rattrapage',
      approuve: 'Approuvé',
      transforme: 'Transformé',
      annule: 'Annulé'
    }
    return labels[statut] || statut
  }
  
  // Pour les autres types
  const found = allStatusOptions.find(s => s.value === statut)
  return found?.label || statut
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
// Vérifications des permissions
// ============================================

const canManageOthers = computed(() => {
  const user = authStore.user
  return user?.is_superuser || user?.est_chef_equipe
})

const canManageThisDemande = (demande: CalendarEvent): boolean => {
  if (!canManageOthers.value) return false
  const finalStatuses = ['approuve', 'refuse', 'annule', 'transforme', 'remplace']
  return !finalStatuses.includes(demande.statut || '')
}

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
  return ['en_attente', 'retourne', 'rattrapage', 'en_cours'].includes(demande.statut || '')
}

// ============================================
// Actions
// ============================================

// ============================================
// Gestion des modals de détails
// ============================================
const openDemandeDetails = (demande: CalendarEvent) => {
  selectedDemande.value = demande
  
  // Récupérer l'ID réel depuis l'événement
  const id = getDemandeId(demande)
  if (!id) {
    alert('ID non trouvé pour cette demande')
    return
  }
  
  console.log('Ouverture des détails:', {
    type: demande.type,
    id: id,
    statut: demande.statut,
    originalEvent: demande.originalEvent
  })
  
  // Rediriger vers la vue appropriée selon le type
  // Ou ouvrir un modal (à implémenter selon votre architecture)
  
  // Option 1: Navigation vers la page de détail
  const router = useRouter()
  switch (demande.type) {
    case 'conge':
      router.push(`/conges/${id}`)
      break
    case 'retard':
      router.push(`/retards/${id}`)
      break
    case 'permission':
      router.push(`/permissions/${id}`)
      break
    case 'repos_medical':
      router.push(`/repos-medical/${id}`)
      break
    case 'ostie':
      router.push(`/ostie/${id}`)
      break
    default:
      alert(`Détails de la demande ${getTypeLabel(demande.type)} (${getStatusLabel(demande.statut, demande.type)})`)
  }
  
  // Option 2: Ouvrir un modal (si vous avez des modals)
  // showModal.value = true
  // modalType.value = demande.type
}

// Fonction utilitaire pour extraire l'ID
const getDemandeId = (demande: CalendarEvent): number | null => {
  const original = demande.originalEvent || demande
  if (!original.id) return null
  
  if (typeof original.id === 'string') {
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
    
    await loadAllData()
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
    await loadAllData()
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
  alert(`Transformation de ${getTypeLabel(demande.type)} - À implémenter`)
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
    
    await loadAllData()
    alert('Demande annulée avec succès !')
  } catch (err) {
    console.error('Erreur annulation:', err)
    alert('Erreur lors de l\'annulation')
  }
}

// ============================================
// Chargement des données
// ============================================
const loadAllData = async () => {
  loading.value = true
  try {
    const currentYear = selectedYear.value
    await Promise.all([
      congesStore.fetchCalendrier({ annee: currentYear }),
      retardsStore.fetchCalendrier({ annee: currentYear }),
      permissionsStore.fetchCalendrier({ annee: currentYear }),
      reposStore.fetchCalendrier({ annee: currentYear }),
      ostieStore.fetchCalendrier({ annee: currentYear })
    ])
    console.log('✅ Données chargées avec succès')
  } catch (error) {
    console.error('❌ Erreur chargement:', error)
  } finally {
    loading.value = false
  }
}

// Watch pour recharger quand l'année change
watch(selectedYear, () => {
  loadAllData()
})

// Initialisation
onMounted(async () => {
  await loadAllData()
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
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-group {
  width: 100%;
}

.filter-group.small {
  max-width: 200px;
}

.filter-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #495057;
  font-size: 0.85rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.filter-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
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
  display: inline-block;
}

.status-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-dot.orange { background: #f39c12; }
.status-dot.green { background: #27ae60; }
.status-dot.red { background: #e74c3c; }
.status-dot.gray { background: #95a5a6; }
.status-dot.blue { background: #3498db; }
.status-dot.purple { background: #9b59b6; }
.status-dot.teal { background: #1abc9c; }

.count {
  background: rgba(0,0,0,0.1);
  padding: 0.1rem 0.4rem;
  border-radius: 12px;
  font-size: 0.7rem;
  margin-left: 0.25rem;
}

.form-select {
  padding: 0.6rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 0.9rem;
  width: 100%;
  background: white;
  cursor: pointer;
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
  flex-wrap: wrap;
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

.demande-status {
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: 600;
  background: #f8f9fa;
  border: 1px solid;
}

.demande-status.en_attente { 
  background: #fff3e0; 
  color: #e67e22; 
  border-color: #f39c12; 
}
.demande-status.approuve { 
  background: #e8f5e9; 
  color: #2e7d32; 
  border-color: #27ae60; 
}
.demande-status.refuse { 
  background: #ffebee; 
  color: #c62828; 
  border-color: #e74c3c; 
}
.demande-status.annule { 
  background: #eceff1; 
  color: #455a64; 
  border-color: #95a5a6; 
}
.demande-status.retourne { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.demande-status.rattrapage { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.demande-status.transforme { 
  background: #f3e5f5; 
  color: #7b1fa2; 
  border-color: #9b59b6; 
}
.demande-status.en_cours { 
  background: #e3f2fd; 
  color: #1976d2; 
  border-color: #3498db; 
}
.demande-status.remplace { 
  background: #e0f2f1; 
  color: #00695c; 
  border-color: #1abc9c; 
}

.demande-date {
  color: #6c757d;
  font-size: 0.8rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
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
  
  .filter-group.small {
    max-width: 100%;
  }
}
</style>