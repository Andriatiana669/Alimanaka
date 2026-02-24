<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <h1>Tableau de Bord</h1>
    <div v-if="user" class="welcome-card">
      <h2>Bienvenue, {{ user.display_name }}!</h2>
      <div class="stats">
        <div class="stat-card">
          <h3>Matricule</h3>
          <p>{{ user.username }}</p>
        </div>
        <div class="stat-card">
          <h3>Email</h3>
          <p>{{ user.email }}</p>
        </div>
        <div class="stat-card">
          <h3>Membre depuis</h3>
          <p>{{ formatDate(user.date_joined) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'

const { user } = useAuth()

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('fr-FR', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}
</script>

<style scoped>
.dashboard {
  padding: 2rem;
}

h1 {
  color: #2c3e50;
  margin-bottom: 2rem;
}

.welcome-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.welcome-card h2 {
  color: #3498db;
  margin-bottom: 1.5rem;
}

.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.stat-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
}

.stat-card h3 {
  color: #7f8c8d;
  font-size: 0.9rem;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.stat-card p {
  color: #2c3e50;
  font-size: 1.2rem;
  font-weight: bold;
  margin: 0;
}
</style>