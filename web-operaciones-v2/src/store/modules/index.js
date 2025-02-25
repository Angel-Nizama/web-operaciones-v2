import { createStore } from 'vuex';
import VuexPersistence from 'vuex-persist';
import operaciones from './modules/operaciones';
import afiliados from './modules/afiliados';
import emparejador from './modules/emparejador';
import ui from './modules/ui';

// Configurar persistencia de estado
const vuexLocal = new VuexPersistence({
  storage: window.localStorage,
  key: 'web-operaciones',
  reducer: (state) => ({
    // Solo persistir ciertas partes del estado
    operaciones: {
      filtros: state.operaciones.filtros,
      paginacion: state.operaciones.paginacion,
    },
    afiliados: {
      filtros: state.afiliados.filtros,
      paginacion: state.afiliados.paginacion,
    },
    emparejador: {
      configuracion: state.emparejador.configuracion
    },
    ui: {
      ultimaSeccion: state.ui.ultimaSeccion
    }
  })
});

export default createStore({
  modules: {
    operaciones,
    afiliados,
    emparejador,
    ui
  },
  plugins: [vuexLocal.plugin]
});