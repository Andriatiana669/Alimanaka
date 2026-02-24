<!-- frontend/src/components/Layout/MainLayout.vue -->
<template>
  <div class="dashboard-layout">
    <Sidebar :collapsed="sidebarCollapsed" />
    
    <div class="main-content" :class="{ 'expanded': sidebarCollapsed }">
      <Navbar />
      
      <div class="content-wrapper">
        <main class="content">
          <slot /> <!-- Contenu injecté ici -->
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

const sidebarCollapsed = ref(false)

// Écouter l'événement de toggle du navbar
const handleSidebarToggle = (event: CustomEvent) => {
  sidebarCollapsed.value = event.detail.collapsed
}

onMounted(() => {
  window.addEventListener('toggle-sidebar', handleSidebarToggle as EventListener)
})

onUnmounted(() => {
  window.removeEventListener('toggle-sidebar', handleSidebarToggle as EventListener)
})
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f5f7fa;
}

.main-content {
  flex: 1;
  margin-left: 250px; /* Largeur de la sidebar par défaut */
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
  min-height: 100vh;
}

.main-content.expanded {
  margin-left: 70px; /* Largeur sidebar réduite */
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  flex: 1;
}

.content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  min-height: calc(100vh - 130px); /* 70px navbar + 60px footer */
}

/* Responsive */
@media (max-width: 1024px) {
  .main-content {
    margin-left: 70px;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
  
  .content {
    padding: 1rem;
  }
}
</style>