<template>
  <div class="app-layout">
    <AppHeader />
    
    <main class="main-content">
      <div class="container">
        <slot></slot>
      </div>
    </main>
    
    <AppFooter />
    
    <Mensajes />
    <Confirmacion />
  </div>
</template>

<script>
import AppHeader from './AppHeader.vue';
import AppFooter from './AppFooter.vue';
import Mensajes from '@/components/common/Mensajes.vue';
import Confirmacion from '@/components/common/Confirmacion.vue';

export default {
  name: 'AppLayout',
  components: {
    AppHeader,
    AppFooter,
    Mensajes,
    Confirmacion
  }
};
</script>

<style>
/* Variables globales */
:root {
  /* Colores principales */
  --color-primario: #0078d7;
  --color-secundario: #005bb5;
  --color-terciario: #003166;
  --color-fondo: #f4f4f9;
  --color-texto: #333333;
  --color-texto-claro: #666666;
  --color-blanco: #ffffff;
  
  /* Variables de color para consistencia */
  --color-borde: #dddddd;
  --color-fondo-hover: #f5f5f5;
  --color-fondo-alterno: #f9f9f9;
  
  /* Colores de estado */
  --color-error: #dc3545;
  --color-exito: #28a745;
  --color-info: #17a2b8;
  --color-advertencia: #ffc107;
  --color-hover: #004494;
  
  /* Espaciado */
  --spacing-xs: 0.25rem;   /* 4px */
  --spacing-sm: 0.5rem;    /* 8px */
  --spacing-md: 1rem;      /* 16px */
  --spacing-lg: 1.5rem;    /* 24px */
  --spacing-xl: 2rem;      /* 32px */
  
  /* Bordes y sombras */
  --border-radius-sm: 3px;
  --border-radius-md: 5px;
  --border-radius-lg: 8px;
  --box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  --box-shadow-hover: 0 4px 8px rgba(0, 0, 0, 0.15);
  
  /* Transiciones */
  --transition-fast: 150ms ease-in-out;
  --transition-normal: 250ms ease-in-out;
  --transition-slow: 350ms ease-in-out;
}

/* Reset y estilos base */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  line-height: 1.6;
  color: var(--color-texto);
  background-color: var(--color-fondo);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* Layout y contenedores */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
  width: 100%;
}

.app-layout {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding: var(--spacing-lg) 0;
}

/* Clases de utilidad */
.text-center {
  text-align: center;
}

.mt-1 { margin-top: var(--spacing-sm); }
.mt-2 { margin-top: var(--spacing-md); }
.mt-3 { margin-top: var(--spacing-lg); }
.mb-1 { margin-bottom: var(--spacing-sm); }
.mb-2 { margin-bottom: var(--spacing-md); }
.mb-3 { margin-bottom: var(--spacing-lg); }

/* Estilos de botones y formularios */
.btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: var(--border-radius-md);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
  text-align: center;
  border: none;
  font-size: 0.9rem;
}

.btn-primario {
  background-color: var(--color-primario);
  color: white;
}

.btn-primario:hover:not(:disabled) {
  background-color: var(--color-secundario);
}

.btn-secundario {
  background-color: #f5f5f5;
  color: var(--color-texto);
  border: 1px solid var(--color-borde);
}

.btn-secundario:hover:not(:disabled) {
  background-color: #e5e5e5;
}

.btn-peligro {
  background-color: var(--color-error);
  color: white;
}

.btn-peligro:hover:not(:disabled) {
  background-color: #bd2130;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Form controls */
.form-control {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 1rem;
  line-height: 1.5;
  color: var(--color-texto);
  background-color: #fff;
  background-clip: padding-box;
  border: 1px solid var(--color-borde);
  border-radius: var(--border-radius-md);
  transition: border-color var(--transition-fast);
}

.form-control:focus {
  border-color: var(--color-primario);
  outline: 0;
  box-shadow: 0 0 0 0.2rem rgba(0, 120, 215, 0.25);
}

/* Form groups */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
}

/* Responsive */
@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
}
</style>