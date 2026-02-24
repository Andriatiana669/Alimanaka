<!-- frontend/src/views/Equipes.vue -->
<template>
  <div class="equipes-page">
    <!-- En-tête -->
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <!-- Badge de rôle -->
      <div v-if="loadingUser" class="role-loading">
        <i class="bi bi-arrow-repeat spin"></i>
      </div>
      
      <span 
        v-else-if="currentUser" 
        class="role-badge-header" 
        :class="getRoleClass(currentUser)"
      >
        {{ getRoleLabel(currentUser) }}
      </span>
      
      <!-- Bouton création (Super Admin uniquement) -->
      <button 
        v-if="canEditEquipeDetails(currentUser)" 
        class="btn-primary" 
        @click="openCreateModal"
      >
        <i class="bi bi-plus-lg"></i>
        Nouvelle équipe
      </button>
    </div>

    <!-- Contenu à venir... -->
    <div class="content-placeholder">
      <p>Chargement des équipes...</p>
    </div>

    <!-- Modal création (vide pour l'instant) -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeCreateModal">
      <div class="modal">
        <h3>Nouvelle équipe</h3>
        <p>Formulaire à venir...</p>
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeCreateModal">Fermer</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { useRoles } from '@/composables/useRoles'
import type { User } from '@/types/user'

// ========== RÔLES ==========
const { getRoleLabel, getRoleClass, canEditEquipeDetails } = useRoles()

// ========== UTILISATEUR ==========
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

// ========== MODAL CRÉATION ==========
const showCreateModal = ref(false)

const openCreateModal = () => {
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

onMounted(() => {
  fetchCurrentUser()
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
  font-weight: 600;
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

.role-loading {
  color: #6c757d;
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

.content-placeholder {
  padding: 3rem;
  text-align: center;
  color: #6c757d;
  background: #f8f9fa;
  border-radius: 8px;
}

/* Modal styles */
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
  border-radius: 8px;
  padding: 1.5rem;
  width: 90%;
  max-width: 500px;
}

.modal h3 {
  margin-top: 0;
  color: #2c3e50;
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

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>