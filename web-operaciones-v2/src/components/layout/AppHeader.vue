<template>
  <header class="app-header">
    <div class="container">
      <h1 class="app-title">Sistema de Gestión de Operaciones</h1>
    </div>
    <nav class="app-nav">
      <div class="container">
        <ul class="nav-list">
          <li>
            <router-link to="/" exact>Inicio</router-link>
          </li>
          <li>
            <router-link to="/emparejador">Emparejador</router-link>
          </li>
          <li>
            <router-link to="/operaciones">Histórico de Operaciones</router-link>
          </li>
          <li>
            <router-link to="/afiliados">Afiliados</router-link>
          </li>
        </ul>
      </div>
    </nav>
  </header>
</template>

<script>
export default {
  name: 'AppHeader'
};
</script>

<style scoped>
.app-header {
  background-color: var(--color-primario);
  color: var(--color-blanco);
  box-shadow: var(--box-shadow);
  position: relative;
  z-index: 10;
}

.app-title {
  margin: 0;
  padding: var(--spacing-md) 0;
  font-size: 1.75rem;
  text-align: center;
  font-weight: 600;
  letter-spacing: -0.5px;
}

.app-nav {
  background-color: var(--color-secundario);
  position: relative;
  z-index: 9;
}

.nav-list {
  list-style: none;
  display: flex;
  justify-content: center;
  margin: 0;
  padding: 0;
  flex-wrap: wrap;
}

.nav-list li {
  position: relative;
}

.nav-list li a {
  display: block;
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-blanco);
  text-decoration: none;
  transition: background-color var(--transition-fast);
  white-space: nowrap;
}

.nav-list li a:hover {
  background-color: var(--color-hover);
}

.nav-list li a.router-link-active {
  background-color: var(--color-terciario);
  font-weight: 500;
}

@media (max-width: 768px) {
  .app-title {
    font-size: 1.5rem;
  }

  .nav-list {
    flex-direction: column;
  }

  .nav-list li a {
    text-align: center;
    padding: var(--spacing-sm) var(--spacing-md);
  }
}
</style>