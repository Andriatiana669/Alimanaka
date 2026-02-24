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
  width: 100vw;                /* ← important */
  overflow-x: hidden;
  position: relative;          /* contexte pour le fixed */
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  width: 100%;                 /* ← force full width */
  margin-left: 0;              /* on gère via padding ou offset */
  box-sizing: border-box;
}

/* Sidebar en fixed (à déplacer dans Sidebar.vue si pas déjà fait) */
:deep(.sidebar) {              /* ou directement dans Sidebar.vue */
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 250px;
  z-index: 900;
  transition: transform 0.3s ease, width 0.3s ease;
  overflow-y: auto;
  background: white;           /* ou ta couleur */
}

/* Quand sidebar est collapsed */
.sidebar.collapsed {
  width: 80px;
}

/* Sur mobile : on cache ou on met en overlay */
@media (max-width: 992px) {
  :deep(.sidebar) {
    transform: translateX(-100%);   /* caché par défaut */
  }
  
  .sidebar.open {                   /* à gérer via une classe JS */
    transform: translateX(0);
  }
  
  .main-content {
    margin-left: 0 !important;
  }
}

/* Content wrapper & content */
.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-x: hidden;
}

.content {
  flex: 1;
  padding: 2rem;
  padding-left: 270px;          /* ← décalage = largeur sidebar + marge */
  background: #f5f7fa;
  overflow-y: auto;
  overflow-x: hidden;
  min-width: 0;
  box-sizing: border-box;
}

/* Sur tablette/mobile, on enlève le padding-left fixe */
@media (max-width: 992px) {
  .content {
    padding-left: 1.5rem;       /* ou 1rem */
    padding-right: 1rem;
  }
}

/* Navbar doit prendre toute la largeur disponible */
:deep(.navbar) {                 /* ou dans Navbar.vue */
  width: 100%;
  position: sticky;
  top: 0;
  left: 0;
  right: 0;
  z-index: 950;
  background: white;
  border-bottom: 1px solid #e1e8ed;
}
</style>