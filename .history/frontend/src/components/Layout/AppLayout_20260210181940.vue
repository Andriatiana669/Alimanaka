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
import { ref, onMounted, onUnmounted } from 'vue'
import { layoutConfig, getCalculatedValues } from '@/config/layout'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

const config = layoutConfig
const calculated = getCalculatedValues(config)
const showSizeWarning = ref(false)

// Fonction pour vérifier la taille de l'écran
const checkScreenSize = () => {
  const width = window.innerWidth
  showSizeWarning.value = width < config.minWidth && width >= config.mobileBreakpoint
  
  if (width < config.minWidth && width >= config.mobileBreakpoint) {
    document.body.style.minWidth = `${config.minWidth}px`
  } else {
    document.body.style.minWidth = ''
  }
}

onMounted(() => {
  checkScreenSize()
  window.addEventListener('resize', checkScreenSize)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkScreenSize)
  document.body.style.minWidth = ''
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
  min-width: 802px; /* config.minWidth */
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  min-width: 552px; /* 802 - 250 = 552px */
  margin-left: 250px; /* config.sidebarWidth */
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px; /* config.sidebarWidthCollapsed */
  min-width: 722px; /* 802 - 80 = 722px */
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: 992px) { /* config.tabletBreakpoint */
  .main-content {
    margin-left: 80px; /* config.sidebarWidthCollapsed */
    min-width: 722px; /* 802 - 80 = 722px */
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
    min-width: 802px; /* config.minWidth */
  }
}

@media (max-width: 802px) { /* config.minWidth */
  .dashboard-layout {
    min-width: 802px;
  }
}

@media (max-width: 768px) { /* config.mobileBreakpoint */
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