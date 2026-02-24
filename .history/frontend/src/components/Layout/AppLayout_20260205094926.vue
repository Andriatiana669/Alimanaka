<!-- frontend/src/components/Layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <Navbar />
    <div class="layout-container">
      <Sidebar />
      <main class="main-content">
        <router-view />
      </main>
    </div>
    <Footer />
  </div>
</template>

<script setup lang="ts">
import Navbar from './Navbar.vue'
import Sidebar from './Sidebar.vue'
import Footer from './Footer.vue'
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
}
</style>