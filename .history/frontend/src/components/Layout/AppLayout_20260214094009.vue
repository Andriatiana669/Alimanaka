<!-- components/Layout/AppLayout.vue -->
<template>

  <div class="dashboard-layout">
    <Sidebar />
    
    
    <div class="main-content">
      <Navbar />
      
      <div class="content-wrapper">
        <main class="content">
          <router-view /> <!-- Contenu injecté ici -->
        </main>
        
        <Footer />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'



</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  margin-left: 250px;
  display: flex;
  flex-direction: column;
  transition: margin-left 0.3s ease;
}

.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 64px);
  position: relative;
}

.content {
  flex: 1;
  padding: 2rem;
  background-color: #f5f7fa;
  overflow-y: auto;
}
</style>