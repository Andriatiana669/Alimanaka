<template>
  <MainLayout>
    <!-- En-tête de la page -->
    <div class="page-header">
      <h1>Tableau de bord</h1>
      <p class="welcome">Bienvenue, {{ authStore.fullName }}</p>
    </div>

    <!-- Grille de statistiques -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon conges">📅</div>
        <div class="stat-info">
          <h3>Congés</h3>
          <p class="stat-value">12</p>
          <span class="stat-label">Jours disponibles</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon retard">⏰</div>
        <div class="stat-info">
          <h3>Retards</h3>
          <p class="stat-value">2</p>
          <span class="stat-label">Ce mois</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon equipe">👥</div>
        <div class="stat-info">
          <h3>Équipe</h3>
          <p class="stat-value">8</p>
          <span class="stat-label">Membres</span>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon ostie">🏥</div>
        <div class="stat-info">
          <h3>OSTIE</h3>
          <p class="stat-value">Actif</p>
          <span class="stat-label">Statut</span>
        </div>
      </div>
    </div>

    <!-- Sections du dashboard -->
    <div class="dashboard-sections">
      <div class="section">
        <h2>Activités récentes</h2>
        <div class="activity-list">
          <div class="activity-item">
            <span class="activity-date">Aujourd'hui</span>
            <span class="activity-text">Demande de congé approuvée</span>
          </div>
          <div class="activity-item">
            <span class="activity-date">Hier</span>
            <span class="activity-text">Mise à jour du profil</span>
          </div>
          <div class="activity-item">
            <span class="activity-date">15 Jan</span>
            <span class="activity-text">Retard signalé</span>
          </div>
          <div class="activity-item">
            <span class="activity-date">12 Jan</span>
            <span class="activity-text">Nouveau membre d'équipe</span>
          </div>
        </div>
      </div>

      <div class="section">
        <h2>En attente d'approbation</h2>
        <div class="pending-list">
          <div class="pending-item">
            <span class="pending-type">Congé</span>
            <span class="pending-details">Jean Dupuis - 3 jours</span>
            <button class="btn-action">Voir</button>
          </div>
          <div class="pending-item">
            <span class="pending-type">Permission</span>
            <span class="pending-details">Marie Curie - 2h</span>
            <button class="btn-action">Voir</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Graphiques ou informations supplémentaires -->
    <div class="charts-container">
      <div class="chart-card">
        <h3>Congés par mois</h3>
        <div class="chart-placeholder">
          <!-- Placeholder pour un graphique -->
          <div class="chart-bars">
            <div class="bar" style="height: 60%; background-color: #3498db;"></div>
            <div class="bar" style="height: 80%; background-color: #2ecc71;"></div>
            <div class="bar" style="height: 45%; background-color: #e74c3c;"></div>
            <div class="bar" style="height: 70%; background-color: #f39c12;"></div>
          </div>
          <div class="chart-labels">
            <span>Jan</span>
            <span>Fév</span>
            <span>Mar</span>
            <span>Avr</span>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <h3>Répartition par équipe</h3>
        <div class="chart-placeholder">
          <!-- Placeholder pour un graphique circulaire -->
          <div class="pie-chart">
            <div class="pie-segment" style="--percentage: 40; --color: #3498db;"></div>
            <div class="pie-segment" style="--percentage: 25; --color: #2ecc71;"></div>
            <div class="pie-segment" style="--percentage: 20; --color: #e74c3c;"></div>
            <div class="pie-segment" style="--percentage: 15; --color: #f39c12;"></div>
          </div>
          <div class="chart-legend">
            <div class="legend-item">
              <span class="legend-color" style="background-color: #3498db;"></span>
              <span>Équipe A</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background-color: #2ecc71;"></span>
              <span>Équipe B</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </MainLayout>
</template>

<script setup lang="ts">
import { useAuth } from '@/composables/useauth'
import MainLayout from '../components/Layout/MainLayout.vue'

const authStore = useAuth()
</script>

<style scoped>
/* En-tête de page */
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

.welcome {
  color: #7f8c8d;
  font-size: 1.1rem;
  font-weight: 500;
}

/* Grille de statistiques */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.3s ease;
  border: 1px solid #eef2f7;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #dbeafe;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  flex-shrink: 0;
}

.stat-icon.conges { 
  background: linear-gradient(135deg, #e3f2fd, #bbdefb);
  color: #1565c0;
}

.stat-icon.retard { 
  background: linear-gradient(135deg, #fff3e0, #ffcc80);
  color: #ef6c00;
}

.stat-icon.equipe { 
  background: linear-gradient(135deg, #e8f5e9, #a5d6a7);
  color: #2e7d32;
}

.stat-icon.ostie { 
  background: linear-gradient(135deg, #fce4ec, #f48fb1);
  color: #ad1457;
}

.stat-info {
  flex: 1;
}

.stat-info h3 {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.5rem;
}

.stat-value {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
  line-height: 1.2;
}

.stat-label {
  color: #95a5a6;
  font-size: 0.85rem;
  font-weight: 500;
}

/* Sections du dashboard */
.dashboard-sections {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.section {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.section h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
  font-weight: 600;
  padding-bottom: 0.75rem;
  border-bottom: 2px solid #f5f7fa;
}

/* Liste d'activités */
.activity-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.activity-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: linear-gradient(to right, #f8f9fa, #ffffff);
  border-radius: 12px;
  border-left: 4px solid #3498db;
  transition: all 0.2s ease;
}

.activity-item:hover {
  background: linear-gradient(to right, #eef2f7, #f8f9fa);
  transform: translateX(4px);
}

.activity-date {
  color: #7f8c8d;
  font-size: 0.85rem;
  font-weight: 600;
  min-width: 80px;
}

.activity-text {
  color: #2c3e50;
  font-weight: 500;
  flex: 1;
  margin-left: 1rem;
}

/* Liste en attente */
.pending-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.pending-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #fff8e1;
  border-radius: 12px;
  border: 1px solid #ffecb3;
}

.pending-type {
  background-color: #ff9800;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
}

.pending-details {
  color: #5d4037;
  font-weight: 500;
  flex: 1;
  margin-left: 1rem;
}

.btn-action {
  background-color: #3498db;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-action:hover {
  background-color: #2980b9;
  transform: scale(1.05);
}

/* Conteneur de graphiques */
.charts-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.chart-card {
  background: white;
  padding: 1.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border: 1px solid #eef2f7;
}

.chart-card h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.2rem;
  font-weight: 600;
}

/* Placeholder graphique */
.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.chart-bars {
  display: flex;
  justify-content: space-around;
  align-items: flex-end;
  height: 120px;
  padding: 0 1rem;
}

.bar {
  width: 40px;
  border-radius: 8px 8px 0 0;
  transition: height 0.3s ease;
}

.chart-labels {
  display: flex;
  justify-content: space-around;
  padding: 0.5rem 1rem;
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Graphique circulaire */
.pie-chart {
  position: relative;
  width: 120px;
  height: 120px;
  border-radius: 50%;
  margin: 0 auto;
  background: conic-gradient(
    var(--color, #3498db) calc(var(--percentage, 0) * 1%),
    transparent 0 100%
  );
}

.pie-segment {
  position: absolute;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  clip-path: polygon(50% 50%, 50% 0%, 100% 0%, 100% 100%, 0% 100%, 0% 0%);
}

.chart-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: center;
  margin-top: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

/* Responsive */
@media (max-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-container {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .dashboard-sections {
    grid-template-columns: 1fr;
  }
  
  .activity-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .activity-text {
    margin-left: 0;
  }
}
</style>