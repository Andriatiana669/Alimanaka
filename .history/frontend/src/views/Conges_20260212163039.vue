<!-- frontend/src/views/Conges.vue -->
<template>
    <div class="page-header">
      <h1>Mes Congés</h1>
    </div>

    <!-- Filtres rapides (optionnel) -->
    <div class="filters-bar">
      <select v-model="yearFilter" class="filter-select">
        <option v-for="y in years" :key="y" :value="y">{{ y }}</option>
      </select>
      <button class="btn-refresh" @click="refreshData">
        <i class="bi bi-arrow-clockwise"></i> Actualiser
      </button>
    </div>

    <!-- Le calendrier réutilisable -->
    <Calendar
      :events="filteredCongesEvents"
      :default-view="'timeline'"
      class="conges-calendar"
    />

    <!-- Modal de demande (placeholder) -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <h3>Nouvelle demande de congé</h3>
        <!-- Formulaire ici plus tard -->
        <div class="modal-actions">
          <button class="btn-secondary" @click="closeModal">Annuler</button>
          <button class="btn-primary">Envoyer</button>
        </div>
      </div>
    </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import Calendar from '@/components/common/Calendar.vue'

// ────────────────────────────────────────────────
// Données (à remplacer par vrai appel API plus tard)
const conges = ref([
  {
    id: 'c1',
    title: 'Congé annuel',
    start: new Date(2025, 1, 17), // 17 février 2025
    end: new Date(2025, 1, 21),
    allDay: true,
    color: '#c8e6c9' // vert clair
  },
  {
    id: 'c2',
    title: 'Repos médical',
    start: new Date(2025, 1, 10, 9, 0),
    end: new Date(2025, 1, 10, 17, 0),
    color: '#ffe0b2' // orange clair
  }
])

// ────────────────────────────────────────────────
// Computed pour passer au calendrier
const filteredCongesEvents = computed(() => conges.value)

// Années pour le filtre (exemple)
const currentYear = new Date().getFullYear()
const years = computed(() => [
  currentYear - 1,
  currentYear,
  currentYear + 1,
  currentYear + 2
])

const yearFilter = ref(currentYear)

// ────────────────────────────────────────────────
// Modal
const showModal = ref(false)

const openRequestModal = () => {
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const refreshData = () => {
  // Plus tard : appel API pour recharger les congés
  console.log('Rafraîchissement des congés...')
}
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

.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.filter-select {
  padding: 0.6rem 1rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  min-width: 140px;
}

.btn-refresh {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  cursor: pointer;
}

.conges-calendar {
  height: calc(100vh - 220px); /* Ajuste selon ta Navbar + header */
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Modal styles (similaire à Poles.vue / Users.vue) */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 90%;
  max-width: 500px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.btn-secondary {
  padding: 0.75rem 1.5rem;
  background: #6c757d;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}
</style>