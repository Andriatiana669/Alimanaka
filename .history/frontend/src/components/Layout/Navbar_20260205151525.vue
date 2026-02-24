<!-- frontend/src/components/Layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <Navbar />
    <div class="layout-container">
      <Sidebar :collapsed="sidebarCollapsed" />
      <main class="main-content" :class="{ 'expanded': sidebarCollapsed }">
        <router-view />
      </main>
    </div>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'


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
  flex-direction: column;
  min-height: 100vh;
}

.layout-container {
  display: flex;
  flex: 1;
}

.main-content {
  flex: 1;
  padding: 2rem;
  background-color: #f8f9fa;
  min-height: calc(100vh - 120px);
  transition: margin-left 0.3s ease;
}

.main-content.expanded {
  margin-left: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 1rem;
  }
}
</style>