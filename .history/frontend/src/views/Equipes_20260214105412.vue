<template>
  <!-- En-tête -->
  <div class="page-header">
    <h1>Gestion des Équipes</h1>
    <!-- <span v-if="currentUser" class="role-badge-header" :class="getRoleClass(currentUser)">
      {{ getRoleLabel(currentUser) }}
    </span> -->
    <!-- DEBUG TEMPORAIRE -->
    <!-- <div v-if="currentUser" style="background: #f0f0f0; padding: 5px 10px; margin-left: 10px; border-radius: 4px; font-size: 12px;">
      Debug: is_superuser={{ currentUser.is_superuser }}, is_staff={{ currentUser.is_staff }}
    </div> -->
  </div>

  <!-- Filtres -->
  <div class="filters-bar">
    <!-- Barre de recherche -->
    <div class="search-wrapper">
      <i class="bi bi-search search-icon"></i>
      <input
        type="text"
        v-model="searchQuery"
        placeholder="Rechercher équipe, membre, manager, co-manager..."
        class="filter-group search-input"
        @input="onSearchInput"
      />
      <button v-if="searchQuery" @click="clearSearch" class="clear-btn">
        <i class="bi bi-x"></i>
      </button>
    </div>

    <select v-model="poleFilter" @change="applyFilters" class="filter-group">
      <option value="">Tous les pôles</option>
      <option v-for="pole in polesStore.polesActifs" :key="pole.id" :value="pole.id">
        {{ pole.code }} - {{ pole.nom }}
      </option>
    </select>

    <select v-model="equipeFilter" @change="applyFilters" class="filter-group" :disabled="!poleFilter && !equipesStore.equipesActives.length">
      <option value="">Toutes les équipes</option>
      <option v-for="eq in equipesFiltreesPourSelect" :key="eq.id" :value="eq.id">
        {{ eq.nom }}
      </option>
    </select>

    <!-- TOGGLE Inactives -->
    <label class="toggle-inactives">
      <input 
        type="checkbox" 
        v-model="afficherInactives" 
        @change="onToggleInactives"
      />
      <span class="toggle-label">
        <i class="bi" :class="afficherInactives ? 'bi-eye' : 'bi-eye-slash'"></i>
        {{ afficherInactives ? 'Masquer' : 'Afficher' }} inactives
      </span>
    </label>

    <button class="btn-refresh" @click="refreshData" title="Actualiser">
      <i class="bi bi-arrow-clockwise"></i>
    </button>
  </div>

  <!-- Barre de stats -->
  <div class="stats-bar" v-if="!loading">
    <span class="stat active">
      <i class="bi bi-check-circle-fill"></i>
      {{ equipesStore.equipesActives.length }} actives
    </span>
    <span class="stat inactive" v-if="afficherInactives && equipesStore.equipesInactives.length > 0">
      <i class="bi bi-x-circle-fill"></i>
      {{ equipesStore.equipesInactives.length }} inactives
    </span>
  </div>

  <!-- Vue en arbre -->
  <div class="tree-view">
    <div v-if="loading" class="loading">
      <i class="bi bi-arrow-repeat spin"></i>
      <span>Chargement des équipes...</span>
    </div>

    <div v-else-if="arbreEquipesFiltrees.length === 0" class="empty">
      <div v-if="searchQuery">
        <i class="bi bi-search"></i>
        <p>Aucun résultat pour "<strong>{{ searchQuery }}</strong>"</p>
        <p class="hint">Essayez avec un autre nom, prénom, pseudo ou matricule</p>
      </div>
      <div v-else>
        <i class="bi bi-tree"></i>
        <p>Aucune équipe trouvée avec les filtres actuels</p>
      </div>
    </div>

    <EquipeNode
      v-else
      v-for="equipe in arbreEquipesFiltrees"
      :key="equipe.id"
      :equipe="equipe"
      :niveau="0"
      :selected-id="selectedEquipe?.id"
      :can-toggle="canToggleStatus"
      @select="selectEquipe"
      @toggle="toggleStatus"
      @refresh="refreshData"
    />
  </div>
</template>











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

.role-badge-header {
  padding: 0.35rem 0.75rem;
  border-radius: 4px;
  font-size: 0.85rem;
  font-weight: 500;
}

.role-badge-header.role-super-admin {
  background: #f5e6ff;
  color: #9b59b6;
}

.role-badge-header.role-admin {
  background: #e8f4fc;
  color: #3498db;
}

.role-badge-header.role-user {
  background: #e9ecef;
  color: #6c757d;
}

.filters-bar {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  align-items: center;
}

/* Wrapper pour la barre de recherche */
.search-wrapper {
  position: relative;
  flex: 1;
  min-width: 300px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  z-index: 1;
}

.search-input {
  width: 100%;
  padding-left: 2.25rem !important;
  padding-right: 2.5rem !important;
  flex: 1;
}

.clear-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #6c757d;
  cursor: pointer;
  padding: 0.25rem;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #e9ecef;
  color: #495057;
}

.filter-group {
  padding: 0.5rem 0.75rem;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  background: white;
  font-size: 0.9rem;
}

.filter-group:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.2);
}

.btn-refresh {
  width: 36px;
  height: 36px;
  border: 1px solid #dee2e6;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  transition: all 0.2s;
}

.btn-refresh:hover {
  background: #f8f9fa;
  color: #495057;
}
/* Barre toogle */
.toggle-inactives {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 6px;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s;
}

.toggle-inactives:hover {
  background: #e9ecef;
}

.toggle-inactives input {
  display: none;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.9rem;
  color: #495057;
}

.stats-bar {
  display: flex;
  gap: 1.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stat {
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.stat.active {
  color: #27ae60;
}

.stat.inactive {
  color: #e74c3c;
}


/* Indicateur de recherche */
.search-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: #e8f4fc;
  border: 1px solid #3498db;
  border-radius: 6px;
  margin-bottom: 1rem;
  color: #2c3e50;
}

.btn-clear-search {
  padding: 0.35rem 0.75rem;
  background: white;
  border: 1px solid #3498db;
  border-radius: 4px;
  color: #3498db;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.btn-clear-search:hover {
  background: #3498db;
  color: white;
}

/* Vue en arbre */
.tree-view {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 1rem;
  min-height: 400px;
}

.loading,
.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #6c757d;
  text-align: center;
}

.loading i,
.empty i {
  font-size: 2.5rem;
  margin-bottom: 1rem;
  display: block;
}

.empty .hint {
  font-size: 0.9rem;
  color: #adb5bd;
  margin-top: 0.5rem;
}

.spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .filters-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    min-width: auto;
  }

  .filter-group {
    width: 100%;
  }
}
</style>