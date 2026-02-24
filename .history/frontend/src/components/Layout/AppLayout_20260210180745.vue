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
import { onMounted, onUnmounted } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

// Applique le min-width sur le body
onMounted(() => {
  document.body.style.minWidth = '1058px'
  document.documentElement.style.minWidth = '1058px'
})

onUnmounted(() => {
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
  min-width: 1058px; /* Largeur minimale garantie */
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
  min-width: 808px; /* 1058 - 250 sidebar */
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: 250px;
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
  min-width: 978px; /* 1058 - 80 */
}

/* Exception pour mobile seulement */
@media (max-width: 768px) {
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

/* Le reste du CSS reste identique */
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
</style>