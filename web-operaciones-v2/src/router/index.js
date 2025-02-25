import { createRouter, createWebHistory } from 'vue-router';
import store from '@/store';

// Importación de vistas
const Home = () => import('@/views/Home.vue');
const Operaciones = () => import('@/views/operaciones/Operaciones.vue');
const Afiliados = () => import('@/views/afiliados/Afiliados.vue');
const EmparejadorRangos = () => import('@/views/emparejador/EmparejadorRangos.vue');
const EmparejadorCalculador = () => import('@/views/emparejador/EmparejadorCalculador.vue');
const NotFound = () => import('@/views/NotFound.vue');

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { title: 'Inicio' }
  },
  {
    path: '/operaciones',
    name: 'Operaciones',
    component: Operaciones,
    meta: { title: 'Histórico de Operaciones' }
  },
  {
    path: '/afiliados',
    name: 'Afiliados',
    component: Afiliados,
    meta: { title: 'Gestión de Afiliados' }
  },
  {
    path: '/emparejador',
    name: 'EmparejadorRangos',
    component: EmparejadorRangos,
    meta: { title: 'Emparejador - Gestión de Rangos' }
  },
  {
    path: '/emparejador/calcular',
    name: 'EmparejadorCalculador',
    component: EmparejadorCalculador,
    meta: { title: 'Emparejador - Cálculo de Emparejamientos' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { title: 'Página no encontrada' }
  }
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition;
    } else {
      return { top: 0 };
    }
  }
});

// Interceptor de navegación
router.beforeEach((to, from, next) => {
  // Actualizar título de la página
  document.title = `${to.meta.title || 'Sistema de Gestión'} | Web Operaciones`;
  
  // Guardar última sección visitada
  store.dispatch('ui/cambiarSeccion', to.name);
  
  next();
});

export default router;