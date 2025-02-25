import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import store from './store';
import dayjs from 'dayjs';
import 'dayjs/locale/es';

// Configuración de dayjs
dayjs.locale('es'); // Usar español

// Crear la aplicación
const app = createApp(App);

// Registrar directivas globales si son necesarias
app.directive('focus', {
  mounted(el) {
    el.focus();
  }
});

// Registrar filtros globales como propiedades computadas
app.config.globalProperties.$filters = {
  formatDate(value, format = 'DD/MM/YYYY') {
    if (!value) return '';
    return dayjs(value).format(format);
  },
  
  formatMoney(value) {
    if (value === undefined || value === null) return '-';
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(value);
  }
};

// Configuración del manejador de errores global
app.config.errorHandler = (err, vm, info) => {
  console.error('Error global:', err);
  console.error('Componente:', vm);
  console.error('Info:', info);
  
  // Mostrar mensaje de error global si lo deseamos
  store.dispatch('ui/mostrarError', 'Ha ocurrido un error inesperado');
};

// Montar la aplicación
app.use(store)
   .use(router)
   .mount('#app');