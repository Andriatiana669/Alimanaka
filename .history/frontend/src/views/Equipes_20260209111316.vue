<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <!-- Badge rôle utilisateur -->
      <span v-if="currentUser" class="role-badge-header" :class="getUserRoleClass(currentUser)">
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
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeDetailsModal">
      <div class="modal modal-large">
        <h3 v-if="selectedEquipe">{{ selectedEquipe.nom }} - Membres</h3>
        <h3 v-else>Membres de l'équipe</h3>
        
        <div v-if="loadingMembres" class="loading">
          <i class="bi bi-arrow-repeat spin"></i> Chargement...
        </div>
        
        <div v-else-if="membres.length > 0">
          <table class="membres-table">
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
          <p class="total-membres">Total: {{ membres.length }} membre(s)</p>
        </div>
        
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
            Membres
          </button>
          <button 
            v-if="canEditEquipeDetails(currentUser)" 
            class="tab" 
            :class="{ active: editTab === 'sous-equipe' }" 
            @click="editTab = 'sous-equipe'"
          >
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
            <button 
              class="btn-primary" 
              @click="saveEquipeInfos" 
              :disabled="saving"
              v-if="canEditEquipeDetails(currentUser)"
            >
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </div>

        <!-- Onglet Membres -->
        <div v-show="editTab === 'membres'" class="tab-content">
          <!-- Ajouter un membre -->
          <div class="ajout-section">
            <h4>Ajouter un membre</h4>
            <div class="form-row">
              <select v-model="nouveauMembreId">
                <option :value="null">Sélectionner un utilisateur</option>
                <option 
                  v-for="user in usersDisponibles" 
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
    <div v-if="showCreateModal && canEditEquipeDetails(currentUser)" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <h3>Nouvelle équipe</h3>
        
        <div class="form-group">
          <label>Nom *</label>
          <input v-model="createForm.nom" type="text" required maxlength="100" />
        </div>
        
        <div class="form-group">
          <label>Description</label>
          <textarea v-model="createForm.description" rows="2"></textarea>
        </div>
        
        <PoleSelect 
          v-model="createForm.pole" 
          label="Pôle" 
          placeholder="Sélectionner un pôle" 
        />
        
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
          <button class="btn-secondary" @click="closeCreateModal">Annuler</button>
          <button class="btn-primary" @click="createEquipe" :disabled="saving">
            {{ saving ? 'Création...' : 'Créer' }}
          </button>
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
import { useAuth } from '@/composables/useAuth'
import { useRoles } from '@/composables/useRoles'
import PoleSelect from '@/components/common/PoleSelect.vue'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { User, Equipe, EquipeMembre } from '@/types/user'

// ========== STORES ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// ========== RÔLES ==========
const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()

// ========== FONCTIONS UTILITAIRES ==========
const getUserRole = (user: User | null) => {
  if (!user) return 'Utilisateur'
  if (user.is_superuser) return 'Super Admin'
  if (user.is_staff) return 'Admin'
  return 'Utilisateur'
}

const getUserRoleClass = (user: User | null): string => {
  if (!user) return 'role-user'
  if (user.is_superuser) return 'role-super-admin'
  if (user.is_staff) return 'role-admin'
  return 'role-user'
}

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

const usersDisponibles = computed(() => {
  return usersStore.users.filter(u => u.is_active !== false)
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
const createForm = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  equipe_parente: null as number | null
})

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

const createEquipe = async () => {
  if (!createForm.value.nom) return
  
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

onMounted(async () => {
  await refreshData()
})
</script>

<style scoped>
/* BADGES DE RÔLE */
.role-badge-header {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 600;
  margin-right: 1rem;
}

.role-super-admin {
  background: #fce8e8;
  color: #e74c3c;
  border: 1px solid #e74c3c;
}

.role-admin {
  background: #e8f4fc;
  color: #3498db;
  border: 1px solid #3498db;
}

.role-user {
  background: #f0f9f0;
  color: #27ae60;
  border: 1px solid #27ae60;
}

/* PAGE HEADER */
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

/* FILTRES */
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

/* TREE VIEW */
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

/* MODAL */
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
  max-height: 90vh;
  overflow-y: auto;
}

.modal.modal-large {
  max-width: 800px;
  width: 90%;
}

.modal h3 {
  margin-top: 0;
  color: #2c3e50;
  margin-bottom: 1.5rem;
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

.btn-secondary:hover {
  background: #5a6268;
}

/* TABLEAU DES MEMBRES */
.membres-table {
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9rem;
}

.membres-table th,
.membres-table td {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #dee2e6;
}

.membres-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
  position: sticky;
  top: 0;
}

.membres-table tbody tr:hover {
  background: #f8f9fa;
}

.pseudo-tag {
  background: #e8f4fc;
  color: #3498db;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.85rem;
  display: inline-block;
}

.matricule {
  font-family: monospace;
  font-weight: bold;
  color: #2c3e50;
  letter-spacing: 0.5px;
}

.total-membres {
  text-align: right;
  font-style: italic;
  color: #6c757d;
  margin-top: 0.5rem;
}

/* ONGLETS */
.tabs {
  display: flex;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-weight: 500;
  color: #6c757d;
  transition: all 0.2s;
}

.tab:hover {
  color: #495057;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
}

.tab-content {
  margin-bottom: 1rem;
}

/* FORMULAIRES */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-row {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.form-row select {
  flex: 1;
  padding: 0.5rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
}

/* BOUTONS ICONES */
.btn-icon.danger {
  color: #e74c3c;
}

.btn-icon.danger:hover {
  background: #fde8e8;
}

.ajout-section,
.membres-liste {
  margin-bottom: 2rem;
}

.ajout-section h4,
.membres-liste h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

/* RESPONSIVE */
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
  
  .modal.modal-large {
    width: 95%;
    max-width: 95%;
    padding: 1rem;
  }
  
  .membres-table {
    font-size: 0.8rem;
  }
  
  .membres-table th,
  .membres-table td {
    padding: 0.5rem;
  }
  
  .tabs {
    flex-direction: column;
  }
  
  .tab {
    width: 100%;
    text-align: left;
  }
}
</style>