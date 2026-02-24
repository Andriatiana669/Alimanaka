<!-- frontend/src/components/Layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <Sidebar :collapsed="sidebarCollapsed" />
    
    <div class="main-container" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <Navbar />
      
      <main class="main-content">
        <router-view />
      </main>
      
      <Footer />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'

const sidebarCollapsed = ref(false)

const handleSidebarToggle = (event: CustomEvent) => {
  sidebarCollapsed.value = event.detail.collapsed
}

onMounted(() => {
  window.addEventListener('toggle-sidebar', handleSidebarToggle as EventListener)
  // Charger l'état initial depuis localStorage
  sidebarCollapsed.value = localStorage.getItem('sidebar-collapsed') === 'true'
})

onUnmounted(() => {
  window.removeEventListener('toggle-sidebar', handleSidebarToggle as EventListener)
})
</script>

<style scoped>
.app-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 250px; /* Largeur sidebar normale */
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-container.sidebar-collapsed {
  margin-left: 80px; /* Largeur sidebar réduite */
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  background-color: #f5f7fa;
  min-height: calc(100vh - 130px); /* Ajuster selon navbar + footer */
}

/* Responsive */
@media (max-width: 768px) {
  .main-container {
    margin-left: 0 !important;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>