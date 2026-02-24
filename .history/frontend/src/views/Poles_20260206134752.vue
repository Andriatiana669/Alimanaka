<template>
  <div class="poles-page">
    <div class="page-header">
      <h1>Gestion des Pôles</h1>
      <button v-if="isAdmin" class="btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg"></i>
        Nouveau pôle
      </button>
    </div>

    <!-- Tableau des pôles -->
    <div class="table-container">
      <div v-if="loading" class="loading">
        <i class="bi bi-arrow-repeat spin"></i>
        <span>Chargement...</span>
      </div>

      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Code</th>
            <th>Nom</th>
            <th>Description</th>
            <th>Équipes</th>
            <th>Membres</th>
            <th>Statut</th>
            <th v-if="isAdmin">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="pole in poles" :key="pole.id" :class="{ 'inactive': !pole.est_actif }">
            <td class="code">{{ pole.code }}</td>
            <td>{{ pole.nom }}</td>
            <td>{{ pole.description || '-' }}</td>
            <td>{{ pole.equipes_count || 0 }}</td>
            <td>{{ pole.utilisateurs_count || 0 }}</td>
            <td>
              <span class="badge" :class="pole.est_actif ? 'active' : 'inactive'">
                {{ pole.est_actif ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td v-if="isAdmin" class="actions">
              <button class="btn-icon edit" @click="openEditModal(pole)" title="Modifier">
                <i class="bi bi-pencil"></i>
              </button>
              <button 
                class="btn-icon toggle" 
                @click="toggleStatus(pole)" 
                :title="pole.est_actif ? 'Désactiver' : 'Activer'"
              >
                <i class="bi" :class="pole.est_actif ? 'bi-pause-circle' : 'bi-play-circle'"></i>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal création/édition -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>{{ editingPole ? 'Modifier' : 'Nouveau' }} pôle</h3>
        
        <form @submit.prevent="savePole">
          <div class="form-group">
            <label>Code *</label>
            <input 
              v-model="form.code" 
              required 
              maxlength="10"
              placeholder="Ex: DEV"
            />
          </div>
          
          <div class="form-group">
            <label>Nom *</label>
            <input 
              v-model="form.nom" 
              required 
              maxlength="100"
              placeholder="Ex: Développement"
            />
          </div>
          
          <div class="form-group">
            <label>Description</label>
            <textarea 
              v-model="form.description" 
              rows="3"
              placeholder="Description du pôle..."
            ></textarea>
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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { usePolesStore } from '@/store/poles'
import { useAuth } from '@/composables/useAuth'
import type { Pole } from '@/types/user'

const polesStore = usePolesStore()
const { isAdmin } = useAuth()

const poles = computed(() => polesStore.poles)
const loading = computed(() => polesStore.loading)

// Modal
const showModal = ref(false)
const editingPole = ref<Pole | null>(null)
const saving = ref(false)

const form = ref({
  code: '',
  nom: '',
  description: ''
})

const openCreateModal = () => {
  editingPole.value = null
  form.value = { code: '', nom: '', description: '' }
  showModal.value = true
}

const openEditModal = (pole: Pole) => {
  editingPole.value = pole
  form.value = {
    code: pole.code,
    nom: pole.nom,
    description: pole.description || ''
  }
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
  editingPole.value = null
}

const savePole = async () => {
  saving.value = true
  try {
    if (editingPole.value) {
      await polesStore.updatePole(editingPole.value.id, {
        code: form.value.code,
        nom: form.value.nom,
        description: form.value.description
      })
    } else {
      await polesStore.createPole({
        code: form.value.code,
        nom: form.value.nom,
        description: form.value.description,
        est_actif: true
      })
    }
    closeModal()
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  } finally {
    saving.value = false
  }
}

const toggleStatus = async (pole: Pole) => {
  if (!confirm(`Voulez-vous ${pole.est_actif ? 'désactiver' : 'activer'} le pôle "${pole.nom}" ?`)) return
  
  try {
    await polesStore.updatePole(pole.id, { est_actif: !pole.est_actif })
  } catch (err) {
    alert('Erreur: ' + (err as Error).message)
  }
}

onMounted(() => {
  polesStore.fetchPoles()
})
</script>

<style scoped>
.poles-page {
  padding: 2rem;
  max-width: 1200px;
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
  font-weight: 500;
}

.btn-primary:hover {
  background: #2980b9;
}

.table-container {
  background: white;
  border-radius: 8px;
  border: 1px solid #e9ecef;
  overflow: hidden;
}

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

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e9ecef;
}

.data-table th {
  background: #f8f9fa;
  font-weight: 600;
  color: #495057;
}

.data-table tr:hover {
  background: #f8fafc;
}

.data-table tr.inactive {
  opacity: 0.6;
}

.code {
  font-family: monospace;
  font-weight: 600;
  color: #3498db;
}

.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}

.badge.active {
  background: #d4edda;
  color: #155724;
}

.badge.inactive {
  background: #f8d7da;
  color: #721c24;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.btn-icon {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-icon.edit {
  background: #e8f4fc;
  color: #3498db;
}

.btn-icon.edit:hover {
  background: #3498db;
  color: white;
}

.btn-icon.toggle {
  background: #fff3e6;
  color: #f39c12;
}

.btn-icon.toggle:hover {
  background: #f39c12;
  color: white;
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
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.modal h3 {
  margin: 0 0 1.5rem 0;
  color: #2c3e50;
}

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
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  font-size: 0.9rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
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

.btn-secondary:hover {
  background: #5a6268;
}
</style>