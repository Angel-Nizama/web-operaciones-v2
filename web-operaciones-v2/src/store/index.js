// src/store/index.js
import { createStore } from 'vuex';
import operaciones from './modules/operaciones';
import afiliados from './modules/afiliados';
import emparejador from './modules/emparejador';
import ui from './modules/ui';

export default createStore({
  modules: {
    operaciones,
    afiliados,
    emparejador,
    ui
  }
});