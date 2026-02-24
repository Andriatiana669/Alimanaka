<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      <!-- DEBUG: Affiche la valeur de isAdmin -->
      <span style="color:red">isAdmin: {{ user.is_Admin }}</span>
      <button v-if="true" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i>
        Nouvelle équipe
      </button>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      <div class="filter-group">
        <label>Pôle</label>
        <select v-model="poleFilter" @change="applyFilters">
          <option value="">Tous les pôles</option>
          <option v-for="pole in polesStore.polesActifs" :key="pole.id" :value="pole.id">
            {{ pole.code }} - {{ pole.nom }}
          </option>
        </select>
      </div>

      <div class="filter-group">
        <label>Équipe</label>
        <select v-model="equipeFilter" @change="applyFilters">
        <!-- <select v-model="equipeFilter" @change="applyFilters" :disabled="!poleFilter"> -->
          <option value="">Toutes les équipes</option>
          <option v-for="eq in equipesFiltrees" :key="eq.id" :value="eq.id">
            {{ eq.nom }}
          </option>
        </select>
      </div>

      <button class="btn-refresh" @click="refreshData" title="Actualiser">
        <i class="bi bi-arrow-clockwise"></i>
      </button>
    </div>

    <!-- Vue en arbre -->
    <div class="tree-view">
      <div v-if="loading" class="loading">
        <i class="bi bi-arrow-repeat spin"></i>
        <span>Chargement...</span>
      </div>

      <div v-else-if="arbreEquipes.length === 0" class="empty">
        Aucune équipe définie
      </div>

      <EquipeNode 
        v-else
        v-for="equipe in arbreEquipesFiltre" 
        :key="equipe.id"
        :equipe="equipe"
        :niveau="0"
        @select="selectEquipe"
        @edit="openEditModal"
        @toggle="toggleStatus"
      />
    </div>

    <!-- Détails de l'équipe sélectionnée -->
    <div v-if="selectedEquipe" class="equipe-details">
      <div class="details-header">
        <h3>{{ selectedEquipe.nom }}</h3>
        <button v-if="isAdmin" class="btn-icon edit" @click="openEditModal(selectedEquipe)">
          <i class="bi bi-pencil"></i> Modifier
        </button>
      </div>
      
      <div class="info-grid">
        <div class="info-item">
          <label>Pôle</label>
          <span>{{ selectedEquipe.pole_details?.nom || 'Non assigné' }}</span>
        </div>
        <div class="info-item">
          <label>Manager</label>
          <span>{{ selectedEquipe.manager_details?.display_name || 'Non assigné' }}</span>
        </div>
        <div class="info-item">
          <label>Membres</label>
          <span>{{ membres.length }}</span>
        </div>
        <div class="info-item">
          <label>Sous-équipes</label>
          <span>{{ selectedEquipe.sous_equipes_count || 0 }}</span>
        </div>
      </div>

      <!-- Liste des membres -->
      <div class="membres-section">
        <h4>Membres de l'équipe</h4>
        <div v-if="loadingMembres" class="loading-small">
          <i class="bi bi-arrow-repeat spin"></i>
        </div>
        <table v-else class="membres-table">
          <thead>
            <tr>
              <th>Matricule</th>
              <th>Nom</th>
              <th>Prénom</th>
              <th>Pseudo</th>
              <th v-if="isAdmin">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="membre in membres" :key="membre.id">
              <td class="matricule">{{ membre.username }}</td>
              <td>{{ membre.last_name }}</td>
              <td>{{ membre.first_name }}</td>
              <td>
                <span v-if="membre.pseudo" class="pseudo-tag">{{ membre.pseudo }}</span>
                <span v-else>-</span>
              </td>
              <td v-if="isAdmin">
                <button 
                  class="btn-icon danger" 
                  @click="retirerMembre(membre as MembreEquipe)" 
                  title="Retirer de l'équipe"
                >
                  <i class="bi bi-person-x"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- MODAL CRÉATION -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <h3>Nouvelle équipe</h3>
        
        <form @submit.prevent="createEquipe">
          <div class="form-group">
            <label>Nom *</label>
            <input v-model="createForm.nom" required maxlength="100" placeholder="Nom de l'équipe" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="createForm.description" rows="2" placeholder="Description..."></textarea>
          </div>

          <PoleSelect v-model="createForm.pole" label="Pôle" placeholder="Sélectionner un pôle" />

          <div class="form-group">
            <label>Équipe parente</label>
            <select v-model="createForm.equipe_parente">
              <option :value="null">Aucune (racine)</option>
              <option v-for="eq in equipesStore.equipesActives" :key="eq.id" :value="eq.id">
                {{ eq.nom }}
              </option>
            </select>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeCreateModal">Annuler</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Création...' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- MODAL MODIFICATION -->
    <!-- MODAL MODIFICATION -->
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">

      <div v-if="modalLoading" class="modal">
        <div class="loading-content">
          <i class="bi bi-arrow-repeat spin"></i>
          <p>Chargement des données...</p>
        </div>
      </div>

      <!-- Cas 1: Données OK -->
      <div v-else-if="editingEquipe" class="modal modal-large">
        <h3>Modifier l'équipe : {{ editingEquipe.nom }}</h3>
        
        <!-- Onglets -->
        <div class="tabs">
          <button 
            class="tab" 
            :class="{ active: editTab === 'infos' }"
            @click="editTab = 'infos'"
          >
            Informations
          </button>
          <button 
            class="tab" 
            :class="{ active: editTab === 'membres' }"
            @click="editTab = 'membres'"
          >
            Gérer les membres ({{ membres.length }})
          </button>
        </div>

        <!-- Contenu onglet Infos -->
        <div v-show="editTab === 'infos'" class="tab-content">
          <form @submit.prevent="saveEquipeInfos">
            <div class="form-group">
              <label>Nom *</label>
              <input 
                v-model="editForm.nom" 
                required 
                maxlength="100"
                placeholder="Nom de l'équipe"
              />
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea 
                v-model="editForm.description" 
                rows="3"
                placeholder="Description de l'équipe..."
              ></textarea>
            </div>

            <div class="form-group">
              <label>Pôle</label>
              <select v-model="editForm.pole">
                <option :value="null">Aucun pôle</option>
                <option 
                  v-for="pole in polesStore.polesActifs" 
                  :key="pole.id" 
                  :value="pole.id"
                >
                  {{ pole.code }} - {{ pole.nom }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Manager</label>
              <select v-model="editForm.manager">
                <option :value="null">Aucun manager</option>
                <option 
                  v-for="user in usersDisponibles" 
                  :key="user.id" 
                  :value="user.id"
                >
                  {{ user.display_name }} ({{ user.username }})
                </option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeEditModal">
                Annuler
              </button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <span v-if="saving"><i class="bi bi-arrow-repeat spin"></i> Enregistrement...</span>
                <span v-else>Enregistrer</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Contenu onglet Membres -->
        <div v-show="editTab === 'membres'" class="tab-content">
          <!-- Ajouter un membre -->
          <div class="ajout-membre">
            <h4>Ajouter un membre</h4>
            <div class="form-row">
              <select v-model="nouveauMembreId" class="flex-1">
                <option :value="null">Sélectionner un utilisateur</option>
                <option 
                  v-for="user in usersSansEquipe" 
                  :key="user.id" 
                  :value="user.id"
                >
                  {{ user.display_name }} ({{ user.username }})
                </option>
              </select>
              <button 
                class="btn-primary" 
                @click="ajouterMembre"
                :disabled="!nouveauMembreId || addingMember"
              >
                <span v-if="addingMember"><i class="bi bi-arrow-repeat spin"></i></span>
                <span v-else><i class="bi bi-person-plus"></i> Ajouter</span>
              </button>
            </div>
          </div>

          <!-- Liste des membres actuels -->
          <div class="membres-actuels">
            <h4>Membres actuels ({{ membres.length }})</h4>
            
            <div v-if="loadingMembres" class="loading-small">
              <i class="bi bi-arrow-repeat spin"></i> Chargement...
            </div>
            
            <table v-else-if="membres.length > 0" class="membres-table">
              <thead>
                <tr>
                  <th>Matricule</th>
                  <th>Nom</th>
                  <th>Prénom</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="membre in membres" :key="membre.id">
                  <td class="matricule">{{ membre.username }}</td>
                  <td>{{ membre.last_name }}</td>
                  <td>{{ membre.first_name }}</td>
                  <td>
                    <button 
                      class="btn-icon danger" 
                      @click="retirerMembre(membre as MembreEquipe)"
                      title="Retirer de l'équipe"
                    >
                      <i class="bi bi-person-x"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-else class="empty-state">
              <i class="bi bi-people"></i>
              <p>Aucun membre dans cette équipe</p>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeEditModal">
              Fermer
            </button>
          </div>
        </div>
      </div>

      <!-- Cas 2: Erreur - données manquantes -->
      <div v-else class="modal error-modal">
        <h3><i class="bi bi-exclamation-triangle"></i> Erreur</h3>
        <p>Les données de l'équipe n'ont pas pu être chargées.</p>
        <p class="debug-info">showEditModal: {{ showEditModal }} | editingEquipe: {{ editingEquipe }}</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeEditModal">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useEquipesStore } from '@/store/equipes'
import { usePolesStore } from '@/store/poles'
import { useUsersStore } from '@/store/users'
import { useAuth } from '@/composables/useAuth'
import PoleSelect from '@/components/common/PoleSelect.vue'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { Equipe, User } from '@/types/user'

const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()
const { isAdmin } = useAuth()

// Filtres
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')

// Ajoute après les imports
interface MembreEquipe {
  id: number
  display_name: string
  username?: string
}

// Data
const arbreEquipes = computed(() => equipesStore.arbreEquipes)
const loading = computed(() => equipesStore.loading)
const membres = computed(() => equipesStore.membresCurrentEquipe)

const selectedEquipe = ref<Equipe | null>(null)
const loadingMembres = ref(false)

// Filtres appliqués
const arbreEquipesFiltre = computed(() => {
  let equipes = arbreEquipes.value
  
  if (poleFilter.value !== '') {
    equipes = filtrerParPole(equipes, Number(poleFilter.value))
  }
  
  if (equipeFilter.value !== '') {
    equipes = filtrerParEquipe(equipes, Number(equipeFilter.value))
  }
  
  return equipes
})

const equipesFiltrees = computed(() => {
  if (!poleFilter.value) return equipesStore.equipesActives
  return equipesStore.equipesActives.filter(e => e.pole === poleFilter.value)
})

// Users pour les selects
const usersDisponibles = computed(() => usersStore.users)
const usersSansEquipe = computed(() => 
  usersStore.users.filter(u => !u.equipe || u.equipe === selectedEquipe.value?.id)
)

// Modal création
const showCreateModal = ref(false)
const saving = ref(false)
const createForm = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  equipe_parente: null as number | null
})

// Modal édition
const showEditModal = ref(false)
const editingEquipe = ref<Equipe | null>(null)
const editTab = ref<'infos' | 'membres'>('infos')
const editForm = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  manager: null as number | null
})
const nouveauMembreId = ref<number | null>(null)
const addingMember = ref(false)


const reloadPage = () => {
  window.location.reload()
}


// Méthodes de filtrage récursif
const filtrerParPole = (equipes: Equipe[], poleId: number): Equipe[] => {
  return equipes.filter(eq => {
    const match = eq.pole === poleId
    const enfantsMatch = eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId).length > 0 : false
    return match || enfantsMatch
  }).map(eq => ({
    ...eq,
    sous_equipes: eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId) : []
  }))
}

const filtrerParEquipe = (equipes: Equipe[], equipeId: number): Equipe[] => {
  return equipes.filter(eq => {
    const match = eq.id === equipeId
    const enfantsMatch = eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId).length > 0 : false
    return match || enfantsMatch
  }).map(eq => ({
    ...eq,
    sous_equipes: eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId) : []
  }))
}

const applyFilters = () => {
  if (poleFilter.value === '') {
    equipeFilter.value = ''
  }
}

const refreshData = async () => {
  await Promise.all([
    equipesStore.fetchArbre(),
    polesStore.fetchPoles(),
    usersStore.fetchUsers()
  ])
}

const selectEquipe = async (equipe: Equipe) => {
  selectedEquipe.value = equipe
  loadingMembres.value = true
  try {
    await equipesStore.fetchMembres(equipe.id)
  } finally {
    loadingMembres.value = false
  }
}

// Modal création
const openCreateModal = () => {
  createForm.value = { nom: '', description: '', pole: null, equipe_parente: null }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

const createEquipe = async () => {
  saving.value = true
  try {
    await equipesStore.createEquipe({
      nom: createForm.value.nom,
      description: createForm.value.description,
      pole: createForm.value.pole,
      equipe_parente: createForm.value.equipe_parente,
      manager: null,
      est_actif: true
    })
    await refreshData()
    closeCreateModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}


const modalLoading = ref(false)


// Modal édition
const openEditModal = async (equipe: Equipe) => {
  console.log('=== openEditModal ===', equipe)
  
  // 1. Ouvrir le modal en mode chargement
  modalLoading.value = true
  showEditModal.value = true
  editingEquipe.value = null // Reset
  
  try {
    // 2. Charger les données nécessaires
    await selectEquipe(equipe)
    
    if (usersStore.users.length === 0) {
      await usersStore.fetchUsers()
    }
    
    // 3. Définir les données du formulaire
    editingEquipe.value = equipe
    editForm.value = {
      nom: equipe.nom || '',
      description: equipe.description || '',
      pole: equipe.pole,
      manager: equipe.manager
    }
    editTab.value = 'infos'
    
    console.log('Modal prêt, editingEquipe:', editingEquipe.value)
    
  } catch (err) {
    console.error('Erreur chargement modal:', err)
    alert('Erreur lors du chargement')
  } finally {
    modalLoading.value = false
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEquipe.value = null
  modalLoading.value = false // Reset le loading
  nouveauMembreId.value = null
}


const saveEquipeInfos = async () => {
  if (!editingEquipe.value) return
  
  saving.value = true
  try {
    await equipesStore.updateEquipe(editingEquipe.value.id, {
      nom: editForm.value.nom,
      description: editForm.value.description,
      pole: editForm.value.pole,
      manager: editForm.value.manager
    })
    await refreshData()
    closeEditModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}

// Gestion des membres
const ajouterMembre = async () => {
  if (!nouveauMembreId.value || !editingEquipe.value) return
  
  addingMember.value = true
  try {
    await usersStore.updateUser(nouveauMembreId.value, { equipe: editingEquipe.value.id })
    await selectEquipe(editingEquipe.value)
    await usersStore.fetchUsers() // Rafraîchir la liste
    nouveauMembreId.value = null
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    addingMember.value = false
  }
}

const retirerMembre = async (membre: MembreEquipe) => {
  if (!confirm(`Retirer ${membre.display_name} de l'équipe ?`)) return
  
  try {
    await usersStore.updateUser(membre.id, { equipe: null })
    if (editingEquipe.value) {
      await selectEquipe(editingEquipe.value)
    }
    await usersStore.fetchUsers()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

const toggleStatus = async (equipe: Equipe) => {
  if (!confirm(`${equipe.est_actif ? 'Désactiver' : 'Activer'} l'équipe "${equipe.nom}" ?`)) return
  
  try {
    await equipesStore.updateEquipe(equipe.id, { est_actif: !equipe.est_actif })
    await refreshData()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

onMounted(() => {
  refreshData()
})
</script>

<style scoped>

.loading-content {
  text-align: center;
  padding: 2rem;
}

.loading-content i {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

.error-modal {
  max-width: 400px;
  text-align: center;
}

.error-modal h3 {
  color: #e74c3c;
}


.equipes-page {
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  color: #2c3e50;
  margin: 0;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background: #3498db;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* Filtres */
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  align-items: flex-end;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-group label {
  font-size: 0.85rem;
  color: #6c757d;
}

.filter-group select {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  min-width: 200px;
}

.btn-refresh {
  padding: 0.5rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  color: #6c757d;
}

/* Tree view */
.tree-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1.5rem;
  margin-bottom: 2rem;
  max-height: 500px;
  overflow-y: auto;
}

/* Détails équipe */
.equipe-details {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1.5rem;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.details-header h3 {
  margin: 0;
  color: #2c3e50;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-item label {
  display: block;
  font-size: 0.85rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.info-item span {
  font-weight: 500;
  color: #2c3e50;
}

/* Membres */
.membres-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.membres-section h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

.membres-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
}

.membres-table th,
.membres-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.membres-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.matricule {
  font-family: monospace;
  font-weight: 600;
  color: #2c3e50;
}

.pseudo-tag {
  background: #e8f4fc;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-large {
  max-width: 700px;
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e9ecef;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  color: #6c757d;
  cursor: pointer;
  font-weight: 500;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-content {
  padding: 1rem 0;
}

/* Forms */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #495057;
  font-weight: 500;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.9rem;
}

.form-row {
  display: flex;
  gap: 0.5rem;
}

.flex-1 {
  flex: 1;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

/* Ajout membre */
.ajout-membre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
}

.ajout-membre h4 {
  margin: 0 0 1rem 0;
  color: #495057;
  font-size: 1rem;
}

.membres-actuels h4 {
  margin: 0 0 1rem 0;
  color: #2c3e50;
}

/* Buttons */
.btn-icon {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem 0.75rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-icon.edit {
  background: #e8f4fc;
  color: #3498db;
}

.btn-icon.danger {
  background: #fce8e8;
  color: #e74c3c;
}

/* Utilities */
.loading {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty {
  padding: 2rem;
  text-align: center;
  color: #6c757d;
}
</style>