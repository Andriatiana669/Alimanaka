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
      <!-- BARRE DE RECHERCHE UNIFIÉE -->
      <div class="search-wrapper">
        <i class="bi bi-search search-icon"></i>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Rechercher équipe, membre, manager, co-manager (nom, prénom, pseudo, matricule)..."
          class="filter-group search-input"
        />
        <button 
          v-if="searchQuery" 
          @click="clearSearch" 
          class="clear-btn"
          title="Effacer"
        >
          <i class="bi bi-x"></i>
        </button>
      </div>

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

    <!-- Indicateur de recherche active -->
    <div v-if="searchQuery" class="search-info">
      <span>
        Recherche : "<strong>{{ searchQuery }}</strong>" - 
        {{ arbreEquipesFiltreRecherche.length }} équipe(s) trouvée(s)
      </span>
      <button @click="clearSearch" class="btn-clear-search">Effacer la recherche</button>
    </div>

    <!-- Vue en arbre -->
    <div class="tree-view">
      <div v-if="loading" class="loading">
        <i class="bi bi-arrow-repeat spin"></i>
        <span>Chargement des équipes...</span>
      </div>

      <div v-else-if="arbreEquipesFiltreRecherche.length === 0" class="empty">
        <div v-if="searchQuery">
          <i class="bi bi-search"></i>
          <p>Aucun résultat pour "<strong>{{ searchQuery }}</strong>"</p>
          <p class="hint">Essayez avec un autre nom, prénom, pseudo ou matricule</p>
        </div>
        <div v-else>
          Aucune équipe trouvée
        </div>
      </div>

      <EquipeNode
        v-else
        v-for="equipe in arbreEquipesFiltreRecherche"
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

// ========== STORES ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// ========== RECHERCHE ==========
const searchQuery = ref('')

// Fonction utilitaire pour chercher dans un utilisateur
const matchUser = (user: { username?: string; first_name?: string; last_name?: string; pseudo?: string | null; display_name?: string }, query: string): boolean => {
  if (!user) return false
  const fields = [
    user.username,
    user.first_name,
    user.last_name,
    user.pseudo,
    user.display_name
  ].filter(Boolean).map(f => f!.toLowerCase())
  
  return fields.some(field => field.includes(query))
}

// Fonction récursive de recherche améliorée
const filtrerEquipesParRecherche = (equipes: Equipe[], query: string): Equipe[] => {
  if (!query) return equipes
  const lowerQuery = query.toLowerCase().trim()
  
  if (!lowerQuery) return equipes

  return equipes
    .map(eq => {
      // 1. Vérifier si le nom de l'équipe correspond
      const matchEquipeNom = (eq.nom ?? '').toLowerCase().includes(lowerQuery)
      
      // 2. Vérifier si le manager correspond
      const matchManager = eq.manager_details ? matchUser(eq.manager_details, lowerQuery) : false
      
      // 3. Vérifier si un co-manager correspond
      const matchCoManagers = eq.co_managers_details?.some(cm => matchUser(cm, lowerQuery)) ?? false
      
      // 4. Filtrer les membres qui correspondent
      const membresFiltres: EquipeMembre[] = eq.membres?.filter(m => matchUser(m, lowerQuery)) ?? []
      
      // 5. Sous-équipes filtrées récursivement
      const sousEquipesFiltrees: Equipe[] = eq.sous_equipes 
        ? filtrerEquipesParRecherche(eq.sous_equipes, query) 
        : []

      // 6. Conserver l'équipe si elle ou ses membres/sous-équipes correspondent
      const hasMatch = matchEquipeNom || matchManager || matchCoManagers || membresFiltres.length > 0 || sousEquipesFiltrees.length > 0
      
      if (hasMatch) {
        return {
          ...eq,
          // Si recherche active, on peut choisir de :
          // Option A: Montrer tous les membres (comportement actuel)
          // Option B: Ne montrer que les membres filtrés + manager/co-managers
          membres: searchQuery.value ? membresFiltres : eq.membres,
          sous_equipes: sousEquipesFiltrees
        } as Equipe
      }

      return null
    })
    .filter((eq): eq is Equipe => eq !== null)
}

const clearSearch = () => {
  searchQuery.value = ''
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

const filtrerParPole = (equipes: Equipe[], poleId: number): Equipe[] => {
  return equipes
    .filter(eq => {
      const match = eq.pole === poleId
      const enfantsMatch = eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId).length > 0 : false
      return match || enfantsMatch
    })
    .map(eq => ({
      ...eq,
      sous_equipes: eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId) : []
    }))
}

const filtrerParEquipe = (equipes: Equipe[], equipeId: number): Equipe[] => {
  return equipes
    .filter(eq => {
      const match = eq.id === equipeId
      const enfantsMatch = eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId).length > 0 : false
      return match || enfantsMatch
    })
    .map(eq => ({
      ...eq,
      sous_equipes: eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId) : []
    }))
}

// ========== ARBRE FILTRÉ FINAL ==========
const arbreEquipesFiltreRecherche = computed(() => {
  let result = arbreEquipes.value

  if (poleFilter.value !== '') {
    result = filtrerParPole(result, Number(poleFilter.value))
  }

  if (equipeFilter.value !== '') {
    result = filtrerParEquipe(result, Number(equipeFilter.value))
  }

  if (searchQuery.value.trim() !== '') {
    result = filtrerEquipesParRecherche(result, searchQuery.value)
  }

  return result
})

// ========== UTILITAIRES ==========
const selectedEquipe = ref<Equipe | null>(null)
const applyFilters = () => {
  if (poleFilter.value === '') equipeFilter.value = ''
}

// ========== ROLES ==========
const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)
const fetchCurrentUser = async () => {
  loadingUser.value = true
  try { currentUser.value = await usersApi.getCurrentUser() } 
  catch (err) { console.error('Erreur récupération user:', err) }
  finally { loadingUser.value = false }
}
const getUserRoleClass = (user: User | null) => {
  if (!user) return 'role-user'
  if (user.is_superuser) return 'role-super-admin'
  if (user.is_staff) return 'role-admin'
  return 'role-user'
}

// ========== ACTIONS ==========
const refreshData = async () => {
  await Promise.all([
    equipesStore.fetchArbre(),
    polesStore.fetchPoles(),
    usersStore.fetchUsers()
  ])
}

const selectEquipe = (equipe: Equipe) => selectedEquipe.value = equipe

const toggleStatus = async (equipe: Equipe) => {
  if (!canEditEquipeDetails(currentUser.value)) return alert('Permission refusée')
  if (!confirm(`${equipe.est_actif ? 'Désactiver' : 'Activer'} "${equipe.nom}" ?`)) return
  try {
    await equipesStore.updateEquipe(equipe.id, { est_actif: !equipe.est_actif })
    await refreshData()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

// ========== MOUNT ==========
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