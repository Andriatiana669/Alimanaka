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
  width: 100%;
  overflow-x: hidden;          /* ← très important */
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;                /* ← empêche le débordement forcé */
  transition: margin-left 0.3s ease;
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: 250px;
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;          /* on passe en mode "sidebar mini" par défaut */
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;             /* sidebar complètement caché → full width */
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;  /* plus de marge fixe sur mobile */
  }
  
  .content {
    padding: 1.5rem 1rem;       /* moins de padding horizontal */
  }
  
  /* Option : sidebar overlay sur mobile (à combiner avec logique JS si besoin) */
  /* .sidebar { position: fixed; transform: translateX(-100%); transition: transform 0.3s; } */
  /* .sidebar.open { transform: translateX(0); } */
}

/* Conteneurs internes */
.content-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1 1 auto;
  min-height: calc(100vh - var(--navbar-height, 64px)); /* plus robuste */
  width: 100%;
  overflow-x: hidden;          /* sécurité supplémentaire */
}

.content {
  flex: 1 1 auto;
  padding: 2rem;
  background-color: #f5f7fa;
  overflow-y: auto;
  overflow-x: hidden;          /* ← clé pour éviter barre horizontale */
  min-width: 0;
}

/* Pour les pages qui ont un tableau large (comme Users.vue) */
.content :deep(.table-container) {
  overflow-x: auto;            /* scroll horizontal SEULEMENT sur le tableau */
  -webkit-overflow-scrolling: touch;
}
</style>