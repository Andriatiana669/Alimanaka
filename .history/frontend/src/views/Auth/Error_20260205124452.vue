<template>
  <div class="not-found">
    <div class="container">
      <div class="error-code">404</div>
      <h1>Page non trouvée</h1>
      <p>Désolé, la page que vous cherchez n'existe pas ou a été déplacée.</p>
      <div class="actions">
        <router-link to="/dashboard" class="btn-primary">
          <span class="icon">←</span>
          Retour au tableau de bord
        </router-link>
        <button @click="goBack" class="btn-secondary">
          <span class="icon">↰</span>
          Page précédente
        </button>
      </div>
      <div class="tips">
        <h3>Que pouvez-vous faire ?</h3>
        <ul>
          <li>Vérifier l'URL dans la barre d'adresse</li>
          <li>Utiliser la navigation par le menu latéral</li>
          <li>Contacter l'administrateur si le problème persiste</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

const goBack = () => {
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/dashboard')
  }
}
</script>

<style scoped>
.not-found {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - 200px);
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.container {
  text-align: center;
  max-width: 600px;
  background: white;
  padding: 3rem;
  border-radius: 15px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
}

.error-code {
  font-size: 8rem;
  font-weight: 900;
  color: #e74c3c;
  line-height: 1;
  margin-bottom: 1rem;
  text-shadow: 3px 3px 0 #f1f3f5;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

p {
  color: #7f8c8d;
  font-size: 1.2rem;
  margin-bottom: 2.5rem;
  line-height: 1.6;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 3rem;
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  text-decoration: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3498db, #2980b9);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(52, 152, 219, 0.4);
}

.btn-secondary {
  background: #f8f9fa;
  color: #495057;
  border: 2px solid #dee2e6;
}

.btn-secondary:hover {
  background: #e9ecef;
  transform: translateY(-2px);
}

.icon {
  font-size: 1.2rem;
  font-weight: bold;
}

.tips {
  text-align: left;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border-left: 4px solid #3498db;
}

.tips h3 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 1rem;
}

.tips ul {
  margin: 0;
  padding-left: 1.5rem;
}

.tips li {
  color: #6c757d;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.tips li:last-child {
  margin-bottom: 0;
}

@media (max-width: 600px) {
  .container {
    padding: 2rem 1.5rem;
  }
  
  .error-code {
    font-size: 6rem;
  }
  
  h1 {
    font-size: 2rem;
  }
  
  .actions {
    flex-direction: column;
  }
  
  .btn-primary, .btn-secondary {
    justify-content: center;
  }
}
</style>