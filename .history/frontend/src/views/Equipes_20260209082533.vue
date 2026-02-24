<template>
  
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
import type { Equipe, EquipeMembre } from '@/types/user'

const equipesStore = useEquipesStore()
const polesStore = usePolesStore()
const usersStore = useUsersStore()
const { user: authUser } = useAuth()
const { 
  getRoleLabel, 
  getRoleClass, 
  canManageEquipes, 
  canEditEquipeDetails,
  canManageEquipeMembers 
} = useRoles()

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
    // Par défaut, onglet infos pour Super Admin, sinon membres
    editTab.value = canEditEquipeDetails(authUser.value) ? 'infos' : 'membres'
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
  if (!editingEquipe.value || !canEditEquipeDetails(authUser.value)) return
  
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
  if (!canEditEquipeDetails(authUser.value)) {
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

onMounted(() => {
  refreshData()
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

.role-indicator {
  font-size: 0.7rem;
  padding: 0.15rem 0.5rem;
  border-radius: 12px;
  margin-left: 0.5rem;
  vertical-align: middle;
}

/* LOADING MODAL */
.loading-content {
  text-align: center;
  padding: 2rem;
}

.loading-content i {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: block;
}

/* ERROR MODAL */
.error-modal {
  max-width: 400px;
  text-align: center;
}

.error-modal h3 {
  color: #e74c3c;
}

/* EMPTY STATE */
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