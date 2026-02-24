<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <span v-if="currentUser" class="role-badge-header" :class="getUserRoleClass(currentUser)">
        {{ getRoleLabel(currentUser) }}
      </span>
    </div>

    <!-- Filtres -->
    <div class="filters-bar">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Rechercher pseudo, matricule, prénom, nom..."
        class="filter-group"
      />

      <select v-model="poleFilter" @change="applyFilters" class="filter-group">
        <option value="">Tous les pôles</option>
        <option v-for="pole in polesStore.polesActifs" :key="pole.id" :value="pole.id">
          {{ pole.code }} - {{ pole.nom }}
        </option>
      </select>

      <select v-model="equipeFilter" @change="applyFilters" class="filter-group">
        <option value="">Toutes les équipes</option>
        <option v-for="eq in equipesFiltreesPourSelect" :key="eq.id" :value="eq.id">
          {{ eq.nom }}
        </option>
      </select>

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

      <!-- CORRECTION : Gestion des événements simplifiée -->
      <EquipeNode 
        v-else
        v-for="equipe in arbreEquipesFiltre" 
        :key="equipe.id"
        :equipe="equipe"
        :niveau="0"
        :selected-id="selectedEquipe?.id"
        @select="selectEquipe"
        @toggle="toggleStatus"
        @refresh="refreshData"
      />
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

// Stores
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// Recherche

const searchQuery = ref('') // texte saisi par l'utilisateur

const arbreEquipesFiltreRecherche = computed(() => {
  let result = arbreEquipesFiltre.value

  if (searchQuery.value.trim() !== '') {
    result = filtrerEquipesParRecherche(result, searchQuery.value)
  }

  return result
})


const filtrerEquipesParRecherche = (equipes: Equipe[], query: string): Equipe[] => {
  if (!query) return equipes

  const lowerQuery = query.toLowerCase()

  return equipes
    .map(eq => {
      // Filtrage des membres
      const membresFiltrees: EquipeMembre[] = eq.membres?.filter((m: EquipeMembre) =>
        (m.pseudo?.toLowerCase().includes(lowerQuery)) ||
        (m.username?.toLowerCase().includes(lowerQuery)) ||
        (m.first_name?.toLowerCase().includes(lowerQuery)) ||
        (m.last_name?.toLowerCase().includes(lowerQuery))
      ) ?? [] // <-- jamais undefined

      // Filtrage des sous-équipes récursif
      const sousEquipesFiltrees: Equipe[] = eq.sous_equipes ? filtrerEquipesParRecherche(eq.sous_equipes, query) : []

      // Si cette équipe ou ses sous-équipes ont un membre correspondant, on garde l'équipe
      if (membresFiltrees.length > 0 || sousEquipesFiltrees.length > 0) {
        return {
          ...eq,
          membres: membresFiltrees,
          sous_equipes: sousEquipesFiltrees
        } as Equipe // <-- cast pour TypeScript
      }

      return null
    })
    .filter((eq): eq is Equipe => eq !== null) // <-- Type predicate correct

}







// Roles
const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()

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

// ========== FONCTIONS UTILITAIRES ==========
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

  if (searchQuery.value.trim() !== '') {
    equipes = filtrerEquipesParRecherche(equipes, searchQuery.value)
  }

  return equipes
})

const selectedEquipe = ref<Equipe | null>(null)

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

// CORRECTION : toggleStatus reçoit l'équipe depuis EquipeNode
const toggleStatus = async (equipe: Equipe) => {
  if (!canEditEquipeDetails(currentUser.value)) {
    alert('Permission refusée')
    return
  }
  
  if (!confirm(`${equipe.est_actif ? 'Désactiver' : 'Activer'} "${equipe.nom}" ?`)) return
  
  try {
    await equipesStore.updateEquipe(equipe.id, { est_actif: !equipe.est_actif })
    await refreshData()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

// ========== MODAL CRÉATION ==========
const showCreateModal = ref(false)
const saving = ref(false)
const createForm = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  equipe_parente: null as number | null
})


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
  await fetchCurrentUser()
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
  margin-bottom: 2.5rem;
}

.page-header h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

/* Recherche */
.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  min-width: 200px;
}
.search-input:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
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
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-group {
  padding: 0.75rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  color: #495057;
  font-size: 0.9rem;
  min-width: 150px;
}


.filter-group:focus {
  outline: none;
  border-color: #3498db;
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