<template>
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      <button v-if="isAdmin" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i>
        Nouvelle équipe
      </button>
    </div>

    <!-- Vue en arbre -->
    <div class="tree-view">
      <div v-if="loading" class="loading">
        <i class="bi bi-arrow-repeat spin"></i>
        <span>Chargement de l'arborescence...</span>
      </div>

      <div v-else-if="arbreEquipes.length === 0" class="empty">
        Aucune équipe définie
      </div>

      <EquipeNode 
        v-else
        v-for="equipe in arbreEquipes" 
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
      <h3>{{ selectedEquipe.nom }}</h3>
      
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
          <span>{{ selectedEquipe.membres_count || 0 }}</span>
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
        <ul v-else class="membres-list">
          <li v-for="membre in membres" :key="membre.id">
            {{ membre.display_name }}
            <span v-if="membre.pseudo" class="pseudo-tag">{{ membre.pseudo }}</span>
          </li>
        </ul>
      </div>
    </div>

    <!-- Modal création/édition -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingEquipe ? 'Modifier' : 'Nouvelle' }} équipe</h3>
        
        <form @submit.prevent="saveEquipe">
          <div class="form-group">
            <label>Nom *</label>
            <input v-model="form.nom" required maxlength="100" />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea v-model="form.description" rows="2"></textarea>
          </div>

          <PoleSelect 
            v-model="form.pole"
            label="Pôle"
            placeholder="Sélectionner un pôle"
          />

          <div class="form-group">
            <label>Équipe parente</label>
            <select v-model="form.equipe_parente">
              <option :value="null">Aucune (racine)</option>
              <option 
                v-for="eq in equipesPossiblesParent" 
                :key="eq.id" 
                :value="eq.id"
              >
                {{ '  '.repeat(eq.niveau_hierarchique || 0) }}{{ eq.nom }}
              </option>
            </select>
          </div>

          <div class="modal-actions">
            <button type="button" class="btn-secondary" @click="closeModal">Annuler</button>
            <button type="submit" class="btn-primary" :disabled="saving">
              {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useEquipesStore } from '@/store/equipes'
import { useAuth } from '@/composables/useAuth'
import PoleSelect from '@/components/common/PoleSelect.vue'
import EquipeNode from '@/components/common/EquipeNode.vue'
import type { Equipe } from '@/types/user'


const equipesStore = useEquipesStore()
const { isAdmin } = useAuth()

const arbreEquipes = computed(() => equipesStore.arbreEquipes)
const equipes = computed(() => equipesStore.equipes)
const loading = computed(() => equipesStore.loading)
const membres = computed(() => equipesStore.membresCurrentEquipe)

const selectedEquipe = ref<Equipe | null>(null)
const loadingMembres = ref(false)

// Modal
const showModal = ref(false)
const editingEquipe = ref<Equipe | null>(null)
const saving = ref(false)

const form = ref({
  nom: '',
  description: '',
  pole: null as number | null,
  equipe_parente: null as number | null
})

// Filtrer les équipes possibles comme parent (pas soi-même, pas ses enfants)
const equipesPossiblesParent = computed(() => {
  const all = equipes.value
  if (!editingEquipe.value) return all
  
  // Exclure l'équipe en cours d'édition et ses descendants
  const idsExclus = new Set([editingEquipe.value.id])
  
  const ajouterDescendants = (equipe: Equipe) => {
    equipe.sous_equipes?.forEach(child => {
      idsExclus.add(child.id)
      ajouterDescendants(child)
    })
  }
  
  const trouverDansArbre = (liste: Equipe[], id: number): Equipe | null => {
    for (const e of liste) {
      if (e.id === id) return e
      const found = trouverDansArbre(e.sous_equipes || [], id)
      if (found) return found
    }
    return null
  }
  
  const current = trouverDansArbre(arbreEquipes.value, editingEquipe.value.id)
  if (current) ajouterDescendants(current)
  
  return all.filter(e => !idsExclus.has(e.id))
})

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
  editingEquipe.value = null
  form.value = { nom: '', description: '', pole: null, equipe_parente: null }
  showModal.value = true
}

const openEditModal = (equipe: Equipe) => {
  editingEquipe.value = equipe
  form.value = {
    nom: equipe.nom,
    description: equipe.description || '',
    pole: equipe.pole,
    equipe_parente: equipe.equipe_parente
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingEquipe.value = null
}

const saveEquipe = async () => {
  saving.value = true
  try {
    const data = {
      nom: form.value.nom,
      description: form.value.description,
      pole: form.value.pole,
      equipe_parente: form.value.equipe_parente,
      manager: null,
      est_actif: true
    }
    
    if (editingEquipe.value) {
      await equipesStore.updateEquipe(editingEquipe.value.id, data)
    } else {
      await equipesStore.createEquipe(data)
    }
    await equipesStore.fetchArbre()
    closeModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (equipe: Equipe) => {
  if (!confirm(`Voulez-vous ${equipe.est_actif ? 'désactiver' : 'activer'} l'équipe "${equipe.nom}" ?`)) return
  
  try {
    await equipesStore.updateEquipe(equipe.id, { est_actif: !equipe.est_actif })
    await equipesStore.fetchArbre()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

onMounted(() => {
  equipesStore.fetchArbre()
})
</script>

<style scoped>

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

.tree-view {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1.5rem;
  margin-bottom: 2rem;
}

.equipe-details {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  padding: 1.5rem;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin: 1rem 0;
}

.info-item label {
  display: block;
  color: #6c757d;
  font-size: 0.85rem;
  margin-bottom: 0.25rem;
}

.info-item span {
  font-weight: 500;
  color: #2c3e50;
}

.membres-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #e9ecef;
}

.membres-list {
  list-style: none;
  padding: 0;
}

.membres-list li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #f8f9fa;
}

.pseudo-tag {
  background: #e8f4fc;
  color: #3498db;
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  margin-left: 0.5rem;
}

/* Modal styles (identiques à Poles.vue) */
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
}

/* ... autres styles identiques à Poles.vue ... */
</style>