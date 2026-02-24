<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <div v-if="loadingUser" class="role-loading">
        <i class="bi bi-arrow-repeat spin"></i>
      </div>
      
      <span 
        v-else-if="currentUser" 
        class="role-badge-header" 
        :class="getRoleClass(currentUser)"
      >
        {{ getRoleLabel(currentUser) }}
      </span>
      
      <button 
        v-if="canEditEquipeDetails(currentUser)" 
        class="btn-primary" 
        @click="openCreateModal"
      >
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
          <option value="">Toutes les équipes</option>
          <option v-for="eq in equipesFiltreesPourSelect" :key="eq.id" :value="eq.id">
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
        <span>Chargement des équipes...</span>
      </div>

      <div v-else-if="arbreEquipesFiltre.length === 0" class="empty">
        Aucune équipe trouvée
      </div>

      <EquipeNode 
        v-else
        v-for="equipe in arbreEquipesFiltre" 
        :key="equipe.id"
        :equipe="equipe"
        :niveau="0"
        :selected-id="selectedEquipe?.id"
        @select="selectEquipe"
        @details="openDetailsModal"
        @edit="openEditModal"
        @toggle="toggleStatus"
      />
    </div>

    <!-- MODAL DÉTAILS (voir membres) -->
    <div v-if="showDetailsModal && selectedEquipe" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal modal-large">
        <h3>{{ selectedEquipe.nom }} - Membres</h3>
        
        <div v-if="loadingMembres" class="loading">
          <i class="bi bi-arrow-repeat spin"></i> Chargement...
        </div>
        
        <table v-else-if="membres.length > 0" class="membres-table">
          <thead>
            <tr>
              <th>Matricule</th>
              <th>Pseudo</th>
              <th>Nom</th>
              <th>Prénom</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="membre in membres" :key="membre.id">
              <td class="matricule">{{ membre.username.toUpperCase() }}</td>
              <td>
                <span v-if="membre.pseudo" class="pseudo-tag">{{ membre.pseudo }}</span>
                <span v-else>-</span>
              </td>
              <td>{{ membre.last_name }}</td>
              <td>{{ membre.first_name }}</td>
            </tr>
          </tbody>
        </table>
        
        <div v-else class="empty">
          Aucun membre dans cette équipe
        </div>

        <div class="modal-actions">
          <button class="btn-secondary" @click="closeDetailsModal">Fermer</button>
        </div>
      </div>
    </div>

    <!-- MODAL MODIFICATION -->
    <div v-if="showEditModal && editingEquipe" class="modal-overlay" @click.self="closeEditModal">
      <div class="modal modal-large">
        <h3>Modifier : {{ editingEquipe.nom }}</h3>
        
        <!-- Onglets -->
        <div class="tabs">
          <button class="tab" :class="{ active: editTab === 'infos' }" @click="editTab = 'infos'">
            Informations
          </button>
          <button class="tab" :class="{ active: editTab === 'membres' }" @click="editTab = 'membres'">
            Membres
          </button>
          <button class="tab" :class="{ active: editTab === 'sous-equipe' }" @click="editTab = 'sous-equipe'">
            Sous-équipe
          </button>
        </div>

        <!-- Onglet Infos -->
        <div v-show="editTab === 'infos'" class="tab-content">
          <div class="form-group">
            <label>Nom de l'équipe</label>
            <input v-model="editForm.nom" type="text" maxlength="100" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="editForm.description" rows="3"></textarea>
          </div>

          <div class="modal-actions">
            <button class="btn-secondary" @click="closeEditModal">Annuler</button>
            <button class="btn-primary" @click="saveEquipeInfos" :disabled="saving">
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>

        <!-- Onglet Membres -->
        <div v-show="editTab === 'membres'" class="tab-content">
          <!-- Ajouter un membre (même pôle uniquement) -->
          <div class="ajout-section">
            <h4>Ajouter un membre</h4>
            <div class="form-row">
              <select v-model="nouveauMembreId">
                <option :value="null">Sélectionner un utilisateur</option>
                <option 
                  v-for="user in usersMemePoleDisponibles" 
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
                <i class="bi bi-person-plus"></i> Ajouter
              </button>
            </div>
          </div>

          <!-- Liste des membres actuels -->
          <div class="membres-liste">
            <h4>Membres actuels ({{ membresEditing.length }})</h4>
            
            <table v-if="membresEditing.length > 0" class="membres-table">
              <thead>
                <tr>
                  <th>Matricule</th>
                  <th>Pseudo</th>
                  <th>Nom</th>
                  <th>Prénom</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="membre in membresEditing" :key="membre.id">
                  <td class="matricule">{{ membre.username.toUpperCase() }}</td>
                  <td>
                    <span v-if="membre.pseudo" class="pseudo-tag">{{ membre.pseudo }}</span>
                    <span v-else>-</span>
                  </td>
                  <td>{{ membre.last_name }}</td>
                  <td>{{ membre.first_name }}</td>
                  <td>
                    <button 
                      class="btn-icon danger" 
                      @click="retirerMembre(membre)"
                      title="Retirer de l'équipe"
                    >
                      <i class="bi bi-person-x"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            
            <div v-else class="empty">Aucun membre</div>
          </div>

          <div class="modal-actions">
            <button class="btn-secondary" @click="closeEditModal">Fermer</button>
          </div>
        </div>

        <!-- Onglet Sous-équipe -->
        <div v-show="editTab === 'sous-equipe'" class="tab-content">
          <h4>Créer une sous-équipe</h4>
          
          <div class="form-group">
            <label>Nom de la sous-équipe *</label>
            <input v-model="sousEquipeForm.nom" type="text" required maxlength="100" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="sousEquipeForm.description" rows="2"></textarea>
          </div>

          <div class="modal-actions">
            <button class="btn-secondary" @click="closeEditModal">Annuler</button>
            <button 
              class="btn-primary" 
              @click="creerSousEquipe"
              :disabled="!sousEquipeForm.nom || saving"
            >
              {{ saving ? 'Création...' : 'Créer la sous-équipe' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- MODAL CRÉATION (racine) -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <h3>Nouvelle équipe</h3>
        <p>Formulaire à venir...</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeCreateModal">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useEquipesStore } from '@/store/equipes'
import { usePolesStore } from '@/store/poles'
import { useUsersStore } from '@/store/users'
import { usersApi } from '@/api/users'
import { useRoles } from '@/composables/useRoles'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { User, Equipe, EquipeMembre } from '@/types/user'

// ========== STORES ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// ========== RÔLES ==========
const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()

// ========== UTILISATEUR ==========
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)

const fetchCurrentUser = async () => {
  loadingUser.value = true
  try {
    currentUser.value = await usersApi.getCurrentUser()
  } catch (err) {
    console.error('Erreur récupération user:', err)
  } finally {
    loadingUser.value = false
  }
}

const monPoleId = computed(() => currentUser.value?.pole || null)

// ========== FILTRES ==========
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')

const loading = computed(() => equipesStore.loading)
const arbreEquipes = computed(() => equipesStore.arbreEquipes)

const equipesFiltreesPourSelect = computed(() => {
  if (!poleFilter.value) return equipesStore.equipesActives
  return equipesStore.equipesActives.filter(e => e.pole === poleFilter.value)
})

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

const selectedEquipe = ref<Equipe | null>(null)

// ========== MÉTHODES DE FILTRAGE ==========
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

// ========== SÉLECTION ==========
const selectEquipe = (equipe: Equipe) => {
  selectedEquipe.value = equipe
  // Ne fait rien d'autre, juste sélection visuelle
}

const toggleStatus = async (equipe: Equipe) => {
  if (!canEditEquipeDetails(currentUser.value)) {
    alert('Seul le Super Admin peut activer/désactiver une équipe')
    return
  }
  
  if (!confirm(`${equipe.est_actif ? 'Désactiver' : 'Activer'} l'équipe "${equipe.nom}" ?`)) return
  
  try {
    await equipesStore.updateEquipe(equipe.id, { est_actif: !equipe.est_actif })
    await refreshData()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

// ========== MODAL DÉTAILS ==========
const showDetailsModal = ref(false)
const loadingMembres = ref(false)
const membres = computed(() => equipesStore.membresCurrentEquipe)

const openDetailsModal = async (equipe: Equipe) => {
  selectedEquipe.value = equipe
  showDetailsModal.value = true
  loadingMembres.value = true
  try {
    await equipesStore.fetchMembres(equipe.id)
  } finally {
    loadingMembres.value = false
  }
}

const closeDetailsModal = () => {
  showDetailsModal.value = false
}

// ========== MODAL ÉDITION ==========
const showEditModal = ref(false)
const editingEquipe = ref<Equipe | null>(null)
const editTab = ref<'infos' | 'membres' | 'sous-equipe'>('infos')
const saving = ref(false)
const addingMember = ref(false)

const editForm = ref({
  nom: '',
  description: ''
})

const nouveauMembreId = ref<number | null>(null)

const sousEquipeForm = ref({
  nom: '',
  description: ''
})

const membresEditing = computed(() => equipesStore.membresCurrentEquipe)

const usersMemePoleDisponibles = computed(() => {
  if (!monPoleId.value) return []
  
  const membresIds = new Set(membresEditing.value.map(m => m.id))
  
  return usersStore.users.filter(u => {
    if (u.pole !== monPoleId.value) return false
    if (membresIds.has(u.id)) return false
    return u.is_active !== false
  })
})

const openEditModal = async (equipe: Equipe) => {
  editingEquipe.value = equipe
  editTab.value = 'infos'
  editForm.value = {
    nom: equipe.nom || '',
    description: equipe.description || ''
  }
  sousEquipeForm.value = { nom: '', description: '' }
  nouveauMembreId.value = null
  
  await equipesStore.fetchMembres(equipe.id)
  if (usersStore.users.length === 0) {
    await usersStore.fetchUsers()
  }
  
  showEditModal.value = true
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEquipe.value = null
}

const saveEquipeInfos = async () => {
  if (!editingEquipe.value) return
  
  saving.value = true
  try {
    await equipesStore.updateEquipe(editingEquipe.value.id, {
      nom: editForm.value.nom,
      description: editForm.value.description
    })
    await refreshData()
    closeEditModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}

const ajouterMembre = async () => {
  if (!nouveauMembreId.value || !editingEquipe.value) return
  
  addingMember.value = true
  try {
    await usersStore.updateUser(nouveauMembreId.value, { 
      equipe: editingEquipe.value.id 
    })
    await equipesStore.fetchMembres(editingEquipe.value.id)
    await usersStore.fetchUsers()
    nouveauMembreId.value = null
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    addingMember.value = false
  }
}

const retirerMembre = async (membre: EquipeMembre) => {
  if (!confirm(`Retirer ${membre.display_name} de l'équipe ?`)) return
  
  try {
    await usersStore.updateUser(membre.id, { equipe: null })
    await equipesStore.fetchMembres(editingEquipe.value!.id)
    await usersStore.fetchUsers()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

const creerSousEquipe = async () => {
  if (!editingEquipe.value || !sousEquipeForm.value.nom) return
  
  saving.value = true
  try {
    await equipesStore.createEquipe({
      nom: sousEquipeForm.value.nom,
      description: sousEquipeForm.value.description,
      pole: editingEquipe.value.pole,
      equipe_parente: editingEquipe.value.id,
      manager: null,
      est_actif: true
    })
    await refreshData()
    closeEditModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}

// ========== MODAL CRÉATION (racine) ==========
const showCreateModal = ref(false)

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

onMounted(async () => {
  await fetchCurrentUser()
  await refreshData()
})
</script>


<style scoped>

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.role-badge-header {
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.role-super-admin {
  background: #e74c3c;
  color: white;
}

.role-admin {
  background: #3498db;
  color: white;
}

.role-user {
  background: #95a5a6;
  color: white;
}

.role-loading {
  color: #6c757d;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  background: #27ae60;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  margin-left: auto;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #229954;
}

/* Filtres */
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  align-items: end;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.filter-group label {
  font-size: 0.85rem;
  color: #6c757d;
  font-weight: 500;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  background: white;
  min-width: 200px;
}

.btn-refresh {
  width: 38px;
  height: 38px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  margin-left: auto;
}

.btn-refresh:hover {
  background: #e9ecef;
  color: #495057;
}

/* Tree view */
.tree-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1rem;
  min-height: 200px;
}

.loading, .empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  padding: 3rem;
  color: #6c757d;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
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
  padding: 1rem;
}

.modal {
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  width: 100%;
  max-width: 500px;
}

.modal h3 {
  margin-top: 0;
  color: #2c3e50;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

.btn-secondary {
  padding: 0.6rem 1.2rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

/* Responsive */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .btn-primary {
    margin-left: 0;
    width: 100%;
    justify-content: center;
  }
  
  .filters-bar {
    flex-direction: column;
  }
  
  .filter-group select {
    width: 100%;
  }
}
</style>