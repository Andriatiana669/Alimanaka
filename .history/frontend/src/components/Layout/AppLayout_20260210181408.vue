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
    
    <!-- Message d'avertissement -->
    <div v-if="showSizeWarning" class="screen-size-warning">
      ⚠️ Pour une expérience optimale, veuillez utiliser une fenêtre d'au moins {{ minWidth }}px de largeur
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

// ================= CONFIGURATION =================
// Modifiez ces valeurs selon vos besoins
const CONFIG = {
  MIN_WIDTH: 802,    // Largeur minimale en pixels
  MIN_HEIGHT: 873,   // Hauteur minimale en pixels (optionnel)
  SIDEBAR_WIDTH: 250, // Largeur de la sidebar ouverte
  SIDEBAR_WIDTH_COLLAPSED: 80, // Largeur de la sidebar réduite
  MOBILE_BREAKPOINT: 768, // Point de rupture pour mobile
  TABLET_BREAKPOINT: 992  // Point de rupture pour tablette
}
// ================================================

// Variables réactives
const showSizeWarning = ref(false)
const minWidth = ref(CONFIG.MIN_WIDTH)

// Calcul des largeurs minimales
const minWidthMain = computed(() => CONFIG.MIN_WIDTH - CONFIG.SIDEBAR_WIDTH)
const minWidthMainCollapsed = computed(() => CONFIG.MIN_WIDTH - CONFIG.SIDEBAR_WIDTH_COLLAPSED)

// Fonction pour vérifier la taille de l'écran
const checkScreenSize = () => {
  const width = window.innerWidth
  const isMobile = width < CONFIG.MOBILE_BREAKPOINT
  const isTablet = width >= CONFIG.MOBILE_BREAKPOINT && width < CONFIG.MIN_WIDTH
  
  showSizeWarning.value = isTablet
  
  // Appliquer le min-width conditionnellement
  if (isTablet) {
    document.body.style.minWidth = `${CONFIG.MIN_WIDTH}px`
    document.documentElement.style.minWidth = `${CONFIG.MIN_WIDTH}px`
  } else if (isMobile) {
    // Pour mobile, on laisse faire le responsive normal
    document.body.style.minWidth = ''
    document.documentElement.style.minWidth = ''
  } else {
    // Pour desktop normal, on nettoie les styles
    document.body.style.minWidth = ''
    document.documentElement.style.minWidth = ''
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  // Nettoyer les styles appliqués
  document.body.style.minWidth = ''
  document.documentElement.style.minWidth = ''
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  min-width: v-bind(CONFIG.MIN_WIDTH + 'px');
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  min-width: v-bind(minWidthMain + 'px');
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: v-bind(CONFIG.SIDEBAR_WIDTH + 'px');
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: v-bind(CONFIG.SIDEBAR_WIDTH_COLLAPSED + 'px');
  min-width: v-bind(minWidthMainCollapsed + 'px');
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: v-bind(CONFIG.TABLET_BREAKPOINT + 'px')) {
  .main-content {
    margin-left: v-bind(CONFIG.SIDEBAR_WIDTH_COLLAPSED + 'px');
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
  }
}

@media (max-width: v-bind(CONFIG.MOBILE_BREAKPOINT + 'px')) {
  .dashboard-layout {
    min-width: 100vw !important;
  }
  
  .main-content {
    margin-left: 0 !important;
    min-width: 100vw !important;
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

/* Message d'avertissement */
.screen-size-warning {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  background: #ff9800;
  color: white;
  padding: 10px;
  text-align: center;
  font-size: 14px;
  z-index: 9999;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    transform: translateY(-100%);
  }
  to {
    transform: translateY(0);
  }
}
</style>