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
      ⚠️ Pour une expérience optimale, veuillez utiliser une fenêtre d'au moins {{ config.minWidth }}px de largeur
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { layoutConfig, getCalculatedValues } from '@/config/layout'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

const config = layoutConfig
const calculated = getCalculatedValues(config)
const showSizeWarning = ref(false)

// Calcul des valeurs CSS dynamiques
const layoutStyles = computed(() => ({
  '--min-width': `${config.minWidth}px`,
  '--sidebar-width': `${config.sidebarWidth}px`,
  '--sidebar-width-collapsed': `${config.sidebarWidthCollapsed}px`,
  '--mobile-breakpoint': `${config.mobileBreakpoint}px`,
  '--tablet-breakpoint': `${config.tabletBreakpoint}px`,
  '--min-width-main': `${calculated.minWidthMain}px`,
  '--min-width-main-collapsed': `${calculated.minWidthMainCollapsed}px`
}))

// Fonction pour vérifier la taille de l'écran
const checkScreenSize = () => {
  const width = window.innerWidth
  showSizeWarning.value = width < config.minWidth && width >= config.mobileBreakpoint
  
  // Appliquer le min-width sur le body si nécessaire
  if (width < config.minWidth && width >= config.mobileBreakpoint) {
    document.body.style.minWidth = `${config.minWidth}px`
    document.documentElement.style.overflowX = 'auto'
  } else if (width < config.mobileBreakpoint) {
    // Pour mobile, on laisse faire le responsive normal
    document.body.style.minWidth = ''
    document.documentElement.style.overflowX = ''
  } else {
    // Pour desktop normal, on nettoie les styles
    document.body.style.minWidth = ''
    document.documentElement.style.overflowX = ''
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
  document.documentElement.style.overflowX = ''
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  min-width: var(--min-width);
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  min-width: var(--min-width-main);
  margin-left: var(--sidebar-width);
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: var(--sidebar-width-collapsed);
  min-width: var(--min-width-main-collapsed);
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: var(--tablet-breakpoint)) {
  .main-content {
    margin-left: var(--sidebar-width-collapsed);
    min-width: var(--min-width-main-collapsed);
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
    min-width: var(--min-width);
  }
}

@media (max-width: var(--min-width)) {
  .dashboard-layout {
    min-width: var(--min-width);
  }
}

@media (max-width: var(--mobile-breakpoint)) {
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