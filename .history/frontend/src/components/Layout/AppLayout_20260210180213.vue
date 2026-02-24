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
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'
import Footer from './Footer.vue'
</script>

<style scoped>
.dashboard-layout {
  display: flex;
  min-height: 100vh;
  width: 100%;
  overflow-x: hidden;
}

.main-content {
  flex: 1 1 auto;
  display: flex;
  flex-direction: column;
  min-width: 0;
  transition: margin-left 0.3s ease;
}

/* Sidebar ouvert (desktop) */
.main-content {
  margin-left: 250px;
}

/* Sidebar fermé */
.sidebar.collapsed ~ .main-content {
  margin-left: 80px;
}

/* ────────────────────────────────
   RESPONSIVE
───────────────────────────────── */

@media (max-width: 992px) {
  .main-content {
    margin-left: 80px;
  }
  
  .sidebar.collapsed ~ .main-content {
    margin-left: 0;
  }
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0 !important;
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
</style>