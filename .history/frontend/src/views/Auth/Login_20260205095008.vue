<!-- frontend/src/views/Auth/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-card">
      <img :src="logoDroite" alt="Logo" class="login-logo" />
      <h2>Connexion à Alimanaka</h2>
      <p>Veuillez vous connecter avec votre compte SSO</p>
      <button @click="handleLogin" class="btn-login-sso" :disabled="loading">
        {{ loading ? 'Connexion en cours...' : 'Se connecter avec SSO' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import logoDroite from '@/../public/logo_droite.svg'

const router = useRouter()
const { login } = useAuth()
const loading = ref(false)

const handleLogin = async () => {
  loading.value = true
  await login()
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  background: white;
  padding: 3rem;
  border-radius: 10px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.login-logo {
  height: 80px;
  margin-bottom: 1.5rem;
}

h2 {
  color: #333;
  margin-bottom: 0.5rem;
}

p {
  color: #666;
  margin-bottom: 2rem;
}

.btn-login-sso {
  width: 100%;
  padding: 1rem;
  background-color: #3498db;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  font-weight: bold;
  cursor: pointer;
  transition: background-color 0.3s;
}

.btn-login-sso:hover:not(:disabled) {
  background-color: #2980b9;
}

.btn-login-sso:disabled {
  background-color: #95a5a6;
  cursor: not-allowed;
}
</style>