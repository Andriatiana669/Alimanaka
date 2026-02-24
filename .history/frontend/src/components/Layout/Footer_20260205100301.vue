<template>
  <div class="sidebar-footer">
    <span class="label">Copyright © Parera Madagascar {{ currentYear }}</span>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const currentYear = ref(new Date().getFullYear())
</script>

<style scoped>
.sidebar-footer {
    color: #2c3e50;
    text-align: center;
    padding: 1rem;
    width: 100%;
    background-color: #f5f7fa;
}
</style>
