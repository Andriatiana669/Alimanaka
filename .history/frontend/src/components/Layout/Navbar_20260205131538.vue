<!-- frontend/src/components/Layout/Sidebar.vue -->
<template>
  <aside class="sidebar" :class="{ 'collapsed': collapsed }">
    <!-- Ton contenu sidebar -->
  </aside>
</template>

<script setup lang="ts">
defineProps<{
  collapsed?: boolean
}>()
</script>

<style scoped>
.sidebar {
  width: 250px;
  background: #2c3e50;
  transition: width 0.3s ease;
}

.sidebar.collapsed {
  width: 60px;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -250px;
    height: calc(100vh - 60px);
    top: 60px;
    z-index: 99;
    transition: left 0.3s ease;
  }
  
  .sidebar.collapsed {
    left: 0;
    width: 250px;
  }
}
</style>