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
}

.page-header h1 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.75rem;
}

.role-badge-header {
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-badge-header.role-super-admin {
  background: #f5e6ff;
  color: #9b59b6;
}

.role-badge-header.role-admin {
  background: #e8f4fc;
  color: #3498db;
}

.role-badge-header.role-user {
  background: #e9ecef;
  color: #6c757d;
}

.filters-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

/* Wrapper pour la barre de recherche */
.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 350px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding-left: 2.25rem !important;
  padding-right: 2.5rem !important;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.filter-group {
  padding: 0.5rem 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.filter-group:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.btn-refresh {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #f8f9fa;
  color: #495057;
}

/* Indicateur de recherche */
.search-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #e8f4fc;
  border: 1px solid #3498db;
  border-radius: 6px;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.btn-clear-search {
  padding: 0.35rem 0.75rem;
  background: white;
  border: 1px solid #3498db;
  border-radius: 4px;
  color: #3498db;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-clear-search:hover {
  background: #3498db;
  color: white;
}

/* Vue en arbre */
.tree-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  min-height: 400px;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6c757d;
  text-align: center;
}

.loading i,
.empty i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

.empty .hint {
  font-size: 0.9rem;
  color: #adb5bd;
  margin-top: 0.5rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    min-width: auto;
  }

  .filter-group {
    width: 100%;
  }
}
</style>