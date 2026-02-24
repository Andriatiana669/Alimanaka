<!-- frontend/src/views/Auth/Callback.vue -->
<template>
  <div class="callback">
    <div class="spinner"></div>
    <p>Connexion en cours...</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { checkAuth } = useAuth()

onMounted(async () => {
  // Vérifier l'authentification après le callback
  await checkAuth()
  
  // Attendre un peu pour que l'utilisateur voie l'animation
  setTimeout(() => {
    router.push('/dashboard')
  }, 500)
})
</script>

<style scoped>
.callback {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.spinner {
  width: 50px;
  height: 50px;
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s ease-in-out infinite;
  margin-bottom: 1.5rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

p {
  font-size: 1.2rem;
  font-weight: 500;
}
</style>