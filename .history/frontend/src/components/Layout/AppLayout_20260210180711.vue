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
import { ref, onMounted, onUnmounted } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

const showSizeWarning = ref(false)
const isMobile = ref(false)

// Fonction pour vérifier la taille de l'écran
const checkScreenSize = () => {
  const width = window.innerWidth
  
  // Mobile : en dessous de 768px
  isMobile.value = width < 768
  
  // Avertissement : entre 768px et 1057px
  showSizeWarning.value = width < 1058 && width >= 768
  
  // Appliquer le min-width directement sur le body pour forcer la taille
  if (width < 1058 && width >= 768) {
    // Pour les tablettes, on force la largeur minimale
    document.body.style.minWidth = '1058px'
    document.body.style.overflowX = 'auto'
  } else if (width < 768) {
    // Pour mobile, on laisse faire le responsive normal
    document.body.style.minWidth = ''
    document.body.style.overflowX = ''
  } else {
    // Pour desktop normal, on nettoie les styles
    document.body.style.minWidth = ''
    document.body.style.overflowX = ''
  }
}

// Fonction pour bloquer le redimensionnement en dessous de 1058px
const handleResize = () => {
  if (window.innerWidth < 1058 && window.innerWidth >= 768) {
    // Empêche le redimensionnement en dessous de 1058px (sauf mobile)
    window.resizeTo(1058, window.innerHeight)
    
    // Ou alternative : forcer le scroll horizontal
    document.documentElement.style.minWidth = '1058px'
    document.body.style.minWidth = '1058px'
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  window.removeEventListener('resize', handleResize)
  
  // Nettoyer les styles appliqués
  document.body.style.minWidth = ''
  document.body.style.overflowX = ''
  document.documentElement.style.minWidth = ''
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: 250px;
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
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
</style>