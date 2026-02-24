<!-- frontend/src/components/Layout/Navbar.vue -->
<template>
  <nav class="navbar">
    <div class="navbar-brand">
      <img :src="logoGauche" alt="Logo" class="logo" />
      <h1>Alimanaka</h1>
    </div>
    <div class="navbar-menu">
      <div v-if="user" class="user-info">
        <span>{{ user.display_name }}</span>
        <button @click="logout" class="btn-logout">Déconnexion</button>
      </div>
      <button v-else @click="login" class="btn-login">Connexion</button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useAuth } from '@/composables/useAuth'
import logoGauche from '@/../public/logo_gauche.svg'

const { user, login, logout } = useAuth()
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2c3e50;
  color: white;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo {
  height: 40px;
}

.navbar-brand h1 {
  margin: 0;
  font-size: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn-login,
.btn-logout {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-login {
  background-color: #3498db;
  color: white;
}

.btn-logout {
  background-color: #e74c3c;
  color: white;
}

.btn-login:hover {
  background-color: #2980b9;
}

.btn-logout:hover {
  background-color: #c0392b;
}
</style>