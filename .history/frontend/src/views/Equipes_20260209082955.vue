<!-- frontend/src/views/Equipes.vue -->
<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      <span v-if="currentUser" class="role-badge-header" :class="getRoleClass(currentUser)">
        {{ getRoleLabel(currentUser) }}
      </span>
      <button v-if="canManageEquipes(currentUser)" class="btn-primary" @click="openCreateModal">
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
        :selected-id="selectedEquipe?.id"
        @select="selectEquipe"
        @edit="openEditModal"
        @toggle="toggleStatus"
      />
    </div>

    <!-- Détails de l'équipe sélectionnée -->
    <div v-if="selectedEquipe" class="equipe-details">
      <div class="details-header">
        <h3>{{ selectedEquipe.nom }}</h3>
        <button 
          v-if="canManageEquipes(currentUser)" 
          class="btn-icon edit" 
          @click="openEditModal(selectedEquipe)"
        >
          <i class="bi bi-pencil"></i> 
          {{ canEditEquipeDetails(currentUser) ? 'Modifier' : 'Gérer membres' }}
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
              <th v-if="canManageEquipes(currentUser)">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="membre in membres" :key="membre.id">
              <td class="matricule">{{ membre.username.toUpperCase() }}</td>
              <td>{{ membre.first_name }}</td>
              <td>{{ membre.last_name }}</td>
              <td>
                <span v-if="membre.pseudo" class="pseudo-tag">{{ membre.pseudo }}</span>
                <span v-else>-</span>
              </td>
              <td v-if="canManageEquipes(currentUser)">
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
      </div>
    </div>

    <!-- MODAL CRÉATION (Super Admin uniquement) -->
    <div v-if="showCreateModal && canEditEquipeDetails(currentUser)" class="modal-overlay" @click.self="closeCreateModal">
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
    <div v-if="showEditModal" class="modal-overlay" @click.self="closeEditModal">
      <div v-if="modalLoading" class="modal">
        <div class="loading-content">
          <i class="bi bi-arrow-repeat spin"></i>
          <p>Chargement des données...</p>
        </div>
      </div>

      <div v-else-if="editingEquipe" class="modal modal-large">
        <h3>
          {{ canEditEquipeDetails(currentUser) ? 'Modifier' : 'Gérer' }} l'équipe : {{ editingEquipe.nom }}
          <span v-if="currentUser" class="role-indicator" :class="getRoleClass(currentUser)">
            {{ getRoleLabel(currentUser) }}
          </span>
        </h3>
        
        <!-- Onglets -->
        <div class="tabs">
          <button 
            v-if="canEditEquipeDetails(currentUser)"
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

        <!-- Contenu onglet Infos (Super Admin uniquement) -->
        <div v-if="canEditEquipeDetails(currentUser)" v-show="editTab === 'infos'" class="tab-content">
          <form @submit.prevent="saveEquipeInfos">
            <div class="form-group">
              <label>Nom *</label>
              <input v-model="editForm.nom" required maxlength="100" />
            </div>
            
            <div class="form-group">
              <label>Description</label>
              <textarea v-model="editForm.description" rows="3"></textarea>
            </div>

            <div class="form-group">
              <label>Pôle</label>
              <select v-model="editForm.pole">
                <option :value="null">Aucun pôle</option>
                <option v-for="pole in polesStore.polesActifs" :key="pole.id" :value="pole.id">
                  {{ pole.code }} - {{ pole.nom }}
                </option>
              </select>
            </div>

            <div class="form-group">
              <label>Manager</label>
              <select v-model="editForm.manager">
                <option :value="null">Aucun manager</option>
                <option v-for="user in usersDisponibles" :key="user.id" :value="user.id">
                  {{ user.display_name }} ({{ user.username }})
                </option>
              </select>
            </div>

            <div class="modal-actions">
              <button type="button" class="btn-secondary" @click="closeEditModal">Annuler</button>
              <button type="submit" class="btn-primary" :disabled="saving">
                <span v-if="saving"><i class="bi bi-arrow-repeat spin"></i> Enregistrement...</span>
                <span v-else>Enregistrer</span>
              </button>
            </div>
          </form>
        </div>

        <!-- Contenu onglet Membres (tous les admins) -->
        <div v-show="editTab === 'membres' || !canEditEquipeDetails(currentUser)" class="tab-content">
          <div class="ajout-membre">
            <h4>Ajouter un membre</h4>
            <div class="form-row">
              <select v-model="nouveauMembreId" class="flex-1">
                <option :value="null">Sélectionner un utilisateur</option>
                <option v-for="user in usersSansEquipe" :key="user.id" :value="user.id">
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
                      @click="retirerMembre(membre)"
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
            <button type="button" class="btn-secondary" @click="closeEditModal">Fermer</button>
          </div>
        </div>
      </div>

      <!-- Erreur -->
      <div v-else class="modal error-modal">
        <h3><i class="bi bi-exclamation-triangle"></i> Erreur</h3>
        <p>Les données de l'équipe n'ont pas pu être chargées.</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeEditModal">Fermer</button>
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
import PoleSelect from '@/components/common/PoleSelect.vue'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { Equipe, EquipeMembre, User } from '@/types/user'

// ========== RÔLES (même logique que Users.vue) ==========
type UserRole = 'super-admin' | 'admin' | 'user'

const getUserRole = (user: User | null): UserRole => {
  if (!user) return 'user'
  if (user.is_superuser) return 'super-admin'
  if (user.is_staff) return 'admin'
  return 'user'
}

const getRoleLabel = (user: User | null): string => {
  const role = getUserRole(user)
  const labels: Record<UserRole, string> = {
    'super-admin': 'Super Admin',
    'admin': 'Admin',
    'user': 'Utilisateur'
  }
  return labels[role]
}

const getRoleClass = (user: User | null): string => {
  const role = getUserRole(user)
  const classes: Record<UserRole, string> = {
    'super-admin': 'role-super-admin',
    'admin': 'role-admin',
    'user': 'role-user'
  }
  return classes[role]
}

const canManageEquipes = (user: User | null): boolean => {
  const role = getUserRole(user)
  return role === 'admin' || role === 'super-admin'
}

const canEditEquipeDetails = (user: User | null): boolean => {
  return getUserRole(user) === 'super-admin'
}

// ========== STORES & API ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// ========== UTILISATEUR COURANT (récupération complète comme dans Users.vue) ==========
const currentUser = ref<User | null>(null)

const fetchCurrentUser = async () => {
  try {
    // Utilise la même API que Users.vue pour avoir les champs complets
    currentUser.value = await usersApi.getUserProfile()
  } catch (err) {
    console.error('Erreur récupération user:', err)
  }
}

// ========== STATE ==========
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')

const arbreEquipes = computed(() => equipesStore.arbreEquipes)
const loading = computed(() => equipesStore.loading)
const membres = computed(() => equipesStore.membresCurrentEquipe)

const selectedEquipe = ref<Equipe | null>(null)
const loadingMembres = ref(false)

// ========== COMPUTED ==========
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

const usersDisponibles = computed(() => usersStore.users)
const usersSansEquipe = computed(() => 
  usersStore.users.filter(u => !u.equipe || u.equipe === selectedEquipe.value?.id)
)

// ========== MODAL CRÉATION ==========
const showCreateModal = ref(false)
const saving = ref(false)
const createForm = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  equipe_parente: null as number | null
})

// ========== MODAL ÉDITION ==========
const showEditModal = ref(false)
const modalLoading = ref(false)
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

// ========== MÉTHODES ==========
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
  if (poleFilter.value === '') equipeFilter.value = ''
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

const openEditModal = async (equipe: Equipe) => {
  modalLoading.value = true
  showEditModal.value = true
  editingEquipe.value = null
  
  try {
    await selectEquipe(equipe)
    if (usersStore.users.length === 0) await usersStore.fetchUsers()
    
    editingEquipe.value = equipe
    editForm.value = {
      nom: equipe.nom || '',
      description: equipe.description || '',
      pole: equipe.pole,
      manager: equipe.manager
    }
    // Par défaut : infos pour Super Admin, sinon membres
    editTab.value = canEditEquipeDetails(currentUser.value) ? 'infos' : 'membres'
  } catch (err) {
    console.error('Erreur:', err)
    alert('Erreur lors du chargement')
  } finally {
    modalLoading.value = false
  }
}

const closeEditModal = () => {
  showEditModal.value = false
  editingEquipe.value = null
  modalLoading.value = false
  nouveauMembreId.value = null
}

const saveEquipeInfos = async () => {
  if (!editingEquipe.value || !canEditEquipeDetails(currentUser.value)) return
  
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

const ajouterMembre = async () => {
  if (!nouveauMembreId.value || !editingEquipe.value) return
  
  addingMember.value = true
  try {
    await usersStore.updateUser(nouveauMembreId.value, { equipe: editingEquipe.value.id })
    await selectEquipe(editingEquipe.value)
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
    if (editingEquipe.value) await selectEquipe(editingEquipe.value)
    await usersStore.fetchUsers()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
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

onMounted(async () => {
  // Récupère d'abord l'utilisateur complet, puis les données
  await fetchCurrentUser()
  await refreshData()
})
</script>

<style scoped>
.equipes-page {
  padding: 1.5rem;
  max-width: 1400px;
  margin: 0 auto;
}

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
  font-weight: 500;
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

.btn-primary:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

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

.tree-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1rem;
  margin-bottom: 1.5rem;
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
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.details-header h3 {
  margin: 0;
  color: #2c3e50;
}

.btn-icon {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn-icon.edit {
  background: #3498db;
  color: white;
}

.btn-icon.danger {
  background: #e74c3c;
  color: white;
  padding: 0.4rem;
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-item label {
  font-size: 0.8rem;
  color: #6c757d;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.info-item span {
  font-weight: 500;
  color: #2c3e50;
}

.membres-section {
  margin-top: 1.5rem;
}

.membres-section h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.membres-table {
  width: 100%;
  border-collapse: collapse;
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
  font-size: 0.9rem;
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

.loading-small {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #6c757d;
}

/* Modals */
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
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.modal-large {
  max-width: 700px;
}

.modal h3 {
  margin: 0;
  padding: 1.5rem;
  border-bottom: 1px solid #e9ecef;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.role-indicator {
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  margin-left: auto;
}

form {
  padding: 1.5rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
  font-size: 0.9rem;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  font-size: 0.95rem;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: #3498db;
}

.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e9ecef;
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

.tabs {
  display: flex;
  gap: 0;
  border-bottom: 1px solid #e9ecef;
  padding: 0 1.5rem;
}

.tab {
  padding: 0.75rem 1.5rem;
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  color: #6c757d;
  font-weight: 500;
  margin-bottom: -1px;
}

.tab.active {
  color: #3498db;
  border-bottom-color: #3498db;
  background: #f8f9fa;
}

.tab-content {
  padding: 1.5rem;
}

.form-row {
  display: flex;
  gap: 0.75rem;
  align-items: stretch;
}

.flex-1 {
  flex: 1;
}

.ajout-membre {
  margin-bottom: 1.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid #e9ecef;
}

.ajout-membre h4,
.membres-actuels h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #495057;
}

.empty-state {
  text-align: center;
  padding: 2rem;
  color: #6c757d;
}

.empty-state i {
  font-size: 2rem;
  margin-bottom: 0.5rem;
  display: block;
}

.error-modal {
  text-align: center;
}

.error-modal h3 {
  color: #e74c3c;
  justify-content: center;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
  color: #6c757d;
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
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .modal {
    max-width: 100%;
    margin: 0.5rem;
  }
}
</style>