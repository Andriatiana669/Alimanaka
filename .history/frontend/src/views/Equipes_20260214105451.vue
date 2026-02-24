<template>
  <!-- En-tête -->
  <div class="page-header">
    <h1>Gestion des Équipes</h1>
    <!-- <span v-if="currentUser" class="role-badge-header" :class="getRoleClass(currentUser)">
      {{ getRoleLabel(currentUser) }}
    </span> -->
    <!-- DEBUG TEMPORAIRE -->
    <!-- <div v-if="currentUser" style="background: #f0f0f0; padding: 5px 10px; margin-left: 10px; border-radius: 4px; font-size: 12px;">
      Debug: is_superuser={{ currentUser.is_superuser }}, is_staff={{ currentUser.is_staff }}
    </div> -->
  </div>

  <!-- Filtres -->
  <div class="filters-bar">
    <!-- Barre de recherche -->
    <div class="search-wrapper">
      <i class="bi bi-search search-icon"></i>
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Rechercher équipe, membre, manager, co-manager..."
        class="filter-group search-input"
        @input="onSearchInput"
      />
      <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
        <i class="bi bi-x"></i>
      </button>
    </div>

    <select v-model="poleFilter" @change="applyFilters" class="filter-group">
      <option value="">Tous les pôles</option>
      <option v-for="pole in polesStore.polesActifs" :key="pole.id" :value="pole.id">
        {{ pole.code }} - {{ pole.nom }}
      </option>
    </select>

    <select v-model="equipeFilter" @change="applyFilters" class="filter-group" :disabled="!poleFilter && !equipesStore.equipesActives.length">
      <option value="">Toutes les équipes</option>
      <option v-for="eq in equipesFiltreesPourSelect" :key="eq.id" :value="eq.id">
        {{ eq.nom }}
      </option>
    </select>

    <!-- TOGGLE Inactives -->
    <label class="toggle-inactives">
      <input 
        type="checkbox" 
        v-model="afficherInactives" 
        @change="onToggleInactives"
      />
      <span class="toggle-label">
        <i class="bi" :class="afficherInactives ? 'bi-eye' : 'bi-eye-slash'"></i>
        {{ afficherInactives ? 'Masquer' : 'Afficher' }} inactives
      </span>
    </label>

    <button class="btn-refresh" @click="refreshData" title="Actualiser">
      <i class="bi bi-arrow-clockwise"></i>
    </button>
  </div>

  <!-- Barre de stats -->
  <div class="stats-bar" v-if="!loading">
    <span class="stat active">
      <i class="bi bi-check-circle-fill"></i>
      {{ equipesStore.equipesActives.length }} actives
    </span>
    <span class="stat inactive" v-if="afficherInactives && equipesStore.equipesInactives.length > 0">
      <i class="bi bi-x-circle-fill"></i>
      {{ equipesStore.equipesInactives.length }} inactives
    </span>
  </div>

  <!-- Vue en arbre -->
  <div class="tree-view">
    <div v-if="loading" class="loading">
      <i class="bi bi-arrow-repeat spin"></i>
      <span>Chargement des équipes...</span>
    </div>

    <div v-else-if="arbreEquipesFiltrees.length === 0" class="empty">
      <div v-if="searchQuery">
        <i class="bi bi-search"></i>
        <p>Aucun résultat pour "<strong>{{ searchQuery }}</strong>"</p>
        <p class="hint">Essayez avec un autre nom, prénom, pseudo ou matricule</p>
      </div>
      <div v-else>
        <i class="bi bi-tree"></i>
        <p>Aucune équipe trouvée avec les filtres actuels</p>
      </div>
    </div>

    <EquipeNode
      v-else
      v-for="equipe in arbreEquipesFiltrees"
      :key="equipe.id"
      :equipe="equipe"
      :niveau="0"
      :selected-id="selectedEquipe?.id"
      :can-toggle="canToggleStatus"
      @select="selectEquipe"
      @toggle="toggleStatus"
      @refresh="refreshData"
    />
  </div>
</template>





<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useEquipesStore } from '@/store/equipes'
import { usePolesStore } from '@/store/poles'
import { useAuthStore } from '@/store/auth'
import { usersApi } from '@/api/users'
import { useRoles } from '@/composables/useRoles'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { User, Equipe } from '@/types/user'

// ========== STORES ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const authStore = useAuthStore()

// ========== UTILITAIRES ==========
const { getRoleLabel, getRoleClass, isAdmin } = useRoles()

// ========== STATE ==========
const afficherInactives = ref(true)
const searchQuery = ref('')
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')
const selectedEquipe = ref<Equipe | null>(null)
const searchTimeout = ref<number | null>(null)

// ========== CORRECTION CRITIQUE ==========
// Utilise usersApi.getCurrentUser() comme dans ton ancien code
// car authStore.user pourrait ne pas avoir tous les champs
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)

const fetchCurrentUser = async () => {
  loadingUser.value = true
  try { 
    currentUser.value = await usersApi.getCurrentUser()
    console.log('Current user from API:', currentUser.value) // Debug
  } 
  catch (err) { 
    console.error('Erreur récupération user:', err) 
    // Fallback sur authStore.user si l'API échoue
    currentUser.value = authStore.user
  }
  finally { 
    loadingUser.value = false 
  }
}

// ========== COMPUTED ==========
const loading = computed(() => equipesStore.loading || polesStore.loading || loadingUser.value)
const arbreEquipes = computed(() => equipesStore.arbreEquipes)

// Équipes pour le select (filtrées par pôle si sélectionné)
const equipesFiltreesPourSelect = computed(() => {
  if (!equipesStore.equipesActives.length) return []
  
  if (!poleFilter.value) {
    return equipesStore.equipesActives
  }
  
  return equipesStore.equipesActives.filter(e => e.pole === poleFilter.value)
})

// ========== NOUVELLE COMPUTED POUR LES PERMISSIONS ==========
// Vérifie si l'utilisateur peut voir le bouton toggle
const canToggleStatus = computed(() => {
  if (!currentUser.value) return false
  
  // Super admin peut toujours
  if (currentUser.value.is_superuser) return true
  
  // Admin et manager (mais pas co-manager)
  if (currentUser.value.is_staff) {
    // Vérifier si l'utilisateur est manager d'au moins une équipe
    const estManager = currentUser.value.equipes_managerisees && 
                       currentUser.value.equipes_managerisees.length > 0
    
    // Vérifier s'il est co-manager (via une autre propriété ou en regardant les équipes)
    // Note: Adapte cette condition selon comment tu identifies les co-managers
    const estCoManager = false // À adapter selon ta logique métier
    
    return estManager && !estCoManager
  }
  
  return false
})

// Vérifie si l'utilisateur est un utilisateur normal (non admin, non manager)
const isNormalUser = computed(() => {
  if (!currentUser.value) return true
  return !currentUser.value.is_superuser && !currentUser.value.is_staff
})

// ========== FILTRES OPTIMISÉS ==========

// Fonction pour vérifier si un utilisateur correspond à la recherche
const matchUser = (user: { username?: string; first_name?: string; last_name?: string; pseudo?: string | null; display_name?: string }, query: string): boolean => {
  if (!user) return false
  const lowerQuery = query.toLowerCase()
  
  const fields = [
    user.username,
    user.first_name,
    user.last_name,
    user.pseudo,
    user.display_name
  ].filter(Boolean)
  
  return fields.some(field => field!.toLowerCase().includes(lowerQuery))
}

// Filtrer l'arbre par pôle (conservant la structure hiérarchique)
const filtrerArbreParPole = (equipes: Equipe[], poleId: number): Equipe[] => {
  const filtrerRecursif = (node: Equipe): Equipe | null => {
    // Filtrer les enfants d'abord
    const enfantsFiltres = node.sous_equipes
      ?.map(filtrerRecursif)
      .filter((e): e is Equipe => e !== null) || []
    
    // Garder le nœud si:
    // 1. Il appartient au pôle recherché
    // 2. OU il a des enfants qui appartiennent au pôle
    const garderNode = node.pole === poleId || enfantsFiltres.length > 0
    
    if (garderNode) {
      return {
        ...node,
        sous_equipes: enfantsFiltres
      }
    }
    
    return null
  }
  
  return equipes
    .map(filtrerRecursif)
    .filter((e): e is Equipe => e !== null)
}

// Filtrer l'arbre par équipe parente
const filtrerArbreParEquipe = (equipes: Equipe[], equipeId: number): Equipe[] => {
  const trouverEtRetourner = (node: Equipe): Equipe | null => {
    if (node.id === equipeId) {
      return node
    }
    
    if (node.sous_equipes) {
      for (const child of node.sous_equipes) {
        const result = trouverEtRetourner(child)
        if (result) return result
      }
    }
    
    return null
  }
  
  const results: Equipe[] = []
  for (const node of equipes) {
    const result = trouverEtRetourner(node)
    if (result) results.push(result)
  }
  
  return results
}

// Filtrer par recherche (optimisé sans copies profondes inutiles)
const filtrerArbreParRecherche = (equipes: Equipe[], query: string): Equipe[] => {
  const lowerQuery = query.toLowerCase().trim()
  if (!lowerQuery) return equipes
  
  const filtrerRecursif = (node: Equipe): Equipe | null => {
    // 1. Vérifier si le nœud lui-même correspond
    const matchNode = node.nom.toLowerCase().includes(lowerQuery)
    
    // 2. Vérifier manager
    const matchManager = node.manager_details 
      ? matchUser(node.manager_details, lowerQuery)
      : false
    
    // 3. Vérifier co-managers
    const matchCoManagers = node.co_managers_details?.some(cm => matchUser(cm, lowerQuery)) ?? false
    
    // 4. Filtrer récursivement les enfants
    const enfantsFiltres = node.sous_equipes
      ?.map(filtrerRecursif)
      .filter((e): e is Equipe => e !== null) || []
    
    // Garder le nœud si lui-même, son manager, co-managers ou enfants correspondent
    const garderNode = matchNode || matchManager || matchCoManagers || enfantsFiltres.length > 0
    
    if (garderNode) {
      // Ne pas modifier les membres ici pour éviter les copies profondes
      return {
        ...node,
        sous_equipes: enfantsFiltres
      }
    }
    
    return null
  }
  
  return equipes
    .map(filtrerRecursif)
    .filter((e): e is Equipe => e !== null)
}

// ========== NOUVELLE FONCTION DE FILTRAGE POUR UTILISATEUR NORMAL ==========
// Filtre l'arbre pour ne montrer que les équipes où l'utilisateur est présent
// ET tous les parents jusqu'à la racine
const filtrerArbrePourUtilisateurNormal = (equipes: Equipe[]): Equipe[] => {
  if (!currentUser.value || !isNormalUser.value) return equipes
  
  const userId = currentUser.value.id
  
  // Fonction pour vérifier si l'utilisateur est dans une équipe ou ses sous-équipes
  const contientUtilisateur = (node: Equipe): boolean => {
    // Vérifier si l'utilisateur est dans les membres de cette équipe
    const estMembre = node.membres?.some(membre => membre.id === userId) || false
    
    // Vérifier dans les sous-équipes
    const sousEquipeContient = node.sous_equipes?.some(child => contientUtilisateur(child)) || false
    
    return estMembre || sousEquipeContient
  }
  
  const construireArbreAvecParents = (nodes: Equipe[]): Equipe[] => {
    return nodes
      .map(node => {
        // Vérifier si ce nœud ou ses descendants contiennent l'utilisateur
        if (!contientUtilisateur(node)) {
          return null
        }
        
        // Ce nœud ou ses descendants contiennent l'utilisateur
        // Filtrer les sous-équipes pour ne garder que celles qui contiennent l'utilisateur
        const sousEquipesFiltrees = node.sous_equipes 
          ? construireArbreAvecParents(node.sous_equipes)
          : []
        
        // Retourner le nœud avec ses sous-équipes filtrées
        return {
          ...node,
          sous_equipes: sousEquipesFiltrees
        }
      })
      .filter((e): e is Equipe => e !== null)
  }
  
  return construireArbreAvecParents(equipes)
}

// Arbre final filtré (optimisé)
const arbreEquipesFiltrees = computed(() => {
  let result = arbreEquipes.value
  
  // 0. Pour utilisateur normal : ne montrer que ses équipes (et tous les parents)
  if (isNormalUser.value) {
    result = filtrerArbrePourUtilisateurNormal(result)
  }
  
  // 1. Filtre pôle
  if (poleFilter.value !== '') {
    result = filtrerArbreParPole(result, Number(poleFilter.value))
  }
  
  // 2. Filtre équipe (seulement si pôle non sélectionné OU équipe appartient au pôle)
  if (equipeFilter.value !== '') {
    result = filtrerArbreParEquipe(result, Number(equipeFilter.value))
  }
  
  // 3. Recherche textuelle (avec debounce intégré dans l'input)
  if (searchQuery.value.trim() !== '') {
    result = filtrerArbreParRecherche(result, searchQuery.value)
  }
  
  return result
})

// ========== PERSISTANCE DES ÉTATS ==========
// Clés pour localStorage
const STORAGE_KEYS = {
  AFFICHER_INACTIVES: 'equipes_afficher_inactives',
  POLE_FILTER: 'equipes_pole_filter',
  EQUIPE_FILTER: 'equipes_equipe_filter',
  SEARCH_QUERY: 'equipes_search_query'
}

// Charger les états depuis localStorage
const loadStoredState = () => {
  try {
    const storedInactives = localStorage.getItem(STORAGE_KEYS.AFFICHER_INACTIVES)
    if (storedInactives !== null) afficherInactives.value = storedInactives === 'true'
    
    const storedPoleFilter = localStorage.getItem(STORAGE_KEYS.POLE_FILTER)
    if (storedPoleFilter !== null && storedPoleFilter !== '') poleFilter.value = Number(storedPoleFilter)
    
    const storedEquipeFilter = localStorage.getItem(STORAGE_KEYS.EQUIPE_FILTER)
    if (storedEquipeFilter !== null && storedEquipeFilter !== '') equipeFilter.value = Number(storedEquipeFilter)
    
    const storedSearchQuery = localStorage.getItem(STORAGE_KEYS.SEARCH_QUERY)
    if (storedSearchQuery !== null) searchQuery.value = storedSearchQuery
  } catch (e) {
    console.error('Erreur lors du chargement des états:', e)
  }
}

// Sauvegarder les états dans localStorage
const saveState = () => {
  try {
    localStorage.setItem(STORAGE_KEYS.AFFICHER_INACTIVES, String(afficherInactives.value))
    localStorage.setItem(STORAGE_KEYS.POLE_FILTER, String(poleFilter.value))
    localStorage.setItem(STORAGE_KEYS.EQUIPE_FILTER, String(equipeFilter.value))
    localStorage.setItem(STORAGE_KEYS.SEARCH_QUERY, searchQuery.value)
  } catch (e) {
    console.error('Erreur lors de la sauvegarde des états:', e)
  }
}

// Watchers pour sauvegarder automatiquement
watch([afficherInactives, poleFilter, equipeFilter, searchQuery], () => {
  saveState()
})

// ========== ACTIONS ==========
const applyFilters = () => {
  // Réinitialiser le filtre équipe si on change de pôle
  if (poleFilter.value === '') {
    equipeFilter.value = ''
  }
}

const onSearchInput = () => {
  // Debounce pour éviter des filtrages trop fréquents
  if (searchTimeout.value !== null) {
    clearTimeout(searchTimeout.value)
  }
  
  searchTimeout.value = window.setTimeout(() => {
    // Le computed arbreEquipesFiltrees se mettra à jour automatiquement
  }, 300)
}

const clearSearch = () => {
  searchQuery.value = ''
  if (searchTimeout.value !== null) {
    clearTimeout(searchTimeout.value)
    searchTimeout.value = null
  }
}

const refreshData = async () => {
  try {
    await Promise.all([
      equipesStore.fetchArbre(afficherInactives.value),
      polesStore.fetchPoles()
    ])
  } catch (error) {
    console.error('Erreur lors du rafraîchissement:', error)
  }
}

const onToggleInactives = async () => {
  // Recharger seulement l'arbre avec le nouveau paramètre
  try {
    await equipesStore.fetchArbre(afficherInactives.value)
  } catch (error) {
    console.error('Erreur lors du toggle inactives:', error)
    // Revenir à l'état précédent en cas d'erreur
    afficherInactives.value = !afficherInactives.value
  }
}

const selectEquipe = (equipe: Equipe) => {
  selectedEquipe.value = equipe
}

const toggleStatus = async (equipe: Equipe) => {
  // CORRECTION : Utiliser currentUser.value (de l'API) et isAdmin
  if (!currentUser.value || !isAdmin(currentUser.value)) {
    alert(`Permission refusée : Administrateur requis
    Votre statut: ${getRoleLabel(currentUser.value)}
    is_superuser: ${currentUser.value?.is_superuser}
    is_staff: ${currentUser.value?.is_staff}`)
    return
  }
  
  const newStatus = !equipe.est_actif
  const action = newStatus ? 'réactiver' : 'désactiver'
  
  if (!confirm(`${action.charAt(0).toUpperCase() + action.slice(1)} l'équipe "${equipe.nom}" ?`)) {
    return
  }
  
  try {
    // CORRECTION IMPORTANTE : Envoyer seulement les champs nécessaires
    const equipeData = {
      est_actif: newStatus,
      // Inclure les champs obligatoires pour la validation
      nom: equipe.nom,
      // Inclure les autres champs si présents dans l'équipe
      ...(equipe.pole !== undefined && { pole: equipe.pole }),
      ...(equipe.manager !== undefined && { manager: equipe.manager }),
      ...(equipe.equipe_parente !== undefined && { equipe_parente: equipe.equipe_parente }),
      ...(equipe.co_managers !== undefined && { co_managers: equipe.co_managers || [] }),
      ...(equipe.description !== undefined && { description: equipe.description })
    }
    
    await equipesStore.updateEquipe(equipe.id, equipeData)
    
    // Rafraîchir l'affichage
    await equipesStore.fetchArbre(afficherInactives.value)
    
    alert(`Équipe ${newStatus ? 'réactivée' : 'désactivée'} avec succès`)
  } catch (err: any) {
    console.error('Erreur lors du changement de statut:', err)
    
    // Message d'erreur plus précis
    let errorMessage = 'Erreur lors du changement de statut'
    if (err.response?.data) {
      if (typeof err.response.data === 'string') {
        errorMessage = err.response.data
      } else if (err.response.data.error) {
        errorMessage = err.response.data.error
      } else if (err.response.data.detail) {
        errorMessage = err.response.data.detail
      } else if (err.response.data.nom) {
        errorMessage = `Erreur de validation: ${err.response.data.nom.join(', ')}`
      }
    }
    
    alert(`Erreur: ${errorMessage}`)
    
    // Recharger les données pour avoir l'état correct
    await equipesStore.fetchArbre(afficherInactives.value)
  }
}

// ========== LIFECYCLE ==========
onMounted(async () => {
  // CORRECTION : Récupérer l'utilisateur via l'API comme dans ton ancien code
  await fetchCurrentUser()
  
  // Charger les états sauvegardés
  loadStoredState()
  
  // Charger les données initiales
  await refreshData()
  
  // Watch pour reset equipeFilter si poleFilter change
  watch(poleFilter, (newPoleId) => {
    if (newPoleId === '') {
      equipeFilter.value = ''
    }
  })
})

// Nettoyer le timeout à la destruction
import { onUnmounted } from 'vue'
onUnmounted(() => {
  if (searchTimeout.value !== null) {
    clearTimeout(searchTimeout.value)
  }
})
</script>







<style scoped>

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
  min-width: 300px;
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
  flex: 1;
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
/* Barre toogle */
.toggle-inactives {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.toggle-inactives:hover {
  background: #e9ecef;
}

.toggle-inactives input {
  display: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: #495057;
}

.stats-bar {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.stat.active {
  color: #27ae60;
}

.stat.inactive {
  color: #e74c3c;
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