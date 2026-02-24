<template>
  <div class="dashboard-layout">
    <Sidebar />
    
    <div class="main-content">
      <Navbar />
      
      <div class="content-wrapper">
        <main class="content">
          <router-view />
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
  width: 100%;
  overflow-x: hidden;
  min-width: 1058px; /* Largeur minimale fixe */
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  min-width: 808px; /* 1058 - 250 (sidebar) = 808px */
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: 250px;
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
  min-width: 978px; /* 1058 - 80 = 978px */
}

/* ────────────────────────────────
   RESPONSIVE AVEC MIN-WIDTH
───────────────────────────────── */

/* Pour les écrans entre 992px et 1058px */
@media (max-width: 1057px) and (min-width: 992px) {
  .dashboard-layout {
    min-width: 992px;
  }
  
  .main-content {
    min-width: 742px; /* 992 - 250 = 742px */
  }
  
  .sidebar.collapsed ~ .main-content {
    min-width: 912px; /* 992 - 80 = 912px */
  }
}

/* Pour les écrans entre 768px et 992px */
@media (max-width: 991px) and (min-width: 768px) {
  .dashboard-layout {
    min-width: 768px;
  }
  
  .main-content {
    margin-left: 80px;
    min-width: 688px; /* 768 - 80 = 688px */
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
    min-width: 768px;
  }
}

/* Pour les écrans mobiles (< 768px) */
@media (max-width: 767px) {
  .dashboard-layout {
    min-width: 100vw; /* Utilise toute la largeur disponible */
    min-width: 0; /* Permet le redimensionnement en dessous */
  }
  
  .main-content {
    margin-left: 0 !important;
    min-width: 100vw;
    min-width: 0;
  }
  
  .content {
    padding: 1.5rem 1rem;
  }
}

/* Conteneurs internes */
.content-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: calc(100vh - var(--navbar-height, 64px));
  width: 100%;
  overflow-x: hidden;
}

.content {
  flex: 1 1 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
}

/* Pour les pages qui ont un tableau large */
.content :deep(.table-container) {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

/* Message d'avertissement pour les petits écrans */
@media (max-width: 1057px) {
  .dashboard-layout::before {
    content: "Pour une expérience optimale, veuillez utiliser une fenêtre d'au moins 1058px de largeur";
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    background: #ff9800;
    color: white;
    padding: 8px;
    text-align: center;
    font-size: 12px;
    z-index: 9999;
    display: none; /* Optionnel: activer si besoin */
  }
}
</style>