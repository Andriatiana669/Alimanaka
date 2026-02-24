<!-- frontend/src/components/Layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <Sidebar :collapsed="sidebarCollapsed" />
    
    <div class="main-container">
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
  margin-left: 250px;
  transition: margin-left 0.3s ease;
}

.main-container.expanded {
  margin-left: 70px;
}

.main-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
  min-height: calc(100vh - 130px);
}

/* Responsive */
@media (max-width: 768px) {
  .main-container {
    margin-left: 0;
  }
  
  .main-content {
    padding: 1rem;
  }
}
</style>