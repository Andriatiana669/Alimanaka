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
  overflow-x: hidden;
}

/* ────────────────────────────────────────
   MAIN CONTENT – gestion du margin-left
───────────────────────────────────────── */
.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  background: #fff; /* fond propre pour éviter transparence bizarre */
}

/* Par défaut (sidebar ouvert) */
.main-content {
  margin-left: 250px;
}

/* Sidebar replié */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

/* ────────────────────────────────────────
   RESPONSIVE – breakpoints progressifs
───────────────────────────────────────── */

/* Tablette large / petit desktop → sidebar mini par défaut */
@media (max-width: 1200px) {
  .main-content {
    margin-left: 80px;
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
  }
}

/* Tablette / mobile paysage → sidebar caché par défaut */
@media (max-width: 992px) {
  .main-content {
    margin-left: 0 !important;
  }
  
  .content {
    padding: 1.5rem 1.25rem;
  }
}

/* Mobile portrait → encore plus compact */
@media (max-width: 768px) {
  .content {
    padding: 1.25rem 1rem;
  }
  
  /* Si tu veux un overlay sidebar sur mobile (optionnel) */
  /* .sidebar { position: fixed; z-index: 1100; transform: translateX(-100%); transition: transform 0.3s; } */
  /* .sidebar.open { transform: translateX(0); } */
}

/* ────────────────────────────────────────
   CONTENEURS INTERNES
───────────────────────────────────────── */
.content-wrapper {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - var(--navbar-height, 100px)); /* adapte à la vraie hauteur de ta Navbar */
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

/* Permet le scroll horizontal LOCALISE sur les tableaux larges */
.content :deep(.table-container),
.content :deep(.users-table-wrapper) {  /* adapte si tu as renommé */
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: thin;
}

/* Option : fond gris clair sur sidebar pour mieux voir la limite */
.sidebar {
  background: #2c3e50; /* ou ta couleur actuelle */
  color: white;
  transition: width 0.3s ease;
}

/* ────────────────────────────────────────
   SOLUTION DE DERNIER RECOURS : taille minimale
   (à décommenter seulement si vraiment nécessaire)
───────────────────────────────────────── */
/* 
.dashboard-layout {
  min-width: 1058px;
  min-height: 873px;
}
*/
</style>