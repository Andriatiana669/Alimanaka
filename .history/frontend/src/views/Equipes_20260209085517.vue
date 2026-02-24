<!-- frontend/src/views/Equipes.vue -->
<template>
  <div class="equipes-page">
    <div class="page-header">
      <h1>Gestion des Équipes</h1>
      
      <!-- Affichage du rôle -->
      <div v-if="loadingUser" class="role-loading">
        <i class="bi bi-arrow-repeat spin"></i> Chargement...
      </div>
      
      <div v-else-if="currentUser" class="user-info">
        <span class="role-badge" :class="getRoleClass(currentUser)">
          {{ getRoleLabel(currentUser) }}
        </span>
        <span class="user-name">{{ currentUser.display_name }}</span>
      </div>
      
      <div v-else class="role-error">
        Non connecté
      </div>
    </div>

    <!-- Debug : afficher les données brutes -->
    <div class="debug-section">
      <h3>Debug - Données utilisateur</h3>
      <pre>{{ JSON.stringify(currentUser, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { usersApi } from '@/api/users'
import { useRoles } from '@/composables/useRoles'
import type { User } from '@/types/user'

// ========== RÔLES ==========
const { getRoleLabel, getRoleClass } = useRoles()

// ========== UTILISATEUR ==========
const currentUser = ref<User | null>(null)
const loadingUser = ref(false)

const fetchCurrentUser = async () => {
  loadingUser.value = true
  try {
    currentUser.value = await usersApi.getCurrentUser()  // <-- CHANGE ICI
    console.log('Utilisateur récupéré:', currentUser.value)
    console.log('is_superuser:', currentUser.value?.is_superuser)
    console.log('is_staff:', currentUser.value?.is_staff)
  } catch (err) {
    console.error('Erreur récupération user:', err)
  } finally {
    loadingUser.value = false
  }
}

onMounted(() => {
  fetchCurrentUser()
})
</script>

<style scoped>
.equipes-page {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e9ecef;
}

.page-header h1 {
  margin: 0;
  font-size: 1.75rem;
  color: #2c3e50;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-left: auto;
}

.role-badge {
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

.user-name {
  color: #6c757d;
  font-size: 0.9rem;
}

.role-loading, .role-error {
  margin-left: auto;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.debug-section {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
}

.debug-section h3 {
  margin-top: 0;
  color: #495057;
  font-size: 1rem;
}

pre {
  background: #2c3e50;
  color: #ecf0f1;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>