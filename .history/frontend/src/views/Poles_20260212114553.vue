<template>
    <div class="page-header">
      <h1>Gestion des Pôles</h1>
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
          </tr>
        </tbody>
      </table>
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



onMounted(() => {
  polesStore.fetchPoles()
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