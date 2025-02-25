<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <h2>Página no encontrada</h2>
      <p>Lo sentimos, la página que buscas no existe o ha sido movida.</p>
      <router-link to="/" class="btn btn-primario">Volver al inicio</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
};
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  text-align: center;
}

.not-found-content {
  background-color: white;
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow);
  max-width: 500px;
}

h1 {
  font-size: 5rem;
  color: var(--color-primario);
  margin: 0;
  line-height: 1;
}

h2 {
  font-size: 1.5rem;
  margin: var(--spacing-md) 0;
  color: var(--color-texto);
}

p {
  margin-bottom: var(--spacing-lg);
  color: var(--color-texto-claro);
}

.btn {
  display: inline-block;
  padding: var(--spacing-sm) var(--spacing-lg);
  text-decoration: none;
}
</style>