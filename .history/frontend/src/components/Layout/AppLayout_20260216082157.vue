<!-- Composants/Layout/AppLayout.vue à MODIFIER -->

<template>
  <div class="dashboard-layout">
    <Sidebar />
    
    <div class="main-content">
      <Navbar />
      
      <div class="content-wrapper">
        <main class="content">
          <router-view /> <!-- Contenu injecté ici -->
        </main>
        
        <Footer />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  width: 100%;
  max-width: 100%;
  overflow-x: hidden;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 64px);
  position: relative;
  width: 100%;
  max-width: 100%;
}

.content {
  flex: 1;
  padding: 2rem;
  background-color: #f5f7fa;
  overflow-y: auto;
  width: 100%; /* ← AJOUTER */
  max-width: 100%;
  box-sizing: border-box; /* ← AJOUTER pour que le padding soit inclus dans la largeur */
}

/* ===== AJOUTER CES MEDIA QUERIES ===== */
@media (max-width: 992px) {
  .main-content {
    margin-left: 0; /* Sidebar se cache ou devient flottante */
    width: 100vw;
    max-width: 100vw;
    overflow-x: hidden;
  }
  
  .content {
    padding: 1rem; /* Réduire le padding sur mobile */
    width: 100%;
    max-width: 100%;
    overflow-x: hidden;
  }
}

@media (max-width: 768px) {
  .content {
    padding: 0.75rem; /* Padding encore plus petit pour petits écrans */
  }
}
</style>