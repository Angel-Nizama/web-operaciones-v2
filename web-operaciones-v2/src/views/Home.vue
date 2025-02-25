<template>
  <div class="home">
    <div class="bienvenida-container">
      <h2>¡Bienvenido al Sistema de Gestión de Operaciones!</h2>
      
      <div class="bienvenida-content">
        <p class="bienvenida-descripcion">
          Este sistema te permite gestionar y optimizar tus operaciones de manera eficiente:
        </p>
        
        <div class="caracteristicas-grid">
          <div class="caracteristica-card" @click="navigateTo('/emparejador')">
            <h3>Emparejador de Operaciones</h3>
            <p>Optimiza el emparejamiento de operaciones entre afiliados basado en criterios específicos y rangos personalizables.</p>
            <div class="card-action">
              <button class="btn btn-primario">Ir al Emparejador</button>
            </div>
          </div>
          
          <div class="caracteristica-card" @click="navigateTo('/operaciones')">
            <h3>Histórico de Operaciones</h3>
            <p>Mantén un registro detallado de todas las operaciones realizadas, con opciones avanzadas de filtrado y búsqueda.</p>
            <div class="card-action">
              <button class="btn btn-primario">Ver Histórico</button>
            </div>
          </div>
          
          <div class="caracteristica-card" @click="navigateTo('/afiliados')">
            <h3>Gestión de Afiliados</h3>
            <p>Administra la información de tus afiliados, monitorea su estado y mantén sus datos actualizados.</p>
            <div class="card-action">
              <button class="btn btn-primario">Ver Afiliados</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView',
  methods: {
    navigateTo(route) {
      this.$router.push(route);
    }
  }
};
</script>

<style scoped>
.bienvenida-container {
  max-width: 1000px;
  margin: 0 auto;
  padding: var(--spacing-xl);
  background-color: white;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--box-shadow);
}

.bienvenida-container h2 {
  color: var(--color-primario);
  font-size: 2rem;
  margin-bottom: var(--spacing-xl);
  text-align: center;
}

.bienvenida-descripcion {
  font-size: 1.2rem;
  color: var(--color-texto);
  margin-bottom: var(--spacing-xl);
  line-height: 1.6;
  text-align: center;
}

.caracteristicas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: var(--spacing-lg);
  margin: var(--spacing-xl) 0;
}

.caracteristica-card {
  background-color: var(--color-blanco);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--box-shadow);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
  cursor: pointer;
  display: flex;
  flex-direction: column;
}

.caracteristica-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--box-shadow-hover);
}

.caracteristica-card h3 {
  color: var(--color-primario);
  margin-bottom: var(--spacing-md);
  font-size: 1.3rem;
}

.caracteristica-card p {
  color: var(--color-texto);
  line-height: 1.5;
  flex-grow: 1;
}

.card-action {
  margin-top: var(--spacing-lg);
  text-align: center;
}

@media (max-width: 768px) {
  .bienvenida-container h2 {
    font-size: 1.75rem;
  }

  .bienvenida-container {
    padding: var(--spacing-lg);
  }

  .caracteristicas-grid {
    grid-template-columns: 1fr;
  }
}
</style>