<!-- frontend/src/components/Layout/AppLayout.vue -->
<template>
  <div class="app-layout">
    <!-- Navbar fixe en haut -->
    <Sidebar />
    
    <div class="layout-container">
      <!-- Sidebar fixe à gauche -->
      <Navbar />
      
      <!-- Contenu principal avec routage -->
      <main class="main-content">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
    
    <!-- Footer fixe en bas -->
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
  margin-top: 64px; /* Hauteur de la navbar */
}

.main-content {
  flex: 1;
  padding: 2rem;
  background-color: #f8fafc;
  min-height: calc(100vh - 64px - 60px); /* viewport - navbar - footer */
  overflow-y: auto;
}

/* Animation pour les transitions de route */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>