<template>

</template>


<script setup lang="ts">


</script>


<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left h1 {
  color: #2c3e50;
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.retard-badge {
  display: flex;
  gap: 0.75rem;
  align-items: center;
  flex-wrap: wrap;
}

.heures-restantes {
  background-color: #fff3e0;
  color: #e65100;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.retards-encours {
  background-color: #e3f2fd;
  color: #0d47a1;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  font-weight: 500;
}

.header-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  background: #ff9800;
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #f57c00;
}

.filters-bar {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.filter-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-tabs button {
  padding: 0.6rem 1.2rem;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
}

.filter-tabs button.active {
  background: #ff9800;
  color: white;
  border-color: #ff9800;
}

.btn-refresh {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.6rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  margin-left: auto;
}

.btn-refresh:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.retards-calendar {
  height: calc(105vh - 280px);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

/* Preview box styles */
.preview-box {
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid;
}

.preview-box.type-leger {
  background: #e8f5e9;
  border-left-color: #4caf50;
}

.preview-box.type-moyen {
  background: #fff3e0;
  border-left-color: #ff9800;
}

.preview-box.type-important {
  background: #ffebee;
  border-left-color: #f44336;
}

.multiplicateur-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.5rem;
}

/* Modal détails */
.detail-section {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  border-radius: 12px;
  margin-bottom: 1.5rem;
  color: white;
}

.detail-avatar {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: rgba(255,255,255,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
  border: 3px solid white;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item label {
  font-size: 0.75rem;
  color: #6c757d;
  text-transform: uppercase;
  font-weight: 600;
}

.detail-minutes {
  font-weight: bold;
}

.detail-minutes.type-leger { color: #4caf50; }
.detail-minutes.type-moyen { color: #ff9800; }
.detail-minutes.type-important { color: #f44336; }

.detail-heures {
  color: #2196f3;
  font-weight: bold;
}

.detail-heures-restantes {
  color: #ff9800;
  font-weight: bold;
}

/* Rattrapages */
.rattrapages-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid #dee2e6;
}

.rattrapages-section h4 {
  margin-bottom: 1rem;
  color: #2c3e50;
}

.rattrapage-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border-left: 3px solid #4caf50;
}

.rattrapage-info {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.rattrapage-date {
  font-weight: 600;
  color: #2c3e50;
  min-width: 100px;
}

.rattrapage-heures {
  background: #4caf50;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.85rem;
  font-weight: 500;
}

.rattrapage-horaires {
  color: #6c757d;
  font-size: 0.9rem;
}

.rattrapage-commentaire {
  margin: 0.5rem 0 0 0;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
  font-style: italic;
  color: #495057;
}

/* Validation boxes */
.validation-box {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
}

.approved-box {
  background: #e8f5e9;
  border-left: 4px solid #4caf50;
}

.cancelled-box {
  background: #ffebee;
  border-left: 4px solid #f44336;
}

.cancelled-comment {
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: rgba(0,0,0,0.05);
  border-radius: 4px;
  font-style: italic;
}

/* Info retard dans modal rattrapage */
.info-retard {
  background: #e3f2fd;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  border-left: 4px solid #2196f3;
}

.info-retard p {
  margin: 0.25rem 0;
}

/* Header couleurs selon statut */
.header-en_attente { background: #ff9800; }
.header-en_cours { background: #2196f3; }
.header-approuve { background: #4caf50; }
.header-annule { background: #9e9e9e; }

.header-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 0.7em;
  margin-left: 10px;
  font-weight: bold;
  background: rgba(255,255,255,0.3);
}

/* Responsive */
@media (max-width: 768px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .rattrapage-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}
</style>