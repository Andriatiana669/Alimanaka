<template>
  <div class="login-page">
    <div class="login-container">
      <h1>Alimanaka</h1>
      <p class="subtitle">Connectez-vous pour accéder à votre calendrier</p>
      
      <div v-if="loading" class="loading">
        <div class="spinner"></div>
        <p>Vérification de votre session...</p>
      </div>
      
      <div v-else-if="error" class="error">
        <p>{{ error }}</p>
        <button @click="retry" class="btn-primary">Réessayer</button>
      </div>
      
      <div v-else-if="!isAuthenticated" class="login-form">
        <button @click="handleLogin" class="btn-sso">
          <span class="icon">🔐</span>
          Se connecter avec SSO
        </button>
        <p class="hint">Vous allez être redirigé vers le portail de connexion</p>
      </div>
      
      <div v-else class="already-auth">
        <p>✅ Vous êtes déjà connecté !</p>
        <button @click="goToDashboard" class="btn-primary">
          Accéder au tableau de bord
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')

const isAuthenticated = computed(() => authStore.isAuthenticated)

onMounted(async () => {
  // Vérifier si on revient d'une erreur
  if (route.query.error) {
    error.value = 'Erreur d\'authentification: ' + route.query.error
    loading.value = false
    return
  }
  
  // Vérifier la session
  try {
    await authStore.checkAuth()
    
    // Si authentifié et qu'on a un redirect, y aller
    if (authStore.isAuthenticated && route.query.redirect) {
      router.push(route.query.redirect as string)
      return
    }
  } catch {
    // Pas authentifié, c'est normal
    console.log('Pas de session active')
  } finally {
    loading.value = false
  }
})

function handleLogin() {
  authStore.login()
}

function goToDashboard() {
  router.push('/dashboard')
}

function retry() {
  error.value = ''
  handleLogin()
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-container {
  background: white;
  padding: 3rem;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

h1 {
  margin: 0 0 0.5rem 0;
  color: #333;
  font-size: 2.5rem;
}

.subtitle {
  color: #666;
  margin-bottom: 2rem;
}

.btn-sso {
  width: 100%;
  padding: 1rem;
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background 0.2s;
}

.btn-sso:hover {
  background: #4338ca;
}

.btn-primary {
  padding: 0.75rem 1.5rem;
  background: #10b981;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.loading, .error, .already-auth {
  padding: 2rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #4f46e5;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.hint {
  color: #999;
  font-size: 0.9rem;
  margin-top: 1rem;
}
</style>