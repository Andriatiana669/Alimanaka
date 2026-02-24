<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <span v-if="currentUser" class="role-badge-header" :class="getUserRoleClass(currentUser)">
        {{ getRoleLabel(currentUser) }}
      </span>
    </div>

    <!-- Filtres + Recherche -->
    <div class="filters-bar">
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Rechercher pseudo, matricule, prénom, nom ou équipe..."
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

      <div v-else-if="arbreEquipesFiltreRecherche.length === 0" class="empty">
        Aucune équipe trouvée
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
import type { User, Equipe, EquipeMembre, Pole } from '@/types/user'

// ========== STORES ==========
const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()

// ========== UTILISATEUR ACTUEL ==========
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

const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()
const getUserRoleClass = (user: User | null): string => {
  if (!user) return 'role-user'
  if (user.is_superuser) return 'role-super-admin'
  if (user.is_staff) return 'role-admin'
  return 'role-user'
}

// ========== FILTRES ==========
const poleFilter = ref<number | ''>('')
const equipeFilter = ref<number | ''>('')

const searchQuery = ref('')

const loading = computed(() => equipesStore.loading)
const arbreEquipes = computed(() => equipesStore.arbreEquipes)

const equipesFiltreesPourSelect = computed(() => {
  if (!poleFilter.value) return equipesStore.equipesActives
  return equipesStore.equipesActives.filter(e => e.pole === poleFilter.value)
})

const selectedEquipe = ref<Equipe | null>(null)

// Filtre par pôle
const filtrerParPole = (equipes: Equipe[], poleId: number): Equipe[] => {
  return equipes
    .filter(eq => eq.pole === poleId || (eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId).length > 0 : false))
    .map(eq => ({
      ...eq,
      sous_equipes: eq.sous_equipes ? filtrerParPole(eq.sous_equipes, poleId) : []
    }))
}

// Filtre par équipe
const filtrerParEquipe = (equipes: Equipe[], equipeId: number): Equipe[] => {
  return equipes
    .filter(eq => eq.id === equipeId || (eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId).length > 0 : false))
    .map(eq => ({
      ...eq,
      sous_equipes: eq.sous_equipes ? filtrerParEquipe(eq.sous_equipes, equipeId) : []
    }))
}

// Application des filtres pôle + équipe
const arbreEquipesFiltre = computed(() => {
  let result = arbreEquipes.value
  if (poleFilter.value !== '') result = filtrerParPole(result, Number(poleFilter.value))
  if (equipeFilter.value !== '') result = filtrerParEquipe(result, Number(equipeFilter.value))
  return result
})

// ========== RECHERCHE ==========
const filtrerEquipesParRecherche = (equipes: Equipe[], query: string): Equipe[] => {
  const lowerQuery = query.toLowerCase()

  return equipes
    .map(eq => {
      // Filtrage des membres
      const membresFiltrees: EquipeMembre[] = eq.membres?.filter(m =>
        m.pseudo?.toLowerCase().includes(lowerQuery) ||
        m.username.toLowerCase().includes(lowerQuery) ||
        m.first_name.toLowerCase().includes(lowerQuery) ||
        m.last_name.toLowerCase().includes(lowerQuery)
      ) ?? []

      // Filtrage récursif des sous-équipes
      const sousEquipesFiltrees: Equipe[] = eq.sous_equipes ? filtrerEquipesParRecherche(eq.sous_equipes, query) : []

      // On garde l'équipe si nom ou membres ou sous-équipes correspondent
      const matchEquipe = eq.nom.toLowerCase().includes(lowerQuery)

      if (matchEquipe || membresFiltrees.length > 0 || sousEquipesFiltrees.length > 0) {
        return {
          ...eq,
          membres: membresFiltrees,
          sous_equipes: sousEquipesFiltrees
        } as Equipe
      }

      return null
    })
    .filter((eq): eq is Equipe => eq !== null)
}

// Arbre final filtré + recherche
const arbreEquipesFiltreRecherche = computed(() => {
  if (!searchQuery.value.trim()) return arbreEquipesFiltre.value
  return filtrerEquipesParRecherche(arbreEquipesFiltre.value, searchQuery.value)
})

// ========== FONCTIONS UTILITAIRES ==========
const applyFilters = () => {
  if (poleFilter.value === '') equipeFilter.value = ''
}

const refreshData = async () => {
  await Promise.all([equipesStore.fetchArbre(), polesStore.fetchPoles(), usersStore.fetchUsers()])
}

const selectEquipe = (equipe: Equipe) => selectedEquipe.value = equipe

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

const closeCreateModal = () => showCreateModal.value = false

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
.profile {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.profile-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 3rem;
  padding-bottom: 2rem;
  border-bottom: 2px solid #f1f3f5;
}

.avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: linear-gradient(135deg, #3498db, #9b59b6);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.5rem;
  font-weight: bold;
  color: white;
}

.avatar-initials {
  text-transform: uppercase;
}

.profile-info h2 {
  color: #2c3e50;
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
}

.email {
  color: #7f8c8d;
  margin: 0 0 0.5rem 0;
}

.role {
  display: inline-block;
  background: #e8f4fc;
  color: #3498db;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  font-weight: 500;
  margin: 0;
}

.detail-section {
  margin-bottom: 2.5rem;
}

.detail-section h3 {
  color: #34495e;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #ecf0f1;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.detail-item {
  background: #f8fafc;
  padding: 1.2rem;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.detail-item label {
  display: block;
  color: #6c757d;
  font-size: 0.9rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.detail-item p {
  color: #495057;
  margin: 0;
  font-size: 1rem;
}

.loading, .error {
  text-align: center;
  padding: 3rem;
  background: #f8f9fa;
  border-radius: 10px;
  border: 1px solid #dee2e6;
}

.error {
  color: #dc3545;
}

.btn-retry {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-retry:hover {
  background-color: #0056b3;
}
</style>