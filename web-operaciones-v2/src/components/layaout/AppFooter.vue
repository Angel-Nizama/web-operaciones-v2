<template>
  <footer class="app-footer">
    <div class="container">
      <p>&copy; {{ currentYear }} Sistema de Gestión de Operaciones - Todos los derechos reservados.</p>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'AppFooter',
  computed: {
    currentYear() {
      return new Date().getFullYear();
    }
  }
};
</script>

<style scoped>
.app-footer {
  background-color: var(--color-terciario);
  color: var(--color-blanco);
  padding: var(--spacing-md) 0;
  text-align: center;
  font-size: 0.9rem;
  margin-top: auto;
}
</style>